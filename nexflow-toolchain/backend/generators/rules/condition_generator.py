"""
Condition Generator Mixin

Generates Java condition evaluation code from L4 Rules condition AST nodes.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Condition generates: Complete condition evaluations, all comparison types
L4 Condition NEVER generates: Placeholder stubs, incomplete conditions
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    to_getter,
    generate_literal,
    generate_value_expr,
    generate_field_path,
    generate_unsupported_comment,
    get_common_imports,
)

LOG = logging.getLogger(__name__)


class ConditionGeneratorMixin:
    """
    Mixin for generating Java condition evaluation code.

    Generates:
    - Wildcard matching
    - Exact value comparisons
    - Range checks
    - Set membership tests
    - Pattern matching
    - Null checks
    """

    def generate_condition(
        self,
        condition: ast.Condition,
        input_var: str,
        field_name: str
    ) -> str:
        """Generate Java code for a condition."""
        if condition is None:
            LOG.warning("Null condition provided")
            return "true"

        field_access = f"{input_var}.get{to_pascal_case(field_name)}()"

        if isinstance(condition, ast.WildcardCondition):
            return "true"  # Wildcard always matches

        if isinstance(condition, ast.ExactMatchCondition):
            return self._generate_exact_match(condition, field_access)

        if isinstance(condition, ast.RangeCondition):
            return self._generate_range_check(condition, field_access)

        if isinstance(condition, ast.SetCondition):
            return self._generate_set_membership(condition, field_access)

        if isinstance(condition, ast.PatternCondition):
            return self._generate_pattern_match(condition, field_access)

        if isinstance(condition, ast.NullCondition):
            return self._generate_null_check(condition, field_access)

        if isinstance(condition, ast.ComparisonCondition):
            return self._generate_comparison(condition, field_access)

        if isinstance(condition, ast.ExpressionCondition):
            return self._generate_expression_condition(condition, input_var)

        return generate_unsupported_comment(f"condition type {type(condition).__name__}", "condition_generator")

    def _generate_exact_match(
        self,
        condition: ast.ExactMatchCondition,
        field_access: str
    ) -> str:
        """Generate exact match comparison."""
        value = getattr(condition, 'value', None)
        literal = generate_literal(value)

        if isinstance(value, ast.StringLiteral):
            return f'{literal}.equals({field_access})'
        if isinstance(value, ast.NullLiteral):
            return f'({field_access} == null)'

        return f'({field_access} == {literal})'

    def _generate_range_check(
        self,
        condition: ast.RangeCondition,
        field_access: str
    ) -> str:
        """Generate range (between) check with null safety."""
        min_val = generate_literal(getattr(condition, 'min_value', None))
        max_val = generate_literal(getattr(condition, 'max_value', None))

        # Add null guard for non-primitive comparisons
        return f'({field_access} != null && {field_access}.compareTo({min_val}) >= 0 && {field_access}.compareTo({max_val}) <= 0)'

    def _generate_set_membership(
        self,
        condition: ast.SetCondition,
        field_access: str
    ) -> str:
        """Generate set membership check."""
        values = getattr(condition, 'values', None) or []
        values_str = ", ".join(generate_literal(v) for v in values)
        check = f'Arrays.asList({values_str}).contains({field_access})'

        negated = getattr(condition, 'negated', False)
        if negated:
            return f'!{check}'
        return check

    def _generate_pattern_match(
        self,
        condition: ast.PatternCondition,
        field_access: str
    ) -> str:
        """Generate pattern matching code with null safety."""
        pattern = getattr(condition, 'pattern', '')
        pattern = pattern.replace('"', '\\"')
        match_type = getattr(condition, 'match_type', None)

        # All string methods need null guard
        if match_type == ast.PatternMatchType.MATCHES:
            return f'({field_access} != null && {field_access}.matches("{pattern}"))'
        if match_type == ast.PatternMatchType.STARTS_WITH:
            return f'({field_access} != null && {field_access}.startsWith("{pattern}"))'
        if match_type == ast.PatternMatchType.ENDS_WITH:
            return f'({field_access} != null && {field_access}.endsWith("{pattern}"))'
        if match_type == ast.PatternMatchType.CONTAINS:
            return f'({field_access} != null && {field_access}.contains("{pattern}"))'

        LOG.warning(f"Unknown PatternMatchType: {match_type}, defaulting to matches")
        return f'({field_access} != null && {field_access}.matches("{pattern}"))'

    def _generate_null_check(
        self,
        condition: ast.NullCondition,
        field_access: str
    ) -> str:
        """Generate null check."""
        is_null = getattr(condition, 'is_null', True)
        if is_null:
            return f'({field_access} == null)'
        return f'({field_access} != null)'

    def _generate_comparison(
        self,
        condition: ast.ComparisonCondition,
        field_access: str
    ) -> str:
        """Generate comparison expression."""
        operator = getattr(condition, 'operator', None)
        op = self._map_comparison_op(operator)
        value = generate_value_expr(getattr(condition, 'value', None))

        return f'({field_access} {op} {value})'

    def _generate_expression_condition(
        self,
        condition: ast.ExpressionCondition,
        input_var: str
    ) -> str:
        """Generate complex boolean expression."""
        expression = getattr(condition, 'expression', None)
        return self._generate_boolean_expr(expression, input_var)

    def _generate_boolean_expr(self, expr, input_var: str) -> str:
        """Generate Java boolean expression.

        AST Structure:
        - BooleanExpr: terms: List[BooleanTerm], operators: List[LogicalOp]
        - BooleanTerm: factor: BooleanFactor, negated: bool
        - BooleanFactor: comparison, nested_expr, or function_call
        """
        if expr is None:
            LOG.warning("Null boolean expression provided")
            return "true"

        # BooleanExpr: combines terms with AND/OR operators
        if isinstance(expr, ast.BooleanExpr):
            terms = getattr(expr, 'terms', None) or []
            operators = getattr(expr, 'operators', None) or []

            if not terms:
                LOG.warning("BooleanExpr has no terms")
                return "true"

            # Generate first term
            result_parts = [self._generate_boolean_expr(terms[0], input_var)]

            # Combine remaining terms with operators
            for i, term in enumerate(terms[1:]):
                op = operators[i] if i < len(operators) else ast.LogicalOp.AND
                java_op = "&&" if op == ast.LogicalOp.AND else "||"
                term_str = self._generate_boolean_expr(term, input_var)
                result_parts.append(f" {java_op} ({term_str})")

            return "(" + result_parts[0] + "".join(result_parts[1:]) + ")"

        # BooleanTerm: single factor with optional NOT
        if isinstance(expr, ast.BooleanTerm):
            negated = getattr(expr, 'negated', False)
            factor = getattr(expr, 'factor', None)

            if factor is None:
                LOG.warning("BooleanTerm has no factor")
                return "true"

            inner = self._generate_boolean_expr(factor, input_var)
            if negated:
                return f"!({inner})"
            return inner

        # BooleanFactor: contains comparison, nested expr, or function call
        if isinstance(expr, ast.BooleanFactor):
            comparison = getattr(expr, 'comparison', None)
            nested_expr = getattr(expr, 'nested_expr', None)
            function_call = getattr(expr, 'function_call', None)

            if comparison is not None:
                return self._generate_comparison_expr(comparison, input_var)
            if nested_expr is not None:
                return self._generate_boolean_expr(nested_expr, input_var)
            if function_call is not None:
                return self._generate_function_call(function_call, input_var)

            LOG.warning("BooleanFactor has no comparison, nested_expr, or function_call")
            return "true"

        # UnaryExpr: negation
        if isinstance(expr, ast.UnaryExpr):
            operand = getattr(expr, 'operand', None)
            inner = self._generate_boolean_expr(operand, input_var)
            return f'!({inner})'

        # ParenExpr: parenthesized expression
        if isinstance(expr, ast.ParenExpr):
            inner_expr = getattr(expr, 'inner', None)
            inner = self._generate_boolean_expr(inner_expr, input_var)
            return f'({inner})'

        # ComparisonExpr: direct comparison
        if isinstance(expr, ast.ComparisonExpr):
            return self._generate_comparison_expr(expr, input_var)

        LOG.warning(f"Unknown boolean expression type: {type(expr).__name__}")
        return "true"

    def _generate_function_call(self, func_call, input_var: str) -> str:
        """Generate Java function call in boolean context."""
        name = getattr(func_call, 'name', None)
        if not name:
            LOG.warning("FunctionCall has no name")
            return "true"

        func_name = to_camel_case(name)
        arguments = getattr(func_call, 'arguments', None) or []
        args = ", ".join(generate_value_expr(a) for a in arguments)
        return f"{func_name}({args})"

    def _generate_comparison_expr(
        self,
        expr: ast.ComparisonExpr,
        input_var: str
    ) -> str:
        """Generate Java comparison expression with IN/NOT IN support.

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
        return f'({left} {op} {right})'

    def _map_comparison_op(self, op) -> str:
        """Map comparison operator to Java."""
        if op is None:
            LOG.warning("Null comparison operator, defaulting to ==")
            return "=="

        op_map = {
            ast.ComparisonOp.EQ: "==",
            ast.ComparisonOp.NE: "!=",
            ast.ComparisonOp.LT: "<",
            ast.ComparisonOp.GT: ">",
            ast.ComparisonOp.LE: "<=",
            ast.ComparisonOp.GE: ">=",
        }
        result = op_map.get(op)
        if result is None:
            LOG.warning(f"Unknown comparison operator: {op}, defaulting to ==")
            return "=="
        return result

    def get_condition_imports(self) -> Set[str]:
        """Get required imports for condition generation."""
        return get_common_imports()
