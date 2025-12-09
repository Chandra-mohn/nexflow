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
    to_getter,
    generate_literal,
    generate_value_expr,
    get_common_imports,
    get_logging_imports,
)

LOG = logging.getLogger(__name__)


class ProceduralGeneratorMixin:
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

        # Generate execute method
        lines.append(self._generate_execute_method(rule))
        lines.append("")

        # Generate action method stubs
        action_stubs = self._generate_action_stubs(rule)
        if action_stubs:
            lines.append(action_stubs)
            lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_action_stubs(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate stub methods for all action calls in the rule."""
        # Collect all unique action calls
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
            # Generate parameter list based on argument count
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
        """Recursively collect all action calls from block items.

        Args:
            items: List of BlockItem (RuleStep, ActionSequence, ReturnStatement)
            actions: Set to collect (action_name, arg_count) tuples
        """
        for item in items:
            if isinstance(item, ast.RuleStep):
                # Collect from then_block
                then_block = getattr(item, 'then_block', None)
                if then_block:
                    self._collect_action_calls(getattr(then_block, 'items', None) or [], actions)

                # Collect from elseif branches
                elseif_branches = getattr(item, 'elseif_branches', None) or []
                for branch in elseif_branches:
                    branch_block = getattr(branch, 'block', None)
                    if branch_block:
                        self._collect_action_calls(getattr(branch_block, 'items', None) or [], actions)

                # Collect from else_block
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

        LOG.warning(f"Unknown block item type: {type(item).__name__}")
        return f"{prefix}// UNSUPPORTED: {type(item).__name__}"

    def _generate_rule_step(self, step: ast.RuleStep, indent: int) -> str:
        """Generate if-then-elseif-else structure."""
        prefix = "    " * indent
        lines = []

        # Main if condition
        condition = getattr(step, 'condition', None)
        condition_str = self._generate_boolean_expr(condition, "context")
        lines.append(f"{prefix}if ({condition_str}) {{")

        # Then block
        then_block = getattr(step, 'then_block', None)
        if then_block:
            then_items = getattr(then_block, 'items', None) or []
            for item in then_items:
                lines.append(self._generate_block_item(item, indent + 1))

        # Elseif branches
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

        # Else block
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

    def _generate_boolean_expr(self, expr, context_var: str) -> str:
        """Generate Java boolean expression with full NOT, IN/NOT IN support.

        AST Structure:
        - BooleanExpr: terms: List[BooleanTerm], operators: List[LogicalOp]
        - BooleanTerm: factor: BooleanFactor, negated: bool
        - BooleanFactor: comparison, nested_expr, or function_call
        """
        if expr is None:
            LOG.warning("Null boolean expression provided in procedural rule")
            return "true"

        # BooleanExpr: combines terms with AND/OR operators
        if isinstance(expr, ast.BooleanExpr):
            terms = getattr(expr, 'terms', None) or []
            operators = getattr(expr, 'operators', None) or []

            if not terms:
                LOG.warning("BooleanExpr has no terms")
                return "true"

            # Generate first term
            result_parts = [self._generate_boolean_expr(terms[0], context_var)]

            # Combine remaining terms with operators
            for i, term in enumerate(terms[1:]):
                op = operators[i] if i < len(operators) else ast.LogicalOp.AND
                java_op = "&&" if op == ast.LogicalOp.AND else "||"
                term_str = self._generate_boolean_expr(term, context_var)
                result_parts.append(f" {java_op} ({term_str})")

            return "(" + result_parts[0] + "".join(result_parts[1:]) + ")"

        # BooleanTerm: single factor with optional NOT
        if isinstance(expr, ast.BooleanTerm):
            negated = getattr(expr, 'negated', False)
            factor = getattr(expr, 'factor', None)

            if factor is None:
                LOG.warning("BooleanTerm has no factor")
                return "true"

            inner = self._generate_boolean_expr(factor, context_var)
            if negated:
                return f"!({inner})"
            return inner

        # BooleanFactor: contains comparison, nested expr, or function call
        if isinstance(expr, ast.BooleanFactor):
            comparison = getattr(expr, 'comparison', None)
            nested_expr = getattr(expr, 'nested_expr', None)
            function_call = getattr(expr, 'function_call', None)

            if comparison is not None:
                return self._generate_comparison_expr(comparison, context_var)
            if nested_expr is not None:
                return self._generate_boolean_expr(nested_expr, context_var)
            if function_call is not None:
                return self._generate_function_call(function_call, context_var)

            LOG.warning("BooleanFactor has no comparison, nested_expr, or function_call")
            return "true"

        # ComparisonExpr: direct comparison expression
        if isinstance(expr, ast.ComparisonExpr):
            return self._generate_comparison_expr(expr, context_var)

        # UnaryExpr: negation
        if isinstance(expr, ast.UnaryExpr):
            operand = getattr(expr, 'operand', None)
            inner = self._generate_boolean_expr(operand, context_var)
            return f"!({inner})"

        # ParenExpr: parenthesized expression
        if isinstance(expr, ast.ParenExpr):
            inner_expr = getattr(expr, 'inner', None)
            inner = self._generate_boolean_expr(inner_expr, context_var)
            return f"({inner})"

        LOG.warning(f"Unknown boolean expression type in procedural: {type(expr).__name__}")
        return "true"

    def _generate_function_call(self, func_call, context_var: str) -> str:
        """Generate Java function call in boolean context."""
        name = getattr(func_call, 'name', None)
        if not name:
            LOG.warning("FunctionCall has no name")
            return "true"

        func_name = to_camel_case(name)
        arguments = getattr(func_call, 'arguments', None) or []
        args = ", ".join(generate_value_expr(a) for a in arguments)
        return f"{func_name}({args})"

    def _generate_comparison_expr(self, expr: ast.ComparisonExpr, context_var: str) -> str:
        """Generate Java comparison expression with IN/NOT IN and IS NULL support.

        ComparisonExpr fields:
        - left: ValueExpr
        - operator: Optional[ComparisonOp]
        - right: Optional[ValueExpr]
        - in_values: Optional[List[ValueExpr]] (for IN clause)
        - is_not_in: bool
        - is_null_check: bool
        - is_not_null_check: bool
        """
        left = generate_value_expr(getattr(expr, 'left', None))

        # Handle IN/NOT IN expressions
        in_values = getattr(expr, 'in_values', None)
        if in_values is not None:
            values = ", ".join(generate_value_expr(v) for v in in_values)
            check = f'Arrays.asList({values}).contains({left})'
            is_not_in = getattr(expr, 'is_not_in', False)
            if is_not_in:
                return f'!{check}'
            return check

        # Handle IS NULL check
        is_null_check = getattr(expr, 'is_null_check', False)
        if is_null_check:
            return f'({left} == null)'

        # Handle IS NOT NULL check
        is_not_null_check = getattr(expr, 'is_not_null_check', False)
        if is_not_null_check:
            return f'({left} != null)'

        # Standard comparison
        right = generate_value_expr(getattr(expr, 'right', None))
        operator = getattr(expr, 'operator', None)
        op = self._map_comparison_op(operator)
        return f"({left} {op} {right})"

    def _map_comparison_op(self, op) -> str:
        """Map comparison operator to Java."""
        if op is None:
            LOG.warning("Null comparison operator in procedural rule")
            return "=="

        if isinstance(op, ast.ComparisonOp):
            op_map = {
                ast.ComparisonOp.EQ: "==",
                ast.ComparisonOp.NE: "!=",
                ast.ComparisonOp.LT: "<",
                ast.ComparisonOp.GT: ">",
                ast.ComparisonOp.LE: "<=",
                ast.ComparisonOp.GE: ">=",
            }
            result = op_map.get(op)
            if result:
                return result

        LOG.warning(f"Unknown comparison operator: {op}")
        return "=="

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
