# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema AST Top-Level Structures

Top-level program and schema definition dataclasses.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from .common import Duration, SourceLocation

if TYPE_CHECKING:
    from backend.ast.common import ImportStatement
    from backend.ast.serialization import SerializationConfig
from .blocks import (
    ComputedBlock,
    ConstraintsBlock,
    EntriesBlock,
    ParametersBlock,
    StateMachineBlock,
    StreamingBlock,
    VersionBlock,
)
from .enums import MutationPattern
from .rules import MigrationBlock, RuleBlock
from .types import FieldsBlock, IdentityBlock, NestedObjectBlock, TypeAliasBlock


@dataclass
class SchemaDefinition:
    """Complete schema definition."""

    name: str
    patterns: List[MutationPattern] = field(default_factory=list)
    version: Optional[VersionBlock] = None
    retention: Optional[Duration] = None
    identity: Optional[IdentityBlock] = None
    streaming: Optional[StreamingBlock] = None
    serialization: Optional["SerializationConfig"] = None  # Kafka serialization format
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
    imports: List["ImportStatement"] = field(default_factory=list)
    location: Optional[SourceLocation] = None
