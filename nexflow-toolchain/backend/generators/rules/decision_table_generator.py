"""
Decision Table Generator Mixin

Generates Java decision table evaluators from L4 Rules decision tables.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Decision Table generates: Complete evaluators with hit policies
L4 Decision Table NEVER generates: Placeholder stubs, incomplete evaluators
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    generate_literal,
    get_java_type,
    get_common_imports,
    get_logging_imports,
    get_collection_imports,
)

LOG = logging.getLogger(__name__)


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
        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Table"
        input_type = class_name + "Input"
        output_type = self._get_output_type(table)

        imports = self._collect_decision_table_imports(table)

        lines = [
            self.generate_java_header(
                class_name, f"Decision Table: {table_name}"
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
        hit_policy = getattr(table, 'hit_policy', None) or ast.HitPolicyType.FIRST_MATCH

        if hit_policy == ast.HitPolicyType.FIRST_MATCH:
            return self._generate_first_match_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.MULTI_HIT:
            return self._generate_multi_hit_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.SINGLE_HIT:
            return self._generate_single_hit_evaluate(table, input_type, output_type)

        LOG.warning(f"Unknown hit policy: {hit_policy}, defaulting to FIRST_MATCH")
        return self._generate_first_match_evaluate(table, input_type, output_type)

    def _generate_first_match_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate first-match hit policy evaluate method."""
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: FIRST_MATCH - returns first matching row's result",
            "     */",
            f"    public Optional<{output_type}> evaluate({input_type} input) {{",
        ]

        for i, row in enumerate(rows or []):
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
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: MULTI_HIT - returns all matching rows' results",
            "     */",
            f"    public List<{output_type}> evaluate({input_type} input) {{",
            f"        List<{output_type}> results = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows or []):
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
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: SINGLE_HIT - validates exactly one row matches",
            "     */",
            f"    public {output_type} evaluate({input_type} input) {{",
            f"        List<{output_type}> matches = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows or []):
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
        decide = getattr(table, 'decide', None)
        if not decide:
            return "    // No decide block defined"

        matrix = getattr(decide, 'matrix', None)
        if not matrix:
            return "    // No matrix defined"

        headers = getattr(matrix, 'headers', None) or []
        rows = getattr(matrix, 'rows', None) or []

        # Determine which headers are conditions vs actions
        given = getattr(table, 'given', None)
        given_params = getattr(given, 'params', None) if given else []
        given_fields = [getattr(p, 'name', '') for p in given_params]

        return_spec = getattr(table, 'return_spec', None)
        return_params = getattr(return_spec, 'params', None) if return_spec else []
        return_fields = [getattr(p, 'name', '') for p in return_params]

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
        row,
        headers: List,
        given_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to check if row matches input."""
        lines = [
            f"    private boolean matchRow{row_num}({input_type} input) {{",
        ]

        conditions = []
        cells = getattr(row, 'cells', None) or []
        for j, cell in enumerate(cells):
            if j < len(headers):
                header_name = getattr(headers[j], 'name', '')
                if header_name in given_fields:
                    content = getattr(cell, 'content', None)
                    cond = self.generate_condition(content, "input", header_name)
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
        row,
        headers: List,
        return_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to get row's result value.

        Extracts action values from cells that match return fields.
        Cell content can be:
        - AssignAction: contains value (Literal)
        - Literal directly (StringLiteral, IntegerLiteral, etc.)
        - CalculateAction: contains expression
        - NoAction: wildcard/skip
        """
        output_type = "String"  # Default, should be derived from return_spec

        lines = [
            f"    private {output_type} getRow{row_num}Result({input_type} input) {{",
        ]

        # Find the action cell (last column typically, or matching return field)
        cells = getattr(row, 'cells', None) or []
        result_generated = False

        for j, cell in enumerate(cells):
            if j < len(headers):
                header_name = getattr(headers[j], 'name', '')
                # Check if this is a return/action column
                if header_name in return_fields or j == len(cells) - 1:
                    content = getattr(cell, 'content', None)
                    value = self._extract_action_value(content)
                    if value is not None:
                        lines.append(f"        return {value};")
                        result_generated = True
                        break

        if not result_generated:
            LOG.warning(f"Row {row_num} has no result value, returning null")
            lines.append('        return null;')

        lines.append("    }")
        return '\n'.join(lines)

    def _extract_action_value(self, content) -> str:
        """Extract Java value expression from action cell content."""
        if content is None:
            return None

        # NoAction - skip
        if isinstance(content, ast.NoAction):
            return None

        # AssignAction - extract the value literal
        if isinstance(content, ast.AssignAction):
            value = getattr(content, 'value', None)
            if value is not None:
                return generate_literal(value)
            return None

        # CalculateAction - extract expression
        if isinstance(content, ast.CalculateAction):
            from backend.generators.rules.utils import generate_value_expr
            expression = getattr(content, 'expression', None)
            if expression is not None:
                return generate_value_expr(expression)
            return None

        # Direct literal values
        if isinstance(content, (ast.StringLiteral, ast.IntegerLiteral,
                               ast.DecimalLiteral, ast.BooleanLiteral)):
            return generate_literal(content)

        LOG.warning(f"Unknown action content type: {type(content).__name__}")
        return None

    def _generate_input_class(
        self,
        table: ast.DecisionTableDef,
        class_name: str
    ) -> str:
        """Generate input POJO class."""
        table_name = getattr(table, 'name', 'unknown')
        lines = [
            f"    /**",
            f"     * Input data class for {table_name}",
            f"     */",
            f"    public static class {class_name} {{",
        ]

        given = getattr(table, 'given', None)
        if given:
            params = getattr(given, 'params', None) or []
            for param in params:
                param_type = getattr(param, 'param_type', None)
                param_name = getattr(param, 'name', 'unknown')
                java_type = get_java_type(param_type)
                field_name = to_camel_case(param_name)
                lines.append(f"        private {java_type} {field_name};")

            lines.append("")

            # Generate getters/setters
            for param in params:
                param_type = getattr(param, 'param_type', None)
                param_name = getattr(param, 'name', 'unknown')
                java_type = get_java_type(param_type)
                field_name = to_camel_case(param_name)
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
        return_spec = getattr(table, 'return_spec', None)
        if return_spec:
            params = getattr(return_spec, 'params', None) or []
            if params:
                param_type = getattr(params[0], 'param_type', None)
                return get_java_type(param_type)
        return "String"

    def _collect_decision_table_imports(
        self,
        table: ast.DecisionTableDef
    ) -> Set[str]:
        """Collect imports for decision table class."""
        imports = set()
        imports.update(get_collection_imports())
        imports.update(get_common_imports())
        imports.update(get_logging_imports())

        imports.update(self.get_condition_imports())
        imports.update(self.get_action_imports())

        return imports

    def generate_java_header(self, class_name: str, description: str) -> str:
        """Generate Java file header comment."""
        return f'''/**
 * {description}
 *
 * Auto-generated by Nexflow L4 Rules Generator.
 * DO NOT EDIT - Changes will be overwritten.
 */'''

    def generate_imports(self, imports: List[str]) -> str:
        """Generate import statements."""
        sorted_imports = sorted(imports)
        return '\n'.join(f'import {imp};' for imp in sorted_imports)
