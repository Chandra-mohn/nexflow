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


# ============================================================================
# Action Method Declarations (RFC Solution 5)
# RFC REFERENCE: See docs/RFC-Method-Implementation-Strategy.md (Solution 5)
#
# Actions categorize domain-specific business operations and their implementations:
# - Emit: Output to side streams (OutputTag pattern)
# - State: Update process state (via StateContext)
# - Audit: Log/audit trail operations
# - Call: External service calls
# ============================================================================

from enum import Enum


class ActionTargetType(Enum):
    """Types of action implementation targets."""
    EMIT = "emit"       # Emit to side output
    STATE = "state"     # Update state
    AUDIT = "audit"     # Audit/logging
    CALL = "call"       # External service call


@dataclass
class ActionDeclParam:
    """Parameter for an action declaration."""
    name: str
    param_type: str
    location: Optional[SourceLocation] = None


@dataclass
class EmitTarget:
    """Target for emit actions - output to side stream."""
    output_name: str
    location: Optional[SourceLocation] = None


@dataclass
class StateOperation:
    """State operation specification."""
    operation_name: str
    argument: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class StateTarget:
    """Target for state-updating actions."""
    state_name: str
    operation: StateOperation
    location: Optional[SourceLocation] = None


@dataclass
class AuditTarget:
    """Target for audit/logging actions."""
    location: Optional[SourceLocation] = None


@dataclass
class CallTarget:
    """Target for external service call actions."""
    service_name: str
    method_name: str
    location: Optional[SourceLocation] = None


@dataclass
class ActionDecl:
    """
    Declaration of an action method and its implementation.

    Example DSL:
        add_risk_factor(name: string, score: integer) -> emit to risk_factors_output
        add_flag(flag: string) -> state flags.add(flag)
        log_decision(decision: string, reason: string) -> audit
        notify_fraud_team(transaction_id: string) -> call NotificationService.alert
    """
    name: str
    params: List[ActionDeclParam] = field(default_factory=list)
    target_type: ActionTargetType = ActionTargetType.EMIT
    # One of these will be set based on target_type
    emit_target: Optional[EmitTarget] = None
    state_target: Optional[StateTarget] = None
    audit_target: Optional[AuditTarget] = None
    call_target: Optional[CallTarget] = None
    location: Optional[SourceLocation] = None

    def is_emit(self) -> bool:
        """Check if this action emits to a side output."""
        return self.target_type == ActionTargetType.EMIT

    def is_state(self) -> bool:
        """Check if this action updates state."""
        return self.target_type == ActionTargetType.STATE

    def is_audit(self) -> bool:
        """Check if this action is an audit operation."""
        return self.target_type == ActionTargetType.AUDIT

    def is_call(self) -> bool:
        """Check if this action calls an external service."""
        return self.target_type == ActionTargetType.CALL


@dataclass
class ActionsBlock:
    """
    Block of action method declarations.

    Example DSL:
        actions {
            add_risk_factor(name: string, score: integer) -> emit to risk_factors_output
            add_flag(flag: string) -> state flags.add(flag)
            log_decision(decision: string, reason: string) -> audit
        }
    """
    actions: List[ActionDecl] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    def get_action(self, name: str) -> Optional[ActionDecl]:
        """Get action declaration by name."""
        for action in self.actions:
            if action.name == name:
                return action
        return None

    def get_emit_actions(self) -> List[ActionDecl]:
        """Get all emit actions."""
        return [a for a in self.actions if a.is_emit()]

    def get_state_actions(self) -> List[ActionDecl]:
        """Get all state-updating actions."""
        return [a for a in self.actions if a.is_state()]

    def get_audit_actions(self) -> List[ActionDecl]:
        """Get all audit actions."""
        return [a for a in self.actions if a.is_audit()]

    def get_call_actions(self) -> List[ActionDecl]:
        """Get all external call actions."""
        return [a for a in self.actions if a.is_call()]
