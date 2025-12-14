"""
Rules AST Condition Types

Condition types for decision table matching.

Extended in v0.6.0+ for marker-based conditions.
"""

from dataclasses import dataclass
from typing import Optional, List, Union, TYPE_CHECKING

from .common import SourceLocation
from .enums import PatternMatchType, ComparisonOp, MarkerStateType
from .literals import Literal, IntegerLiteral, DecimalLiteral, MoneyLiteral

if TYPE_CHECKING:
    from .expressions import ValueExpr, BooleanExpr


@dataclass
class WildcardCondition:
    """Wildcard condition (*) - matches any value."""
    location: Optional[SourceLocation] = None


@dataclass
class ExactMatchCondition:
    """Exact match condition - value equals literal."""
    value: Literal
    location: Optional[SourceLocation] = None


@dataclass
class RangeCondition:
    """Range condition - value between min and max (inclusive)."""
    min_value: Union[IntegerLiteral, DecimalLiteral, MoneyLiteral]
    max_value: Union[IntegerLiteral, DecimalLiteral, MoneyLiteral]
    location: Optional[SourceLocation] = None


@dataclass
class SetCondition:
    """Set membership condition - value in/not in set."""
    values: List[Literal]
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class PatternCondition:
    """Pattern matching condition."""
    match_type: PatternMatchType
    pattern: str
    location: Optional[SourceLocation] = None


@dataclass
class NullCondition:
    """Null check condition."""
    is_null: bool  # True for "is null", False for "is not null"
    location: Optional[SourceLocation] = None


@dataclass
class ComparisonCondition:
    """Comparison condition (>, <, >=, <=, =, !=)."""
    operator: ComparisonOp
    value: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class ExpressionCondition:
    """Complex boolean expression condition."""
    expression: 'BooleanExpr'
    location: Optional[SourceLocation] = None


@dataclass
class MarkerStateCondition:
    """Marker state condition for phase-aware rules (v0.6.0+).

    Examples:
        - when marker eod_1 fired
        - when marker eod_1 pending
        - when between eod_1 and eod_2
    """
    state_type: MarkerStateType
    marker_name: str
    end_marker: Optional[str] = None  # For BETWEEN state type
    location: Optional[SourceLocation] = None


Condition = Union[
    WildcardCondition,
    ExactMatchCondition,
    RangeCondition,
    SetCondition,
    PatternCondition,
    NullCondition,
    ComparisonCondition,
    ExpressionCondition,
    MarkerStateCondition,
]
