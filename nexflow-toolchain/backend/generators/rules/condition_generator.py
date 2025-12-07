"""
Condition Generator Mixin

Generates Java condition evaluation code from L4 Rules condition AST nodes.
"""

from typing import Set

from backend.ast import rules_ast as ast


class ConditionGeneratorMixin:
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
        field_access = f"{input_var}.get{self._to_pascal_case(field_name)}()"

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

        return "/* UNSUPPORTED CONDITION */"

    def _generate_exact_match(
        self,
        condition: ast.ExactMatchCondition,
        field_access: str
    ) -> str:
        """Generate exact match comparison."""
        value = self._generate_literal(condition.value)

        if isinstance(condition.value, ast.StringLiteral):
            return f'{value}.equals({field_access})'
        if isinstance(condition.value, ast.NullLiteral):
            return f'({field_access} == null)'

        return f'({field_access} == {value})'

    def _generate_range_check(
        self,
        condition: ast.RangeCondition,
        field_access: str
    ) -> str:
        """Generate range (between) check."""
        min_val = self._generate_literal(condition.min_value)
        max_val = self._generate_literal(condition.max_value)

        return f'({field_access} >= {min_val} && {field_access} <= {max_val})'

    def _generate_set_membership(
        self,
        condition: ast.SetCondition,
        field_access: str
    ) -> str:
        """Generate set membership check."""
        values = ", ".join(self._generate_literal(v) for v in condition.values)
        check = f'Arrays.asList({values}).contains({field_access})'

        if condition.negated:
            return f'!{check}'
        return check

    def _generate_pattern_match(
        self,
        condition: ast.PatternCondition,
        field_access: str
    ) -> str:
        """Generate pattern matching code."""
        pattern = condition.pattern.replace('"', '\\"')
        match_type = condition.match_type

        if match_type == ast.PatternMatchType.MATCHES:
            return f'{field_access}.matches("{pattern}")'
        if match_type == ast.PatternMatchType.STARTS_WITH:
            return f'{field_access}.startsWith("{pattern}")'
        if match_type == ast.PatternMatchType.ENDS_WITH:
            return f'{field_access}.endsWith("{pattern}")'
        if match_type == ast.PatternMatchType.CONTAINS:
            return f'{field_access}.contains("{pattern}")'

        return f'{field_access}.matches("{pattern}")'

    def _generate_null_check(
        self,
        condition: ast.NullCondition,
        field_access: str
    ) -> str:
        """Generate null check."""
        if condition.is_null:
            return f'({field_access} == null)'
        return f'({field_access} != null)'

    def _generate_comparison(
        self,
        condition: ast.ComparisonCondition,
        field_access: str
    ) -> str:
        """Generate comparison expression."""
        op = self._map_comparison_op(condition.operator)
        value = self._generate_value_expr(condition.value)

        return f'({field_access} {op} {value})'

    def _generate_expression_condition(
        self,
        condition: ast.ExpressionCondition,
        input_var: str
    ) -> str:
        """Generate complex boolean expression."""
        return self._generate_boolean_expr(condition.expression, input_var)

    def _generate_literal(self, literal: ast.Literal) -> str:
        """Generate Java literal from AST literal."""
        if isinstance(literal, ast.StringLiteral):
            return f'"{literal.value}"'
        if isinstance(literal, ast.IntegerLiteral):
            return f'{literal.value}L'
        if isinstance(literal, ast.DecimalLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.MoneyLiteral):
            return f'new BigDecimal("{literal.value}")'
        if isinstance(literal, ast.PercentageLiteral):
            return f'new BigDecimal("{literal.value / 100.0}")'
        if isinstance(literal, ast.BooleanLiteral):
            return 'true' if literal.value else 'false'
        if isinstance(literal, ast.NullLiteral):
            return 'null'
        if isinstance(literal, ast.ListLiteral):
            elements = ", ".join(self._generate_literal(e) for e in literal.values)
            return f'Arrays.asList({elements})'
        return 'null'

    def _generate_value_expr(self, expr: ast.ValueExpr) -> str:
        """Generate Java code for a value expression."""
        if isinstance(expr, ast.FieldPath):
            return self._generate_field_path(expr)
        if isinstance(expr, ast.FunctionCall):
            return self._generate_function_call(expr)
        if isinstance(expr, (ast.StringLiteral, ast.IntegerLiteral,
                            ast.DecimalLiteral, ast.BooleanLiteral,
                            ast.NullLiteral, ast.MoneyLiteral)):
            return self._generate_literal(expr)
        return "/* UNSUPPORTED VALUE EXPR */"

    def _generate_boolean_expr(self, expr: ast.BooleanExpr, input_var: str) -> str:
        """Generate Java boolean expression."""
        if isinstance(expr, ast.BooleanTerm):
            terms = [self._generate_boolean_expr(t, input_var) for t in expr.terms]
            return " || ".join(terms) if len(terms) > 1 else terms[0]
        if isinstance(expr, ast.BooleanFactor):
            factors = [self._generate_boolean_expr(f, input_var) for f in expr.factors]
            return " && ".join(factors) if len(factors) > 1 else factors[0]
        if isinstance(expr, ast.ComparisonExpr):
            left = self._generate_value_expr(expr.left)
            right = self._generate_value_expr(expr.right)
            op = self._map_comparison_op(expr.operator)
            return f'({left} {op} {right})'
        return "true"

    def _generate_field_path(self, fp: ast.FieldPath) -> str:
        """Generate Java getter chain for field path."""
        parts = fp.parts
        if len(parts) == 1:
            return self._to_getter(parts[0])
        getters = [self._to_getter(p) for p in parts]
        return ".".join(getters)

    def _generate_function_call(self, func: ast.FunctionCall) -> str:
        """Generate Java function call."""
        args = ", ".join(self._generate_value_expr(a) for a in func.arguments)
        java_name = self._to_camel_case(func.name)
        return f"{java_name}({args})"

    def _map_comparison_op(self, op: ast.ComparisonOp) -> str:
        """Map comparison operator to Java."""
        op_map = {
            ast.ComparisonOp.EQ: "==",
            ast.ComparisonOp.NE: "!=",
            ast.ComparisonOp.LT: "<",
            ast.ComparisonOp.GT: ">",
            ast.ComparisonOp.LE: "<=",
            ast.ComparisonOp.GE: ">=",
        }
        return op_map.get(op, "==")

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_condition_imports(self) -> Set[str]:
        """Get required imports for condition generation."""
        return {
            'java.util.Arrays',
            'java.math.BigDecimal',
        }
