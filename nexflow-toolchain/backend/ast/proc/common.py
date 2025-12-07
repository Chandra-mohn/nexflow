"""
Process AST Common Types

Common dataclass types used across process AST definitions.
"""

from dataclasses import dataclass
from typing import Optional, List


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
class FieldPath:
    """Field path reference (e.g., 'order.customer.id')."""
    parts: List[str]

    @property
    def path(self) -> str:
        return '.'.join(self.parts)
