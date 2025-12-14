# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Expression Operators Mixin

Handles binary and unary expression generation with operator mapping.
"""

from typing import List, Optional

from backend.ast import transform_ast as ast


class ExpressionOperatorsMixin:
    """Mixin for generating binary and unary expressions."""

    # Maps DSL string operators to Java operators
    DSL_TO_JAVA_OPERATORS = {
        # Logical operators
        'and': '&&',
        'or': '||',
        '&&': '&&',
        '||': '||',
        # Comparison operators
        '=': '==',  # DSL equality uses single =
        '==': '==',
        '!=': '!=',
        '<>': '!=',
        '<': '<',
        '>': '>',
        '<=': '<=',
        '>=': '>=',
        # Arithmetic operators
        '+': '+',
        '-': '-',
        '*': '*',
        '/': '/',
        '%': '%',
    }

    def _generate_binary_expression(
        self,
        binary: ast.BinaryExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate binary operation."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        op = binary.operator

        # Handle null coalesce operator ?? first (before generating operands)
        if op == "??":
            left = self.generate_expression(binary.left, use_map, local_vars, assigned_output_fields)
            right = self.generate_expression(binary.right, use_map, local_vars, assigned_output_fields)
            return f"({left} != null ? {left} : {right})"

        # Determine if this is a numeric operation requiring casting
        is_arithmetic = (
            isinstance(op, ast.ArithmeticOp) or
            (isinstance(op, str) and op in ('+', '-', '*', '/', '%'))
        )
        is_numeric_comparison = (
            isinstance(op, ast.ComparisonOp) and
            op in (ast.ComparisonOp.LT, ast.ComparisonOp.GT,
                   ast.ComparisonOp.LE, ast.ComparisonOp.GE) or
            (isinstance(op, str) and op in ('<', '>', '<=', '>='))
        )

        # For numeric operations with Map access, wrap field paths in numeric cast
        if use_map and (is_arithmetic or is_numeric_comparison):
            left = self._wrap_numeric_if_field(binary.left, use_map, local_vars, assigned_output_fields, force_double=True)
            right = self._wrap_numeric_if_field(binary.right, use_map, local_vars, assigned_output_fields, force_double=True)
        else:
            left = self.generate_expression(binary.left, use_map, local_vars, assigned_output_fields)
            right = self.generate_expression(binary.right, use_map, local_vars, assigned_output_fields)

        # Map operators to Java - handle both enum and string types
        if isinstance(op, ast.ArithmeticOp):
            java_op = op.value
        elif isinstance(op, ast.ComparisonOp):
            java_op = self._map_comparison_op(op)
            # Handle null-safe equality operator (=?)
            if op == ast.ComparisonOp.NULLSAFE_EQ:
                return self._generate_nullsafe_equality(left, right)
            # Use .equals() for string equality comparisons
            if self._is_string_comparison(binary, op):
                return self._generate_string_comparison(left, right, op)
        elif isinstance(op, ast.LogicalOp):
            java_op = "&&" if op == ast.LogicalOp.AND else "||"
        elif isinstance(op, str):
            # Handle string operators from parser
            java_op = self._map_string_operator(op)
            # Check for string equality with string operators
            if op in ('=', '==', '!=', '<>'):
                if self._is_string_comparison_raw(binary):
                    return self._generate_string_comparison_raw(left, right, op)
        else:
            java_op = str(op)

        return f"({left} {java_op} {right})"

    def _wrap_numeric_if_field(
        self,
        expr: ast.Expression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None,
        force_double: bool = False
    ) -> str:
        """Wrap expression to produce numeric (double) value if needed."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        if isinstance(expr, ast.FieldPath) and use_map:
            # Check if it's a local variable (don't wrap those)
            first_part_camel = self.to_camel_case(expr.parts[0])
            if first_part_camel in local_vars:
                return self.generate_expression(expr, use_map, local_vars, assigned_output_fields)
            # Wrap Map.get() in Number cast for arithmetic
            raw = self.generate_expression(expr, use_map, local_vars, assigned_output_fields)
            return f"((Number){raw}).doubleValue()"
        # For integer literals in arithmetic with doubles, use double suffix
        if isinstance(expr, ast.IntegerLiteral):
            return f"{expr.value}d"
        # For decimal literals, convert to double to ensure type consistency
        if force_double and isinstance(expr, ast.DecimalLiteral):
            return f"{expr.value}d"
        # For literals and other expressions, generate normally
        return self.generate_expression(expr, use_map, local_vars, assigned_output_fields)

    def _is_string_comparison(
        self,
        binary: ast.BinaryExpression,
        op: ast.ComparisonOp
    ) -> bool:
        """Check if this is a string equality comparison."""
        if op not in (ast.ComparisonOp.EQ, ast.ComparisonOp.NE):
            return False
        return (isinstance(binary.left, ast.StringLiteral) or
                isinstance(binary.right, ast.StringLiteral))

    def _is_string_comparison_raw(self, binary: ast.BinaryExpression) -> bool:
        """Check if this is a string comparison (raw string operator version)."""
        return (isinstance(binary.left, ast.StringLiteral) or
                isinstance(binary.right, ast.StringLiteral))

    def _generate_string_comparison(
        self,
        left: str,
        right: str,
        op: ast.ComparisonOp
    ) -> str:
        """Generate null-safe string comparison using .equals()."""
        if op == ast.ComparisonOp.EQ:
            return f"Objects.equals({left}, {right})"
        elif op == ast.ComparisonOp.NE:
            return f"!Objects.equals({left}, {right})"
        return f"({left} == {right})"

    def _generate_nullsafe_equality(self, left: str, right: str) -> str:
        """Generate null-safe equality comparison (=? operator)."""
        return f"Objects.equals({left}, {right})"

    def _generate_string_comparison_raw(
        self,
        left: str,
        right: str,
        op: str
    ) -> str:
        """Generate null-safe string comparison for raw string operators."""
        if op in ('=', '=='):
            return f"Objects.equals({left}, {right})"
        elif op in ('!=', '<>'):
            return f"!Objects.equals({left}, {right})"
        return f"({left} == {right})"

    def _map_string_operator(self, op: str) -> str:
        """Map string operator from parser to Java operator."""
        op_lower = op.lower().strip()
        return self.DSL_TO_JAVA_OPERATORS.get(op_lower, op)

    def _generate_unary_expression(
        self,
        unary: ast.UnaryExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate unary operation."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        operand = self.generate_expression(unary.operand, use_map, local_vars, assigned_output_fields)
        if unary.operator == ast.UnaryOp.NOT:
            return f"!({operand})"
        if unary.operator == ast.UnaryOp.MINUS:
            return f"-({operand})"
        return operand

    def _map_comparison_op(self, op: ast.ComparisonOp) -> str:
        """Map comparison operator to Java."""
        op_map = {
            ast.ComparisonOp.EQ: "==",
            ast.ComparisonOp.NE: "!=",
            ast.ComparisonOp.LT: "<",
            ast.ComparisonOp.GT: ">",
            ast.ComparisonOp.LE: "<=",
            ast.ComparisonOp.GE: ">=",
            ast.ComparisonOp.NULLSAFE_EQ: "NULLSAFE",  # Handled specially
        }
        return op_map.get(op, "==")
