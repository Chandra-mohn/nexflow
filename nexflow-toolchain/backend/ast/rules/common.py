# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Common Types

Common dataclasses shared across rules AST nodes.
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
class FieldPath:
    """Field path reference (e.g., 'order.customer.id')."""
    parts: List[str]
    index: Optional[int] = None  # For array access like customer[0]

    @property
    def path(self) -> str:
        result = '.'.join(self.parts)
        if self.index is not None:
            # Insert index after first part
            parts = self.parts.copy()
            parts[0] = f"{parts[0]}[{self.index}]"
            result = '.'.join(parts)
        return result
