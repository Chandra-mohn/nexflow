"""
Data models for Excel Schema Importer.

These models represent the intermediate representation between
Excel workbook data and Nexflow Schema DSL output.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EntityQualifier(Enum):
    """BAIN terminology for entity classification."""
    BOM = "BOM"  # Business Object Model - core business entities
    BQ = "BQ"    # Business Qualifier - reference/lookup data
    CR = "CR"    # Control Record - operational/processing metadata
    NONE = ""    # Unclassified


class PersistencePattern(Enum):
    """Persistence pattern for entity storage."""
    MASTER = "Master"   # Reference/lookup data (slow-changing)
    EVENT = "Event"     # Immutable event records (append-only)
    LEDGER = "Ledger"   # Auditable transaction records
    NONE = ""           # No specific pattern


class EntityStereotype(Enum):
    """Entity stereotype modifier."""
    ARRAY = "Array"
    ENUM = "Enum"
    NONE = ""


class ObjectType(Enum):
    """Entity object type classification."""
    ENTITY = "Entity"
    SHORTCUT = "Shortcut Entity"


class RelationshipType(Enum):
    """Cardinality of parent-child relationship."""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:n"


@dataclass
class EnumValue:
    """Single enum constant with label."""
    entity_name: str
    attribute_name: str
    value: str          # UPPER_SNAKE_CASE constant
    label: str          # Human-readable label


@dataclass
class Attribute:
    """Field definition within an entity."""
    entity_name: str
    entity_code: str
    name: str                       # Field name (will be camelCase)
    code: str
    datatype: str                   # Excel datatype
    length: Optional[str] = None    # Length or precision (e.g., "18,2")
    mandatory: bool = False
    primary_identifier: bool = False
    foreign_identifier: bool = False
    foreign_parent_entity: Optional[str] = None
    foreign_parent_code: Optional[str] = None
    json_name: Optional[str] = None      # Serialization name
    pii_pci_indicator: Optional[str] = None  # PII, PCI, or None
    stereotype: EntityStereotype = EntityStereotype.NONE
    identifier_type: Optional[str] = None
    domain: Optional[str] = None
    comment: Optional[str] = None
    copybook_field: Optional[str] = None  # Legacy COBOL reference

    def is_enum(self) -> bool:
        """Check if this attribute references an enum."""
        return self.stereotype == EntityStereotype.ENUM


@dataclass
class Relationship:
    """Parent-child composition relationship."""
    name: str
    code: str
    parent_entity: str
    child_entity: str
    relationship_type: RelationshipType
    join_attributes: Optional[str] = None
    stereotype: str = ""  # "composition" for inline embedding
    comment: Optional[str] = None

    def is_composition(self) -> bool:
        """Check if this is a composition (embedded) relationship."""
        return self.stereotype.lower() == "composition"

    def is_array(self) -> bool:
        """Check if this relationship produces an array field."""
        return self.relationship_type == RelationshipType.ONE_TO_MANY


@dataclass
class Entity:
    """Schema/type definition."""
    entity_name: str            # Original business name
    entity_code: str
    collection_name: str        # DB collection / Java Record name
    object_type: ObjectType = ObjectType.ENTITY
    pattern: PersistencePattern = PersistencePattern.NONE
    stereotype: EntityStereotype = EntityStereotype.NONE
    qualifier: EntityQualifier = EntityQualifier.NONE
    bim_entity_name: Optional[str] = None  # If present, this domain manages CRUD
    comment: Optional[str] = None

    # Populated during graph building
    attributes: list[Attribute] = field(default_factory=list)
    child_relationships: list[Relationship] = field(default_factory=list)
    enum_values: dict[str, list[EnumValue]] = field(default_factory=dict)

    def is_managed(self) -> bool:
        """Check if this entity is managed (CRUD) by this domain."""
        return self.bim_entity_name is not None and self.bim_entity_name.strip() != ""

    def is_shortcut(self) -> bool:
        """Check if this is a shortcut (external reference)."""
        return self.object_type == ObjectType.SHORTCUT

    def is_enum_entity(self) -> bool:
        """Check if this entity is itself an enum type."""
        return self.stereotype == EntityStereotype.ENUM

    def get_schema_name(self) -> str:
        """Get the PascalCase schema name from collection_name."""
        return to_pascal_case(self.collection_name or self.entity_name)


@dataclass
class ServiceDomain:
    """Service domain containing multiple entities."""
    name: str
    source_file: str
    entities: dict[str, Entity] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)
    enum_values: list[EnumValue] = field(default_factory=list)

    # Computed during graph building
    managed_entities: list[str] = field(default_factory=list)
    external_references: list[str] = field(default_factory=list)

    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Find entity by EntityName."""
        return self.entities.get(name)

    def get_entity_by_code(self, code: str) -> Optional[Entity]:
        """Find entity by EntityCode."""
        for entity in self.entities.values():
            if entity.entity_code == code:
                return entity
        return None


def to_pascal_case(name: str) -> str:
    """
    Convert name to PascalCase for Java Record/Schema names.

    Examples:
        orders -> Order
        order_line_items -> OrderLineItem
        Order -> Order
        order line item -> OrderLineItem
    """
    if not name:
        return name

    # Replace common separators with spaces
    normalized = name.replace("_", " ").replace("-", " ")

    # Title case each word and join
    words = normalized.split()
    result = "".join(word.capitalize() for word in words)

    # Handle already PascalCase input
    if not result:
        result = name

    return result


def to_camel_case(name: str) -> str:
    """
    Convert name to camelCase for Java field names.

    Examples:
        order_id -> orderId
        OrderId -> orderId
        order id -> orderId
    """
    if not name:
        return name

    pascal = to_pascal_case(name)
    if len(pascal) > 0:
        return pascal[0].lower() + pascal[1:]
    return pascal


def to_upper_snake(name: str) -> str:
    """
    Convert name to UPPER_SNAKE_CASE for enum constants.

    Examples:
        pending -> PENDING
        Pending -> PENDING
        in_progress -> IN_PROGRESS
    """
    if not name:
        return name

    # Replace spaces with underscores, uppercase
    return name.replace(" ", "_").replace("-", "_").upper()
