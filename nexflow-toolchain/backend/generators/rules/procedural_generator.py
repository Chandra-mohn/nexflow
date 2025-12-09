"""
Procedural Generator Mixin

Generates Java code from L4 Rules procedural rule definitions.
"""

from typing import Set, List

from backend.ast import rules_ast as ast


class ProceduralGeneratorMixin:
    """
    Mixin for generating Java procedural rule classes.

    Generates:
    - Rule evaluation methods with conditionals
    - If-then-else chains
    - Action sequences
    """

    def generate_procedural_rule_class(
        self,
        rule: ast.ProceduralRuleDef,
        package: str
    ) -> str:
        """Generate complete procedural rule class."""
        class_name = self._to_pascal_case(rule.name) + "Rule"

        imports = self._collect_procedural_imports(rule)

        lines = [
            self.generate_java_header(
                class_name, f"Procedural Rule: {rule.name}"
            ),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name} {{",
            "",
            "    private static final Logger LOG = LoggerFactory.getLogger("
            f"{class_name}.class);",
            "",
        ]

        # Generate execute method
        lines.append(self._generate_execute_method(rule))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_execute_method(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate main execute method for procedural rule."""
        lines = [
            "    /**",
            f"     * Execute rule: {rule.name}",
            "     */",
            "    public void execute(Object context) {",
        ]

        for item in rule.items:
            lines.append(self._generate_block_item(item, 2))

        lines.append("    }")

        return '\n'.join(lines)

    def _generate_block_item(self, item: ast.BlockItem, indent: int) -> str:
        """Generate code for a block item."""
        prefix = "    " * indent

        if isinstance(item, ast.RuleStep):
            return self._generate_rule_step(item, indent)

        if isinstance(item, ast.ActionSequence):
            return self._generate_action_sequence(item, indent)

        if isinstance(item, ast.ReturnStatement):
            return f"{prefix}return;"

        return f"{prefix}// Unknown block item"

    def _generate_rule_step(self, step: ast.RuleStep, indent: int) -> str:
        """Generate if-then-elseif-else structure."""
        prefix = "    " * indent
        lines = []

        # Main if condition
        condition = self._generate_boolean_expr(step.condition, "context")
        lines.append(f"{prefix}if ({condition}) {{")

        # Then block
        for item in step.then_block.items:
            lines.append(self._generate_block_item(item, indent + 1))

        # Elseif branches
        for branch in step.elseif_branches:
            branch_cond = self._generate_boolean_expr(branch.condition, "context")
            lines.append(f"{prefix}}} else if ({branch_cond}) {{")
            for item in branch.block.items:
                lines.append(self._generate_block_item(item, indent + 1))

        # Else block
        if step.else_block:
            lines.append(f"{prefix}}} else {{")
            for item in step.else_block.items:
                lines.append(self._generate_block_item(item, indent + 1))

        lines.append(f"{prefix}}}")

        return '\n'.join(lines)

    def _generate_action_sequence(
        self,
        seq: ast.ActionSequence,
        indent: int
    ) -> str:
        """Generate action sequence."""
        prefix = "    " * indent
        lines = []

        for action in seq.actions:
            func_name = self._to_camel_case(action.name)
            args = ", ".join(
                self._generate_value_expr(a) for a in action.arguments
            )
            lines.append(f"{prefix}{func_name}({args});")

        return '\n'.join(lines)

    def _generate_boolean_expr(self, expr, context_var: str) -> str:
        """Generate Java boolean expression with full NOT, IN/NOT IN support."""
        if isinstance(expr, ast.BooleanExpr):
            if hasattr(expr, 'terms') and expr.terms:
                terms = [self._generate_boolean_expr(t, context_var)
                        for t in expr.terms]
                return " || ".join(f"({t})" for t in terms)
            if hasattr(expr, 'factors') and expr.factors:
                factors = [self._generate_boolean_expr(f, context_var)
                          for f in expr.factors]
                return " && ".join(f"({f})" for f in factors)

        if isinstance(expr, ast.BooleanTerm):
            # Handle NOT prefix on BooleanTerm
            if hasattr(expr, 'negated') and expr.negated:
                inner_terms = [self._generate_boolean_expr(t, context_var)
                              for t in expr.terms]
                if len(inner_terms) == 1:
                    return f"!({inner_terms[0]})"
                return f"!({' || '.join(f'({t})' for t in inner_terms)})"
            terms = [self._generate_boolean_expr(t, context_var)
                    for t in expr.terms]
            if len(terms) == 1:
                return terms[0]
            return " || ".join(f"({t})" for t in terms)

        if isinstance(expr, ast.BooleanFactor):
            factors = [self._generate_boolean_expr(f, context_var)
                      for f in expr.factors]
            if len(factors) == 1:
                return factors[0]
            return " && ".join(f"({f})" for f in factors)

        if isinstance(expr, ast.ComparisonExpr):
            return self._generate_comparison_expr(expr, context_var)

        if isinstance(expr, ast.UnaryExpr):
            inner = self._generate_boolean_expr(expr.operand, context_var)
            if expr.operator == "not":
                return f"!({inner})"
            return inner

        if isinstance(expr, ast.ParenExpr):
            inner = self._generate_boolean_expr(expr.expression, context_var)
            return f"({inner})"

        return "true"

    def _generate_comparison_expr(self, expr: ast.ComparisonExpr, context_var: str) -> str:
        """Generate Java comparison expression with IN/NOT IN and IS NULL support."""
        left = self._generate_value_expr(expr.left)

        # Handle IN/NOT IN expressions
        if hasattr(expr, 'in_list') and expr.in_list is not None:
            values = ", ".join(self._generate_value_expr(v) for v in expr.in_list)
            check = f'Arrays.asList({values}).contains({left})'
            if hasattr(expr, 'negated') and expr.negated:
                return f'!{check}'
            return check

        # Handle IS NULL / IS NOT NULL
        if hasattr(expr, 'is_null_check') and expr.is_null_check:
            if hasattr(expr, 'negated') and expr.negated:
                return f'({left} != null)'
            return f'({left} == null)'

        # Standard comparison
        right = self._generate_value_expr(expr.right)
        op = self._map_comparison_op(expr.operator)
        return f"({left} {op} {right})"

    def _generate_value_expr(self, expr) -> str:
        """Generate Java value expression."""
        if isinstance(expr, ast.FieldPath):
            parts = expr.parts
            if len(parts) == 1:
                return self._to_getter(parts[0])
            return ".".join(self._to_getter(p) for p in parts)

        if isinstance(expr, ast.FunctionCall):
            args = ", ".join(self._generate_value_expr(a) for a in expr.arguments)
            return f"{self._to_camel_case(expr.name)}({args})"

        if isinstance(expr, ast.StringLiteral):
            return f'"{expr.value}"'
        if isinstance(expr, ast.IntegerLiteral):
            return f'{expr.value}L'
        if isinstance(expr, ast.DecimalLiteral):
            return f'new BigDecimal("{expr.value}")'
        if isinstance(expr, ast.BooleanLiteral):
            return 'true' if expr.value else 'false'
        if isinstance(expr, ast.NullLiteral):
            return 'null'
        if isinstance(expr, ast.ListLiteral):
            elements = ", ".join(self._generate_value_expr(e) for e in expr.values)
            return f'Arrays.asList({elements})'

        return str(expr)

    def _map_comparison_op(self, op) -> str:
        """Map comparison operator to Java."""
        if isinstance(op, ast.ComparisonOp):
            op_map = {
                ast.ComparisonOp.EQ: "==",
                ast.ComparisonOp.NE: "!=",
                ast.ComparisonOp.LT: "<",
                ast.ComparisonOp.GT: ">",
                ast.ComparisonOp.LE: "<=",
                ast.ComparisonOp.GE: ">=",
            }
            return op_map.get(op, "==")
        return "=="

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _collect_procedural_imports(self, rule: ast.ProceduralRuleDef) -> Set[str]:
        """Collect imports for procedural rule class."""
        imports = {
            'java.util.Arrays',
            'java.math.BigDecimal',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }
        return imports

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
