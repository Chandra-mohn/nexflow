"""
Schema AST Block Types

Block-level dataclasses for streaming, version, state machine, parameters, etc.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation, Duration, SizeSpec, FieldPath
from .enums import (
    CompatibilityMode, TimeSemantics, WatermarkStrategy,
    LateDataStrategy, IdleBehavior, RetentionPolicy
)
from .types import FieldType


# =============================================================================
# Version Block
# =============================================================================

@dataclass
class DeprecationDecl:
    """Deprecation information."""
    message: str
    deprecated_since: Optional[str] = None
    removal_version: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class VersionBlock:
    """Schema version and evolution configuration."""
    version: str
    compatibility: Optional[CompatibilityMode] = None
    previous_version: Optional[str] = None
    deprecation: Optional[DeprecationDecl] = None
    migration_guide: Optional[str] = None
    location: Optional[SourceLocation] = None


# =============================================================================
# Streaming Block
# =============================================================================

@dataclass
class SparsityBlock:
    """Field sparsity configuration."""
    dense_fields: Optional[List[str]] = None
    moderate_fields: Optional[List[str]] = None
    sparse_fields: Optional[List[str]] = None
    location: Optional[SourceLocation] = None


@dataclass
class RetentionOptions:
    """Retention configuration options."""
    time: Optional[Duration] = None
    size: Optional[SizeSpec] = None
    policy: Optional[RetentionPolicy] = None
    location: Optional[SourceLocation] = None


@dataclass
class StreamingBlock:
    """Streaming configuration for schema."""
    key_fields: Optional[List[str]] = None
    time_field: Optional[FieldPath] = None
    time_semantics: Optional[TimeSemantics] = None
    watermark_delay: Optional[Duration] = None
    watermark_strategy: Optional[WatermarkStrategy] = None
    max_out_of_orderness: Optional[Duration] = None
    watermark_interval: Optional[Duration] = None
    watermark_field: Optional[FieldPath] = None
    late_data_handling: Optional[LateDataStrategy] = None
    late_data_stream: Optional[str] = None
    allowed_lateness: Optional[Duration] = None
    idle_timeout: Optional[Duration] = None
    idle_behavior: Optional[IdleBehavior] = None
    sparsity: Optional[SparsityBlock] = None
    retention: Optional[RetentionOptions] = None
    location: Optional[SourceLocation] = None


# =============================================================================
# State Machine Block
# =============================================================================

@dataclass
class ActionCall:
    """Action call with parameters."""
    action_name: str
    parameters: List[str] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class TransitionDecl:
    """State transition declaration."""
    from_state: str
    to_states: List[str]
    trigger: Optional[str] = None       # Event that triggers transition (arrow syntax)
    location: Optional[SourceLocation] = None


@dataclass
class TransitionAction:
    """Action triggered on transition."""
    to_state: str
    action: ActionCall
    location: Optional[SourceLocation] = None


@dataclass
class StateMachineBlock:
    """State machine configuration."""
    for_entity: Optional[str] = None
    states: List[str] = field(default_factory=list)
    initial_state: Optional[str] = None
    transitions: List[TransitionDecl] = field(default_factory=list)
    on_transition_actions: List[TransitionAction] = field(default_factory=list)
    terminal_states: List[str] = field(default_factory=list)  # States marked as terminal/final
    location: Optional[SourceLocation] = None


# =============================================================================
# Parameters Block
# =============================================================================

@dataclass
class ParameterOption:
    """Parameter configuration option."""
    default_value: Optional['Literal'] = None
    range_spec: Optional['RangeSpec'] = None
    can_schedule: Optional[bool] = None
    change_frequency: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class ParameterDecl:
    """Parameter declaration."""
    name: str
    field_type: FieldType
    options: List[ParameterOption] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class ParametersBlock:
    """Parameters block for operational_parameters pattern."""
    parameters: List[ParameterDecl]
    location: Optional[SourceLocation] = None


# =============================================================================
# Entries Block
# =============================================================================

@dataclass
class EntryField:
    """Entry field value."""
    name: str
    value: 'Literal'
    location: Optional[SourceLocation] = None


@dataclass
class EntryDecl:
    """Reference data entry declaration."""
    key: str
    fields: List[EntryField]
    deprecated: bool = False
    deprecated_reason: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class EntriesBlock:
    """Entries block for reference_data pattern."""
    entries: List[EntryDecl]
    location: Optional[SourceLocation] = None


# =============================================================================
# Constraints Block
# =============================================================================

@dataclass
class ConstraintDecl:
    """Constraint declaration with condition and message."""
    condition: str
    message: str
    location: Optional[SourceLocation] = None


@dataclass
class ConstraintsBlock:
    """Constraints block for business rule validation."""
    constraints: List[ConstraintDecl]
    location: Optional[SourceLocation] = None
