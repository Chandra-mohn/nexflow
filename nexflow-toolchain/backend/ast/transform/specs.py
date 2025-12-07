"""
Transform AST Input/Output Specifications

Input and output field specification dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation
from .types import FieldType, Qualifier


@dataclass
class InputFieldDecl:
    """Input field declaration."""
    name: str
    field_type: FieldType
    qualifiers: List[Qualifier] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class OutputFieldDecl:
    """Output field declaration."""
    name: str
    field_type: FieldType
    qualifiers: List[Qualifier] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class InputSpec:
    """Input specification (single or multiple fields)."""
    single_type: Optional[FieldType] = None
    single_qualifiers: Optional[List[Qualifier]] = None
    fields: List[InputFieldDecl] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    @property
    def is_single(self) -> bool:
        return self.single_type is not None


@dataclass
class OutputSpec:
    """Output specification (single or multiple fields)."""
    single_type: Optional[FieldType] = None
    single_qualifiers: Optional[List[Qualifier]] = None
    fields: List[OutputFieldDecl] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    @property
    def is_single(self) -> bool:
        return self.single_type is not None
