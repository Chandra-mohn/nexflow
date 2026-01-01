# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Policy Validator Module

Validates serialization format choices against organization policies.
Enforces top-down governance: Org -> Team -> Schema -> Connector.

Enforcement behavior:
    - Violation of org policy: Warning (allows build to proceed)
    - Missing format specification: Uses org default with info message
    - Registry requirement violation: Error (blocks build)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

from backend.ast.serialization import SerializationFormat
from backend.config.org_policy import OrganizationPolicy


class ViolationLevel(Enum):
    """Severity level of policy violations."""
    INFO = "info"       # Informational (e.g., using default)
    WARNING = "warning"  # Policy violation but build continues
    ERROR = "error"      # Critical violation, blocks build


@dataclass
class PolicyViolation:
    """
    Represents a policy violation or informational message.

    Attributes:
        level: Severity of the violation
        message: Human-readable description
        source_file: File where violation was detected
        requested_format: Format that was requested
        allowed_formats: Formats permitted by policy
        suggestion: Recommended action
    """
    level: ViolationLevel
    message: str
    source_file: Optional[Path] = None
    requested_format: Optional[SerializationFormat] = None
    allowed_formats: Optional[List[SerializationFormat]] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"[{self.level.value.upper()}] {self.message}"]
        if self.source_file:
            parts.append(f"  File: {self.source_file}")
        if self.requested_format:
            parts.append(f"  Requested: {self.requested_format.value}")
        if self.allowed_formats:
            allowed = ", ".join(f.value for f in self.allowed_formats)
            parts.append(f"  Allowed: {allowed}")
        if self.suggestion:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)


