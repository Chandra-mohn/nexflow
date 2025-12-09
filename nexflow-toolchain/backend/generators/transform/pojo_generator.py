"""
POJO Generator Mixin

Generates Java POJO classes for L3 Transform input/output schemas.
Used when block transforms define structured input/output fields.
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class PojoGeneratorMixin:
    """
    Mixin for generating Java POJO classes.

    Generates:
    - Input POJO classes for block transforms
    - Output POJO classes for block transforms
    - Builder patterns for complex POJOs
    - Serializable implementations for Flink
    """

    def generate_input_pojo(
        self,
        block: ast.TransformBlockDef,
        package: str
    ) -> str:
        """Generate Input POJO class for a block transform.

        Args:
            block: The transform block AST node
            package: Java package name

        Returns:
            Java POJO class code
        """
        if not block.input or not block.input.fields:
            return ""

        # Only generate if multiple fields (single field uses primitive type)
        if len(block.input.fields) == 1:
            return ""

        class_name = self.to_pascal_case(block.name) + "Input"
        return self._generate_pojo_class(
            class_name,
            block.input.fields,
            package,
            f"Input POJO for {block.name} transform"
        )

    def generate_output_pojo(
        self,
        block: ast.TransformBlockDef,
        package: str
    ) -> str:
        """Generate Output POJO class for a block transform.

        Args:
            block: The transform block AST node
            package: Java package name

        Returns:
            Java POJO class code
        """
        if not block.output or not block.output.fields:
            return ""

        # Only generate if multiple fields (single field uses primitive type)
        if len(block.output.fields) == 1:
            return ""

        class_name = self.to_pascal_case(block.name) + "Output"
        return self._generate_pojo_class(
            class_name,
            block.output.fields,
            package,
            f"Output POJO for {block.name} transform"
        )

    def _generate_pojo_class(
        self,
        class_name: str,
        fields: List[ast.FieldDecl],
        package: str,
        description: str
    ) -> str:
        """Generate a complete POJO class."""
        lines = [
            self.generate_java_header(class_name, description),
            f"package {package};",
            "",
            self.generate_imports(list(self.get_pojo_imports())),
            "",
            "/**",
            f" * {description}",
            " */",
            f"public class {class_name} implements Serializable {{",
            "",
            "    private static final long serialVersionUID = 1L;",
            "",
        ]

        # Generate fields
        for field in fields:
            java_type = self._field_type_to_java(field.field_type)
            field_name = self.to_camel_case(field.name)
            lines.append(f"    private {java_type} {field_name};")

        lines.append("")

        # Generate default constructor
        lines.extend([
            "    /**",
            "     * Default constructor for serialization.",
            "     */",
            f"    public {class_name}() {{",
            "    }",
            "",
        ])

        # Generate all-args constructor
        lines.extend(self._generate_all_args_constructor(class_name, fields))
        lines.append("")

        # Generate getters and setters
        for field in fields:
            java_type = self._field_type_to_java(field.field_type)
            field_name = self.to_camel_case(field.name)
            lines.extend(self._generate_getter_setter(field_name, java_type))
            lines.append("")

        # Generate builder
        lines.extend(self._generate_builder(class_name, fields))
        lines.append("")

        # Generate toString
        lines.extend(self._generate_to_string(class_name, fields))
        lines.append("")

        # Generate equals and hashCode
        lines.extend(self._generate_equals_hashcode(class_name, fields))

        lines.append("}")

        return '\n'.join(lines)

    def _generate_all_args_constructor(
        self,
        class_name: str,
        fields: List[ast.FieldDecl]
    ) -> List[str]:
        """Generate constructor with all fields as arguments."""
        params = []
        for field in fields:
            java_type = self._field_type_to_java(field.field_type)
            field_name = self.to_camel_case(field.name)
            params.append(f"{java_type} {field_name}")

        lines = [
            "    /**",
            "     * All-args constructor.",
            "     */",
            f"    public {class_name}({', '.join(params)}) {{",
        ]

        for field in fields:
            field_name = self.to_camel_case(field.name)
            lines.append(f"        this.{field_name} = {field_name};")

        lines.append("    }")
        return lines

    def _generate_getter_setter(
        self,
        field_name: str,
        java_type: str
    ) -> List[str]:
        """Generate getter and setter for a field."""
        getter_name = self.to_getter(field_name)
        setter_name = self.to_setter(field_name)

        return [
            f"    public {java_type} {getter_name} {{",
            f"        return {field_name};",
            "    }",
            "",
            f"    public void {setter_name}({java_type} {field_name}) {{",
            f"        this.{field_name} = {field_name};",
            "    }",
        ]

    def _generate_builder(
        self,
        class_name: str,
        fields: List[ast.FieldDecl]
    ) -> List[str]:
        """Generate builder pattern for POJO."""
        lines = [
            "    /**",
            "     * Builder for fluent construction.",
            "     */",
            f"    public static class Builder {{",
        ]

        # Builder fields
        for field in fields:
            java_type = self._field_type_to_java(field.field_type)
            field_name = self.to_camel_case(field.name)
            lines.append(f"        private {java_type} {field_name};")

        lines.append("")

        # Builder methods
        for field in fields:
            java_type = self._field_type_to_java(field.field_type)
            field_name = self.to_camel_case(field.name)
            lines.extend([
                f"        public Builder {field_name}({java_type} {field_name}) {{",
                f"            this.{field_name} = {field_name};",
                "            return this;",
                "        }",
                "",
            ])

        # Build method
        args = ", ".join(self.to_camel_case(f.name) for f in fields)
        lines.extend([
            f"        public {class_name} build() {{",
            f"            return new {class_name}({args});",
            "        }",
            "    }",
            "",
            f"    public static Builder builder() {{",
            "        return new Builder();",
            "    }",
        ])

        return lines

    def _generate_to_string(
        self,
        class_name: str,
        fields: List[ast.FieldDecl]
    ) -> List[str]:
        """Generate toString method."""
        field_strs = []
        for field in fields:
            field_name = self.to_camel_case(field.name)
            field_strs.append(f'"{field_name}=" + {field_name}')

        lines = [
            "    @Override",
            "    public String toString() {",
            f'        return "{class_name}{{" +',
        ]

        for i, fs in enumerate(field_strs):
            if i < len(field_strs) - 1:
                lines.append(f'                {fs} + ", " +')
            else:
                lines.append(f"                {fs} +")

        lines.extend([
            '                "}";',
            "    }",
        ])

        return lines

    def _generate_equals_hashcode(
        self,
        class_name: str,
        fields: List[ast.FieldDecl]
    ) -> List[str]:
        """Generate equals and hashCode methods."""
        field_names = [self.to_camel_case(f.name) for f in fields]

        lines = [
            "    @Override",
            "    public boolean equals(Object o) {",
            "        if (this == o) return true;",
            f"        if (o == null || getClass() != o.getClass()) return false;",
            f"        {class_name} that = ({class_name}) o;",
            "        return " + " &&\n               ".join(
                f"Objects.equals({fn}, that.{fn})" for fn in field_names
            ) + ";",
            "    }",
            "",
            "    @Override",
            "    public int hashCode() {",
            f"        return Objects.hash({', '.join(field_names)});",
            "    }",
        ]

        return lines

    def _field_type_to_java(self, field_type: ast.FieldType) -> str:
        """Convert field type to Java type string."""
        if not field_type:
            return "Object"

        base_type = field_type.base_type
        if isinstance(base_type, ast.BaseType):
            java_type = self.get_java_type(base_type.value)
        elif isinstance(base_type, str):
            java_type = self.to_pascal_case(base_type)
        else:
            java_type = "Object"

        # Handle collections
        if field_type.is_list:
            return f"List<{java_type}>"
        if field_type.is_map:
            return f"Map<String, {java_type}>"

        return java_type

    def should_generate_input_pojo(self, block: ast.TransformBlockDef) -> bool:
        """Check if input POJO generation is needed."""
        return (
            block.input and
            block.input.fields and
            len(block.input.fields) > 1
        )

    def should_generate_output_pojo(self, block: ast.TransformBlockDef) -> bool:
        """Check if output POJO generation is needed."""
        return (
            block.output and
            block.output.fields and
            len(block.output.fields) > 1
        )

    def get_pojo_imports(self) -> Set[str]:
        """Get required imports for POJO generation."""
        return {
            'java.io.Serializable',
            'java.util.Objects',
            'java.util.List',
            'java.util.Map',
        }
