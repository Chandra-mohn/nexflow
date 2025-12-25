# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Serialization Configuration Resolver

Resolves effective serialization configuration using hierarchical lookup:
1. Process-level override (in .proc file)
2. Schema-level declaration (in .schema file)
3. Team config (nexflow.toml in process directory)
4. Environment overlay (nexflow.{env}.toml)
5. Built-in default (json)

Supports multi-team environments with distributed configuration.
"""

import os
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

from backend.ast.serialization import (
    GlobalSerializationConfig,
    SerializationConfig,
    SerializationFormat,
)


class SerializationResolver:
    """
    Resolves serialization configuration from hierarchical sources.

    Usage:
        resolver = SerializationResolver(process_file_path, environment='prod')
        config = resolver.get_effective_config(schema_config, process_override)
    """

    def __init__(
        self,
        process_file_path: str,
        environment: Optional[str] = None,
    ):
        """
        Initialize resolver for a specific process file.

        Args:
            process_file_path: Path to the .proc file being compiled
            environment: Environment name (dev, staging, prod).
                        Falls back to NEXFLOW_ENV env var.
        """
        self.process_path = Path(process_file_path).resolve()
        self.process_dir = self.process_path.parent
        self.environment = environment or os.environ.get("NEXFLOW_ENV", "")
        self._global_config: Optional[GlobalSerializationConfig] = None

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

        Args:
            schema_config: Config from schema's serialization block
            process_override: Explicit format override in process connector

        Returns:
            Resolved SerializationConfig with all values populated
        """
        global_config = self.get_global_config()
        return global_config.get_effective_config(schema_config, process_override)

    def get_registry_url(self) -> Optional[str]:
        """Get schema registry URL from config."""
        config = self.get_global_config()
        return config.registry.url if config.registry else None

    def get_default_format(self) -> SerializationFormat:
        """Get default serialization format from config."""
        return self.get_global_config().default_format

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
