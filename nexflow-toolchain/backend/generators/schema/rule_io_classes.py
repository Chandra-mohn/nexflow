# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rule I/O Classes Mixin

Generates input and output classes for business rules.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class RuleIOClassesMixin:
    """Mixin providing rule input/output class generation."""

    def _generate_input_class(self: BaseGenerator,
                               rule: ast.RuleBlock,
                               rule_name: str) -> str:
        """Generate input class from given block.

        Returns Java class for rule inputs.
        """
        if not rule.given or not rule.given.fields:
            return f'''    /**
     * Input parameters for {rule.name} rule (no inputs defined).
     */
    public static class {rule_name}Input {{
        public {rule_name}Input() {{
        }}
    }}'''

        # Generate fields
        field_declarations = []
        constructor_params = []
        constructor_assigns = []
        getters = []

        for field in rule.given.fields:
            java_field = self.to_java_field_name(field.name)
            java_type = self._get_rule_field_type(field.field_type)
            capitalized = java_field[0].upper() + java_field[1:]

            field_declarations.append(f'        private final {java_type} {java_field};')
            constructor_params.append(f'{java_type} {java_field}')
            constructor_assigns.append(f'            this.{java_field} = {java_field};')
            getters.append(f'''        public {java_type} get{capitalized}() {{
            return this.{java_field};
        }}''')

        fields_block = '\n'.join(field_declarations)
        params_block = ', '.join(constructor_params)
        assigns_block = '\n'.join(constructor_assigns)
        getters_block = '\n\n'.join(getters)

        return f'''    /**
     * Input parameters for {rule.name} rule.
     */
    public static class {rule_name}Input {{
{fields_block}

        public {rule_name}Input({params_block}) {{
{assigns_block}
        }}

{getters_block}

        @Override
        public String toString() {{
            return "{rule_name}Input{{{self._generate_to_string_fields(rule.given.fields)}}}";
        }}
    }}'''

    def _generate_output_class(self: BaseGenerator,
                                rule: ast.RuleBlock,
                                rule_name: str) -> str:
        """Generate output class from return block.

        Returns Java class for rule outputs.
        """
        if not rule.return_block or not rule.return_block.fields:
            return f'''    /**
     * Output result for {rule.name} rule (no outputs defined).
     */
    public static class {rule_name}Output {{
        public {rule_name}Output() {{
        }}
    }}'''

        # Generate fields
        field_declarations = []
        constructor_params = []
        constructor_assigns = []
        getters = []

        for field in rule.return_block.fields:
            java_field = self.to_java_field_name(field.name)
            java_type = self._get_rule_field_type(field.field_type)
            capitalized = java_field[0].upper() + java_field[1:]

            field_declarations.append(f'        private final {java_type} {java_field};')
            constructor_params.append(f'{java_type} {java_field}')
            constructor_assigns.append(f'            this.{java_field} = {java_field};')
            getters.append(f'''        public {java_type} get{capitalized}() {{
            return this.{java_field};
        }}''')

        fields_block = '\n'.join(field_declarations)
        params_block = ', '.join(constructor_params)
        assigns_block = '\n'.join(constructor_assigns)
        getters_block = '\n\n'.join(getters)

        return f'''    /**
     * Output result for {rule.name} rule.
     */
    public static class {rule_name}Output {{
{fields_block}

        public {rule_name}Output({params_block}) {{
{assigns_block}
        }}

{getters_block}

        @Override
        public String toString() {{
            return "{rule_name}Output{{{self._generate_to_string_fields(rule.return_block.fields)}}}";
        }}
    }}'''

    def _get_rule_field_type(self: BaseGenerator, field_type: ast.FieldType) -> str:
        """Get Java type for rule field type."""
        if field_type.base_type:
            return self.get_java_type(field_type.base_type.value)
        return "Object"

    def _generate_to_string_fields(self: BaseGenerator,
                                    fields: List[ast.RuleFieldDecl]) -> str:
        """Generate toString() field representations."""
        parts = []
        for i, field in enumerate(fields):
            java_field = self.to_java_field_name(field.name)
            separator = '' if i == 0 else ', '
            parts.append(f'{separator}{java_field}=' + '" + ' + f'{java_field} + "')
        return ''.join(parts)
