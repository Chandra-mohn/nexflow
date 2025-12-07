"""
Process AST Enumerations

Enum definitions for L1 Process Orchestration DSL.
"""

from enum import Enum


class ModeType(Enum):
    STREAM = "stream"
    BATCH = "batch"
    MICRO_BATCH = "micro_batch"


class WindowType(Enum):
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"


class JoinType(Enum):
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    OUTER = "outer"


class StateType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    MAP = "map"
    LIST = "list"


class BufferType(Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"


class TtlType(Enum):
    SLIDING = "sliding"
    ABSOLUTE = "absolute"


class CleanupStrategy(Enum):
    ON_CHECKPOINT = "on_checkpoint"
    ON_ACCESS = "on_access"
    BACKGROUND = "background"


class TimeoutActionType(Enum):
    EMIT = "emit"
    DEAD_LETTER = "dead_letter"
    SKIP = "skip"


class ErrorType(Enum):
    TRANSFORM_FAILURE = "transform_failure"
    LOOKUP_FAILURE = "lookup_failure"
    RULE_FAILURE = "rule_failure"
    CORRELATION_FAILURE = "correlation_failure"


class ErrorActionType(Enum):
    DEAD_LETTER = "dead_letter"
    SKIP = "skip"
    RETRY = "retry"


class BackpressureStrategy(Enum):
    BLOCK = "block"
    DROP = "drop"
    SAMPLE = "sample"


class FanoutType(Enum):
    BROADCAST = "broadcast"
    ROUND_ROBIN = "round_robin"


class CompletionConditionType(Enum):
    COUNT = "count"
    MARKER = "marker"
    RULE = "rule"
