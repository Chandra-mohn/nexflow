"""
Expression Generator Mixin

Generates Java code from L3 Transform expression AST nodes.
"""

from typing import Set, Union, List, Optional

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

    def generate_expression(
        self,
        expr: ast.Expression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate Java code for an expression.

        Args:
            expr: The expression AST node
            use_map: If True, generate Map.get() access instead of getter methods
            local_vars: List of local variable names to reference directly
        """
        if local_vars is None:
            local_vars = []

        if isinstance(expr, ast.StringLiteral):
            return f'"{expr.value}"'

        if isinstance(expr, ast.IntegerLiteral):
            return f"{expr.value}L"

        if isinstance(expr, ast.DecimalLiteral):
            return f'new BigDecimal("{expr.value}")'

        if isinstance(expr, ast.BooleanLiteral):
            return "true" if expr.value else "false"

        if isinstance(expr, ast.NullLiteral):
            return "null"

        if isinstance(expr, ast.ListLiteral):
            elements = ", ".join(self.generate_expression(e, use_map, local_vars) for e in expr.values)
            return f"Arrays.asList({elements})"

        if isinstance(expr, ast.FieldPath):
            return self._generate_field_path(expr, use_map, local_vars)

        if isinstance(expr, ast.FunctionCall):
            return self._generate_function_call(expr, use_map, local_vars)

        if isinstance(expr, ast.WhenExpression):
            return self._generate_when_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.BinaryExpression):
            return self._generate_binary_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.UnaryExpression):
            return self._generate_unary_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.BetweenExpression):
            return self._generate_between_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.InExpression):
            return self._generate_in_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.IsNullExpression):
            return self._generate_is_null_expression(expr, use_map, local_vars)

        if isinstance(expr, ast.ParenExpression):
            inner = self.generate_expression(expr.inner, use_map, local_vars)
            return f"({inner})"

        if isinstance(expr, ast.OptionalChainExpression):
            return self._generate_optional_chain(expr, use_map, local_vars)

        if isinstance(expr, ast.IndexExpression):
            return self._generate_index_expression(expr, use_map, local_vars)

        return "/* UNSUPPORTED EXPRESSION */"

    def _generate_field_path(
        self,
        fp: ast.FieldPath,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate Java getter chain for field path.

        Args:
            fp: The field path AST node
            use_map: If True, generate Map.get() access instead of getter methods
            local_vars: List of local variable names to reference directly
        """
        if local_vars is None:
            local_vars = []

        parts = fp.parts
        first_part = parts[0]

        # Check if first part is a local variable
        first_part_camel = self._to_camel_case(first_part)
        if first_part_camel in local_vars:
            # Local variable reference - use directly
            if len(parts) == 1:
                return first_part_camel
            # For nested access on local var, use getter chain
            rest = ".".join(self._to_getter(p) for p in parts[1:])
            return f"{first_part_camel}.{rest}"

        # Input field access
        if use_map:
            # Use Map.get() for dynamic field access
            # Cast to Number for arithmetic operations (will need explicit cast at usage site)
            if len(parts) == 1:
                return f'((Number)input.get("{first_part}")).doubleValue()'
            # For nested paths: input.get("a") then chain getters
            # This assumes first level is Map, nested levels are POJOs
            rest = ".".join(self._to_getter(p) for p in parts[1:])
            return f'((Object)input.get("{first_part}")).{rest}'

        # Standard getter chain: a.b.c -> getA().getB().getC()
        if len(parts) == 1:
            return self._to_getter(parts[0])
        getters = [self._to_getter(p) for p in parts]
        return ".".join(getters)

    def _generate_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate Java function call."""
        if local_vars is None:
            local_vars = []
        args = ", ".join(self.generate_expression(a, use_map, local_vars) for a in func.arguments)
        java_name = self._map_function_name(func.name)
        return f"{java_name}({args})"

    def _generate_when_expression(
        self,
        when: ast.WhenExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate nested ternary for when/otherwise."""
        if local_vars is None:
            local_vars = []
        result = self.generate_expression(when.otherwise, use_map, local_vars)

        # Build from inside out
        for branch in reversed(when.branches):
            condition = self.generate_expression(branch.condition, use_map, local_vars)
            branch_result = self.generate_expression(branch.result, use_map, local_vars)
            result = f"({condition}) ? {branch_result} : {result}"

        return result

    def _generate_binary_expression(
        self,
        binary: ast.BinaryExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate binary operation."""
        if local_vars is None:
            local_vars = []
        left = self.generate_expression(binary.left, use_map, local_vars)
        right = self.generate_expression(binary.right, use_map, local_vars)
        op = binary.operator

        # Handle null coalesce operator ??
        if op == "??":
            return f"({left} != null ? {left} : {right})"

        # Map operators to Java - handle both enum and string types
        if isinstance(op, ast.ArithmeticOp):
            java_op = op.value
        elif isinstance(op, ast.ComparisonOp):
            java_op = self._map_comparison_op(op)
        elif isinstance(op, ast.LogicalOp):
            java_op = "&&" if op == ast.LogicalOp.AND else "||"
        elif isinstance(op, str):
            # Handle string operators from parser
            java_op = self._map_string_operator(op)
        else:
            java_op = str(op)

        return f"({left} {java_op} {right})"

    def _map_string_operator(self, op: str) -> str:
        """Map string operator from parser to Java operator."""
        op_lower = op.lower().strip()
        string_op_map = {
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
        return string_op_map.get(op_lower, op)

    def _generate_unary_expression(
        self,
        unary: ast.UnaryExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate unary operation."""
        if local_vars is None:
            local_vars = []
        operand = self.generate_expression(unary.operand, use_map, local_vars)
        if unary.operator == ast.UnaryOp.NOT:
            return f"!({operand})"
        if unary.operator == ast.UnaryOp.MINUS:
            return f"-({operand})"
        return operand

    def _generate_between_expression(
        self,
        between: ast.BetweenExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate between check."""
        if local_vars is None:
            local_vars = []
        value = self.generate_expression(between.value, use_map, local_vars)
        lower = self.generate_expression(between.lower, use_map, local_vars)
        upper = self.generate_expression(between.upper, use_map, local_vars)

        expr = f"({value} >= {lower} && {value} <= {upper})"
        if between.negated:
            expr = f"!{expr}"
        return expr

    def _generate_in_expression(
        self,
        in_expr: ast.InExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate set membership check."""
        if local_vars is None:
            local_vars = []
        value = self.generate_expression(in_expr.value, use_map, local_vars)
        elements = ", ".join(
            self.generate_expression(e, use_map, local_vars) for e in in_expr.values.values
        )
        expr = f"Arrays.asList({elements}).contains({value})"
        if in_expr.negated:
            expr = f"!{expr}"
        return expr

    def _generate_is_null_expression(
        self,
        is_null: ast.IsNullExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate null check."""
        if local_vars is None:
            local_vars = []
        value = self.generate_expression(is_null.value, use_map, local_vars)
        if is_null.negated:
            return f"({value} != null)"
        return f"({value} == null)"

    def _generate_optional_chain(
        self,
        chain: ast.OptionalChainExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate null-safe navigation."""
        if local_vars is None:
            local_vars = []
        base = self._generate_field_path(chain.base, use_map, local_vars)
        for field_name in chain.chain:
            getter = self._to_getter(field_name)
            base = f"Optional.ofNullable({base}).map(v -> v.{getter}).orElse(null)"
        return base

    def _generate_index_expression(
        self,
        index: ast.IndexExpression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None
    ) -> str:
        """Generate array/list index access."""
        if local_vars is None:
            local_vars = []
        base = self._generate_field_path(index.base, use_map, local_vars)
        idx = self.generate_expression(index.index, use_map, local_vars)
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
            ast.ComparisonOp.NULLSAFE_EQ: "==",  # Handle null check separately
        }
        return op_map.get(op, "==")

    def _map_function_name(self, name: str) -> str:
        """Map DSL function name to Java method."""
        function_map = {
            "min": "Math.min",
            "max": "Math.max",
            "abs": "Math.abs",
            "round": "Math.round",
            "floor": "Math.floor",
            "ceil": "Math.ceil",
            "sqrt": "Math.sqrt",
            "pow": "Math.pow",
            "now": "Instant.now",
            "today": "LocalDate.now",
            "len": "String::length",
            "upper": "String::toUpperCase",
            "lower": "String::toLowerCase",
            "trim": "String::trim",
            "concat": "String::concat",
            "substring": "String::substring",
            "contains": "String::contains",
            "starts_with": "String::startsWith",
            "ends_with": "String::endsWith",
            "coalesce": "Objects::requireNonNullElse",
        }
        return function_map.get(name, self._to_camel_case(name))

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

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
