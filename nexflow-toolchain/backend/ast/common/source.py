"""
Source Location AST Type

Represents source location information for error reporting.
"""

from dataclasses import dataclass


@dataclass
class SourceLocation:
    """Source location for error reporting."""
    line: int
    column: int
    start_index: int = 0
    stop_index: int = 0
    file_path: str = ""

    def __str__(self) -> str:
        if self.file_path:
            return f"{self.file_path}:{self.line}:{self.column}"
        return f"line {self.line}, column {self.column}"
