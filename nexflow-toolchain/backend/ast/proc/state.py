# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST State Block

State-related dataclasses for process AST.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation, Duration, FieldPath
from .enums import StateType, BufferType, TtlType, CleanupStrategy


@dataclass
class TtlDecl:
    """Time-to-live declaration."""
    duration: Duration
    ttl_type: TtlType = TtlType.SLIDING
    location: Optional[SourceLocation] = None


@dataclass
class CleanupDecl:
    """Cleanup strategy declaration."""
    strategy: CleanupStrategy
    location: Optional[SourceLocation] = None


@dataclass
class UsesDecl:
    """External state reference declaration."""
    state_name: str
    location: Optional[SourceLocation] = None


@dataclass
class LocalDecl:
    """Local state declaration."""
    name: str
    keyed_by: List[str]
    state_type: StateType
    ttl: Optional[TtlDecl] = None
    cleanup: Optional[CleanupDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class BufferDecl:
    """Named buffer declaration."""
    name: str
    keyed_by: List[str]
    buffer_type: BufferType
    priority_field: Optional[FieldPath] = None  # For priority buffers
    ttl: Optional[TtlDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class StateBlock:
    """State declarations."""
    uses: List[UsesDecl] = field(default_factory=list)
    locals: List[LocalDecl] = field(default_factory=list)
    buffers: List[BufferDecl] = field(default_factory=list)
    location: Optional[SourceLocation] = None
