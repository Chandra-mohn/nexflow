"""
Process AST Processing Block

Processing-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation, Duration
from .execution import LatenessDecl, LateDataDecl
from .enums import WindowType, JoinType


@dataclass
class EnrichDecl:
    """Enrich using lookup declaration."""
    lookup_name: str
    on_fields: List[str]
    select_fields: Optional[List[str]] = None
    location: Optional[SourceLocation] = None


@dataclass
class TransformDecl:
    """Transform using L3 declaration."""
    transform_name: str
    location: Optional[SourceLocation] = None


@dataclass
class RouteDecl:
    """Route using L4 rules declaration."""
    rule_name: str
    location: Optional[SourceLocation] = None


@dataclass
class AggregateDecl:
    """Aggregate using L3 declaration."""
    transform_name: str
    location: Optional[SourceLocation] = None


@dataclass
class MergeDecl:
    """Merge multiple streams declaration."""
    streams: List[str]
    output_alias: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class WindowOptions:
    """Window configuration options."""
    lateness: Optional[LatenessDecl] = None
    late_data: Optional[LateDataDecl] = None


@dataclass
class WindowDecl:
    """Window declaration."""
    window_type: WindowType
    size: Duration
    slide: Optional[Duration] = None  # For sliding windows
    key_by: Optional[str] = None  # Key by field path (v0.5.0+)
    options: Optional[WindowOptions] = None
    location: Optional[SourceLocation] = None


@dataclass
class JoinDecl:
    """Join declaration."""
    left: str
    right: str
    on_fields: List[str]
    within: Duration
    join_type: JoinType = JoinType.INNER
    location: Optional[SourceLocation] = None
