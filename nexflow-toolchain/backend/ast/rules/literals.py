"""
Rules AST Literal Types

Literal value types for the Rules DSL.
"""

from dataclasses import dataclass
from typing import List, Any, Union
from decimal import Decimal


@dataclass
class StringLiteral:
    value: str
    quote_type: str = '"'  # '"' or "'"


@dataclass
class IntegerLiteral:
    value: int


@dataclass
class DecimalLiteral:
    value: float


@dataclass
class MoneyLiteral:
    """Money literal like $100.00."""
    value: Decimal
    currency: str = "USD"


@dataclass
class PercentageLiteral:
    """Percentage literal like 25%."""
    value: float


@dataclass
class BooleanLiteral:
    value: bool


@dataclass
class NullLiteral:
    pass


@dataclass
class ListLiteral:
    values: List[Any]


Literal = Union[StringLiteral, IntegerLiteral, DecimalLiteral, MoneyLiteral,
                PercentageLiteral, BooleanLiteral, NullLiteral, ListLiteral]
