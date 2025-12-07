"""
Action Generator Mixin

Generates Java action code from L4 Rules action AST nodes.
"""

from typing import Set

from backend.ast import rules_ast as ast


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
        action: ast.Action,
        output_var: str,
        output_field: str = None
    ) -> str:
        """Generate Java code for an action."""
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

        return "/* UNSUPPORTED ACTION */"

    def _generate_assign_action(
        self,
        action: ast.AssignAction,
        output_var: str,
        output_field: str
    ) -> str:
        """Generate assignment action."""
        setter = self._to_setter(action.field)
        value = self._generate_literal(action.value)
        return f'{output_var}.{setter}({value});'

    def _generate_calculate_action(
        self,
        action: ast.CalculateAction,
        output_var: str
    ) -> str:
        """Generate calculation action."""
        expr = self._generate_value_expr(action.expression)
        if action.target:
            setter = self._to_setter(action.target)
            return f'{output_var}.{setter}({expr});'
        return expr

    def _generate_lookup_action(
        self,
        action: ast.LookupAction,
        output_var: str
    ) -> str:
        """Generate lookup action."""
        lookup_name = self._to_camel_case(action.lookup_name)
        args = ", ".join(self._generate_value_expr(a) for a in action.arguments)

        lines = [f'// Lookup: {action.lookup_name}']
        lines.append(f'var lookupResult = {lookup_name}({args});')

        if action.target:
            setter = self._to_setter(action.target)
            lines.append(f'{output_var}.{setter}(lookupResult);')

        return '\n'.join(lines)

    def _generate_call_action(self, action: ast.CallAction) -> str:
        """Generate function call action."""
        func_name = self._to_camel_case(action.function_name)
        args = ", ".join(
            self._generate_action_arg(a) for a in action.arguments
        )
        return f'{func_name}({args});'

    def _generate_emit_action(self, action: ast.EmitAction) -> str:
        """Generate emit to output stream action."""
        target = action.target
        return f'ctx.output({target}Tag, value);'

    def _generate_literal_action(
        self,
        literal: ast.Literal,
        output_var: str,
        output_field: str
    ) -> str:
        """Generate action for direct literal value."""
        value = self._generate_literal(literal)
        if output_field:
            setter = self._to_setter(output_field)
            return f'{output_var}.{setter}({value});'
        return f'return {value};'

    def _generate_action_arg(self, arg: ast.ActionArg) -> str:
        """Generate action argument."""
        if arg.name:
            # Named argument
            return f'/* {arg.name}: */ {self._generate_value_expr(arg.value)}'
        return self._generate_value_expr(arg.value)

    def generate_action_call_stmt(self, stmt: ast.ActionCallStmt) -> str:
        """Generate action call statement for procedural rules."""
        func_name = self._to_camel_case(stmt.name)
        args = ", ".join(self._generate_value_expr(a) for a in stmt.arguments)
        return f'{func_name}({args});'

    def generate_action_sequence(self, seq: ast.ActionSequence) -> str:
        """Generate sequence of action calls."""
        lines = [self.generate_action_call_stmt(a) for a in seq.actions]
        return '\n'.join(lines)

    def _generate_literal(self, literal: ast.Literal) -> str:
        """Generate Java literal from AST literal."""
        if isinstance(literal, ast.StringLiteral):
            return f'"{literal.value}"'
        if isinstance(literal, ast.IntegerLiteral):
            return f'{literal.value}L'
        if isinstance(literal, ast.DecimalLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.MoneyLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.PercentageLiteral):
            return f'new BigDecimal("{literal.value / 100.0}")'
        if isinstance(literal, ast.BooleanLiteral):
            return 'true' if literal.value else 'false'
        if isinstance(literal, ast.NullLiteral):
            return 'null'
        return 'null'

    def _generate_value_expr(self, expr) -> str:
        """Generate Java code for a value expression."""
        if isinstance(expr, ast.FieldPath):
            return self._generate_field_path(expr)
        if isinstance(expr, ast.FunctionCall):
            args = ", ".join(self._generate_value_expr(a) for a in expr.arguments)
            return f'{self._to_camel_case(expr.name)}({args})'
        if hasattr(expr, 'value'):
            return self._generate_literal(expr)
        return str(expr)

    def _generate_field_path(self, fp: ast.FieldPath) -> str:
        """Generate Java getter chain."""
        parts = fp.parts
        if len(parts) == 1:
            return self._to_getter(parts[0])
        return ".".join(self._to_getter(p) for p in parts)

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _to_setter(self, field_name: str) -> str:
        """Convert field name to setter method name."""
        camel = self._to_camel_case(field_name)
        return f"set{camel[0].upper()}{camel[1:]}"

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_action_imports(self) -> Set[str]:
        """Get required imports for action generation."""
        return {
            'java.math.BigDecimal',
        }
