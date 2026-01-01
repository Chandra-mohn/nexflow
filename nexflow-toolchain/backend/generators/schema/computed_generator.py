# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Computed Field Generator Module

Generates Java computed property methods from Schema AST computed blocks.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
"""

from typing import TYPE_CHECKING

from backend.ast import schema_ast as ast

if TYPE_CHECKING:
    from backend.generators.schema_generator import SchemaGenerator


class ComputedGeneratorMixin:
    """Mixin providing computed field generation capabilities.

    Generates Java methods for computed/derived fields that:
    - Support arithmetic expressions (+, -, *, /)
    - Support comparison expressions (==, !=, <, >, <=, >=)
    - Support logical expressions (and, or, not)
    - Support when/then/else conditionals
    - Support function calls (runtime library functions)
    - Support field references
    """

    def _generate_computed_methods(
        self: 'SchemaGenerator',
        schema: ast.SchemaDefinition,
        class_name: str
    ) -> str:
        """Generate all computed property methods for the schema."""
        if not schema.computed or not schema.computed.fields:
            return ""

        methods = []
        for computed_field in schema.computed.fields:
            method = self._generate_computed_method(computed_field, class_name)
            methods.append(method)

        if not methods:
            return ""

        return f'''    // =========================================================================
    // Computed Properties (auto-generated from DSL)
    // =========================================================================

{chr(10).join(methods)}'''

    def _generate_computed_method(
        self: 'SchemaGenerator',
        field: ast.ComputedFieldDecl,
        class_name: str
    ) -> str:
        """Generate a single computed property method."""
        method_name = self.to_java_field_name(field.name)
        java_type = self._infer_computed_type(field.expression)
        expr_code = self._generate_computed_expression(field.expression)

        # Generate javadoc with the original DSL expression
        dsl_expr = self._computed_expr_to_string(field.expression)

        return f'''    /**
     * Computed: {dsl_expr}
     */
    public {java_type} {method_name}() {{
        return {expr_code};
    }}
'''

    def _infer_computed_type(
        self: 'SchemaGenerator',
        expr: ast.ComputedExpression
    ) -> str:
        """Infer the Java return type from a computed expression."""
        if isinstance(expr, ast.BinaryExpression):
            # Arithmetic operators return BigDecimal for numeric operations
            if expr.operator in ('+', '-', '*', '/'):
                return 'BigDecimal'
            # Comparison operators return boolean
            if expr.operator in ('==', '!=', '<', '>', '<=', '>=', '='):
                return 'boolean'
            # Logical operators return boolean
            if expr.operator in ('and', 'or'):
                return 'boolean'
            return 'Object'

        if isinstance(expr, ast.UnaryExpression):
            if expr.operator == 'not':
                return 'boolean'
            return 'Object'

        if isinstance(expr, ast.LiteralExpression):
            return self._literal_to_java_type(expr.value)

        if isinstance(expr, ast.WhenExpression):
            # Infer from the first branch result type
            if expr.branches:
                return self._infer_computed_type(expr.branches[0].result)
            return self._infer_computed_type(expr.else_result)

        if isinstance(expr, ast.FunctionCallExpression):
            # Runtime function return types
            return self._function_return_type(expr.function_name)

        if isinstance(expr, ast.FieldRefExpression):
            # Field references - assume BigDecimal for now, could enhance with schema lookup
            return 'BigDecimal'

        return 'Object'

    def _literal_to_java_type(self: 'SchemaGenerator', literal) -> str:
        """Get Java type from a literal."""
        if isinstance(literal, ast.DecimalLiteral):
            return 'BigDecimal'
        if isinstance(literal, ast.IntegerLiteral):
            return 'Long'
        if isinstance(literal, ast.StringLiteral):
            return 'String'
        if isinstance(literal, ast.BooleanLiteral):
            return 'boolean'
        return 'Object'

    def _function_return_type(self: 'SchemaGenerator', function_name: str) -> str:
        """Get return type for a runtime function."""
        # Map runtime function names to return types
        return_types = {
            # Math functions
            'abs': 'BigDecimal',
            'min': 'BigDecimal',
            'max': 'BigDecimal',
            'round': 'BigDecimal',
            'ceil': 'BigDecimal',
            'floor': 'BigDecimal',
            'pow': 'BigDecimal',
            'percentOf': 'BigDecimal',
            # String functions
            'upper': 'String',
            'lower': 'String',
            'trim': 'String',
            'concat': 'String',
            'substring': 'String',
            'replace': 'String',
            # Time functions
            'hour': 'int',
            'dayOfWeek': 'int',
            'dayOfMonth': 'int',
            'month': 'int',
            'year': 'int',
            'now': 'Instant',
            'today': 'LocalDate',
            'daysBetween': 'long',
            'addDays': 'LocalDate',
            # Collection functions
            'length': 'int',
            'first': 'Object',
            'last': 'Object',
            # Boolean functions
            'isNull': 'boolean',
            'isNotNull': 'boolean',
            'isEmpty': 'boolean',
            'isBlank': 'boolean',
            'startsWith': 'boolean',
            'endsWith': 'boolean',
            'contains': 'boolean',
            'between': 'boolean',
            'equals': 'boolean',
            # Conversion functions
            'toLong': 'Long',
            'toDecimal': 'BigDecimal',
            'toString': 'String',
            'toBoolean': 'Boolean',
            # Comparison functions
            'coalesce': 'Object',
            'nvl': 'Object',
            'compare': 'int',
        }
        return return_types.get(function_name, 'Object')

    def _generate_computed_expression(
        self: 'SchemaGenerator',
        expr: ast.ComputedExpression
    ) -> str:
        """Generate Java code for a computed expression."""
        if isinstance(expr, ast.BinaryExpression):
            return self._generate_binary_expression(expr)

        if isinstance(expr, ast.UnaryExpression):
            return self._generate_unary_expression(expr)

        if isinstance(expr, ast.LiteralExpression):
            return self._generate_literal_expression(expr)

        if isinstance(expr, ast.FieldRefExpression):
            return self._generate_field_ref_expression(expr)

        if isinstance(expr, ast.FunctionCallExpression):
            return self._generate_function_call_expression(expr)

        if isinstance(expr, ast.WhenExpression):
            return self._generate_when_expression(expr)

        return "null /* unsupported expression */"

    def _generate_binary_expression(
        self: 'SchemaGenerator',
        expr: ast.BinaryExpression
    ) -> str:
        """Generate Java code for binary expression."""
        left = self._generate_computed_expression(expr.left)
        right = self._generate_computed_expression(expr.right)

        # Arithmetic operators need BigDecimal methods
        if expr.operator == '+':
            return f'({left}).add({right})'
        if expr.operator == '-':
            return f'({left}).subtract({right})'
        if expr.operator == '*':
            return f'({left}).multiply({right})'
        if expr.operator == '/':
            return f'({left}).divide({right}, java.math.RoundingMode.HALF_UP)'

        # Comparison operators
        if expr.operator in ('==', '='):
            return f'java.util.Objects.equals({left}, {right})'
        if expr.operator == '!=':
            return f'!java.util.Objects.equals({left}, {right})'
        if expr.operator == '<':
            return f'({left}).compareTo({right}) < 0'
        if expr.operator == '>':
            return f'({left}).compareTo({right}) > 0'
        if expr.operator == '<=':
            return f'({left}).compareTo({right}) <= 0'
        if expr.operator == '>=':
            return f'({left}).compareTo({right}) >= 0'

        # Logical operators
        if expr.operator == 'and':
            return f'({left}) && ({right})'
        if expr.operator == 'or':
            return f'({left}) || ({right})'

        return f'({left} {expr.operator} {right})'

    def _generate_unary_expression(
        self: 'SchemaGenerator',
        expr: ast.UnaryExpression
    ) -> str:
        """Generate Java code for unary expression."""
        operand = self._generate_computed_expression(expr.operand)
        if expr.operator == 'not':
            return f'!({operand})'
        return f'{expr.operator}({operand})'

    def _generate_literal_expression(
        self: 'SchemaGenerator',
        expr: ast.LiteralExpression
    ) -> str:
        """Generate Java code for literal expression."""
        literal = expr.value
        if isinstance(literal, ast.DecimalLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.IntegerLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.StringLiteral):
            escaped = literal.value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(literal, ast.BooleanLiteral):
            return 'true' if literal.value else 'false'
        if isinstance(literal, ast.NullLiteral):
            return 'null'
        return str(literal)

    def _generate_field_ref_expression(
        self: 'SchemaGenerator',
        expr: ast.FieldRefExpression
    ) -> str:
        """Generate Java code for field reference expression."""
        # Use record accessor pattern: fieldName()
        parts = expr.field_path.parts
        if len(parts) == 1:
            field_name = self.to_java_field_name(parts[0])
            return f'{field_name}()'
        else:
            # For nested paths: obj().nested()
            accessors = [f'{self.to_java_field_name(p)}()' for p in parts]
            return '.'.join(accessors)

    def _generate_function_call_expression(
        self: 'SchemaGenerator',
        expr: ast.FunctionCallExpression
    ) -> str:
        """Generate Java code for function call expression."""
        args = [self._generate_computed_expression(arg) for arg in expr.arguments]
        args_str = ', '.join(args)
        return f'{expr.function_name}({args_str})'

    def _generate_when_expression(
        self: 'SchemaGenerator',
        expr: ast.WhenExpression
    ) -> str:
        """Generate Java code for when/then/else expression."""
        # Generate nested ternary operators
        result = self._generate_computed_expression(expr.else_result)

        # Build from innermost to outermost
        for branch in reversed(expr.branches):
            condition = self._generate_computed_expression(branch.condition)
            then_result = self._generate_computed_expression(branch.result)
            result = f'({condition}) ? {then_result} : {result}'

        return result

    def _computed_expr_to_string(
        self: 'SchemaGenerator',
        expr: ast.ComputedExpression
    ) -> str:
        """Convert computed expression back to DSL string for documentation."""
        if isinstance(expr, ast.BinaryExpression):
            left = self._computed_expr_to_string(expr.left)
            right = self._computed_expr_to_string(expr.right)
            return f'({left} {expr.operator} {right})'

        if isinstance(expr, ast.UnaryExpression):
            operand = self._computed_expr_to_string(expr.operand)
            return f'{expr.operator} {operand}'

        if isinstance(expr, ast.LiteralExpression):
            literal = expr.value
            if isinstance(literal, ast.StringLiteral):
                return f'"{literal.value}"'
            if isinstance(literal, ast.BooleanLiteral):
                return 'true' if literal.value else 'false'
            if isinstance(literal, ast.NullLiteral):
                return 'null'
            return str(literal.value) if hasattr(literal, 'value') else str(literal)

        if isinstance(expr, ast.FieldRefExpression):
            return '.'.join(expr.field_path.parts)

        if isinstance(expr, ast.FunctionCallExpression):
            args = [self._computed_expr_to_string(arg) for arg in expr.arguments]
            return f'{expr.function_name}({", ".join(args)})'

        if isinstance(expr, ast.WhenExpression):
            parts = []
            for branch in expr.branches:
                cond = self._computed_expr_to_string(branch.condition)
                result = self._computed_expr_to_string(branch.result)
                parts.append(f'when {cond} then {result}')
            else_result = self._computed_expr_to_string(expr.else_result)
            parts.append(f'else {else_result}')
            return ' '.join(parts)

        return str(expr)
