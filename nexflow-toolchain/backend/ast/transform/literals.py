# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform AST Literal Types

Literal value types for the Transform DSL.
"""

from dataclasses import dataclass
from typing import List, Any, Union


@dataclass
class StringLiteral:
    value: str


@dataclass
class IntegerLiteral:
    value: int


@dataclass
class DecimalLiteral:
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


Literal = Union[StringLiteral, IntegerLiteral, DecimalLiteral, BooleanLiteral, NullLiteral, ListLiteral]
