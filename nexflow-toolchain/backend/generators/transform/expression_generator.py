"""
Expression Generator Mixin

Generates Java code from L3 Transform expression AST nodes.
"""

from typing import Set, List, Optional

from backend.ast import transform_ast as ast


class ExpressionGeneratorMixin:
    """
    Mixin for generating Java expressions from Transform AST.

    Generates:
    - Arithmetic and logical expressions
    - Conditional when/otherwise expressions
    - Function calls
    - Field access and null-safe navigation
    """

    # =========================================================================
    # Operator Mapping Constants
    # =========================================================================

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

    # Maps DSL function names to Java method equivalents
    DSL_TO_JAVA_FUNCTIONS = {
        # Math functions
        "min": "Math.min",
        "max": "Math.max",
        "abs": "Math.abs",
        "round": "Math.round",
        "floor": "Math.floor",
        "ceil": "Math.ceil",
        "sqrt": "Math.sqrt",
        "pow": "Math.pow",
        # Date/time functions
        "now": "Instant.now",
        "today": "LocalDate.now",
        # String functions
        "len": "String::length",
        "upper": "String::toUpperCase",
        "lower": "String::toLowerCase",
        "trim": "String::trim",
        "concat": "String::concat",
        "substring": "String::substring",
        "contains": "String::contains",
        "starts_with": "String::startsWith",
        "ends_with": "String::endsWith",
        # Utility functions
        "coalesce": "Objects::requireNonNullElse",
    }

    # =========================================================================
    # Expression Generation Methods
    # =========================================================================

    def generate_expression(
        self,
        expr: ast.Expression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None,
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java code for an expression.

        Args:
            expr: The expression AST node
            use_map: If True, generate Map.get() access instead of getter methods
            local_vars: List of local variable names to reference directly
            assigned_output_fields: List of output fields already assigned to result map
        """
        if local_vars is None:
            local_vars = []
        if assigned_output_fields is None:
            assigned_output_fields = []

        if isinstance(expr, ast.StringLiteral):
            return f'"{expr.value}"'

        if isinstance(expr, ast.IntegerLiteral):
            # Use double suffix when likely used in arithmetic with doubles
            # Long suffix for standalone integer values
            return f"{expr.value}L"

        if isinstance(expr, ast.DecimalLiteral):
            return f'new BigDecimal("{expr.value}")'

        if isinstance(expr, ast.BooleanLiteral):
            return "true" if expr.value else "false"

        if isinstance(expr, ast.NullLiteral):
            return "null"

        if isinstance(expr, ast.ListLiteral):
            elements = ", ".join(self.generate_expression(e, use_map, local_vars, assigned_output_fields) for e in expr.values)
            return f"Arrays.asList({elements})"

        if isinstance(expr, ast.FieldPath):
            return self._generate_field_path(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.FunctionCall):
            return self._generate_function_call(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.WhenExpression):
            return self._generate_when_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.BinaryExpression):
            return self._generate_binary_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.UnaryExpression):
            return self._generate_unary_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.BetweenExpression):
            return self._generate_between_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.InExpression):
            return self._generate_in_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.IsNullExpression):
            return self._generate_is_null_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.ParenExpression):
            inner = self.generate_expression(expr.inner, use_map, local_vars, assigned_output_fields)
            return f"({inner})"

        if isinstance(expr, ast.OptionalChainExpression):
            return self._generate_optional_chain(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.IndexExpression):
            return self._generate_index_expression(expr, use_map, local_vars, assigned_output_fields)

        return "/* UNSUPPORTED EXPRESSION */"

    def _generate_field_path(
        self,
        fp: ast.FieldPath,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: List[str] = None
    ) -> str:
        """Generate Java getter chain for field path.

        Args:
            fp: The field path AST node
            use_map: If True, generate Map.get() access instead of getter methods
            local_vars: List of local variable names to reference directly (normalized by caller)
            assigned_output_fields: List of output fields already assigned to result map
        """
        if assigned_output_fields is None:
            assigned_output_fields = []

        parts = fp.parts
        first_part = parts[0]

        # Check if first part is a local variable
        first_part_camel = self.to_camel_case(first_part)
        if first_part_camel in local_vars:
            # Local variable reference - use directly
            if len(parts) == 1:
                return first_part_camel
            # For nested access on local var, use getter chain
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f"{first_part_camel}.{rest}"

        # Check if this is an already-assigned output field (reference to result map)
        if use_map and first_part in assigned_output_fields:
            # Access from result map, not input
            if len(parts) == 1:
                return f'result.get("{first_part}")'
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f'((Object)result.get("{first_part}")).{rest}'

        # Input field access
        if use_map:
            # Use Map.get() for dynamic field access
            # Return raw Object - let usage context determine casting
            if len(parts) == 1:
                return f'input.get("{first_part}")'
            # For nested paths: input.get("a") then chain getters
            # This assumes first level is Map, nested levels are POJOs
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f'((Object)input.get("{first_part}")).{rest}'

        # Standard getter chain: a.b.c -> input.getA().getB().getC()
        # Always prefix with 'input.' to access the transform input object
        if len(parts) == 1:
            return f"input.{self.to_getter(parts[0])}"
        getters = [self.to_getter(p) for p in parts]
        return f"input.{'.'.join(getters)}"

    def _generate_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: List[str] = None
    ) -> str:
        """Generate Java function call."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        java_name = self._map_function_name(func.name)

        # For numeric functions like min/max, ensure arguments are numeric (double)
        if func.name in ('min', 'max') and use_map:
            args = ", ".join(
                self._wrap_numeric_if_field(a, use_map, local_vars, assigned_output_fields, force_double=True)
                for a in func.arguments
            )
        else:
            args = ", ".join(
                self.generate_expression(a, use_map, local_vars, assigned_output_fields)
                for a in func.arguments
            )
        return f"{java_name}({args})"

    def _generate_when_expression(
        self,
        when: ast.WhenExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: List[str] = None
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

    def _generate_binary_expression(
        self,
        binary: ast.BinaryExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: List[str] = None
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
        # and convert numeric literals to double for type consistency
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
        assigned_output_fields: List[str] = None,
        force_double: bool = False
    ) -> str:
        """Wrap expression to produce numeric (double) value if needed.

        Args:
            expr: The expression to process
            use_map: Whether Map-based access is used
            local_vars: Local variable names
            assigned_output_fields: Output fields already assigned
            force_double: If True, convert numeric literals to double
        """
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
        # For integer literals in arithmetic with doubles, use double suffix for type consistency
        if isinstance(expr, ast.IntegerLiteral):
            return f"{expr.value}d"  # Use double suffix instead of Long
        # For decimal literals, convert to double to ensure type consistency
        if force_double and isinstance(expr, ast.DecimalLiteral):
            return f"{expr.value}d"  # Append 'd' suffix for double literal
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
        # Check if either operand is a string literal
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
        """Generate null-safe equality comparison (=? operator).

        Returns true if both are null OR both are non-null and equal.
        This differs from Objects.equals() in explicitly handling the
        "both null is equal" case as a feature, not an edge case.
        """
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
        assigned_output_fields: List[str] = None
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

    def _generate_between_expression(
        self,
        between: ast.BetweenExpression,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: List[str] = None
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
        assigned_output_fields: List[str] = None
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
        assigned_output_fields: List[str] = None
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
        assigned_output_fields: List[str] = None
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
        assigned_output_fields: List[str] = None
    ) -> str:
        """Generate array/list index access."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        base = self._generate_field_path(index.base, use_map, local_vars, assigned_output_fields)
        idx = self.generate_expression(index.index, use_map, local_vars, assigned_output_fields)
        return f"{base}.get((int)({idx}))"

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

    def _map_function_name(self, name: str) -> str:
        """Map DSL function name to Java method."""
        return self.DSL_TO_JAVA_FUNCTIONS.get(name, self.to_camel_case(name))

    def get_expression_imports(self) -> Set[str]:
        """Get required imports for expression generation."""
        return {
            'java.util.Arrays',
            'java.util.Optional',
            'java.util.Objects',
            'java.math.BigDecimal',
            'java.time.Instant',
            'java.time.LocalDate',
        }
