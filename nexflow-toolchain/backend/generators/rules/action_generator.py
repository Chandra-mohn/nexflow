# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Action Generator Mixin

Generates Java action code from L4 Rules action AST nodes.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Action generates: Complete action execution code, all action types
L4 Action NEVER generates: Placeholder stubs, incomplete actions
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_getter,
    to_setter,
    generate_literal,
    generate_value_expr,
    generate_field_path,
    generate_unsupported_comment,
    get_common_imports,
)

LOG = logging.getLogger(__name__)


class ActionGeneratorMixin:
    """
    Mixin for generating Java action execution code.

    Generates:
    - Assign actions (set output value)
    - Calculate actions (compute value)
    - Lookup actions (external lookups)
    - Call actions (function calls)
    - Emit actions (output to stream)
    """

    def generate_action(
        self,
        action,
        output_var: str,
        output_field: str = None
    ) -> str:
        """Generate Java code for an action."""
        if action is None:
            LOG.warning("Null action provided")
            return "// ERROR: null action"

        if isinstance(action, ast.NoAction):
            return "// No action"

        if isinstance(action, ast.AssignAction):
            return self._generate_assign_action(action, output_var, output_field)

        if isinstance(action, ast.CalculateAction):
            return self._generate_calculate_action(action, output_var)

        if isinstance(action, ast.LookupAction):
            return self._generate_lookup_action(action, output_var)

        if isinstance(action, ast.CallAction):
            return self._generate_call_action(action)

        if isinstance(action, ast.EmitAction):
            return self._generate_emit_action(action)

        # For literal values used directly as actions
        if isinstance(action, (ast.StringLiteral, ast.IntegerLiteral,
                              ast.DecimalLiteral, ast.BooleanLiteral)):
            return self._generate_literal_action(action, output_var, output_field)

        return generate_unsupported_comment(f"action type {type(action).__name__}", "action_generator")

    def _generate_assign_action(
        self,
        action: ast.AssignAction,
        output_var: str,
        output_field: str
    ) -> str:
        """Generate assignment action."""
        field = getattr(action, 'field', None)
        if not field:
            LOG.warning("AssignAction missing field")
            return "// ERROR: assign action missing field"

        setter = to_setter(field)
        value = generate_literal(getattr(action, 'value', None))
        return f'{output_var}.{setter}({value});'

    def _generate_calculate_action(
        self,
        action: ast.CalculateAction,
        output_var: str
    ) -> str:
        """Generate calculation action."""
        expression = getattr(action, 'expression', None)
        expr = generate_value_expr(expression)
        target = getattr(action, 'target', None)
        if target:
            setter = to_setter(target)
            return f'{output_var}.{setter}({expr});'
        return expr

    def _generate_lookup_action(
        self,
        action: ast.LookupAction,
        output_var: str
    ) -> str:
        """Generate lookup action."""
        lookup_name = getattr(action, 'lookup_name', None)
        if not lookup_name:
            LOG.warning("LookupAction missing lookup_name")
            return "// ERROR: lookup action missing lookup_name"

        lookup_method = to_camel_case(lookup_name)
        arguments = getattr(action, 'arguments', None) or []
        args = ", ".join(generate_value_expr(a) for a in arguments)

        lines = [f'// Lookup: {lookup_name}']
        lines.append(f'var lookupResult = {lookup_method}({args});')

        target = getattr(action, 'target', None)
        if target:
            setter = to_setter(target)
            lines.append(f'{output_var}.{setter}(lookupResult);')

        return '\n'.join(lines)

    def _generate_call_action(self, action: ast.CallAction) -> str:
        """Generate function call action."""
        function_name = getattr(action, 'function_name', None)
        if not function_name:
            LOG.warning("CallAction missing function_name")
            return "// ERROR: call action missing function_name"

        func_name = to_camel_case(function_name)
        arguments = getattr(action, 'arguments', None) or []
        args = ", ".join(self._generate_action_arg(a) for a in arguments)
        return f'{func_name}({args});'

    def _generate_emit_action(self, action: ast.EmitAction) -> str:
        """Generate emit to output stream action."""
        target = getattr(action, 'target', None)
        if not target:
            LOG.warning("EmitAction missing target")
            return "// ERROR: emit action missing target"
        return f'ctx.output({target}Tag, value);'

    def _generate_literal_action(
        self,
        literal,
        output_var: str,
        output_field: str
    ) -> str:
        """Generate action for direct literal value."""
        value = generate_literal(literal)
        if output_field:
            setter = to_setter(output_field)
            return f'{output_var}.{setter}({value});'
        return f'return {value};'

    def _generate_action_arg(self, arg) -> str:
        """Generate action argument."""
        if arg is None:
            return "null"

        name = getattr(arg, 'name', None)
        value = getattr(arg, 'value', None)
        value_expr = generate_value_expr(value)

        if name:
            # Named argument (as comment for clarity)
            return f'/* {name}: */ {value_expr}'
        return value_expr

    def generate_action_call_stmt(self, stmt) -> str:
        """Generate action call statement for procedural rules."""
        if stmt is None:
            LOG.warning("Null action call statement")
            return "// ERROR: null action call statement"

        name = getattr(stmt, 'name', None)
        if not name:
            LOG.warning("ActionCallStmt missing name")
            return "// ERROR: action call missing name"

        func_name = to_camel_case(name)
        arguments = getattr(stmt, 'arguments', None) or []
        args = ", ".join(generate_value_expr(a) for a in arguments)
        return f'{func_name}({args});'

    def generate_action_sequence(self, seq) -> str:
        """Generate sequence of action calls."""
        if seq is None:
            return ""

        actions = getattr(seq, 'actions', None) or []
        lines = [self.generate_action_call_stmt(a) for a in actions]
        return '\n'.join(lines)

    def get_action_imports(self) -> Set[str]:
        """Get required imports for action generation."""
        return get_common_imports()
