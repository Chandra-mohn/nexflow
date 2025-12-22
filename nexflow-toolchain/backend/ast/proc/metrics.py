# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Metrics Block

Metrics-related dataclasses for Flink metrics generation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from .common import SourceLocation, Duration


class MetricType(Enum):
    """Supported metric types for Flink metrics."""
    COUNTER = "counter"       # Simple increment/decrement counter
    GAUGE = "gauge"          # Current value metric
    HISTOGRAM = "histogram"  # Distribution of values
    METER = "meter"          # Rate of events (events/second)


class MetricScope(Enum):
    """Scope for metric registration."""
    OPERATOR = "operator"     # Per-operator metrics
    TASK = "task"            # Per-task (parallelism) metrics
    JOB = "job"              # Job-wide metrics


@dataclass
class MetricDecl:
    """Single metric declaration.

    Examples:
        counter processed_events
        gauge active_sessions
        histogram response_times window 1 minute
        meter throughput
    """
    metric_type: MetricType
    name: str
    description: Optional[str] = None
    window: Optional[Duration] = None  # For histogram/rate calculations
    scope: MetricScope = MetricScope.OPERATOR
    labels: Optional[List[str]] = None  # Additional metric labels
    location: Optional[SourceLocation] = None


@dataclass
class MetricUpdateDecl:
    """Metric update operation within processing.

    Examples:
        increment processed_events
        set active_sessions to count
        record response_times value latency
    """
    operation: str  # increment, decrement, set, record
    metric_name: str
    value_expression: Optional[str] = None  # For set/record operations
    location: Optional[SourceLocation] = None


@dataclass
class MetricsBlock:
    """Container for metrics declarations within a process.

    Generates:
    - Flink metric registration in open()
    - Metric accessors and update methods
    - Metric group configuration
    """
    metrics: List[MetricDecl]
    group_name: Optional[str] = None  # Custom metric group name
    location: Optional[SourceLocation] = None
