# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Params Generator Mixin

Generates Java code for L3 Transform params blocks.
Provides configurable transform parameters with type safety and defaults.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L3 Params Block Features:
- typed parameter declarations (string, integer, decimal, boolean)
- required/optional modifiers
- default values
- runtime parameter injection
- params accessor object for DSL-style access
─────────────────────────────────────────────────────────────────────
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class ParamsGeneratorMixin:
    """
    Mixin for generating Java transform parameter code.

    Generates:
    - Parameter field declarations with types
    - Parameter initialization with defaults
    - Params accessor object for DSL-style access (params.threshold)
    - Parameter validation for required fields
    - Type-safe getter methods
    """

    # Map DSL types to Java types
    PARAM_TYPE_MAP = {
        'string': 'String',
        'integer': 'Long',
        'decimal': 'BigDecimal',
        'boolean': 'Boolean',
        'date': 'LocalDate',
        'timestamp': 'Instant',
    }

    def generate_params_declarations(self, params: ast.ParamsBlock) -> str:
        """Generate parameter field declarations.

        Example output:
            private BigDecimal threshold;
            private String mode = "standard";
            private BigDecimal multiplier = new BigDecimal("1.0");
        """
        if not params or not params.params:
            return ""

        lines = [
            "    // Transform parameters",
        ]

        for param in params.params:
            java_type = self._get_param_java_type(param.param_type)
            field_name = self.to_camel_case(param.name)

            if param.default_value:
                default_val = self._generate_default_value(
                    param.param_type, param.default_value
                )
                lines.append(f"    private {java_type} {field_name} = {default_val};")
            else:
                lines.append(f"    private {java_type} {field_name};")

        lines.append("")
        return '\n'.join(lines)

    def generate_params_accessor_object(self, params: ast.ParamsBlock) -> str:
        """Generate params accessor object for DSL-style access.

        This allows transform code to use params.threshold syntax.

        Example output:
            private final ParamsAccessor params = new ParamsAccessor();
        """
        if not params or not params.params:
            return ""

        return """    // Params accessor for DSL-style access (params.name)
    private final ParamsAccessor params = new ParamsAccessor();
"""

    def generate_params_accessor_class(self, params: ast.ParamsBlock) -> str:
        """Generate inner class for DSL-style params access.

        Example output:
            private class ParamsAccessor {
                public BigDecimal threshold() { return threshold; }
                public String mode() { return mode; }
            }
        """
        if not params or not params.params:
            return ""

        lines = [
            "    /**",
            "     * Accessor class for DSL-style params access.",
            "     * Enables syntax like: params.threshold, params.mode",
            "     */",
            "    private class ParamsAccessor {",
        ]

        for param in params.params:
            java_type = self._get_param_java_type(param.param_type)
            field_name = self.to_camel_case(param.name)
            # Use record-style accessor (fieldName() instead of getFieldName())
            lines.append(f"        public {java_type} {field_name}() {{ return {field_name}; }}")

        lines.append("    }")
        lines.append("")

        return '\n'.join(lines)

    def generate_params_setters(self, params: ast.ParamsBlock) -> str:
        """Generate setter methods for parameters.

        Example output:
            public void setThreshold(BigDecimal threshold) {
                this.threshold = threshold;
            }
        """
        if not params or not params.params:
            return ""

        lines = []

        for param in params.params:
            java_type = self._get_param_java_type(param.param_type)
            field_name = self.to_camel_case(param.name)
            setter_name = "set" + self.to_pascal_case(param.name)

            lines.extend([
                f"    /**",
                f"     * Set the {param.name} parameter.",
                f"     */",
                f"    public void {setter_name}({java_type} {field_name}) {{",
                f"        this.{field_name} = {field_name};",
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def generate_params_validation(self, params: ast.ParamsBlock) -> str:
        """Generate parameter validation method.

        Validates that all required parameters are set.

        Example output:
            private void validateParams() throws IllegalStateException {
                if (threshold == null) {
                    throw new IllegalStateException("Required parameter 'threshold' is not set");
                }
            }
        """
        if not params or not params.params:
            return ""

        required_params = [p for p in params.params if p.required and not p.default_value]
        if not required_params:
            return ""

        lines = [
            "    /**",
            "     * Validate that all required parameters are set.",
            "     * @throws IllegalStateException if a required parameter is missing",
            "     */",
            "    private void validateParams() throws IllegalStateException {",
        ]

        for param in required_params:
            field_name = self.to_camel_case(param.name)
            lines.extend([
                f"        if ({field_name} == null) {{",
                f'            throw new IllegalStateException("Required parameter \'{param.name}\' is not set");',
                f"        }}",
            ])

        lines.extend([
            "    }",
            "",
        ])

        return '\n'.join(lines)

    def generate_params_builder(self, params: ast.ParamsBlock, class_name: str) -> str:
        """Generate a builder pattern for parameter configuration.

        Example output:
            public static class Builder {
                private BigDecimal threshold;
                private String mode = "standard";

                public Builder threshold(BigDecimal threshold) {
                    this.threshold = threshold;
                    return this;
                }

                public TransformFunction build() {
                    TransformFunction instance = new TransformFunction();
                    instance.threshold = this.threshold;
                    return instance;
                }
            }
        """
        if not params or not params.params:
            return ""

        lines = [
            "    /**",
            "     * Builder for configuring transform parameters.",
            "     */",
            "    public static class Builder {",
        ]

        # Field declarations
        for param in params.params:
            java_type = self._get_param_java_type(param.param_type)
            field_name = self.to_camel_case(param.name)
            if param.default_value:
                default_val = self._generate_default_value(
                    param.param_type, param.default_value
                )
                lines.append(f"        private {java_type} {field_name} = {default_val};")
            else:
                lines.append(f"        private {java_type} {field_name};")

        lines.append("")

        # Builder methods
        for param in params.params:
            java_type = self._get_param_java_type(param.param_type)
            field_name = self.to_camel_case(param.name)
            lines.extend([
                f"        public Builder {field_name}({java_type} {field_name}) {{",
                f"            this.{field_name} = {field_name};",
                f"            return this;",
                f"        }}",
                "",
            ])

        # Build method
        lines.extend([
            f"        public {class_name} build() {{",
            f"            {class_name} instance = new {class_name}();",
        ])

        for param in params.params:
            field_name = self.to_camel_case(param.name)
            lines.append(f"            instance.{field_name} = this.{field_name};")

        lines.extend([
            "            return instance;",
            "        }",
            "    }",
            "",
        ])

        return '\n'.join(lines)

    def generate_params_from_config(self, params: ast.ParamsBlock) -> str:
        """Generate method to load parameters from configuration.

        Example output:
            public void loadParams(Map<String, Object> config) {
                if (config.containsKey("threshold")) {
                    this.threshold = (BigDecimal) config.get("threshold");
                }
            }
        """
        if not params or not params.params:
            return ""

        lines = [
            "    /**",
            "     * Load parameters from a configuration map.",
            "     * @param config Map of parameter name to value",
            "     */",
            "    public void loadParams(Map<String, Object> config) {",
        ]

        for param in params.params:
            field_name = self.to_camel_case(param.name)
            java_type = self._get_param_java_type(param.param_type)
            lines.extend([
                f'        if (config.containsKey("{param.name}")) {{',
                f'            this.{field_name} = ({java_type}) config.get("{param.name}");',
                f"        }}",
            ])

        lines.extend([
            "    }",
            "",
        ])

        return '\n'.join(lines)

    def _get_param_java_type(self, param_type: str) -> str:
        """Get Java type for a parameter type."""
        return self.PARAM_TYPE_MAP.get(param_type.lower(), 'Object')

    def _generate_default_value(self, param_type: str, default_value: str) -> str:
        """Generate Java code for a default value."""
        type_lower = param_type.lower()

        if type_lower == 'string':
            # Remove surrounding quotes if present
            val = default_value.strip('"\'')
            return f'"{val}"'
        elif type_lower == 'integer':
            return f'{default_value}L'
        elif type_lower == 'decimal':
            return f'new BigDecimal("{default_value}")'
        elif type_lower == 'boolean':
            return default_value.lower()
        elif type_lower == 'date':
            return f'LocalDate.parse("{default_value}")'
        elif type_lower == 'timestamp':
            return f'Instant.parse("{default_value}")'
        else:
            return default_value

    def get_params_imports(self) -> Set[str]:
        """Get required imports for params generation."""
        return {
            'java.math.BigDecimal',
            'java.time.LocalDate',
            'java.time.Instant',
            'java.util.Map',
        }
