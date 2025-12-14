# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Parameters Generator Module

Generates Java parameter configuration code from Schema AST definitions.
Supports operational_parameters pattern with defaults, ranges, and scheduling.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator
from backend.generators.schema.parameters_validation import ParametersValidationMixin


class ParametersGeneratorMixin(ParametersValidationMixin):
    """Mixin providing parameter code generation capabilities.

    Generates:
    - Parameter constants with default values
    - Parameter getter methods
    - Range validation for bounded parameters
    - Schedule-aware configuration support
    """

    def _generate_parameters_class(self: BaseGenerator,
                                    schema: ast.SchemaDefinition,
                                    class_name: str,
                                    package: str) -> str:
        """Generate parameters helper class for operational_parameters pattern."""
        if not schema.parameters:
            return ""

        params_block = schema.parameters

        header = self.generate_java_header(
            f"{class_name}Parameters",
            f"Runtime parameters for {schema.name} schema"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'java.util.Optional',
            'java.util.function.Supplier',
        ])

        param_constants = self._generate_parameter_constants(params_block)
        param_fields = self._generate_parameter_fields(params_block)
        param_getters = self._generate_parameter_getters(params_block)
        validation_methods = self._generate_parameter_validation(params_block)
        schedule_methods = self._generate_schedule_methods(params_block)

        return f'''{header}
{package_decl}
{imports}

/**
 * Runtime parameters for {schema.name}.
 *
 * Pattern: operational_parameters
 * Purpose: Configurable runtime values with defaults and validation
 */
public class {class_name}Parameters {{

{param_constants}

{param_fields}

    public {class_name}Parameters() {{
        resetToDefaults();
    }}

{param_getters}

{validation_methods}

{schedule_methods}

    /**
     * Reset all parameters to their default values.
     */
    public void resetToDefaults() {{
{self._generate_reset_to_defaults(params_block)}
    }}
}}
'''

    def _generate_parameter_constants(self: BaseGenerator,
                                       params_block: ast.ParametersBlock) -> str:
        """Generate parameter name and default value constants."""
        constants = []

        constants.append('''    // =========================================================================
    // Parameter Name Constants
    // =========================================================================
''')

        for param in params_block.parameters:
            const_name = self.to_java_constant(param.name)
            constants.append(f'    public static final String PARAM_{const_name} = "{param.name}";')

        constants.append('')
        constants.append('''    // =========================================================================
    // Default Value Constants
    // =========================================================================
''')

        for param in params_block.parameters:
            const_name = self.to_java_constant(param.name)
            default_value = self._get_parameter_default(param)
            java_type = self._get_param_java_type(param.field_type)

            if default_value is not None:
                if java_type == 'String':
                    constants.append(f'    public static final {java_type} DEFAULT_{const_name} = "{default_value}";')
                elif java_type in ('Long', 'Integer', 'Double', 'Float'):
                    suffix = 'L' if java_type == 'Long' else ('D' if java_type == 'Double' else ('F' if java_type == 'Float' else ''))
                    constants.append(f'    public static final {java_type} DEFAULT_{const_name} = {default_value}{suffix};')
                elif java_type == 'Boolean':
                    constants.append(f'    public static final {java_type} DEFAULT_{const_name} = {str(default_value).lower()};')
                else:
                    constants.append(f'    public static final {java_type} DEFAULT_{const_name} = {default_value};')
            else:
                constants.append(f'    public static final {java_type} DEFAULT_{const_name} = null;')

        return '\n'.join(constants)

    def _generate_parameter_fields(self: BaseGenerator,
                                    params_block: ast.ParametersBlock) -> str:
        """Generate parameter instance fields."""
        fields = []
        fields.append('''    // =========================================================================
    // Parameter Fields
    // =========================================================================
''')

        for param in params_block.parameters:
            field_name = self.to_java_field_name(param.name)
            java_type = self._get_param_java_type(param.field_type)
            fields.append(f'    private {java_type} {field_name};')

        return '\n'.join(fields)

    def _generate_parameter_getters(self: BaseGenerator,
                                     params_block: ast.ParametersBlock) -> str:
        """Generate getter and setter methods for parameters."""
        methods = []

        for param in params_block.parameters:
            field_name = self.to_java_field_name(param.name)
            java_type = self._get_param_java_type(param.field_type)
            const_name = self.to_java_constant(param.name)
            capitalized = field_name[0].upper() + field_name[1:]

            has_range = self._has_range_spec(param)

            # Getter
            methods.append(f'''    /**
     * Get the current value of {param.name}.
     */
    public {java_type} get{capitalized}() {{
        return this.{field_name} != null ? this.{field_name} : DEFAULT_{const_name};
    }}''')

            # Setter with optional validation
            if has_range:
                methods.append(f'''
    /**
     * Set the value of {param.name} with range validation.
     */
    public void set{capitalized}({java_type} value) {{
        validate{capitalized}(value);
        this.{field_name} = value;
    }}''')
            else:
                methods.append(f'''
    /**
     * Set the value of {param.name}.
     */
    public void set{capitalized}({java_type} value) {{
        this.{field_name} = value;
    }}''')

            methods.append('')

        return '\n'.join(methods)
