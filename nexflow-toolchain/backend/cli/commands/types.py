# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
CLI Command Result Types

Data classes for command results.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationError:
    """Validation error with location."""
    file: str
    line: Optional[int]
    column: Optional[int]
    message: str
    severity: str = "error"


@dataclass
class BuildResult:
    """Result of build command."""
    success: bool
    files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidateResult:
    """Result of validate command."""
    success: bool
    file_count: int = 0
    errors: List[ValidationError] = field(default_factory=list)


@dataclass
class ParseResult:
    """Result of parse command."""
    success: bool
    output: str = ""
    errors: List[ValidationError] = field(default_factory=list)


@dataclass
class InitResult:
    """Result of init command."""
    success: bool
    created: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class CleanResult:
    """Result of clean command."""
    success: bool
    removed_count: int = 0