@dataclass
class ValidationResult:
    """
    Result of policy validation.

    Attributes:
        violations: List of all violations found
        resolved_format: The format to use after policy resolution
        used_default: Whether the org default was applied
    """
    violations: List[PolicyViolation] = field(default_factory=list)
    resolved_format: Optional[SerializationFormat] = None
    used_default: bool = False

    @property
    def has_errors(self) -> bool:
        """Check if any error-level violations exist."""
        return any(v.level == ViolationLevel.ERROR for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        """Check if any warning-level violations exist."""
        return any(v.level == ViolationLevel.WARNING for v in self.violations)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return not self.has_errors

    def add_violation(self, violation: PolicyViolation) -> None:
        """Add a violation to the result."""
        self.violations.append(violation)

    def get_messages(self, min_level: ViolationLevel = ViolationLevel.INFO) -> List[str]:
        """Get formatted messages at or above the specified level."""
        level_order = [ViolationLevel.INFO, ViolationLevel.WARNING, ViolationLevel.ERROR]
        min_index = level_order.index(min_level)
        return [
            str(v) for v in self.violations
            if level_order.index(v.level) >= min_index
        ]


class PolicyValidator:
    """
    Validates serialization format choices against organization policy.

    Implements the governance hierarchy:
        Organization -> Team -> Schema -> Connector

    Each level can only use formats allowed by the level above.
    """

    def __init__(self, org_policy: OrganizationPolicy):
        """
        Initialize validator with organization policy.

        Args:
            org_policy: The organization-level policy to enforce
        """
        self.org_policy = org_policy

    def validate_format(
        self,
        requested_format: Optional[SerializationFormat],
        source_file: Optional[Path] = None,
        context: str = "connector"
    ) -> ValidationResult:
        """
        Validate a format choice against organization policy.

        Args:
            requested_format: The format requested (None = use default)
            source_file: File making the request (for error messages)
            context: Description of where format is being used

        Returns:
            ValidationResult with resolved format and any violations
        """
        result = ValidationResult()

        # Case 1: No format specified -> use org default
        if requested_format is None:
            result.resolved_format = self.org_policy.default_format
            result.used_default = True
            result.add_violation(PolicyViolation(
                level=ViolationLevel.INFO,
                message=f"No serialization format specified for {context}. "
                        f"Using organization default: {self.org_policy.default_format.value}",
                source_file=source_file,
                suggestion=f"Add 'serialization: {self.org_policy.default_format.value}' "
                          f"to explicitly set the format"
            ))
            return result

        # Case 2: Format specified but not allowed by org policy
        if not self.org_policy.is_format_allowed(requested_format):
            result.resolved_format = self.org_policy.default_format
            result.used_default = True
            result.add_violation(PolicyViolation(
                level=ViolationLevel.WARNING,
                message=f"Format '{requested_format.value}' is not allowed "
                        f"by organization policy for {context}",
                source_file=source_file,
                requested_format=requested_format,
                allowed_formats=list(self.org_policy.allowed_formats),
                suggestion=f"Change to an allowed format or update organization policy. "
                          f"Using default: {self.org_policy.default_format.value}"
            ))
            return result

        # Case 3: Format allowed -> use it
        result.resolved_format = requested_format
        return result

    def validate_registry_requirement(
        self,
        format: SerializationFormat,
        has_registry_config: bool,
        source_file: Optional[Path] = None
    ) -> ValidationResult:
        """
        Validate that formats requiring schema registry have it configured.

        Args:
            format: The serialization format being used
            has_registry_config: Whether schema registry is configured
            source_file: File where format is being used

        Returns:
            ValidationResult with any registry-related violations
        """
        result = ValidationResult()
        result.resolved_format = format

        if self.org_policy.requires_registry(format) and not has_registry_config:
            result.add_violation(PolicyViolation(
                level=ViolationLevel.ERROR,
                message=f"Format '{format.value}' requires schema registry "
                        f"but none is configured",
                source_file=source_file,
                requested_format=format,
                suggestion="Configure schema registry in nexflow.toml under "
                          "[kafka.schema_registry] or choose a format that "
                          "doesn't require registry (e.g., json, avro)"
            ))

        return result

    def validate_connector_config(
        self,
        connector_format: Optional[SerializationFormat],
        schema_format: Optional[SerializationFormat],
        team_format: Optional[SerializationFormat],
        has_registry: bool = False,
        source_file: Optional[Path] = None
    ) -> ValidationResult:
        """
        Validate full connector serialization configuration.

        Applies governance hierarchy:
            1. Check connector format against org policy
            2. If connector has no format, check schema format
            3. If schema has no format, check team format
            4. If nothing specified, use org default
            5. Validate registry requirements

        Args:
            connector_format: Format specified at connector level
            schema_format: Format specified at schema level
            team_format: Format specified at team/project level
            has_registry: Whether schema registry is configured
            source_file: Source file for error messages

        Returns:
            ValidationResult with resolved format and all violations
        """
        result = ValidationResult()

        # Determine effective format using hierarchy
        effective_format = None
        format_source = "organization default"

        if connector_format is not None:
            effective_format = connector_format
            format_source = "connector"
        elif schema_format is not None:
            effective_format = schema_format
            format_source = "schema"
        elif team_format is not None:
            effective_format = team_format
            format_source = "team"

        # Validate the effective format against org policy
        format_result = self.validate_format(
            effective_format,
            source_file=source_file,
            context=format_source
        )
        result.violations.extend(format_result.violations)
        result.resolved_format = format_result.resolved_format
        result.used_default = format_result.used_default

        # Validate registry requirements
        if result.resolved_format:
            registry_result = self.validate_registry_requirement(
                result.resolved_format,
                has_registry,
                source_file=source_file
            )
            result.violations.extend(registry_result.violations)

        return result


def create_validator(project_path: Path, strict: bool = False) -> PolicyValidator:
    """
    Create a policy validator for a project.

    Convenience function that loads org policy and creates validator.

    Args:
        project_path: Path to project directory
        strict: Whether to require org policy file

    Returns:
        PolicyValidator configured with org policy
    """
    from backend.config.org_policy import load_org_policy

    policy = load_org_policy(project_path, strict=strict)
    return PolicyValidator(policy)
