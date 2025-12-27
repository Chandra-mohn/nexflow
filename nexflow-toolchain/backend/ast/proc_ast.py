# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow L1 (Flow/Process) AST Definitions

Python dataclass definitions for L1 Process Orchestration DSL AST nodes.
Maps directly to the ProcDSL.g4 grammar.

This module re-exports all types from the modular proc/ subpackage
for backward compatibility.
"""

# Explicit re-exports from the modular package (no wildcard imports)
from .proc import (
    # Enums
    ModeType, WindowType, JoinType, StateType, BufferType, TtlType,
    CleanupStrategy, TimeoutActionType, ErrorType, ErrorActionType,
    BackpressureStrategy, FanoutType, CompletionConditionType,
    PhaseType, MarkerConditionType, ScheduleType,
    # Common
    SourceLocation, Duration, FieldPath,
    # Execution
    WatermarkDecl, LateDataDecl, LatenessDecl, TimeDecl, ModeDecl, ExecutionBlock,
    # Input
    ConnectorType, SchemaDecl, ProjectClause, StoreAction, MatchAction,
    RedisConfig, StateStoreConfig, SchedulerConfig,
    TimestampBounds, ParquetConfig, CsvConfig,
    ReceiveDecl, InputBlock,
    # Processing
    EnrichDecl, TransformDecl, RouteDecl, AggregateDecl, MergeDecl,
    WindowOptions, WindowDecl, JoinDecl,
    EvaluateDecl, TransitionDecl, EmitAuditDecl, DeduplicateDecl,
    LookupDecl, BranchDecl, ParallelDecl, ValidateInputDecl,
    CallDecl, ScheduleDecl, SetDecl,
    SqlTransformDecl,
    # Correlation
    TimeoutAction, CompletionCondition, CompletionClause, AwaitDecl, HoldDecl,
    # Output
    PersistMode, PersistErrorAction, PersistErrorHandler, PersistDecl,
    FanoutDecl, EmitDecl, OutputBlock, CorrelationDecl, IncludeDecl,
    OnCommitDecl, OnCommitFailureDecl, CompletionBlock,
    # State
    TtlDecl, CleanupDecl, UsesDecl, LocalDecl, BufferDecl, StateBlock,
    # Resilience
    ErrorAction, ErrorHandler, ErrorBlock, CheckpointBlock, AlertDecl,
    BackpressureBlock, ResilienceBlock,
    # Program
    ProcessDefinition, Program,
    # Metrics
    MetricType, MetricScope, MetricDecl, MetricUpdateDecl, MetricsBlock,
    # Markers and Phases
    SignalCondition, MarkerRefCondition, StreamDrainedCondition,
    CountThresholdCondition, TimeBasedCondition, ApiCheckCondition, CompoundCondition,
    AnyMarkerCondition, MarkerDef, MarkersBlock, OnCompleteClause,
    PhaseSpec, PhaseBlock, BusinessDateDecl, ProcessingDateDecl,
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
    'TimestampBounds', 'ParquetConfig', 'CsvConfig',
    'ReceiveDecl', 'InputBlock',
    # Processing
    'EnrichDecl', 'TransformDecl', 'RouteDecl', 'AggregateDecl', 'MergeDecl',
    'WindowOptions', 'WindowDecl', 'JoinDecl',
    'EvaluateDecl', 'TransitionDecl', 'EmitAuditDecl', 'DeduplicateDecl',
    'LookupDecl', 'BranchDecl', 'ParallelDecl', 'ValidateInputDecl',
    'CallDecl', 'ScheduleDecl', 'SetDecl',
    'SqlTransformDecl',
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
