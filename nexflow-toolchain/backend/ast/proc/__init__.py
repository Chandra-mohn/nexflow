# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Module

Re-exports all process AST types for backward compatibility.
"""

# Enumerations
# Common types
from .common import (
    Duration,
    FieldPath,
    SourceLocation,
)

# Correlation block
from .correlation import (
    AwaitDecl,
    CompletionClause,
    CompletionCondition,
    HoldDecl,
    TimeoutAction,
)
from .enums import (
    BackpressureStrategy,
    BufferType,
    CleanupStrategy,
    CompletionConditionType,
    ErrorActionType,
    ErrorType,
    FanoutType,
    JoinType,
    MarkerConditionType,
    ModeType,
    PhaseType,
    ScheduleType,
    StateType,
    TimeoutActionType,
    TtlType,
    WindowType,
)

# Execution block
from .execution import (
    ExecutionBlock,
    LateDataDecl,
    LatenessDecl,
    ModeDecl,
    TimeDecl,
    WatermarkDecl,
)

# Input block
from .input import (
    ConnectorType,
    CsvConfig,
    InputBlock,
    MatchAction,
    ParquetConfig,
    ProjectClause,
    ReceiveDecl,
    RedisConfig,
    SchedulerConfig,
    SchemaDecl,
    StateStoreConfig,
    StoreAction,
    TimestampBounds,
)

# Markers and Phases (EOD markers, business date)
from .markers import (
    AnyMarkerCondition,
    ApiCheckCondition,
    BusinessDateDecl,
    CompoundCondition,
    CountThresholdCondition,
    MarkerDef,
    MarkerRefCondition,
    MarkersBlock,
    OnCompleteClause,
    PhaseBlock,
    PhaseSpec,
    ProcessingDateDecl,
    SignalCondition,
    StreamDrainedCondition,
    TimeBasedCondition,
)

# Metrics
from .metrics import (
    MetricDecl,
    MetricsBlock,
    MetricScope,
    MetricType,
    MetricUpdateDecl,
)

# Output and completion blocks
from .output import (
    CompletionBlock,
    CorrelationDecl,
    EmitDecl,
    FanoutDecl,
    IncludeDecl,
    OnCommitDecl,
    OnCommitFailureDecl,
    OutputBlock,
    PersistDecl,
    PersistErrorAction,
    PersistErrorHandler,
    PersistMode,
)

# Processing block
from .processing import (
    AggregateDecl,
    BranchDecl,
    CallDecl,
    DeduplicateDecl,
    EmitAuditDecl,
    EnrichDecl,
    # Additional statements
    EvaluateDecl,
    JoinDecl,
    LookupDecl,
    MergeDecl,
    ParallelDecl,
    RouteDecl,
    ScheduleDecl,
    SetDecl,
    SqlTransformDecl,
    TransformDecl,
    TransitionDecl,
    ValidateInputDecl,
    WindowDecl,
    WindowOptions,
)

# Program
from .program import (
    ProcessDefinition,
    Program,
)

# Resilience block
from .resilience import (
    AlertDecl,
    BackpressureBlock,
    CheckpointBlock,
    ErrorAction,
    ErrorBlock,
    ErrorHandler,
    ResilienceBlock,
)

# State block
from .state import (
    BufferDecl,
    CleanupDecl,
    LocalDecl,
    StateBlock,
    TtlDecl,
    UsesDecl,
)

__all__ = [
    # Enums
    "ModeType",
    "WindowType",
    "JoinType",
    "StateType",
    "BufferType",
    "TtlType",
    "CleanupStrategy",
    "TimeoutActionType",
    "ErrorType",
    "ErrorActionType",
    "BackpressureStrategy",
    "FanoutType",
    "CompletionConditionType",
    "PhaseType",
    "MarkerConditionType",
    "ScheduleType",
    # Common
    "SourceLocation",
    "Duration",
    "FieldPath",
    # Execution
    "WatermarkDecl",
    "LateDataDecl",
    "LatenessDecl",
    "TimeDecl",
    "ModeDecl",
    "ExecutionBlock",
    # Input
    "ConnectorType",
    "SchemaDecl",
    "ProjectClause",
    "StoreAction",
    "MatchAction",
    "RedisConfig",
    "StateStoreConfig",
    "SchedulerConfig",
    "TimestampBounds",
    "ParquetConfig",
    "CsvConfig",
    "ReceiveDecl",
    "InputBlock",
    # Processing
    "EnrichDecl",
    "TransformDecl",
    "RouteDecl",
    "AggregateDecl",
    "MergeDecl",
    "WindowOptions",
    "WindowDecl",
    "JoinDecl",
    "EvaluateDecl",
    "TransitionDecl",
    "EmitAuditDecl",
    "DeduplicateDecl",
    "LookupDecl",
    "BranchDecl",
    "ParallelDecl",
    "ValidateInputDecl",
    "CallDecl",
    "ScheduleDecl",
    "SetDecl",
    "SqlTransformDecl",
    # Correlation
    "TimeoutAction",
    "CompletionCondition",
    "CompletionClause",
    "AwaitDecl",
    "HoldDecl",
    # Output
    "PersistMode",
    "PersistErrorAction",
    "PersistErrorHandler",
    "PersistDecl",
    "FanoutDecl",
    "EmitDecl",
    "OutputBlock",
    "CorrelationDecl",
    "IncludeDecl",
    "OnCommitDecl",
    "OnCommitFailureDecl",
    "CompletionBlock",
    # State
    "TtlDecl",
    "CleanupDecl",
    "UsesDecl",
    "LocalDecl",
    "BufferDecl",
    "StateBlock",
    # Resilience
    "ErrorAction",
    "ErrorHandler",
    "ErrorBlock",
    "CheckpointBlock",
    "AlertDecl",
    "BackpressureBlock",
    "ResilienceBlock",
    # Program
    "ProcessDefinition",
    "Program",
    # Metrics
    "MetricType",
    "MetricScope",
    "MetricDecl",
    "MetricUpdateDecl",
    "MetricsBlock",
    # Markers and Phases
    "SignalCondition",
    "MarkerRefCondition",
    "StreamDrainedCondition",
    "CountThresholdCondition",
    "TimeBasedCondition",
    "ApiCheckCondition",
    "CompoundCondition",
    "AnyMarkerCondition",
    "MarkerDef",
    "MarkersBlock",
    "OnCompleteClause",
    "PhaseSpec",
    "PhaseBlock",
    "BusinessDateDecl",
    "ProcessingDateDecl",
]
