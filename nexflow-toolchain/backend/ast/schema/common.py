# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema AST Common Types

Common dataclass types used across schema AST definitions.
"""

from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class SourceLocation:
    """Source location for error reporting."""
    line: int
    column: int
    start_index: int = 0
    stop_index: int = 0


@dataclass
class Duration:
    """Duration value with unit."""
    value: int
    unit: str  # 'ms', 's', 'm', 'h', 'd'

    def to_milliseconds(self) -> int:
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return self.value * multipliers.get(self.unit, 1)


@dataclass
class SizeSpec:
    """Size specification."""
    value: int
    unit: str  # 'KB', 'MB', 'GB', 'TB'


@dataclass
class FieldPath:
    """Field path reference (e.g., 'order.customer.id')."""
    parts: List[str]

    @property
    def path(self) -> str:
        return '.'.join(self.parts)


@dataclass
class RangeSpec:
    """Range specification for constraints."""
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_inclusive: bool = True
    max_inclusive: bool = True


@dataclass
class LengthSpec:
    """Length constraint specification."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
