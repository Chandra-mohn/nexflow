"""
Validation rules for Excel schema import.

Validates parsed data models before schema generation.
"""

from dataclasses import dataclass, field
from typing import Optional
import logging

from .models import ServiceDomain
from .graph import DomainGraph

logger = logging.getLogger(__name__)


class ValidationSeverity:
    """Validation issue severity levels."""
    ERROR = "ERROR"      # Abort import
    WARNING = "WARNING"  # Continue with warning


@dataclass
class ValidationIssue:
    """A validation error or warning."""
    severity: str
    code: str
    message: str
    entity: Optional[str] = None
    attribute: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation."""
    issues: list[ValidationIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return any(i.severity == ValidationSeverity.ERROR for i in self.issues)

    def errors(self) -> list[ValidationIssue]:
        """Get all errors."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def warnings(self) -> list[ValidationIssue]:
        """Get all warnings."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


class SchemaValidator:
    """Validate parsed domain model before schema generation."""

    def __init__(self, domain: ServiceDomain, graph: DomainGraph):
        self.domain = domain
        self.graph = graph
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Run all validations and return result."""
        self._validate_entities()
        self._validate_attributes()
        self._validate_relationships()
        self._validate_enums()
        self._validate_graph()

        return self.result

    def _add_error(self, code: str, message: str, entity: str = None, attribute: str = None):
        """Add an error issue."""
        self.result.issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code=code,
            message=message,
            entity=entity,
            attribute=attribute,
        ))

    def _add_warning(self, code: str, message: str, entity: str = None, attribute: str = None):
        """Add a warning issue."""
        self.result.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code=code,
            message=message,
            entity=entity,
            attribute=attribute,
        ))

    def _validate_entities(self):
        """Validate entity definitions."""
        seen_collections = {}

        for entity_name, entity in self.domain.entities.items():
            # Check for duplicate collection names
            collection = entity.collection_name or entity_name
            if collection in seen_collections:
                self._add_error(
                    "DUPLICATE_COLLECTION",
                    f"Collection name '{collection}' used by both "
                    f"'{seen_collections[collection]}' and '{entity_name}'",
                    entity=entity_name,
                )
            else:
                seen_collections[collection] = entity_name

            # Validate entity has at least one attribute (unless shortcut)
            if not entity.is_shortcut() and len(entity.attributes) == 0:
                self._add_warning(
                    "EMPTY_ENTITY",
                    f"Entity '{entity_name}' has no attributes",
                    entity=entity_name,
                )

            # Check for primary key
            has_primary = any(a.primary_identifier for a in entity.attributes)
            if not entity.is_shortcut() and not has_primary:
                self._add_warning(
                    "NO_PRIMARY_KEY",
                    f"Entity '{entity_name}' has no primary identifier",
                    entity=entity_name,
                )

    def _validate_attributes(self):
        """Validate attribute definitions."""
        for entity_name, entity in self.domain.entities.items():
            seen_attrs = set()

            for attr in entity.attributes:
                # Check for duplicate attribute names
                attr_lower = attr.name.lower()
                if attr_lower in seen_attrs:
                    self._add_error(
                        "DUPLICATE_ATTRIBUTE",
                        f"Duplicate attribute name '{attr.name}' in entity '{entity_name}'",
                        entity=entity_name,
                        attribute=attr.name,
                    )
                else:
                    seen_attrs.add(attr_lower)

                # Validate datatype
                if not attr.datatype:
                    self._add_warning(
                        "MISSING_DATATYPE",
                        f"Attribute '{attr.name}' in entity '{entity_name}' has no datatype",
                        entity=entity_name,
                        attribute=attr.name,
                    )

                # Validate foreign key reference exists
                if attr.foreign_identifier and attr.foreign_parent_entity:
                    if attr.foreign_parent_entity not in self.domain.entities:
                        self._add_warning(
                            "INVALID_FOREIGN_REF",
                            f"Attribute '{attr.name}' references unknown entity "
                            f"'{attr.foreign_parent_entity}'",
                            entity=entity_name,
                            attribute=attr.name,
                        )

                # Check enum has values
                if attr.is_enum():
                    if attr.name not in entity.enum_values:
                        self._add_warning(
                            "ENUM_NO_VALUES",
                            f"Attribute '{attr.name}' is marked as Enum but has no enum values",
                            entity=entity_name,
                            attribute=attr.name,
                        )

                # PII without handler (informational)
                if attr.pii_pci_indicator:
                    self._add_warning(
                        "PII_FIELD",
                        f"Attribute '{attr.name}' is marked as {attr.pii_pci_indicator} - "
                        "ensure proper handling",
                        entity=entity_name,
                        attribute=attr.name,
                    )

    def _validate_relationships(self):
        """Validate relationship definitions."""
        for rel in self.domain.relationships:
            # Check parent exists
            if rel.parent_entity not in self.domain.entities:
                self._add_error(
                    "ORPHAN_RELATIONSHIP",
                    f"Relationship '{rel.name}' references unknown parent '{rel.parent_entity}'",
                )

            # Check child exists
            if rel.child_entity not in self.domain.entities:
                self._add_error(
                    "ORPHAN_RELATIONSHIP",
                    f"Relationship '{rel.name}' references unknown child '{rel.child_entity}'",
                )

            # Check for self-reference
            if rel.parent_entity == rel.child_entity:
                self._add_warning(
                    "SELF_REFERENCE",
                    f"Relationship '{rel.name}' is a self-reference on '{rel.parent_entity}'",
                )

    def _validate_enums(self):
        """Validate enum definitions."""
        for enum_val in self.domain.enum_values:
            # Check entity exists
            entity = self.domain.entities.get(enum_val.entity_name)
            if not entity:
                self._add_warning(
                    "ORPHAN_ENUM",
                    f"Enum value for unknown entity '{enum_val.entity_name}'",
                )
                continue

            # Check attribute exists
            attr_exists = any(a.name == enum_val.attribute_name for a in entity.attributes)
            if not attr_exists:
                self._add_warning(
                    "ORPHAN_ENUM",
                    f"Enum value for unknown attribute '{enum_val.attribute_name}' "
                    f"in entity '{enum_val.entity_name}'",
                )

    def _validate_graph(self):
        """Validate relationship graph."""
        # Check for circular compositions (from graph builder warnings)
        for warning in self.graph.warnings:
            if "CIRCULAR" in warning:
                self._add_error("CIRCULAR_COMPOSITION", warning)
            else:
                self._add_warning("GRAPH_WARNING", warning)

        # Check all root entities are properly classified
        for root in self.graph.root_entities:
            entity = self.domain.entities.get(root)
            if entity and not entity.is_managed() and not entity.is_shortcut():
                self._add_warning(
                    "UNMANAGED_ROOT",
                    f"Root entity '{root}' is not marked as managed (no BIMEntityName)",
                    entity=root,
                )
