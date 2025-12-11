"""
Transform AST Expression Types

Expression AST nodes for the Transform DSL.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation, FieldPath
from .enums import UnaryOp, ArithmeticOp, ComparisonOp, LogicalOp
from .literals import Literal, ListLiteral


@dataclass
class FunctionCall:
    """Function call expression."""
    name: str
    arguments: List['Expression'] = field(default_factory=list)
    object_ref: Optional['FieldPath'] = None  # For method calls like state.get_window(...)
    location: Optional[SourceLocation] = None


@dataclass
class WhenBranch:
    """When expression branch."""
    condition: 'Expression'
    result: 'Expression'
    location: Optional[SourceLocation] = None


@dataclass
class WhenExpression:
    """When-Otherwise conditional expression."""
    branches: List[WhenBranch]
    otherwise: 'Expression'
    location: Optional[SourceLocation] = None


@dataclass
class IndexExpression:
    """Array/list index expression."""
    base: FieldPath
    index: 'Expression'
    location: Optional[SourceLocation] = None


@dataclass
class OptionalChainExpression:
    """Optional chaining for null-safe access."""
    base: FieldPath
    chain: List[str]  # Additional field names accessed via ?.
    location: Optional[SourceLocation] = None


@dataclass
class UnaryExpression:
    """Unary operation expression."""
    operator: UnaryOp
    operand: 'Expression'
    location: Optional[SourceLocation] = None


@dataclass
class BinaryExpression:
    """Binary operation expression."""
    left: 'Expression'
    operator: Union[ArithmeticOp, ComparisonOp, LogicalOp, str]  # str for '??'
    right: 'Expression'
    location: Optional[SourceLocation] = None


@dataclass
class BetweenExpression:
    """Between expression for range checks."""
    value: 'Expression'
    lower: 'Expression'
    upper: 'Expression'
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class InExpression:
    """In expression for set membership."""
    value: 'Expression'
    values: ListLiteral
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class IsNullExpression:
    """Is null expression."""
    value: 'Expression'
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class ParenExpression:
    """Parenthesized expression."""
    inner: 'Expression'
    location: Optional[SourceLocation] = None


Expression = Union[
    Literal,
    FieldPath,
    FunctionCall,
    WhenExpression,
    IndexExpression,
    OptionalChainExpression,
    UnaryExpression,
    BinaryExpression,
    BetweenExpression,
    InExpression,
    IsNullExpression,
    ParenExpression
]
