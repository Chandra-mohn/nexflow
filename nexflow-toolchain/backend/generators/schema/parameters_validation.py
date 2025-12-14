# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Parameters Validation Mixin

Generates validation and schedule methods for operational parameters.
"""

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class ParametersValidationMixin:
    """Mixin providing parameter validation generation."""

    def _generate_parameter_validation(self: BaseGenerator,
                                        params_block: ast.ParametersBlock) -> str:
        """Generate validation methods for parameters with range specs."""
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
        """Generate schedule-related methods for parameters."""
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
        """Generate reset statements for all parameters."""
        statements = []
        for param in params_block.parameters:
            field_name = self.to_java_field_name(param.name)
            const_name = self.to_java_constant(param.name)
            statements.append(f'        this.{field_name} = DEFAULT_{const_name};')
        return '\n'.join(statements)

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
