"""
Rules AST Expression Types

Expression language types for the Rules DSL.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation, FieldPath
from .enums import ComparisonOp, LogicalOp
from .literals import Literal, ListLiteral


@dataclass
class FunctionCall:
    """Function call expression."""
    name: str
    arguments: List['ValueExpr'] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class UnaryExpr:
    """Unary expression (negation)."""
    operand: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class BinaryExpr:
    """Binary arithmetic expression."""
    left: 'ValueExpr'
    operator: str  # '+', '-', '*', '/', '%'
    right: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class ParenExpr:
    """Parenthesized expression."""
    inner: 'ValueExpr'
    location: Optional[SourceLocation] = None


ValueExpr = Union[Literal, FieldPath, FunctionCall, UnaryExpr, BinaryExpr, ParenExpr, ListLiteral]


@dataclass
class ComparisonExpr:
    """Comparison expression for boolean context."""
    left: ValueExpr
    operator: Optional[ComparisonOp] = None  # None for in/not in/null checks
    right: Optional[ValueExpr] = None
    in_values: Optional[List[ValueExpr]] = None  # For IN clause
    is_not_in: bool = False
    is_null_check: bool = False
    is_not_null_check: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class BooleanFactor:
    """Boolean factor - comparison, parenthesized expr, or function call."""
    comparison: Optional[ComparisonExpr] = None
    nested_expr: Optional['BooleanExpr'] = None
    function_call: Optional[FunctionCall] = None
    location: Optional[SourceLocation] = None


@dataclass
class BooleanTerm:
    """Boolean term with optional NOT."""
    factor: BooleanFactor
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class BooleanExpr:
    """Boolean expression with AND/OR."""
    terms: List[BooleanTerm]
    operators: List[LogicalOp] = field(default_factory=list)  # AND/OR between terms
    location: Optional[SourceLocation] = None
