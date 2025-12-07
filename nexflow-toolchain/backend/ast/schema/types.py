"""
Schema AST Type System

Type-related dataclasses for schema AST including fields, constraints, and qualifiers.
"""

from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from .common import SourceLocation, RangeSpec, LengthSpec
from .enums import BaseType, FieldQualifierType

if TYPE_CHECKING:
    from .literals import Literal


@dataclass
class Constraint:
    """Field constraint specification."""
    range_spec: Optional[RangeSpec] = None
    length_spec: Optional[LengthSpec] = None
    pattern: Optional[str] = None
    values: Optional[List['Literal']] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    location: Optional[SourceLocation] = None


@dataclass
class CollectionType:
    """Collection type (list, set, map)."""
    collection_kind: str  # 'list', 'set', 'map'
    element_type: 'FieldType'
    key_type: Optional['FieldType'] = None  # For maps
    location: Optional[SourceLocation] = None


@dataclass
class FieldType:
    """Field type specification."""
    base_type: Optional[BaseType] = None
    collection_type: Optional[CollectionType] = None
    custom_type: Optional[str] = None  # Domain type or alias
    constraints: List[Constraint] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class FieldQualifier:
    """Field qualifier (required, optional, pii, etc.)."""
    qualifier_type: FieldQualifierType
    default_value: Optional['Literal'] = None  # For default qualifier
    pii_profile: Optional[str] = None  # For pii.profile syntax (e.g., 'ssn', 'pan', 'email')
    location: Optional[SourceLocation] = None


@dataclass
class FieldDecl:
    """Field declaration."""
    name: str
    field_type: FieldType
    qualifiers: List[FieldQualifier] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class IdentityBlock:
    """Identity fields block."""
    fields: List[FieldDecl]
    location: Optional[SourceLocation] = None


@dataclass
class FieldsBlock:
    """Fields block."""
    fields: List[FieldDecl]
    location: Optional[SourceLocation] = None


@dataclass
class NestedObjectBlock:
    """Nested object definition."""
    name: str
    is_list: bool = False
    fields: List[FieldDecl] = field(default_factory=list)
    nested_objects: List['NestedObjectBlock'] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class TypeAlias:
    """Type alias definition."""
    name: str
    field_type: Optional[FieldType] = None
    object_fields: Optional[List[FieldDecl]] = None  # For object type alias
    location: Optional[SourceLocation] = None


@dataclass
class TypeAliasBlock:
    """Type aliases block."""
    aliases: List[TypeAlias]
    location: Optional[SourceLocation] = None
