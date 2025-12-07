"""
Decision Table Generator Mixin

Generates Java decision table evaluators from L4 Rules decision tables.
"""

from typing import Set, List

from backend.ast import rules_ast as ast


class DecisionTableGeneratorMixin:
    """
    Mixin for generating Java decision table evaluator classes.

    Generates:
    - Rule evaluation methods with hit policies
    - Row matching logic
    - Result collection based on hit policy
    """

    def generate_decision_table_class(
        self,
        table: ast.DecisionTableDef,
        package: str
    ) -> str:
        """Generate complete decision table evaluator class."""
        class_name = self._to_pascal_case(table.name) + "Table"
        input_type = class_name + "Input"
        output_type = self._get_output_type(table)

        imports = self._collect_decision_table_imports(table)

        lines = [
            self.generate_java_header(
                class_name, f"Decision Table: {table.name}"
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

        # Generate evaluate method based on hit policy
        lines.append(self._generate_evaluate_method(table, input_type, output_type))
        lines.append("")

        # Generate row evaluation methods
        lines.append(self._generate_row_methods(table, input_type))
        lines.append("")

        # Generate input POJO
        lines.append(self._generate_input_class(table, input_type))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_evaluate_method(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate main evaluate method based on hit policy."""
        hit_policy = table.hit_policy or ast.HitPolicyType.FIRST_MATCH

        if hit_policy == ast.HitPolicyType.FIRST_MATCH:
            return self._generate_first_match_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.MULTI_HIT:
            return self._generate_multi_hit_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.SINGLE_HIT:
            return self._generate_single_hit_evaluate(table, input_type, output_type)

        return self._generate_first_match_evaluate(table, input_type, output_type)

    def _generate_first_match_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate first-match hit policy evaluate method."""
        rows = table.decide.matrix.rows if table.decide else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table.name}",
            "     * Hit Policy: FIRST_MATCH - returns first matching row's result",
            "     */",
            f"    public Optional<{output_type}> evaluate({input_type} input) {{",
        ]

        for i, row in enumerate(rows):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            return Optional.of(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "        // No matching rule",
            "        return Optional.empty();",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_multi_hit_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate multi-hit hit policy evaluate method."""
        rows = table.decide.matrix.rows if table.decide else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table.name}",
            "     * Hit Policy: MULTI_HIT - returns all matching rows' results",
            "     */",
            f"    public List<{output_type}> evaluate({input_type} input) {{",
            f"        List<{output_type}> results = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            results.add(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "",
            "        return results;",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_single_hit_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate single-hit hit policy evaluate method."""
        rows = table.decide.matrix.rows if table.decide else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table.name}",
            "     * Hit Policy: SINGLE_HIT - validates exactly one row matches",
            "     */",
            f"    public {output_type} evaluate({input_type} input) {{",
            f"        List<{output_type}> matches = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            matches.add(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "",
            "        if (matches.isEmpty()) {",
            '            throw new IllegalStateException("No rule matched");',
            "        }",
            "        if (matches.size() > 1) {",
            '            throw new IllegalStateException("Multiple rules matched: " + matches.size());',
            "        }",
            "",
            "        return matches.get(0);",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_row_methods(
        self,
        table: ast.DecisionTableDef,
        input_type: str
    ) -> str:
        """Generate row matching and result methods."""
        if not table.decide or not table.decide.matrix:
            return "    // No rows defined"

        matrix = table.decide.matrix
        headers = matrix.headers
        rows = matrix.rows

        # Determine which headers are conditions vs actions
        given_fields = []
        if table.given:
            given_fields = [p.name for p in table.given.params]

        return_fields = []
        if table.return_spec:
            return_fields = [p.name for p in table.return_spec.params]

        lines = []
        for i, row in enumerate(rows):
            row_num = i + 1

            # Generate match method
            lines.append(self._generate_row_match_method(
                row_num, row, headers, given_fields, input_type
            ))
            lines.append("")

            # Generate result method
            lines.append(self._generate_row_result_method(
                row_num, row, headers, return_fields, input_type
            ))
            lines.append("")

        return '\n'.join(lines)

    def _generate_row_match_method(
        self,
        row_num: int,
        row: ast.TableRow,
        headers: List[ast.ColumnHeader],
        given_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to check if row matches input."""
        lines = [
            f"    private boolean matchRow{row_num}({input_type} input) {{",
        ]

        conditions = []
        for j, cell in enumerate(row.cells):
            if j < len(headers):
                header_name = headers[j].name
                if header_name in given_fields:
                    cond = self.generate_condition(
                        cell.content, "input", header_name
                    )
                    conditions.append(cond)

        if conditions:
            condition_str = " && ".join(f"({c})" for c in conditions)
            lines.append(f"        return {condition_str};")
        else:
            lines.append("        return true;")

        lines.append("    }")
        return '\n'.join(lines)

    def _generate_row_result_method(
        self,
        row_num: int,
        row: ast.TableRow,
        headers: List[ast.ColumnHeader],
        return_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to get row's result value."""
        output_type = "String"  # Default, should be derived from return_spec

        lines = [
            f"    private {output_type} getRow{row_num}Result({input_type} input) {{",
        ]

        # Find the action cell (last column typically, or matching return field)
        for j, cell in enumerate(row.cells):
            if j < len(headers):
                header_name = headers[j].name
                if header_name in return_fields or j == len(row.cells) - 1:
                    result = self.generate_action(
                        cell.content, "result", header_name
                    )
                    if isinstance(cell.content, (ast.StringLiteral,
                                                 ast.IntegerLiteral,
                                                 ast.DecimalLiteral)):
                        value = self._generate_literal(cell.content)
                        lines.append(f"        return {value};")
                        break
        else:
            lines.append('        return null;')

        lines.append("    }")
        return '\n'.join(lines)

    def _generate_input_class(
        self,
        table: ast.DecisionTableDef,
        class_name: str
    ) -> str:
        """Generate input POJO class."""
        lines = [
            f"    /**",
            f"     * Input data class for {table.name}",
            f"     */",
            f"    public static class {class_name} {{",
        ]

        if table.given:
            for param in table.given.params:
                java_type = self._get_java_type(param.param_type)
                field_name = self._to_camel_case(param.name)
                lines.append(f"        private {java_type} {field_name};")

            lines.append("")

            # Generate getters/setters
            for param in table.given.params:
                java_type = self._get_java_type(param.param_type)
                field_name = self._to_camel_case(param.name)
                getter_name = f"get{field_name[0].upper()}{field_name[1:]}"
                setter_name = f"set{field_name[0].upper()}{field_name[1:]}"

                lines.append(
                    f"        public {java_type} {getter_name}() {{ "
                    f"return {field_name}; }}"
                )
                lines.append(
                    f"        public void {setter_name}({java_type} {field_name}) {{ "
                    f"this.{field_name} = {field_name}; }}"
                )

        lines.append("    }")
        return '\n'.join(lines)

    def _get_output_type(self, table: ast.DecisionTableDef) -> str:
        """Get Java type for decision table output."""
        if table.return_spec and table.return_spec.params:
            param = table.return_spec.params[0]
            return self._get_java_type(param.param_type)
        return "String"

    def _get_java_type(self, param_type) -> str:
        """Convert rule type to Java type."""
        if isinstance(param_type, ast.BaseType):
            type_map = {
                ast.BaseType.TEXT: "String",
                ast.BaseType.NUMBER: "Long",
                ast.BaseType.BOOLEAN: "Boolean",
                ast.BaseType.DATE: "LocalDate",
                ast.BaseType.TIMESTAMP: "Instant",
                ast.BaseType.MONEY: "BigDecimal",
                ast.BaseType.PERCENTAGE: "BigDecimal",
            }
            return type_map.get(param_type, "Object")
        if isinstance(param_type, str):
            return self._to_pascal_case(param_type)
        return "Object"

    def _generate_literal(self, literal) -> str:
        """Generate Java literal."""
        if isinstance(literal, ast.StringLiteral):
            return f'"{literal.value}"'
        if isinstance(literal, ast.IntegerLiteral):
            return f'{literal.value}L'
        if isinstance(literal, ast.DecimalLiteral):
            return f'new BigDecimal("{literal.value}")'
        return 'null'

    def _collect_decision_table_imports(
        self,
        table: ast.DecisionTableDef
    ) -> Set[str]:
        """Collect imports for decision table class."""
        imports = {
            'java.util.Optional',
            'java.util.List',
            'java.util.ArrayList',
            'java.util.Arrays',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }

        imports.update(self.get_condition_imports())
        imports.update(self.get_action_imports())

        return imports

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
