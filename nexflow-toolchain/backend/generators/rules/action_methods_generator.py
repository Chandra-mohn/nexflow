# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Action Methods Generator Mixin

Generates Java code for L4 action method declarations.

RFC REFERENCE: See docs/RFC-Method-Implementation-Strategy.md (Solution 5)
─────────────────────────────────────────────────────────────────────
Action methods generate: Complete action implementations based on target type
Actions categorize:
- Emit: Output to side streams (OutputTag pattern)
- State: Update process state (via StateContext)
- Audit: Log/audit trail operations
- Call: External service calls
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List, Optional, TYPE_CHECKING

from backend.ast.rules.actions import (
    ActionsBlock, ActionDecl, ActionTargetType, ActionDeclParam,
    EmitTarget, StateTarget, AuditTarget, CallTarget
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class ActionMethodsGeneratorMixin:
    """
    Mixin for generating Java action method code.

    Generates:
    - Action method implementations with proper signatures
    - Emit actions with OutputTag integration
    - State actions with StateContext calls
    - Audit actions with logging/audit trail
    - Call actions with service delegation
    """

    def generate_action_methods(self, actions: ActionsBlock, context_class: str = "context") -> str:
        """Generate action method implementations.

        Args:
            actions: ActionsBlock AST node
            context_class: Name of the context variable (for state/emit access)

        Returns:
            Java code for action methods
        """
        if not actions or not actions.actions:
            return ""

        lines = []
        lines.append("    // =========================================================================")
        lines.append("    // Action Methods (auto-generated from DSL actions block)")
        lines.append("    // RFC: docs/RFC-Method-Implementation-Strategy.md (Solution 5)")
        lines.append("    // =========================================================================")
        lines.append("")

        for action in actions.actions:
            lines.append(self._generate_action_method(action, context_class))
            lines.append("")

        return '\n'.join(lines)

    def _generate_action_method(self, action: ActionDecl, context_class: str) -> str:
        """Generate a single action method."""
        method_name = self._to_java_method_name(action.name)
        params = self._generate_action_method_params(action.params)
        
        lines = []
        lines.append(f"    /**")
        lines.append(f"     * Action: {action.name}")
        lines.append(f"     * Target: {action.target_type.value}")
        if action.emit_target:
            lines.append(f"     * Emits to: {action.emit_target.output_name}")
        if action.state_target:
            lines.append(f"     * Updates: {action.state_target.state_name}.{action.state_target.operation.operation_name}")
        if action.call_target:
            lines.append(f"     * Calls: {action.call_target.service_name}.{action.call_target.method_name}")
        lines.append(f"     */")

        if action.target_type == ActionTargetType.EMIT:
            lines.extend(self._generate_emit_action_method(action, method_name, params, context_class))
        elif action.target_type == ActionTargetType.STATE:
            lines.extend(self._generate_state_action_method(action, method_name, params, context_class))
        elif action.target_type == ActionTargetType.AUDIT:
            lines.extend(self._generate_audit_action_method(action, method_name, params))
        elif action.target_type == ActionTargetType.CALL:
            lines.extend(self._generate_call_action_method(action, method_name, params))

        return '\n'.join(lines)

    def _generate_emit_action_method(
        self,
        action: ActionDecl,
        method_name: str,
        params: str,
        context_class: str
    ) -> List[str]:
        """Generate emit action method body."""
        lines = []
        output_tag = self._to_output_tag_name(action.emit_target.output_name)
        
        # Determine what to emit based on parameters
        if len(action.params) == 1:
            # Single parameter - emit directly
            emit_value = action.params[0].name
        elif len(action.params) > 1:
            # Multiple parameters - create a record/map
            emit_value = self._build_emit_record(action.params)
        else:
            emit_value = "null"

        lines.append(f"    protected void {method_name}({params}, Context ctx) {{")
        lines.append(f"        ctx.output({output_tag}, {emit_value});")
        lines.append(f"    }}")

        return lines

    def _generate_state_action_method(
        self,
        action: ActionDecl,
        method_name: str,
        params: str,
        context_class: str
    ) -> List[str]:
        """Generate state-updating action method body."""
        lines = []
        state_name = action.state_target.state_name
        operation = action.state_target.operation
        
        # Map common operations to context method calls
        op_name = operation.operation_name.lower()
        state_method = self._to_state_method(state_name, op_name)
        
        # Build argument list for state method
        if operation.argument:
            # Use the operation's hardcoded argument
            state_args = f'"{operation.argument}"'
        elif action.params:
            # Use the action's parameters
            state_args = ", ".join(p.name for p in action.params)
        else:
            state_args = ""

        lines.append(f"    protected void {method_name}({params}) throws Exception {{")
        lines.append(f"        {context_class}.{state_method}({state_args});")
        lines.append(f"    }}")

        return lines

    def _generate_audit_action_method(
        self,
        action: ActionDecl,
        method_name: str,
        params: str
    ) -> List[str]:
        """Generate audit/logging action method body."""
        lines = []
        
        # Build audit map from parameters
        audit_entries = []
        for param in action.params:
            audit_entries.append(f'"{param.name}", {param.name}')

        lines.append(f"    protected void {method_name}({params}) {{")
        if audit_entries:
            lines.append(f"        AuditLog.log(\"{action.name}\", Map.of(")
            lines.append(f"            {', '.join(audit_entries)},")
            lines.append(f"            \"timestamp\", Instant.now()")
            lines.append(f"        ));")
        else:
            lines.append(f"        AuditLog.log(\"{action.name}\", Map.of(")
            lines.append(f"            \"timestamp\", Instant.now()")
            lines.append(f"        ));")
        lines.append(f"    }}")

        return lines

    def _generate_call_action_method(
        self,
        action: ActionDecl,
        method_name: str,
        params: str
    ) -> List[str]:
        """Generate external service call action method body."""
        lines = []
        service_field = self._to_field_name(action.call_target.service_name)
        service_method = action.call_target.method_name
        
        # Build argument list for service call
        call_args = ", ".join(p.name for p in action.params)

        lines.append(f"    protected void {method_name}({params}) {{")
        lines.append(f"        {service_field}.{service_method}({call_args});")
        lines.append(f"    }}")

        return lines

    def _generate_action_method_params(self, params: List[ActionDeclParam]) -> str:
        """Generate Java parameter list for action method."""
        java_params = []
        for param in params:
            java_type = self._map_action_param_type(param.param_type)
            java_params.append(f"{java_type} {param.name}")
        return ", ".join(java_params)

    def _map_action_param_type(self, param_type: str) -> str:
        """Map DSL parameter type to Java type."""
        type_map = {
            'text': 'String',
            'string': 'String',
            'number': 'BigDecimal',
            'decimal': 'BigDecimal',
            'integer': 'Integer',
            'int': 'Integer',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'date': 'LocalDate',
            'timestamp': 'Instant',
            'datetime': 'Instant',
        }
        return type_map.get(param_type.lower(), param_type)

    def _to_java_method_name(self, name: str) -> str:
        """Convert DSL action name to Java method name (camelCase)."""
        parts = name.replace('-', '_').split('_')
        return parts[0].lower() + ''.join(part.capitalize() for part in parts[1:])

    def _to_output_tag_name(self, name: str) -> str:
        """Convert output name to OutputTag constant name."""
        return name.upper() + "_TAG"

    def _to_state_method(self, state_name: str, operation: str) -> str:
        """Build state context method name."""
        state_pascal = ''.join(part.capitalize() for part in state_name.split('_'))
        
        # Map common operations to standard method names
        op_map = {
            'add': f'add{state_pascal}',
            'remove': f'remove{state_pascal}',
            'clear': f'clear{state_pascal}',
            'set': f'set{state_pascal}',
            'get': f'get{state_pascal}',
            'append': f'append{state_pascal}',
            'increment': f'increment{state_pascal}',
            'decrement': f'decrement{state_pascal}',
        }
        return op_map.get(operation, f'{operation}{state_pascal}')

    def _to_field_name(self, class_name: str) -> str:
        """Convert class name to field name (camelCase)."""
        if not class_name:
            return "service"
        return class_name[0].lower() + class_name[1:]

    def _build_emit_record(self, params: List[ActionDeclParam]) -> str:
        """Build a record/map for multiple emit parameters."""
        entries = ", ".join(f'"{p.name}", {p.name}' for p in params)
        return f"Map.of({entries})"

    def get_action_methods_imports(self, actions: ActionsBlock) -> Set[str]:
        """Get required imports for action method generation."""
        if not actions or not actions.actions:
            return set()

        imports = set()
        imports.add('java.time.Instant')
        imports.add('java.util.Map')

        for action in actions.actions:
            # Add type imports based on parameters
            for param in action.params:
                param_type = self._map_action_param_type(param.param_type)
                if param_type == 'BigDecimal':
                    imports.add('java.math.BigDecimal')
                elif param_type == 'LocalDate':
                    imports.add('java.time.LocalDate')
                elif param_type == 'Instant':
                    imports.add('java.time.Instant')

            # Add Flink context import for emit actions
            if action.target_type == ActionTargetType.EMIT:
                imports.add('org.apache.flink.streaming.api.functions.ProcessFunction.Context')

        return imports

    def has_actions(self, program: 'ast.Program') -> bool:
        """Check if program has action declarations."""
        return program.actions is not None and len(program.actions.actions) > 0
