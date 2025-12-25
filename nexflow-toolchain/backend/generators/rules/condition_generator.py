# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
    to_record_accessor,
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
        field_name: str,
        field_type=None
    ) -> str:
        """Generate Java code for a condition.

        Args:
            condition: Condition AST node
            input_var: Variable name for input object (e.g., "input")
            field_name: Name of the field being compared
            field_type: Optional AST type node for the field (for type-aware comparisons)

        Returns:
            Java boolean expression string
        """
        if condition is None:
            LOG.warning("Null condition provided")
            return "true"

        # Use Record accessor pattern: fieldName() instead of getFieldName()
        field_access = f"{input_var}.{to_record_accessor(field_name)}"

        if isinstance(condition, ast.WildcardCondition):
            return "true"  # Wildcard always matches

        if isinstance(condition, ast.ExactMatchCondition):
            return self._generate_exact_match(condition, field_access)

        if isinstance(condition, ast.RangeCondition):
            return self._generate_range_check(condition, field_access, field_type)

        if isinstance(condition, ast.SetCondition):
            return self._generate_set_membership(condition, field_access)

        if isinstance(condition, ast.PatternCondition):
            return self._generate_pattern_match(condition, field_access)

        if isinstance(condition, ast.NullCondition):
            return self._generate_null_check(condition, field_access)

        if isinstance(condition, ast.ComparisonCondition):
            return self._generate_comparison(condition, field_access, field_type)

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
        field_access: str,
        field_type=None
    ) -> str:
        """Generate range (between) check with null safety.

        For BigDecimal fields (money type), uses compareTo().
        For primitive types (number), uses direct comparison.
        """
        min_val = generate_literal(getattr(condition, 'min_value', None))
        max_val = generate_literal(getattr(condition, 'max_value', None))

        # Check if field is BigDecimal (money type)
        if self._is_money_type(field_type):
            # Convert integer literals to BigDecimal for comparison
            min_val = self._ensure_bigdecimal(min_val)
            max_val = self._ensure_bigdecimal(max_val)
            return f'({field_access} != null && {field_access}.compareTo({min_val}) >= 0 && {field_access}.compareTo({max_val}) <= 0)'

        # For Long/number types, use direct comparison
        return f'({field_access} != null && {field_access} >= {min_val} && {field_access} <= {max_val})'

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
        field_access: str,
        field_type=None
    ) -> str:
        """Generate comparison expression.

        Handles different types appropriately:
        - Primitives (Long, int): use direct comparison operators
        - BigDecimal: use compareTo() method
        - Objects: use Objects.equals() for equality

        Args:
            condition: ComparisonCondition AST node
            field_access: Java field accessor expression
            field_type: Optional AST type node for type-aware comparison
        """
        operator = getattr(condition, 'operator', None)
        value_node = getattr(condition, 'value', None)
        value = generate_value_expr(value_node)

        # Determine if we need BigDecimal-style comparison
        # Either because the value is decimal OR the field type is money/decimal
        is_decimal_comparison = self._is_decimal_value(value_node) or self._is_money_type(field_type)

        if is_decimal_comparison:
            # Ensure the comparison value is BigDecimal
            value = self._ensure_bigdecimal(value)
            return self._generate_decimal_comparison(field_access, operator, value)

        op = self._map_comparison_op(operator)
        return f'({field_access} {op} {value})'

    def _is_decimal_value(self, value_node) -> bool:
        """Check if value requires BigDecimal comparison."""
        if isinstance(value_node, (ast.DecimalLiteral, ast.MoneyLiteral, ast.PercentageLiteral)):
            return True
        return False

    def _is_money_type(self, field_type) -> bool:
        """Check if field type is money/decimal (requires BigDecimal comparison).

        Args:
            field_type: AST type node or None

        Returns:
            True if field should use BigDecimal comparison
        """
        if field_type is None:
            return False

        # Handle BaseType enum
        if isinstance(field_type, ast.BaseType):
            return field_type in (ast.BaseType.MONEY, ast.BaseType.PERCENTAGE)

        # Handle string type names
        if isinstance(field_type, str):
            return field_type.lower() in ('money', 'decimal', 'percentage')

        return False

    def _ensure_bigdecimal(self, value: str) -> str:
        """Ensure value is a BigDecimal expression.

        Converts integer literals like '50000L' to 'new BigDecimal("50000")'.
        Leaves existing BigDecimal expressions unchanged.

        Args:
            value: Java literal or expression string

        Returns:
            BigDecimal-compatible expression
        """
        if value is None:
            return 'null'

        # Already a BigDecimal constructor
        if 'new BigDecimal' in value:
            return value

        # Integer literal with L suffix
        if value.endswith('L'):
            number = value[:-1]
            return f'new BigDecimal("{number}")'

        # Plain integer
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return f'new BigDecimal("{value}")'

        # Already an expression or reference - wrap it
        # This handles cases like input.getSomeValue()
        return value

    def _generate_decimal_comparison(
        self,
        field_access: str,
        operator,
        value: str
    ) -> str:
        """Generate BigDecimal-safe comparison.

        BigDecimal requires compareTo() for ordering comparisons.
        """
        if operator == ast.ComparisonOp.EQ:
            return f'({field_access} != null && {field_access}.compareTo({value}) == 0)'
        if operator == ast.ComparisonOp.NE:
            return f'({field_access} == null || {field_access}.compareTo({value}) != 0)'
        if operator == ast.ComparisonOp.LT:
            return f'({field_access} != null && {field_access}.compareTo({value}) < 0)'
        if operator == ast.ComparisonOp.GT:
            return f'({field_access} != null && {field_access}.compareTo({value}) > 0)'
        if operator == ast.ComparisonOp.LE:
            return f'({field_access} != null && {field_access}.compareTo({value}) <= 0)'
        if operator == ast.ComparisonOp.GE:
            return f'({field_access} != null && {field_access}.compareTo({value}) >= 0)'

        # Default to equality
        LOG.warning(f"Unknown operator {operator} for decimal comparison, using equals")
        return f'({field_access} != null && {field_access}.compareTo({value}) == 0)'

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
