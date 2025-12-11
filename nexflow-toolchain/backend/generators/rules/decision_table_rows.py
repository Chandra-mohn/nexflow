"""
Decision Table Rows Mixin

Generates row matching and result extraction methods for decision tables.
"""

import logging
from typing import List, Tuple

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
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

        # Determine output type based on return params count
        table_name = getattr(table, 'name', 'unknown')
        if len(return_params) > 1:
            output_type = to_pascal_case(table_name) + "Output"
        elif len(return_params) == 1:
            param_type = getattr(return_params[0], 'param_type', None)
            output_type = get_java_type(param_type)
        else:
            output_type = "String"

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
                row_num, row, headers, return_params, input_type, output_type
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
        return_params: List,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate method to get row's result value.

        For single return param: returns the value directly
        For multiple return params: returns Output POJO with all fields
        """
        lines = [
            f"    private {output_type} getRow{row_num}Result({input_type} input) {{",
        ]

        cells = getattr(row, 'cells', None) or []
        return_fields = [getattr(p, 'name', '') for p in return_params]

        # Build mapping of header name to cell value
        header_to_value = {}
        for j, cell in enumerate(cells):
            if j < len(headers):
                header_name = getattr(headers[j], 'name', '')
                if header_name in return_fields:
                    content = getattr(cell, 'content', None)
                    value = self._extract_action_value(content)
                    if value is not None:
                        header_to_value[header_name] = value

        # Single return param: return value directly
        if len(return_params) == 1:
            field_name = return_fields[0]
            if field_name in header_to_value:
                lines.append(f"        return {header_to_value[field_name]};")
            else:
                LOG.warning(f"Row {row_num} has no result for {field_name}, returning null")
                lines.append('        return null;')
        # Multiple return params: return Output POJO
        elif len(return_params) > 1:
            lines.append(f"        return {output_type}.builder()")
            for param in return_params:
                field_name = getattr(param, 'name', '')
                setter_name = to_camel_case(field_name)
                if field_name in header_to_value:
                    lines.append(f"            .{setter_name}({header_to_value[field_name]})")
                else:
                    lines.append(f"            .{setter_name}(null)")
            lines.append("            .build();")
        else:
            LOG.warning(f"Row {row_num} has no return params, returning null")
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

        # Handle condition types used as action values (e.g., "block" in action column)
        # ExactMatchCondition wraps a literal value which is the actual action result
        if isinstance(content, ast.ExactMatchCondition):
            value = getattr(content, 'value', None)
            if value is not None:
                return generate_literal(value)
            return None

        # ComparisonCondition with a literal value can also be used as action
        if isinstance(content, ast.ComparisonCondition):
            value = getattr(content, 'value', None)
            if value is not None:
                return generate_literal(value)
            return None

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
