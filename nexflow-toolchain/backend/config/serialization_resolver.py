# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Serialization Configuration Resolver

Resolves effective serialization configuration using hierarchical lookup
with organization policy enforcement:

Governance Hierarchy (top-down constraint):
    1. Organization policy (nexflow-org.toml) - CONSTRAINS what's allowed
    2. Team config (nexflow.toml) - Can only use org-allowed formats
    3. Schema-level declaration - Can only use org-allowed formats
    4. Process-level override - Can only use org-allowed formats

Legacy hierarchy (for merging within allowed formats):
    1. Process-level override (highest priority)
    2. Schema-level declaration
    3. Team config (nexflow.toml)
    4. Environment overlay (nexflow.{env}.toml)
    5. Organization default (nexflow-org.toml)
    6. Built-in default (json)

Supports multi-team environments with distributed configuration.
"""

import os
from pathlib import Path
from typing import Optional, List, Callable

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

from backend.ast.serialization import (
    GlobalSerializationConfig,
    SerializationConfig,
    SerializationFormat,
)
from backend.config.org_policy import OrganizationPolicy, load_org_policy
from backend.config.policy_validator import (
    PolicyValidator,
    ValidationResult,
)


class SerializationResolver:
    """
    Resolves serialization configuration from hierarchical sources
    with organization policy enforcement.

    Usage:
        resolver = SerializationResolver(process_file_path, environment='prod')
        config, result = resolver.get_effective_config_with_validation(
            schema_config, process_override
        )
        if result.has_warnings:
            for msg in result.get_messages(ViolationLevel.WARNING):
                print(msg)
    """

    def __init__(
        self,
        process_file_path: str,
        environment: Optional[str] = None,
        strict_policy: bool = False,
    ):
        """
        Initialize resolver for a specific process file.

        Args:
            process_file_path: Path to the .proc file being compiled
            environment: Environment name (dev, staging, prod).
                        Falls back to NEXFLOW_ENV env var.
            strict_policy: If True, requires nexflow-org.toml to exist
        """
        self.process_path = Path(process_file_path).resolve()
        self.process_dir = self.process_path.parent
        self.environment = environment or os.environ.get("NEXFLOW_ENV", "")
        self.strict_policy = strict_policy
        self._global_config: Optional[GlobalSerializationConfig] = None
        self._org_policy: Optional[OrganizationPolicy] = None
        self._validator: Optional[PolicyValidator] = None
        self._violation_handlers: List[Callable[[ValidationResult], None]] = []

    def get_org_policy(self) -> OrganizationPolicy:
        """
        Load organization policy from nexflow-org.toml.

        Returns permissive policy if no file found (backward compatibility).
        """
        if self._org_policy is None:
            self._org_policy = load_org_policy(
                self.process_dir,
                strict=self.strict_policy
            )
        return self._org_policy

    def get_validator(self) -> PolicyValidator:
        """Get policy validator instance."""
        if self._validator is None:
            self._validator = PolicyValidator(self.get_org_policy())
        return self._validator

    def add_violation_handler(
        self,
        handler: Callable[[ValidationResult], None]
    ) -> None:
        """
        Add a handler to be called when violations are detected.

        Handlers receive the ValidationResult and can log, report, or
        otherwise process the violations.
        """
        self._violation_handlers.append(handler)

    def _notify_violations(self, result: ValidationResult) -> None:
        """Notify all registered handlers of validation result."""
        for handler in self._violation_handlers:
            handler(result)

    def get_global_config(self) -> GlobalSerializationConfig:
        """
        Load global configuration from nexflow.toml hierarchy.

        Walks up directory tree to find and merge config files.
        """
        if self._global_config is not None:
            return self._global_config

        config_chain: list[dict] = []
        current = self.process_dir

        # Walk up directory tree collecting configs
        while current != current.parent:
            base_config = current / "nexflow.toml"
            if base_config.exists():
                config_chain.insert(0, self._load_toml(base_config))

            # Environment-specific overlay (higher priority)
            if self.environment:
                env_config = current / f"nexflow.{self.environment}.toml"
                if env_config.exists():
                    config_chain.insert(0, self._load_toml(env_config))

            current = current.parent

        # Merge configs (later in chain = higher priority)
        merged = {}
        for cfg in reversed(config_chain):
            self._deep_merge(merged, cfg)

        # Extract serialization section
        serialization_section = merged.get("serialization", {})
        self._global_config = GlobalSerializationConfig.from_dict(serialization_section)

        return self._global_config

    def get_effective_config(
        self,
        schema_config: Optional[SerializationConfig] = None,
        process_override: Optional[SerializationConfig] = None,
    ) -> SerializationConfig:
        """
        Resolve effective serialization config using full hierarchy.

        This method maintains backward compatibility by returning only
        the config. Use get_effective_config_with_validation() to also
        get policy violation information.

        Args:
            schema_config: Config from schema's serialization block
            process_override: Explicit format override in process connector

        Returns:
            Resolved SerializationConfig with all values populated
        """
        config, _ = self.get_effective_config_with_validation(
            schema_config, process_override
        )
        return config

    def get_effective_config_with_validation(
        self,
        schema_config: Optional[SerializationConfig] = None,
        process_override: Optional[SerializationConfig] = None,
    ) -> tuple[SerializationConfig, ValidationResult]:
        """
        Resolve effective serialization config with policy validation.

        Applies organization policy governance:
        1. Determine requested format from hierarchy
        2. Validate against org policy
        3. Use org default if format not allowed (with warning)
        4. Validate registry requirements

        Args:
            schema_config: Config from schema's serialization block
            process_override: Explicit format override in process connector

        Returns:
            Tuple of (resolved config, validation result with any violations)
        """
        from dataclasses import replace

        global_config = self.get_global_config()
        org_policy = self.get_org_policy()
        validator = self.get_validator()

        # Validate against policy
        has_registry = bool(global_config.registry and global_config.registry.url)
        result = validator.validate_connector_config(
            connector_format=getattr(process_override, 'format', None),
            schema_format=getattr(schema_config, 'format', None),
            team_format=global_config.default_format,
            has_registry=has_registry,
            source_file=self.process_path,
        )

        if result.violations:
            self._notify_violations(result)

        # Build base config from global settings
        effective = SerializationConfig(
            format=result.resolved_format or org_policy.default_format,
            compatibility=global_config.avro_compatibility,
            registry_url=global_config.registry.url if global_config.registry else None,
        )

        # Layer configs using existing merge_with(), then enforce policy format
        if schema_config:
            effective = schema_config.merge_with(effective)
        if process_override:
            effective = process_override.merge_with(effective)

        # Ensure policy-resolved format is always used (policy overrides user choice)
        policy_format = result.resolved_format or org_policy.default_format
        if effective.format != policy_format:
            effective = replace(effective, format=policy_format)

        return effective, result

    def get_registry_url(self) -> Optional[str]:
        """Get schema registry URL from config."""
        config = self.get_global_config()
        return config.registry.url if config.registry else None

    def get_default_format(self) -> SerializationFormat:
        """
        Get default serialization format.

        Returns organization default if policy exists, otherwise team default.
        """
        org_policy = self.get_org_policy()
        return org_policy.default_format

    def get_allowed_formats(self) -> list[SerializationFormat]:
        """Get list of formats allowed by organization policy."""
        return list(self.get_org_policy().allowed_formats)

    def is_format_allowed(self, fmt: SerializationFormat) -> bool:
        """Check if a format is allowed by organization policy."""
        return self.get_org_policy().is_format_allowed(fmt)

    def _load_toml(self, path: Path) -> dict:
        """Load and parse a TOML file."""
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            # Log warning but don't fail - use defaults
            print(f"Warning: Could not load {path}: {e}")
            return {}

    def _deep_merge(self, base: dict, overlay: dict) -> None:
        """
        Deep merge overlay into base dict (mutates base).

        Overlay values take precedence over base values.
        Nested dicts are recursively merged.
        """
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


def resolve_serialization(
    process_file: str,
    schema_config: Optional[SerializationConfig] = None,
    process_override: Optional[SerializationConfig] = None,
    environment: Optional[str] = None,
) -> SerializationConfig:
    """
    Convenience function to resolve serialization config.

    Args:
        process_file: Path to .proc file being compiled
        schema_config: Config from schema's serialization block
        process_override: Explicit format override in connector
        environment: Environment name (optional)

    Returns:
        Resolved SerializationConfig
    """
    resolver = SerializationResolver(process_file, environment)
    return resolver.get_effective_config(schema_config, process_override)


def resolve_serialization_with_validation(
    process_file: str,
    schema_config: Optional[SerializationConfig] = None,
    process_override: Optional[SerializationConfig] = None,
    environment: Optional[str] = None,
    strict_policy: bool = False,
) -> tuple[SerializationConfig, ValidationResult]:
    """
    Convenience function to resolve serialization config with policy validation.

    Args:
        process_file: Path to .proc file being compiled
        schema_config: Config from schema's serialization block
        process_override: Explicit format override in connector
        environment: Environment name (optional)
        strict_policy: If True, requires nexflow-org.toml to exist

    Returns:
        Tuple of (resolved config, validation result)
    """
    resolver = SerializationResolver(
        process_file,
        environment,
        strict_policy=strict_policy
    )
    return resolver.get_effective_config_with_validation(schema_config, process_override)
