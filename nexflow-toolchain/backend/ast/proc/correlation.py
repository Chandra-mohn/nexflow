# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Correlation Block

Correlation-related dataclasses for process AST.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation, Duration
from .enums import TimeoutActionType, CompletionConditionType


@dataclass
class TimeoutAction:
    """Timeout action configuration."""
    action_type: TimeoutActionType
    target: Optional[str] = None  # For emit/dead_letter
    location: Optional[SourceLocation] = None


@dataclass
class CompletionCondition:
    """Completion condition for hold buffers."""
    condition_type: CompletionConditionType
    count_threshold: Optional[int] = None  # For COUNT type
    rule_name: Optional[str] = None  # For RULE type
    location: Optional[SourceLocation] = None


@dataclass
class CompletionClause:
    """Hold completion clause."""
    condition: CompletionCondition
    location: Optional[SourceLocation] = None


@dataclass
class AwaitDecl:
    """Await (event-driven correlation) declaration."""
    initial_event: str
    trigger_event: str
    matching_fields: List[str]
    timeout: Duration
    timeout_action: TimeoutAction
    location: Optional[SourceLocation] = None


@dataclass
class HoldDecl:
    """Hold (buffer-based correlation) declaration."""
    event: str
    buffer_name: Optional[str] = None
    keyed_by: List[str] = field(default_factory=list)
    completion: Optional[CompletionClause] = None
    timeout: Optional[Duration] = None
    timeout_action: Optional[TimeoutAction] = None
    location: Optional[SourceLocation] = None
