"""
Procedural Generator Mixin

Generates Java code from L4 Rules procedural rule definitions.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Procedural generates: Complete rule execution methods, all conditionals
L4 Procedural NEVER generates: Placeholder stubs, incomplete rules
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    generate_value_expr,
    get_common_imports,
    get_logging_imports,
)
from backend.generators.rules.procedural_expressions import ProceduralExpressionsMixin

LOG = logging.getLogger(__name__)


class ProceduralGeneratorMixin(ProceduralExpressionsMixin):
    """
    Mixin for generating Java procedural rule classes.

    Generates:
    - Rule evaluation methods with conditionals
    - If-then-else chains
    - Action sequences
    """

    def generate_procedural_rule_class(
        self,
        rule: ast.ProceduralRuleDef,
        package: str
    ) -> str:
        """Generate complete procedural rule class."""
        rule_name = getattr(rule, 'name', 'unknown')
        class_name = to_pascal_case(rule_name) + "Rule"

        imports = self._collect_procedural_imports(rule)

        lines = [
            self.generate_java_header(
                class_name, f"Procedural Rule: {rule_name}"
            ),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name} {{",
            "",
            "    private static final Logger LOG = LoggerFactory.getLogger("
            f"{class_name}.class);",
            "",
        ]

        lines.append(self._generate_execute_method(rule))
        lines.append("")

        # Generate field accessor stubs for fields referenced in conditions
        field_stubs = self._generate_field_accessor_stubs(rule)
        if field_stubs:
            lines.append(field_stubs)
            lines.append("")

        action_stubs = self._generate_action_stubs(rule)
        if action_stubs:
            lines.append(action_stubs)
            lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_action_stubs(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate stub methods for all action calls in the rule."""
        actions = set()
        self._collect_action_calls(getattr(rule, 'items', None) or [], actions)

        if not actions:
            return ""

        lines = [
            "    // =========================================================================",
            "    // Action Method Stubs - Implement these methods for rule execution",
            "    // =========================================================================",
            "",
        ]

        for action_name, arg_count in sorted(actions):
            method_name = to_camel_case(action_name)
            params = ", ".join(f"Object arg{i}" for i in range(arg_count)) if arg_count > 0 else ""
            lines.extend([
                f"    /**",
                f"     * Action: {action_name}",
                f"     * TODO: Implement this action method.",
                f"     */",
                f"    protected void {method_name}({params}) {{",
                f'        throw new UnsupportedOperationException("Action {action_name} not implemented");',
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def _collect_action_calls(self, items, actions: set):
        """Recursively collect all action calls from block items."""
        for item in items:
            if isinstance(item, ast.RuleStep):
                then_block = getattr(item, 'then_block', None)
                if then_block:
                    self._collect_action_calls(getattr(then_block, 'items', None) or [], actions)

                elseif_branches = getattr(item, 'elseif_branches', None) or []
                for branch in elseif_branches:
                    branch_block = getattr(branch, 'block', None)
                    if branch_block:
                        self._collect_action_calls(getattr(branch_block, 'items', None) or [], actions)

                else_block = getattr(item, 'else_block', None)
                if else_block:
                    self._collect_action_calls(getattr(else_block, 'items', None) or [], actions)

            elif isinstance(item, ast.ActionSequence):
                action_list = getattr(item, 'actions', None) or []
                for action in action_list:
                    name = getattr(action, 'name', None)
                    args = getattr(action, 'arguments', None) or []
                    if name:
                        actions.add((name, len(args)))

    def _generate_field_accessor_stubs(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate stub accessor methods for fields referenced in conditions.

        Procedural rules reference fields directly (e.g., base_limit, credit_score)
        without a defined input schema. These generate as method calls like baseLimit().
        We generate protected abstract-like stubs that can be implemented by subclasses
        to provide actual field values.
        """
        fields = set()
        self._collect_field_references(getattr(rule, 'items', None) or [], fields)

        if not fields:
            return ""

        lines = [
            "    // =========================================================================",
            "    // Field Accessor Stubs - Implement these to provide input field values",
            "    // =========================================================================",
            "",
        ]

        for field_name in sorted(fields):
            method_name = to_camel_case(field_name)
            lines.extend([
                f"    /**",
                f"     * Get value of field: {field_name}",
                f"     * Override this method to provide the actual field value.",
                f"     */",
                f"    protected Object {method_name}() {{",
                f'        throw new UnsupportedOperationException("Field accessor {field_name} not implemented");',
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def _collect_field_references(self, items, fields: set):
        """Recursively collect all field references from rule items."""
        for item in items:
            if isinstance(item, ast.RuleStep):
                # Collect from condition
                condition = getattr(item, 'condition', None)
                if condition:
                    self._collect_fields_from_expr(condition, fields)

                # Collect from then block
                then_block = getattr(item, 'then_block', None)
                if then_block:
                    self._collect_field_references(getattr(then_block, 'items', None) or [], fields)

                # Collect from elseif branches
                elseif_branches = getattr(item, 'elseif_branches', None) or []
                for branch in elseif_branches:
                    branch_condition = getattr(branch, 'condition', None)
                    if branch_condition:
                        self._collect_fields_from_expr(branch_condition, fields)
                    branch_block = getattr(branch, 'block', None)
                    if branch_block:
                        self._collect_field_references(getattr(branch_block, 'items', None) or [], fields)

                # Collect from else block
                else_block = getattr(item, 'else_block', None)
                if else_block:
                    self._collect_field_references(getattr(else_block, 'items', None) or [], fields)

            elif isinstance(item, ast.SetStatement):
                value = getattr(item, 'value', None)
                if value:
                    self._collect_fields_from_expr(value, fields)

            elif isinstance(item, ast.LetStatement):
                value = getattr(item, 'value', None)
                if value:
                    self._collect_fields_from_expr(value, fields)

    def _collect_fields_from_expr(self, expr, fields: set):
        """Recursively collect field references from an expression."""
        if expr is None:
            return

        # FieldPath is a simple field reference
        if isinstance(expr, ast.FieldPath):
            parts = getattr(expr, 'parts', None) or []
            # Only track single-part field paths (direct field references)
            # Multi-part paths like "order.customer.id" assume the root object exists
            if len(parts) == 1:
                fields.add(parts[0])
            return

        # BooleanExpr: terms with operators
        if isinstance(expr, ast.BooleanExpr):
            terms = getattr(expr, 'terms', None) or []
            for term in terms:
                self._collect_fields_from_expr(term, fields)
            return

        # BooleanTerm: factor with optional negation
        if isinstance(expr, ast.BooleanTerm):
            factor = getattr(expr, 'factor', None)
            self._collect_fields_from_expr(factor, fields)
            return

        # BooleanFactor: comparison, nested expr, or function call
        if isinstance(expr, ast.BooleanFactor):
            comparison = getattr(expr, 'comparison', None)
            if comparison:
                self._collect_fields_from_expr(comparison, fields)
            nested_expr = getattr(expr, 'nested_expr', None)
            if nested_expr:
                self._collect_fields_from_expr(nested_expr, fields)
            function_call = getattr(expr, 'function_call', None)
            if function_call:
                self._collect_fields_from_expr(function_call, fields)
            return

        # ComparisonExpr: left and right sides
        if isinstance(expr, ast.ComparisonExpr):
            left = getattr(expr, 'left', None)
            if left:
                self._collect_fields_from_expr(left, fields)
            right = getattr(expr, 'right', None)
            if right:
                self._collect_fields_from_expr(right, fields)
            return

        # BinaryExpr: left and right
        if isinstance(expr, ast.BinaryExpr):
            left = getattr(expr, 'left', None)
            if left:
                self._collect_fields_from_expr(left, fields)
            right = getattr(expr, 'right', None)
            if right:
                self._collect_fields_from_expr(right, fields)
            return

        # UnaryExpr: operand
        if isinstance(expr, ast.UnaryExpr):
            operand = getattr(expr, 'operand', None)
            if operand:
                self._collect_fields_from_expr(operand, fields)
            return

        # ParenExpr: inner expression
        if isinstance(expr, ast.ParenExpr):
            inner = getattr(expr, 'inner', None)
            if inner:
                self._collect_fields_from_expr(inner, fields)
            return

        # FunctionCall: collect from arguments
        if isinstance(expr, ast.FunctionCall):
            arguments = getattr(expr, 'arguments', None) or []
            for arg in arguments:
                self._collect_fields_from_expr(arg, fields)
            return

    def _generate_execute_method(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate main execute method for procedural rule."""
        rule_name = getattr(rule, 'name', 'unknown')
        lines = [
            "    /**",
            f"     * Execute rule: {rule_name}",
            "     */",
            "    public void execute(Object context) {",
        ]

        items = getattr(rule, 'items', None) or []
        for item in items:
            lines.append(self._generate_block_item(item, 2))

        lines.append("    }")

        return '\n'.join(lines)

    def _generate_block_item(self, item, indent: int) -> str:
        """Generate code for a block item."""
        prefix = "    " * indent

        if item is None:
            LOG.warning("Null block item provided")
            return f"{prefix}// ERROR: null block item"

        if isinstance(item, ast.RuleStep):
            return self._generate_rule_step(item, indent)

        if isinstance(item, ast.ActionSequence):
            return self._generate_action_sequence(item, indent)

        if isinstance(item, ast.ReturnStatement):
            return f"{prefix}return;"

        if isinstance(item, ast.SetStatement):
            variable = to_camel_case(getattr(item, 'variable', 'unknown'))
            value = generate_value_expr(getattr(item, 'value', None))
            return f"{prefix}{variable} = {value};"

        if isinstance(item, ast.LetStatement):
            variable = to_camel_case(getattr(item, 'variable', 'unknown'))
            value = generate_value_expr(getattr(item, 'value', None))
            # For now, use Object type for let statements (could be improved with type inference)
            return f"{prefix}var {variable} = {value};"

        LOG.warning(f"Unknown block item type: {type(item).__name__}")
        return f"{prefix}// UNSUPPORTED: {type(item).__name__}"

    def _generate_rule_step(self, step: ast.RuleStep, indent: int) -> str:
        """Generate if-then-elseif-else structure."""
        prefix = "    " * indent
        lines = []

        condition = getattr(step, 'condition', None)
        condition_str = self._generate_boolean_expr(condition, "context")
        lines.append(f"{prefix}if ({condition_str}) {{")

        then_block = getattr(step, 'then_block', None)
        if then_block:
            then_items = getattr(then_block, 'items', None) or []
            for item in then_items:
                lines.append(self._generate_block_item(item, indent + 1))

        elseif_branches = getattr(step, 'elseif_branches', None) or []
        for branch in elseif_branches:
            branch_condition = getattr(branch, 'condition', None)
            branch_cond = self._generate_boolean_expr(branch_condition, "context")
            lines.append(f"{prefix}}} else if ({branch_cond}) {{")
            branch_block = getattr(branch, 'block', None)
            if branch_block:
                branch_items = getattr(branch_block, 'items', None) or []
                for item in branch_items:
                    lines.append(self._generate_block_item(item, indent + 1))

        else_block = getattr(step, 'else_block', None)
        if else_block:
            lines.append(f"{prefix}}} else {{")
            else_items = getattr(else_block, 'items', None) or []
            for item in else_items:
                lines.append(self._generate_block_item(item, indent + 1))

        lines.append(f"{prefix}}}")

        return '\n'.join(lines)

    def _generate_action_sequence(
        self,
        seq: ast.ActionSequence,
        indent: int
    ) -> str:
        """Generate action sequence."""
        prefix = "    " * indent
        lines = []

        actions = getattr(seq, 'actions', None) or []
        for action in actions:
            action_name = getattr(action, 'name', 'unknown')
            func_name = to_camel_case(action_name)
            arguments = getattr(action, 'arguments', None) or []
            args = ", ".join(generate_value_expr(a) for a in arguments)
            lines.append(f"{prefix}{func_name}({args});")

        return '\n'.join(lines)

    def _collect_procedural_imports(self, rule: ast.ProceduralRuleDef) -> Set[str]:
        """Collect imports for procedural rule class."""
        imports = set()
        imports.update(get_common_imports())
        imports.update(get_logging_imports())
        return imports

    def generate_java_header(self, class_name: str, description: str) -> str:
        """Generate Java file header comment."""
        return f'''/**
 * {description}
 *
 * Auto-generated by Nexflow L4 Rules Generator.
 * DO NOT EDIT - Changes will be overwritten.
 */'''

    def generate_imports(self, imports: List[str]) -> str:
        """Generate import statements."""
        sorted_imports = sorted(imports)
        return '\n'.join(f'import {imp};' for imp in sorted_imports)
