"""
Expression Generator Mixin

Generates Java code from L3 Transform expression AST nodes.
"""

from typing import Set, List, Optional

from backend.ast import transform_ast as ast
from backend.generators.transform.expression_operators import ExpressionOperatorsMixin
from backend.generators.transform.expression_special import ExpressionSpecialMixin


class ExpressionGeneratorMixin(ExpressionOperatorsMixin, ExpressionSpecialMixin):
    """
    Mixin for generating Java expressions from Transform AST.

    Generates:
    - Arithmetic and logical expressions
    - Conditional when/otherwise expressions
    - Function calls
    - Field access and null-safe navigation
    """

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
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java getter chain for field path."""
        if assigned_output_fields is None:
            assigned_output_fields = []

        parts = fp.parts
        first_part = parts[0]

        # Check if first part is a local variable
        first_part_camel = self.to_camel_case(first_part)
        if first_part_camel in local_vars:
            if len(parts) == 1:
                return first_part_camel
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f"{first_part_camel}.{rest}"

        # Check if this is an already-assigned output field (reference to result map)
        if use_map and first_part in assigned_output_fields:
            if len(parts) == 1:
                return f'result.get("{first_part}")'
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f'((Object)result.get("{first_part}")).{rest}'

        # Input field access
        if use_map:
            if len(parts) == 1:
                return f'input.get("{first_part}")'
            rest = ".".join(self.to_getter(p) for p in parts[1:])
            return f'((Object)input.get("{first_part}")).{rest}'

        # Standard getter chain
        if len(parts) == 1:
            return f"input.{self.to_getter(parts[0])}"
        getters = [self.to_getter(p) for p in parts]
        return f"input.{'.'.join(getters)}"

    def _generate_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java function call."""
        if assigned_output_fields is None:
            assigned_output_fields = []
        java_name = self._map_function_name(func.name)

        # For numeric functions like min/max, ensure arguments are numeric
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
