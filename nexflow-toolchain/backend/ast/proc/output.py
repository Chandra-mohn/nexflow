"""
Process AST Output and Completion Blocks

Output and completion-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List, Union

from .common import SourceLocation, FieldPath
from .input import SchemaDecl
from .processing import RouteDecl
from .enums import FanoutType


@dataclass
class FanoutDecl:
    """Fanout configuration declaration."""
    strategy: FanoutType
    location: Optional[SourceLocation] = None


@dataclass
class EmitDecl:
    """Emit to output declaration."""
    target: str
    schema: Optional[SchemaDecl] = None
    fanout: Optional[FanoutDecl] = None
    options: Optional[dict] = None  # reason, preserve_state, etc.
    location: Optional[SourceLocation] = None


@dataclass
class OutputBlock:
    """Process output declarations."""
    outputs: List[Union[EmitDecl, RouteDecl]]
    location: Optional[SourceLocation] = None


# =============================================================================
# Completion Block
# =============================================================================

@dataclass
class CorrelationDecl:
    """Correlation field declaration for completion events."""
    field_path: FieldPath
    location: Optional[SourceLocation] = None


@dataclass
class IncludeDecl:
    """Include additional fields in completion event."""
    fields: List[str]
    location: Optional[SourceLocation] = None


@dataclass
class OnCommitDecl:
    """Success completion event declaration."""
    target: str
    correlation: CorrelationDecl
    include: Optional[IncludeDecl] = None
    schema: Optional[SchemaDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class OnCommitFailureDecl:
    """Failure completion event declaration."""
    target: str
    correlation: CorrelationDecl
    include: Optional[IncludeDecl] = None
    schema: Optional[SchemaDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class CompletionBlock:
    """Completion event declarations."""
    on_commit: Optional[OnCommitDecl] = None
    on_commit_failure: Optional[OnCommitFailureDecl] = None
    location: Optional[SourceLocation] = None
