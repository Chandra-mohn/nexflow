# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Output and Completion Blocks

Output and completion-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List, Union
from enum import Enum

from .common import SourceLocation, FieldPath
from .input import SchemaDecl
from .processing import RouteDecl
from .enums import FanoutType


class PersistMode(Enum):
    """Persistence mode for MongoDB async writes."""
    ASYNC = "async"  # Non-blocking write
    SYNC = "sync"    # Blocking write


class PersistErrorAction(Enum):
    """Error handling for persistence failures."""
    CONTINUE = "continue"  # Ignore errors
    FAIL = "fail"          # Fail the pipeline
    EMIT = "emit"          # Send to DLQ


@dataclass
class PersistErrorHandler:
    """Error handling configuration for persistence."""
    action: PersistErrorAction
    dlq_target: Optional[str] = None  # For EMIT action
    location: Optional[SourceLocation] = None


@dataclass
class PersistDecl:
    """L5 Integration: MongoDB persistence declaration.

    Allows emit to persist data to MongoDB asynchronously.

    Example DSL:
        emit to processed_events
            persist to transaction_store async
            batch size 100
            flush interval 5s
            on error continue
    """
    target: str                           # Logical name from L5 persistence config
    mode: PersistMode = PersistMode.ASYNC # async or sync
    batch_size: Optional[int] = None      # Override L5 config batch_size
    flush_interval: Optional[str] = None  # Override L5 config flush_interval
    error_handler: Optional[PersistErrorHandler] = None
    location: Optional[SourceLocation] = None


@dataclass
class FanoutDecl:
    """Fanout configuration declaration."""
    strategy: FanoutType
    location: Optional[SourceLocation] = None


@dataclass
class EmitDecl:
    """Emit to output declaration.

    Attributes:
        target: Logical sink name (resolved from L5)
        schema: Optional schema for the output
        fanout: Fanout strategy (broadcast/round_robin)
        persist: Optional MongoDB persistence configuration
        options: Additional options (reason, preserve_state, etc.)
        location: Source location for error reporting
    """
    target: str
    schema: Optional[SchemaDecl] = None
    fanout: Optional[FanoutDecl] = None
    persist: Optional[PersistDecl] = None   # L5 Integration: MongoDB persistence
    options: Optional[dict] = None          # reason, preserve_state, etc.
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
