"""
Boolean Expression Generator Mixin

Generates Java boolean expressions from L4 Rules boolean AST nodes.
"""

import logging
from typing import TYPE_CHECKING

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    generate_value_expr,
    generate_unsupported_comment,
)

LOG = logging.getLogger(__name__)


class BooleanExpressionMixin:
    """
    Mixin for generating Java boolean expressions.

    Generates:
    - Boolean expression trees (AND/OR)
    - Boolean terms with negation
    - Comparison expressions
    - Function calls in boolean context
    """

    def _generate_boolean_expr(self, expr, input_var: str) -> str:
        """Generate Java boolean expression.

        AST Structure:
        - BooleanExpr: terms: List[BooleanTerm], operators: List[LogicalOp]
        - BooleanTerm: factor: BooleanFactor, negated: bool
        - BooleanFactor: comparison, nested_expr, or function_call
        """
        from backend.ast import rules_ast as ast

        if expr is None:
            LOG.warning("Null boolean expression provided")
            return "true"

        # BooleanExpr: combines terms with AND/OR operators
        if isinstance(expr, ast.BooleanExpr):
            return self._generate_boolean_expr_node(expr, input_var)

        # BooleanTerm: single factor with optional NOT
        if isinstance(expr, ast.BooleanTerm):
            return self._generate_boolean_term(expr, input_var)

        # BooleanFactor: contains comparison, nested expr, or function call
        if isinstance(expr, ast.BooleanFactor):
            return self._generate_boolean_factor(expr, input_var)

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

    def _generate_boolean_expr_node(self, expr, input_var: str) -> str:
        """Generate BooleanExpr node (combines terms with AND/OR)."""
        from backend.ast import rules_ast as ast

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

    def _generate_boolean_term(self, expr, input_var: str) -> str:
        """Generate BooleanTerm (single factor with optional NOT)."""
        negated = getattr(expr, 'negated', False)
        factor = getattr(expr, 'factor', None)

        if factor is None:
            LOG.warning("BooleanTerm has no factor")
            return "true"

        inner = self._generate_boolean_expr(factor, input_var)
        if negated:
            return f"!({inner})"
        return inner

    def _generate_boolean_factor(self, expr, input_var: str) -> str:
        """Generate BooleanFactor (comparison, nested expr, or function call)."""
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
        expr,
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
        right_expr = getattr(expr, 'right', None)
        right = generate_value_expr(right_expr)
        operator = getattr(expr, 'operator', None)

        # Use .equals() for String comparisons (EQ/NE with string literals)
        if self._is_string_comparison(right_expr, operator):
            if operator == ast.ComparisonOp.EQ:
                return f'{right}.equals({left})'
            elif operator == ast.ComparisonOp.NE:
                return f'!{right}.equals({left})'

        op = self._map_comparison_op(operator)
        return f'({left} {op} {right})'

    def _is_string_comparison(self, right_expr, operator) -> bool:
        """Check if this is a string equality/inequality comparison."""
        if operator not in (ast.ComparisonOp.EQ, ast.ComparisonOp.NE):
            return False
        # Check if right side is a string literal
        return isinstance(right_expr, ast.StringLiteral)
