"""
Expression Special Forms Mixin

Handles when/otherwise, between, in, is_null, optional chain, and index expressions.
"""

from typing import List, Optional

from backend.ast import transform_ast as ast


class ExpressionSpecialMixin:
    """Mixin for generating special expression forms."""

    def _generate_when_expression(
        self,
        when: ast.WhenExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate nested ternary for when/otherwise."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        result = self.generate_expression(when.otherwise, use_map, local_vars, assigned_output_fields)

        # Build from inside out
        for branch in reversed(when.branches):
            condition = self.generate_expression(branch.condition, use_map, local_vars, assigned_output_fields)
            branch_result = self.generate_expression(branch.result, use_map, local_vars, assigned_output_fields)
            result = f"({condition}) ? {branch_result} : {result}"

        return result

    def _generate_between_expression(
        self,
        between: ast.BetweenExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate between check."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        value = self.generate_expression(between.value, use_map, local_vars, assigned_output_fields)
        lower = self.generate_expression(between.lower, use_map, local_vars, assigned_output_fields)
        upper = self.generate_expression(between.upper, use_map, local_vars, assigned_output_fields)

        expr = f"({value} >= {lower} && {value} <= {upper})"
        if between.negated:
            expr = f"!{expr}"
        return expr

    def _generate_in_expression(
        self,
        in_expr: ast.InExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate set membership check."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        value = self.generate_expression(in_expr.value, use_map, local_vars, assigned_output_fields)
        elements = ", ".join(
            self.generate_expression(e, use_map, local_vars, assigned_output_fields) for e in in_expr.values.values
        )
        expr = f"Arrays.asList({elements}).contains({value})"
        if in_expr.negated:
            expr = f"!{expr}"
        return expr

    def _generate_is_null_expression(
        self,
        is_null: ast.IsNullExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate null check."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        value = self.generate_expression(is_null.value, use_map, local_vars, assigned_output_fields)
        if is_null.negated:
            return f"({value} != null)"
        return f"({value} == null)"

    def _generate_optional_chain(
        self,
        chain: ast.OptionalChainExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate null-safe navigation."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        base = self._generate_field_path(chain.base, use_map, local_vars, assigned_output_fields)
        for field_name in chain.chain:
            getter = self.to_getter(field_name)
            base = f"Optional.ofNullable({base}).map(v -> v.{getter}).orElse(null)"
        return base

    def _generate_index_expression(
        self,
        index: ast.IndexExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate array/list index access."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        base = self._generate_field_path(index.base, use_map, local_vars, assigned_output_fields)
        idx = self.generate_expression(index.index, use_map, local_vars, assigned_output_fields)
        return f"{base}.get((int)({idx}))"
