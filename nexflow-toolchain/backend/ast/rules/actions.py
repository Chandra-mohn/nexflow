"""
Rules AST Action Types

Action types for decision table results.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union, TYPE_CHECKING

from .common import SourceLocation
from .literals import Literal

if TYPE_CHECKING:
    from .expressions import ValueExpr


@dataclass
class NoAction:
    """No action (- wildcard in action column)."""
    location: Optional[SourceLocation] = None


@dataclass
class AssignAction:
    """Assign literal value action."""
    value: Literal
    location: Optional[SourceLocation] = None


@dataclass
class CalculateAction:
    """Calculate expression action."""
    expression: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class LookupAction:
    """Lookup from reference data action."""
    table_name: str
    keys: List['ValueExpr'] = field(default_factory=list)
    default_value: Optional['ValueExpr'] = None
    as_of: Optional['ValueExpr'] = None  # For temporal lookups
    location: Optional[SourceLocation] = None


@dataclass
class ActionArg:
    """Action argument (positional or named)."""
    value: 'ValueExpr'
    name: Optional[str] = None  # For named arguments
    location: Optional[SourceLocation] = None


@dataclass
class CallAction:
    """Call function/action action."""
    function_name: str
    arguments: List[ActionArg] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class EmitAction:
    """Emit to output stream action."""
    target: str
    location: Optional[SourceLocation] = None


Action = Union[NoAction, AssignAction, CalculateAction, LookupAction, CallAction, EmitAction]
