"""
Schema AST Top-Level Structures

Top-level program and schema definition dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation, Duration
from .enums import MutationPattern
from .types import IdentityBlock, FieldsBlock, NestedObjectBlock, TypeAliasBlock
from .blocks import (
    VersionBlock, StreamingBlock, StateMachineBlock,
    ParametersBlock, EntriesBlock, ConstraintsBlock, ComputedBlock
)
from .rules import RuleBlock, MigrationBlock


@dataclass
class SchemaDefinition:
    """Complete schema definition."""
    name: str
    patterns: List[MutationPattern] = field(default_factory=list)
    version: Optional[VersionBlock] = None
    retention: Optional[Duration] = None
    identity: Optional[IdentityBlock] = None
    streaming: Optional[StreamingBlock] = None
    fields: Optional[FieldsBlock] = None
    nested_objects: List[NestedObjectBlock] = field(default_factory=list)
    computed: Optional[ComputedBlock] = None  # Computed/derived fields
    constraints: Optional[ConstraintsBlock] = None
    immutable: Optional[bool] = None
    state_machine: Optional[StateMachineBlock] = None
    parameters: Optional[ParametersBlock] = None
    entries: Optional[EntriesBlock] = None
    rules: List[RuleBlock] = field(default_factory=list)
    migration: Optional[MigrationBlock] = None
    location: Optional[SourceLocation] = None


@dataclass
class Program:
    """Top-level program containing schema definitions and type aliases."""
    schemas: List[SchemaDefinition] = field(default_factory=list)
    type_aliases: List[TypeAliasBlock] = field(default_factory=list)
    location: Optional[SourceLocation] = None
