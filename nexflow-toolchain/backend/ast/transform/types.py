# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform AST Type System

Type system dataclasses for field types, constraints, and qualifiers.
"""

from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from .common import SourceLocation, RangeSpec, LengthSpec
from .enums import BaseType, QualifierType

if TYPE_CHECKING:
    from .expressions import Expression


@dataclass
class Constraint:
    """Field constraint specification."""
    range_spec: Optional[RangeSpec] = None
    length_spec: Optional[LengthSpec] = None
    pattern: Optional[str] = None
    values: Optional[List[str]] = None
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
    custom_type: Optional[str] = None  # Schema reference or alias
    constraints: List[Constraint] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class Qualifier:
    """Field qualifier (nullable, required, default)."""
    qualifier_type: QualifierType
    default_value: Optional['Expression'] = None  # For default qualifier
    location: Optional[SourceLocation] = None
