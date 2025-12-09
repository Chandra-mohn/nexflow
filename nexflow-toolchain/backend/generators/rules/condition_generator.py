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
    to_pascal_case,
    generate_literal,
    generate_value_expr,
    generate_unsupported_comment,
    get_common_imports,
)
from backend.generators.rules.condition_boolean import BooleanExpressionMixin

LOG = logging.getLogger(__name__)


class ConditionGeneratorMixin(BooleanExpressionMixin):
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
