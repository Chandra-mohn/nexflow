"""
Transform AST Block Types

Apply, mappings, compose, validation, and error handling blocks.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation, FieldPath
from .enums import ComposeType, SeverityLevel, ErrorActionType, LogLevel
from .expressions import Expression


# =============================================================================
# Apply Block
# =============================================================================

@dataclass
class Assignment:
    """Field assignment."""
    target: FieldPath
    value: Expression
    location: Optional[SourceLocation] = None


@dataclass
class LocalAssignment:
    """Local variable assignment."""
    name: str
    value: Expression
    location: Optional[SourceLocation] = None


@dataclass
class ApplyBlock:
    """Apply block containing transformation logic."""
    statements: List[Union[Assignment, LocalAssignment]]
    location: Optional[SourceLocation] = None


# =============================================================================
# Mappings Block
# =============================================================================

@dataclass
class Mapping:
    """Field mapping."""
    target: FieldPath
    expression: Expression
    location: Optional[SourceLocation] = None


@dataclass
class MappingsBlock:
    """Mappings block for block-level transforms."""
    mappings: List[Mapping]
    location: Optional[SourceLocation] = None


# =============================================================================
# Compose Block
# =============================================================================

@dataclass
class ComposeRef:
    """Transform composition reference."""
    transform_name: str
    condition: Optional[Expression] = None  # For conditional composition
    is_otherwise: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class ComposeBlock:
    """Transform composition block."""
    compose_type: Optional[ComposeType] = None
    refs: List[ComposeRef] = field(default_factory=list)
    then_type: Optional[ComposeType] = None
    then_refs: List[ComposeRef] = field(default_factory=list)
    location: Optional[SourceLocation] = None


# =============================================================================
# Validation Blocks
# =============================================================================

@dataclass
class ValidationMessageObject:
    """Structured validation message."""
    message: str
    code: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    location: Optional[SourceLocation] = None


@dataclass
class ValidationRule:
    """Validation rule."""
    condition: Expression
    message: Union[str, ValidationMessageObject]
    nested_rules: Optional[List['ValidationRule']] = None  # For when blocks
    location: Optional[SourceLocation] = None


@dataclass
class ValidateInputBlock:
    """Input validation block."""
    rules: List[ValidationRule]
    location: Optional[SourceLocation] = None


@dataclass
class ValidateOutputBlock:
    """Output validation block."""
    rules: List[ValidationRule]
    location: Optional[SourceLocation] = None


@dataclass
class InvariantBlock:
    """Invariant validation block."""
    rules: List[ValidationRule]
    location: Optional[SourceLocation] = None


# =============================================================================
# Error Handling
# =============================================================================

@dataclass
class ErrorAction:
    """Error handling action."""
    action_type: Optional[ErrorActionType] = None
    default_value: Optional[Expression] = None
    log_level: Optional[LogLevel] = None
    emit_to: Optional[str] = None
    error_code: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class OnErrorBlock:
    """Error handling block."""
    actions: List[ErrorAction]
    location: Optional[SourceLocation] = None


# =============================================================================
# On Change Block
# =============================================================================

@dataclass
class RecalculateBlock:
    """Recalculation block."""
    assignments: List[Assignment]
    location: Optional[SourceLocation] = None


@dataclass
class OnChangeBlock:
    """Change tracking block."""
    watched_fields: List[str]
    recalculate: RecalculateBlock
    location: Optional[SourceLocation] = None
