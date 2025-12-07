"""
Transform AST Top-Level Structures

Top-level program and transform definition dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation
from .metadata import TransformMetadata, CacheDecl
from .specs import InputSpec, OutputSpec
from .blocks import (
    ApplyBlock,
    MappingsBlock,
    ComposeBlock,
    ValidateInputBlock,
    ValidateOutputBlock,
    InvariantBlock,
    OnErrorBlock,
    OnChangeBlock,
)


@dataclass
class TransformDef:
    """Field/Expression level transform definition."""
    name: str
    metadata: Optional[TransformMetadata] = None
    pure: Optional[bool] = None
    cache: Optional[CacheDecl] = None
    input: Optional[InputSpec] = None
    output: Optional[OutputSpec] = None
    validate_input: Optional[ValidateInputBlock] = None
    apply: Optional[ApplyBlock] = None
    validate_output: Optional[ValidateOutputBlock] = None
    on_error: Optional[OnErrorBlock] = None
    location: Optional[SourceLocation] = None


@dataclass
class UseBlock:
    """Use block for importing other transforms."""
    transforms: List[str]
    location: Optional[SourceLocation] = None


@dataclass
class TransformBlockDef:
    """Block-level transform definition."""
    name: str
    metadata: Optional[TransformMetadata] = None
    use: Optional[UseBlock] = None
    input: Optional[InputSpec] = None
    output: Optional[OutputSpec] = None
    validate_input: Optional[ValidateInputBlock] = None
    invariant: Optional[InvariantBlock] = None
    mappings: Optional[MappingsBlock] = None
    compose: Optional[ComposeBlock] = None
    validate_output: Optional[ValidateOutputBlock] = None
    on_change: Optional[OnChangeBlock] = None
    on_error: Optional[OnErrorBlock] = None
    location: Optional[SourceLocation] = None


@dataclass
class Program:
    """Top-level program containing transform definitions."""
    transforms: List[TransformDef] = field(default_factory=list)
    transform_blocks: List[TransformBlockDef] = field(default_factory=list)
    location: Optional[SourceLocation] = None
