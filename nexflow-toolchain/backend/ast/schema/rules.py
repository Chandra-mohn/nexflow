# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema AST Rule Blocks

Rule-related dataclasses for business_logic pattern.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation
from .types import FieldType


@dataclass
class RuleFieldDecl:
    """Rule field declaration (for given/return blocks)."""
    name: str
    field_type: FieldType
    location: Optional[SourceLocation] = None


@dataclass
class Expression:
    """Expression for calculations (simplified representation)."""
    raw_text: str  # Store raw expression text for now
    location: Optional[SourceLocation] = None


@dataclass
class Calculation:
    """Calculation assignment."""
    field_name: str
    expression: Expression
    location: Optional[SourceLocation] = None


@dataclass
class GivenBlock:
    """Given block (input parameters)."""
    fields: List[RuleFieldDecl]
    location: Optional[SourceLocation] = None


@dataclass
class CalculateBlock:
    """Calculate block (intermediate calculations)."""
    calculations: List[Calculation]
    location: Optional[SourceLocation] = None


@dataclass
class ReturnBlock:
    """Return block (output fields)."""
    fields: List[RuleFieldDecl]
    location: Optional[SourceLocation] = None


@dataclass
class RuleBlock:
    """Rule definition for business_logic pattern."""
    name: str
    given: GivenBlock
    calculate: Optional[CalculateBlock] = None
    return_block: ReturnBlock = None
    location: Optional[SourceLocation] = None


# =============================================================================
# Migration Block
# =============================================================================

@dataclass
class MigrationStatement:
    """Migration statement for schema evolution."""
    target_fields: List[str]  # Can be single field or multiple
    expression: Expression
    location: Optional[SourceLocation] = None


@dataclass
class MigrationBlock:
    """Migration block for schema evolution."""
    statements: List[MigrationStatement]
    location: Optional[SourceLocation] = None
