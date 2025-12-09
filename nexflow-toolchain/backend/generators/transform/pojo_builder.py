"""
POJO Builder Pattern Mixin

Generates builder pattern, toString, equals, and hashCode methods for POJOs.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.ast import transform_ast as ast


class PojoBuilderMixin:
    """
    Mixin for generating builder pattern and utility methods.

    Generates:
    - Builder inner class with fluent setters
    - toString method
    - equals and hashCode methods
    """

    def _generate_all_args_constructor(
        self,
        class_name: str,
        fields: List['ast.FieldDecl']
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
        fields: List['ast.FieldDecl']
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
        fields: List['ast.FieldDecl']
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
        fields: List['ast.FieldDecl']
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

    def _field_type_to_java(self, field_type: 'ast.FieldType') -> str:
        """Convert field type to Java type string."""
        from backend.ast import transform_ast as ast

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
