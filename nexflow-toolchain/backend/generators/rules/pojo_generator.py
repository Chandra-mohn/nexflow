"""
POJO Generator Mixin for Rules

Generates Java POJO classes for L4 Rules input/output types with multiple fields.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 POJO generates: Input/Output POJOs with builders, complete types
L4 POJO NEVER generates: Incomplete classes, missing methods
─────────────────────────────────────────────────────────────────────
"""

from typing import Set, List, Optional

from backend.ast import rules_ast as ast


class RulesPojoGeneratorMixin:
    """
    Mixin for generating Java POJO classes for rules input/output.

    Generates:
    - Output POJOs when multiple return parameters
    - Builder pattern for POJOs
    - Serializable implementations
    """

    def generate_output_pojo(
        self,
        table: ast.DecisionTableDef,
        package: str
    ) -> str:
        """Generate Output POJO class for decision table with multiple returns.

        Args:
            table: Decision table definition
            package: Java package name

        Returns:
            Complete Java class for output POJO
        """
        if not table.return_spec or len(table.return_spec.params) <= 1:
            return ""

        class_name = self._to_pascal_case(table.name) + "Output"
        params = table.return_spec.params

        lines = [
            self.generate_java_header(
                class_name, f"Output POJO for {table.name} decision table"
            ),
            f"package {package};",
            "",
            "import java.io.Serializable;",
            "import java.math.BigDecimal;",
            "import java.time.LocalDate;",
            "import java.time.Instant;",
            "import java.util.Objects;",
            "",
            f"/**",
            f" * Output data class for {table.name} decision table.",
            f" * Contains {len(params)} fields from return specification.",
            f" */",
            f"public class {class_name} implements Serializable {{",
            "",
            "    private static final long serialVersionUID = 1L;",
            "",
        ]

        # Generate fields
        for param in params:
            java_type = self._get_java_type(param.param_type)
            field_name = self._to_camel_case(param.name)
            lines.append(f"    private {java_type} {field_name};")

        lines.append("")

        # No-args constructor
        lines.append(f"    public {class_name}() {{}}")
        lines.append("")

        # All-args constructor
        lines.extend(self._generate_all_args_constructor(class_name, params))
        lines.append("")

        # Getters and setters
        for param in params:
            java_type = self._get_java_type(param.param_type)
            field_name = self._to_camel_case(param.name)
            pascal_name = self._to_pascal_case(param.name)

            lines.append(f"    public {java_type} get{pascal_name}() {{")
            lines.append(f"        return {field_name};")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    public void set{pascal_name}({java_type} {field_name}) {{")
            lines.append(f"        this.{field_name} = {field_name};")
            lines.append(f"    }}")
            lines.append("")

        # Builder
        lines.extend(self._generate_builder(class_name, params))
        lines.append("")

        # equals, hashCode, toString
        lines.extend(self._generate_equals_hashcode(class_name, params))
        lines.append("")
        lines.extend(self._generate_to_string(class_name, params))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_all_args_constructor(
        self,
        class_name: str,
        params: List[ast.ReturnParam]
    ) -> List[str]:
        """Generate all-arguments constructor."""
        lines = []

        # Constructor signature
        constructor_params = ", ".join(
            f"{self._get_java_type(p.param_type)} {self._to_camel_case(p.name)}"
            for p in params
        )
        lines.append(f"    public {class_name}({constructor_params}) {{")

        # Assignments
        for param in params:
            field_name = self._to_camel_case(param.name)
            lines.append(f"        this.{field_name} = {field_name};")

        lines.append("    }")

        return lines

    def _generate_builder(
        self,
        class_name: str,
        params: List[ast.ReturnParam]
    ) -> List[str]:
        """Generate Builder inner class."""
        lines = [
            f"    /**",
            f"     * Builder for {class_name}.",
            f"     */",
            f"    public static class Builder {{",
        ]

        # Builder fields
        for param in params:
            java_type = self._get_java_type(param.param_type)
            field_name = self._to_camel_case(param.name)
            lines.append(f"        private {java_type} {field_name};")

        lines.append("")

        # Builder setters (returning this for chaining)
        for param in params:
            java_type = self._get_java_type(param.param_type)
            field_name = self._to_camel_case(param.name)

            lines.append(f"        public Builder {field_name}({java_type} {field_name}) {{")
            lines.append(f"            this.{field_name} = {field_name};")
            lines.append(f"            return this;")
            lines.append(f"        }}")
            lines.append("")

        # Build method
        lines.append(f"        public {class_name} build() {{")
        args = ", ".join(self._to_camel_case(p.name) for p in params)
        lines.append(f"            return new {class_name}({args});")
        lines.append(f"        }}")

        lines.append("    }")
        lines.append("")

        # Static builder() method
        lines.append(f"    public static Builder builder() {{")
        lines.append(f"        return new Builder();")
        lines.append(f"    }}")

        return lines

    def _generate_equals_hashcode(
        self,
        class_name: str,
        params: List[ast.ReturnParam]
    ) -> List[str]:
        """Generate equals and hashCode methods."""
        field_names = [self._to_camel_case(p.name) for p in params]

        lines = [
            f"    @Override",
            f"    public boolean equals(Object o) {{",
            f"        if (this == o) return true;",
            f"        if (o == null || getClass() != o.getClass()) return false;",
            f"        {class_name} that = ({class_name}) o;",
        ]

        # Generate equals comparisons
        comparisons = " && ".join(
            f"Objects.equals({fn}, that.{fn})" for fn in field_names
        )
        lines.append(f"        return {comparisons};")
        lines.append(f"    }}")
        lines.append("")

        # hashCode
        lines.append(f"    @Override")
        lines.append(f"    public int hashCode() {{")
        hash_args = ", ".join(field_names)
        lines.append(f"        return Objects.hash({hash_args});")
        lines.append(f"    }}")

        return lines

    def _generate_to_string(
        self,
        class_name: str,
        params: List[ast.ReturnParam]
    ) -> List[str]:
        """Generate toString method."""
        field_names = [self._to_camel_case(p.name) for p in params]

        lines = [
            f"    @Override",
            f"    public String toString() {{",
            f'        return "{class_name}{{" +',
        ]

        for i, fn in enumerate(field_names):
            if i == 0:
                lines.append(f'            "{fn}=" + {fn} +')
            else:
                lines.append(f'            ", {fn}=" + {fn} +')

        lines.append(f'            "}}";')
        lines.append(f"    }}")

        return lines

    def should_generate_output_pojo(self, table: ast.DecisionTableDef) -> bool:
        """Check if table needs an output POJO (multiple return params)."""
        return (
            table.return_spec is not None and
            len(table.return_spec.params) > 1
        )

    def get_output_type(self, table: ast.DecisionTableDef) -> str:
        """Get the appropriate output type for the table.

        Returns:
            - Simple type if single return param
            - POJO class name if multiple return params
            - "Object" if no return spec
        """
        if not table.return_spec:
            return "Object"

        if len(table.return_spec.params) == 1:
            return self._get_java_type(table.return_spec.params[0].param_type)

        return self._to_pascal_case(table.name) + "Output"

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

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def generate_java_header(self, class_name: str, description: str) -> str:
        """Generate Java file header comment."""
        return f'''/**
 * {description}
 *
 * Auto-generated by Nexflow L4 Rules Generator.
 * DO NOT EDIT - Changes will be overwritten.
 */'''
