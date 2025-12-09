"""
Procedural Expressions Mixin

Generates Java boolean and comparison expressions for procedural rules.
"""

import logging

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    generate_value_expr,
)

LOG = logging.getLogger(__name__)


class ProceduralExpressionsMixin:
    """Mixin for generating boolean expressions in procedural rules."""

    def _generate_boolean_expr(self, expr, context_var: str) -> str:
        """Generate Java boolean expression with full NOT, IN/NOT IN support."""
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

            result_parts = [self._generate_boolean_expr(terms[0], context_var)]

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
        """Generate Java comparison expression with IN/NOT IN and IS NULL support."""
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
