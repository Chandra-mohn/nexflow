"""
Process AST Module

Re-exports all process AST types for backward compatibility.
"""

# Enumerations
from .enums import (
    ModeType,
    WindowType,
    JoinType,
    StateType,
    BufferType,
    TtlType,
    CleanupStrategy,
    TimeoutActionType,
    ErrorType,
    ErrorActionType,
    BackpressureStrategy,
    FanoutType,
    CompletionConditionType,
)

# Common types
from .common import (
    SourceLocation,
    Duration,
    FieldPath,
)

# Execution block
from .execution import (
    WatermarkDecl,
    LateDataDecl,
    LatenessDecl,
    TimeDecl,
    ModeDecl,
    ExecutionBlock,
)

# Input block
from .input import (
    SchemaDecl,
    ProjectClause,
    StoreAction,
    MatchAction,
    ReceiveDecl,
    InputBlock,
)

# Processing block
from .processing import (
    EnrichDecl,
    TransformDecl,
    RouteDecl,
    AggregateDecl,
    MergeDecl,
    WindowOptions,
    WindowDecl,
    JoinDecl,
    # Additional statements
    EvaluateDecl,
    TransitionDecl,
    EmitAuditDecl,
    DeduplicateDecl,
    LookupDecl,
    BranchDecl,
    ParallelDecl,
    ValidateInputDecl,
    ForeachDecl,
    CallDecl,
    ScheduleDecl,
    SetDecl,
)

# Correlation block
from .correlation import (
    TimeoutAction,
    CompletionCondition,
    CompletionClause,
    AwaitDecl,
    HoldDecl,
)

# Output and completion blocks
from .output import (
    FanoutDecl,
    EmitDecl,
    OutputBlock,
    CorrelationDecl,
    IncludeDecl,
    OnCommitDecl,
    OnCommitFailureDecl,
    CompletionBlock,
)

# State block
from .state import (
    TtlDecl,
    CleanupDecl,
    UsesDecl,
    LocalDecl,
    BufferDecl,
    StateBlock,
)

# Resilience block
from .resilience import (
    ErrorAction,
    ErrorHandler,
    ErrorBlock,
    CheckpointBlock,
    AlertDecl,
    BackpressureBlock,
    ResilienceBlock,
)

# Program
from .program import (
    ProcessDefinition,
    Program,
)

__all__ = [
    # Enums
    'ModeType', 'WindowType', 'JoinType', 'StateType', 'BufferType', 'TtlType',
    'CleanupStrategy', 'TimeoutActionType', 'ErrorType', 'ErrorActionType',
    'BackpressureStrategy', 'FanoutType', 'CompletionConditionType',
    # Common
    'SourceLocation', 'Duration', 'FieldPath',
    # Execution
    'WatermarkDecl', 'LateDataDecl', 'LatenessDecl', 'TimeDecl', 'ModeDecl', 'ExecutionBlock',
    # Input
    'SchemaDecl', 'ProjectClause', 'StoreAction', 'MatchAction', 'ReceiveDecl', 'InputBlock',
    # Processing
    'EnrichDecl', 'TransformDecl', 'RouteDecl', 'AggregateDecl', 'MergeDecl',
    'WindowOptions', 'WindowDecl', 'JoinDecl',
    'EvaluateDecl', 'TransitionDecl', 'EmitAuditDecl', 'DeduplicateDecl',
    'LookupDecl', 'BranchDecl', 'ParallelDecl', 'ValidateInputDecl',
    'ForeachDecl', 'CallDecl', 'ScheduleDecl', 'SetDecl',
    # Correlation
    'TimeoutAction', 'CompletionCondition', 'CompletionClause', 'AwaitDecl', 'HoldDecl',
    # Output
    'FanoutDecl', 'EmitDecl', 'OutputBlock', 'CorrelationDecl', 'IncludeDecl',
    'OnCommitDecl', 'OnCommitFailureDecl', 'CompletionBlock',
    # State
    'TtlDecl', 'CleanupDecl', 'UsesDecl', 'LocalDecl', 'BufferDecl', 'StateBlock',
    # Resilience
    'ErrorAction', 'ErrorHandler', 'ErrorBlock', 'CheckpointBlock', 'AlertDecl',
    'BackpressureBlock', 'ResilienceBlock',
    # Program
    'ProcessDefinition', 'Program',
]
