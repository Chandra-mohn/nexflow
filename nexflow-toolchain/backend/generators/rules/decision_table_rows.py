"""
Decision Table Rows Mixin

Generates row matching and result extraction methods for decision tables.
"""

import logging
from typing import List

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    generate_literal,
    get_java_type,
)

LOG = logging.getLogger(__name__)


class DecisionTableRowsMixin:
    """Mixin for generating decision table row evaluation methods."""

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
        """Generate method to get row's result value."""
        output_type = "String"

        lines = [
            f"    private {output_type} getRow{row_num}Result({input_type} input) {{",
        ]

        cells = getattr(row, 'cells', None) or []
        result_generated = False

        for j, cell in enumerate(cells):
            if j < len(headers):
                header_name = getattr(headers[j], 'name', '')
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

        if isinstance(content, ast.NoAction):
            return None

        if isinstance(content, ast.AssignAction):
            value = getattr(content, 'value', None)
            if value is not None:
                return generate_literal(value)
            return None

        if isinstance(content, ast.CalculateAction):
            from backend.generators.rules.utils import generate_value_expr
            expression = getattr(content, 'expression', None)
            if expression is not None:
                return generate_value_expr(expression)
            return None

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
