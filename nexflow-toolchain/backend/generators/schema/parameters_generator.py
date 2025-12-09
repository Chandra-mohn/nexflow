"""
Parameters Generator Module

Generates Java parameter configuration code from Schema AST definitions.
Supports operational_parameters pattern with defaults, ranges, and scheduling.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class ParametersGeneratorMixin:
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
        """Generate parameters helper class for operational_parameters pattern.

        Returns complete Java class for runtime parameter configuration.
        """
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

        # Generate components
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
        // Initialize with defaults
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
        """Generate parameter name and default value constants.

        Returns Java constants block for parameter metadata.
        """
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
        """Generate parameter instance fields.

        Returns Java field declarations for parameters.
        """
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
        """Generate getter and setter methods for parameters.

        Returns Java methods for parameter access.
        """
        methods = []

        for param in params_block.parameters:
            field_name = self.to_java_field_name(param.name)
            java_type = self._get_param_java_type(param.field_type)
            const_name = self.to_java_constant(param.name)
            capitalized = field_name[0].upper() + field_name[1:]

            # Check if parameter has range validation
            has_range = self._has_range_spec(param)

            # Getter
            methods.append(f'''    /**
     * Get the current value of {param.name}.
     * @return Current value or default if not set
     */
    public {java_type} get{capitalized}() {{
        return this.{field_name} != null ? this.{field_name} : DEFAULT_{const_name};
    }}''')

            # Setter with optional validation
            if has_range:
                methods.append(f'''
    /**
     * Set the value of {param.name} with range validation.
     * @param value The new value
     * @throws IllegalArgumentException if value is out of range
     */
    public void set{capitalized}({java_type} value) {{
        validate{capitalized}(value);
        this.{field_name} = value;
    }}''')
            else:
                methods.append(f'''
    /**
     * Set the value of {param.name}.
     * @param value The new value
     */
    public void set{capitalized}({java_type} value) {{
        this.{field_name} = value;
    }}''')

            methods.append('')

        return '\n'.join(methods)

    def _generate_parameter_validation(self: BaseGenerator,
                                        params_block: ast.ParametersBlock) -> str:
        """Generate validation methods for parameters with range specs.

        Returns Java validation methods.
        """
        methods = []
        methods.append('''    // =========================================================================
    // Parameter Validation Methods
    // =========================================================================
''')

        has_validation = False
        for param in params_block.parameters:
            range_spec = self._get_range_spec(param)
            if range_spec:
                has_validation = True
                field_name = self.to_java_field_name(param.name)
                java_type = self._get_param_java_type(param.field_type)
                capitalized = field_name[0].upper() + field_name[1:]

                min_val = getattr(range_spec, 'min_value', None)
                max_val = getattr(range_spec, 'max_value', None)

                conditions = []
                if min_val is not None:
                    conditions.append(f'value < {min_val}')
                if max_val is not None:
                    conditions.append(f'value > {max_val}')

                if conditions:
                    condition = ' || '.join(conditions)
                    range_desc = f"[{min_val if min_val is not None else '*'}, {max_val if max_val is not None else '*'}]"

                    methods.append(f'''    /**
     * Validate {param.name} against range {range_desc}.
     * @param value Value to validate
     * @throws IllegalArgumentException if out of range
     */
    private void validate{capitalized}({java_type} value) {{
        if (value != null && ({condition})) {{
            throw new IllegalArgumentException(
                "Parameter {param.name} value " + value + " is out of range {range_desc}");
        }}
    }}
''')

        if not has_validation:
            methods.append('    // No range validations defined\n')

        return '\n'.join(methods)

    def _generate_schedule_methods(self: BaseGenerator,
                                    params_block: ast.ParametersBlock) -> str:
        """Generate schedule-related methods for parameters.

        Returns Java methods for scheduled parameter updates.
        """
        schedulable_params = [p for p in params_block.parameters if self._is_schedulable(p)]

        if not schedulable_params:
            return '''    // =========================================================================
    // Schedule Support (no schedulable parameters defined)
    // =========================================================================

    /**
     * Check if any parameters support scheduling.
     */
    public static boolean hasSchedulableParameters() {
        return false;
    }
'''

        param_list = ', '.join(f'PARAM_{self.to_java_constant(p.name)}' for p in schedulable_params)

        return f'''    // =========================================================================
    // Schedule Support
    // =========================================================================

    private static final String[] SCHEDULABLE_PARAMS = {{{param_list}}};

    /**
     * Check if any parameters support scheduling.
     */
    public static boolean hasSchedulableParameters() {{
        return true;
    }}

    /**
     * Get list of schedulable parameter names.
     */
    public static String[] getSchedulableParameters() {{
        return SCHEDULABLE_PARAMS.clone();
    }}

    /**
     * Check if a specific parameter supports scheduling.
     * @param paramName The parameter name
     * @return true if the parameter can be scheduled
     */
    public static boolean isSchedulable(String paramName) {{
        for (String p : SCHEDULABLE_PARAMS) {{
            if (p.equals(paramName)) return true;
        }}
        return false;
    }}
'''

    def _generate_reset_to_defaults(self: BaseGenerator,
                                     params_block: ast.ParametersBlock) -> str:
        """Generate reset statements for all parameters.

        Returns Java statements to reset parameters to defaults.
        """
        statements = []
        for param in params_block.parameters:
            field_name = self.to_java_field_name(param.name)
            const_name = self.to_java_constant(param.name)
            statements.append(f'        this.{field_name} = DEFAULT_{const_name};')
        return '\n'.join(statements)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_param_java_type(self: BaseGenerator, field_type: ast.FieldType) -> str:
        """Get Java type for parameter field type."""
        if field_type.base_type:
            return self.get_java_type(field_type.base_type.value)
        return "Object"

    def _get_parameter_default(self: BaseGenerator, param: ast.ParameterDecl):
        """Extract default value from parameter options."""
        for option in param.options:
            if option.default_value is not None:
                return self._literal_to_value(option.default_value)
        return None

    def _literal_to_value(self: BaseGenerator, literal):
        """Convert AST literal to Python value."""
        if hasattr(literal, 'value'):
            return literal.value
        return literal

    def _has_range_spec(self: BaseGenerator, param: ast.ParameterDecl) -> bool:
        """Check if parameter has range specification."""
        return self._get_range_spec(param) is not None

    def _get_range_spec(self: BaseGenerator, param: ast.ParameterDecl):
        """Extract range specification from parameter options."""
        for option in param.options:
            if option.range_spec is not None:
                return option.range_spec
        return None

    def _is_schedulable(self: BaseGenerator, param: ast.ParameterDecl) -> bool:
        """Check if parameter can be scheduled."""
        for option in param.options:
            if option.can_schedule:
                return True
        return False
