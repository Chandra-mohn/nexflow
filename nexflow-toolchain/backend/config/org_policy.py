# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Organization Policy Module

Loads and manages organization-level serialization policies from nexflow-org.toml.
Organization policies define what serialization formats teams/projects CAN use.

Governance Hierarchy:
    Organization (nexflow-org.toml)
        └── Team/Project (nexflow.toml)
             └── Schema (.schema file)
                  └── Connector (.proc file)

Higher levels CONSTRAIN what lower levels can use.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Set, List

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

from backend.ast.serialization import SerializationFormat


@dataclass
class OrganizationPolicy:
    """
    Organization-level serialization policy.

    Defines which formats are permitted across the organization
    and sets organizational defaults.
    """

    # Formats permitted for use in this organization
    allowed_formats: Set[SerializationFormat] = field(
        default_factory=lambda: {f for f in SerializationFormat}
    )

    # Default format when not specified at any lower level
    default_format: SerializationFormat = SerializationFormat.JSON

    # Formats that require schema registry (enforced)
    require_registry_for: Set[SerializationFormat] = field(
        default_factory=lambda: {SerializationFormat.CONFLUENT_AVRO}
    )

    # Source file path (for error messages)
    source_path: Optional[Path] = None

    @classmethod
    def permissive(cls) -> 'OrganizationPolicy':
        """
        Create a permissive policy allowing all formats.

        Used when no nexflow-org.toml is found (backward compatibility).
        """
        return cls(
            allowed_formats={f for f in SerializationFormat},
            default_format=SerializationFormat.JSON,
        )

    @classmethod
    def from_dict(cls, data: dict, source_path: Optional[Path] = None) -> 'OrganizationPolicy':
        """
        Create policy from dictionary (parsed TOML).

        Expected structure:
            [serialization]
            allowed_formats = ["json", "avro", "confluent_avro"]
            default_format = "confluent_avro"
            require_registry_for = ["confluent_avro"]
        """
        serialization = data.get('serialization', {})

        # Parse allowed formats
        allowed_raw = serialization.get('allowed_formats', [])
        if allowed_raw:
            allowed_formats = {
                SerializationFormat.from_string(f) for f in allowed_raw
            }
        else:
            # No restriction = all formats allowed
            allowed_formats = {f for f in SerializationFormat}

        # Parse default format
        default_raw = serialization.get('default_format', 'json')
        default_format = SerializationFormat.from_string(default_raw)

        # Validate default is in allowed
        if default_format not in allowed_formats:
            raise ValueError(
                f"Organization default_format '{default_format.value}' "
                f"is not in allowed_formats: {[f.value for f in allowed_formats]}"
            )

        # Parse registry requirements
        registry_raw = serialization.get('require_registry_for', ['confluent_avro'])
        require_registry_for = {
            SerializationFormat.from_string(f) for f in registry_raw
        }

        return cls(
            allowed_formats=allowed_formats,
            default_format=default_format,
            require_registry_for=require_registry_for,
            source_path=source_path,
        )

    def is_format_allowed(self, fmt: SerializationFormat) -> bool:
        """Check if a format is permitted by this policy."""
        return fmt in self.allowed_formats

    def requires_registry(self, fmt: SerializationFormat) -> bool:
        """Check if a format requires schema registry."""
        return fmt in self.require_registry_for

    def get_allowed_format_names(self) -> List[str]:
        """Get list of allowed format names (for error messages)."""
        return sorted(f.value for f in self.allowed_formats)


def find_org_policy_file(start_path: Path) -> Optional[Path]:
    """
    Find nexflow-org.toml by walking up the directory tree.

    Organization policy files can be placed at:
    - Project root
    - Parent directories (for multi-project repos)
    - Repository root

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to nexflow-org.toml if found, None otherwise
    """
    current = start_path.resolve()
    if current.is_file():
        current = current.parent

    while current != current.parent:
        policy_file = current / "nexflow-org.toml"
        if policy_file.exists():
            return policy_file

        # Also check in .nexflow directory
        nexflow_dir_policy = current / ".nexflow" / "org-policy.toml"
        if nexflow_dir_policy.exists():
            return nexflow_dir_policy

        current = current.parent

    return None


def load_org_policy(
    start_path: Path,
    strict: bool = False
) -> OrganizationPolicy:
    """
    Load organization policy from nexflow-org.toml.

    If no policy file is found:
    - strict=True: raises FileNotFoundError
    - strict=False: returns permissive policy (all formats allowed)

    Args:
        start_path: Directory to start searching from
        strict: Whether to require a policy file

    Returns:
        OrganizationPolicy instance
    """
    policy_path = find_org_policy_file(start_path)

    if policy_path is None:
        if strict:
            raise FileNotFoundError(
                f"No nexflow-org.toml found in directory tree from {start_path}"
            )
        return OrganizationPolicy.permissive()

    try:
        with open(policy_path, 'rb') as f:
            data = tomllib.load(f)
        return OrganizationPolicy.from_dict(data, source_path=policy_path)
    except Exception as e:
        if strict:
            raise ValueError(f"Failed to load org policy from {policy_path}: {e}")
        # Return permissive on error for backward compatibility
        return OrganizationPolicy.permissive()
