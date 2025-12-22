# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
    PhaseType,
    MarkerConditionType,
    ScheduleType,  # v0.8.0+
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
    ConnectorType,
    SchemaDecl,
    ProjectClause,
    StoreAction,
    MatchAction,
    RedisConfig,
    StateStoreConfig,
    SchedulerConfig,
    TimestampBounds,  # v0.8.0+
    ParquetConfig,    # v0.8.0+
    CsvConfig,        # v0.8.0+
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
    SqlTransformDecl,     # v0.8.0+
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
    PersistMode,
    PersistErrorAction,
    PersistErrorHandler,
    PersistDecl,
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

# Metrics
from .metrics import (
    MetricType,
    MetricScope,
    MetricDecl,
    MetricUpdateDecl,
    MetricsBlock,
)

# Markers and Phases (EOD markers, business date)
from .markers import (
    SignalCondition,
    MarkerRefCondition,
    StreamDrainedCondition,
    CountThresholdCondition,
    TimeBasedCondition,
    ApiCheckCondition,
    CompoundCondition,
    AnyMarkerCondition,
    MarkerDef,
    MarkersBlock,
    OnCompleteClause,
    PhaseSpec,
    PhaseBlock,
    BusinessDateDecl,
    ProcessingDateDecl,
)

__all__ = [
    # Enums
    'ModeType', 'WindowType', 'JoinType', 'StateType', 'BufferType', 'TtlType',
    'CleanupStrategy', 'TimeoutActionType', 'ErrorType', 'ErrorActionType',
    'BackpressureStrategy', 'FanoutType', 'CompletionConditionType',
    'PhaseType', 'MarkerConditionType', 'ScheduleType',
    # Common
    'SourceLocation', 'Duration', 'FieldPath',
    # Execution
    'WatermarkDecl', 'LateDataDecl', 'LatenessDecl', 'TimeDecl', 'ModeDecl', 'ExecutionBlock',
    # Input
    'ConnectorType', 'SchemaDecl', 'ProjectClause', 'StoreAction', 'MatchAction',
    'RedisConfig', 'StateStoreConfig', 'SchedulerConfig',
    'TimestampBounds', 'ParquetConfig', 'CsvConfig',  # v0.8.0+
    'ReceiveDecl', 'InputBlock',
    # Processing
    'EnrichDecl', 'TransformDecl', 'RouteDecl', 'AggregateDecl', 'MergeDecl',
    'WindowOptions', 'WindowDecl', 'JoinDecl',
    'EvaluateDecl', 'TransitionDecl', 'EmitAuditDecl', 'DeduplicateDecl',
    'LookupDecl', 'BranchDecl', 'ParallelDecl', 'ValidateInputDecl',
    'ForeachDecl', 'CallDecl', 'ScheduleDecl', 'SetDecl',
    'SqlTransformDecl',  # v0.8.0+
    # Correlation
    'TimeoutAction', 'CompletionCondition', 'CompletionClause', 'AwaitDecl', 'HoldDecl',
    # Output
    'PersistMode', 'PersistErrorAction', 'PersistErrorHandler', 'PersistDecl',
    'FanoutDecl', 'EmitDecl', 'OutputBlock', 'CorrelationDecl', 'IncludeDecl',
    'OnCommitDecl', 'OnCommitFailureDecl', 'CompletionBlock',
    # State
    'TtlDecl', 'CleanupDecl', 'UsesDecl', 'LocalDecl', 'BufferDecl', 'StateBlock',
    # Resilience
    'ErrorAction', 'ErrorHandler', 'ErrorBlock', 'CheckpointBlock', 'AlertDecl',
    'BackpressureBlock', 'ResilienceBlock',
    # Program
    'ProcessDefinition', 'Program',
    # Metrics
    'MetricType', 'MetricScope', 'MetricDecl', 'MetricUpdateDecl', 'MetricsBlock',
    # Markers and Phases
    'SignalCondition', 'MarkerRefCondition', 'StreamDrainedCondition',
    'CountThresholdCondition', 'TimeBasedCondition', 'ApiCheckCondition', 'CompoundCondition',
    'AnyMarkerCondition', 'MarkerDef', 'MarkersBlock', 'OnCompleteClause',
    'PhaseSpec', 'PhaseBlock', 'BusinessDateDecl', 'ProcessingDateDecl',
]
