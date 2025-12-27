# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
    """Transform using L3 declaration.

    Can include on_success/on_failure blocks for conditional processing.
    """
    transform_name: str
    on_success: Optional[List] = None  # List of processing operations on success
    on_failure: Optional[List] = None  # List of processing operations on failure
    location: Optional[SourceLocation] = None


@dataclass
class RouteDecl:
    """Route using L4 rules or inline condition.

    Supports two forms:
    - route using <rule_name>: References an L4 rules table
    - route when <condition>: Inline conditional routing
    """
    rule_name: Optional[str] = None  # For 'route using' form
    condition: Optional[str] = None  # For 'route when' form (expression as string)
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


# =============================================================================
# Additional Processing Statements (Placeholder implementations)
# These represent various DSL statements that affect the processing pipeline
# =============================================================================

@dataclass
class EvaluateDecl:
    """Evaluate expression statement."""
    expression: str
    location: Optional[SourceLocation] = None


@dataclass
class TransitionDecl:
    """State transition statement."""
    target_state: str
    location: Optional[SourceLocation] = None


@dataclass
class EmitAuditDecl:
    """Emit audit event statement."""
    event_name: str
    location: Optional[SourceLocation] = None


@dataclass
class DeduplicateDecl:
    """Deduplicate by field statement."""
    key_field: str
    location: Optional[SourceLocation] = None


@dataclass
class LookupDecl:
    """Lookup data source statement."""
    source_name: str
    location: Optional[SourceLocation] = None


@dataclass
class BranchDecl:
    """Parallel branch statement."""
    branch_name: str
    body: List = None  # List of statements in the branch
    location: Optional[SourceLocation] = None

    def __post_init__(self):
        if self.body is None:
            self.body = []


@dataclass
class ParallelDecl:
    """Parallel execution block."""
    name: str
    branches: List[BranchDecl] = None
    location: Optional[SourceLocation] = None

    def __post_init__(self):
        if self.branches is None:
            self.branches = []


@dataclass
class ValidateInputDecl:
    """Validate input statement."""
    expression: str
    location: Optional[SourceLocation] = None


@dataclass
class CallDecl:
    """Call external function/service statement."""
    target: str
    location: Optional[SourceLocation] = None


@dataclass
class ScheduleDecl:
    """Schedule delayed execution statement."""
    delay: Duration
    target: str
    location: Optional[SourceLocation] = None


@dataclass
class SetDecl:
    """Set variable statement."""
    variable: str
    value: str
    location: Optional[SourceLocation] = None


@dataclass
class SqlTransformDecl:
    """Embedded SQL transform statement (v0.8.0+).

    Allows embedding SQL directly in the ProcDSL for Flink SQL or Spark SQL execution.

    Example:
        sql ```
            SELECT region, SUM(amount) as total
            FROM sales
            GROUP BY region
        ```
        as SalesSummary
    """
    sql_content: str                          # Raw SQL content
    output_type: Optional[str] = None         # Optional output schema name
    location: Optional[SourceLocation] = None
