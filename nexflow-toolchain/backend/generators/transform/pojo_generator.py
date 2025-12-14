# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
POJO Generator Mixin

Generates Java POJO classes for L3 Transform input/output schemas.
Used when block transforms define structured input/output fields.
"""

from typing import Set, List, TYPE_CHECKING

from backend.generators.transform.pojo_builder import PojoBuilderMixin

if TYPE_CHECKING:
    from backend.ast import transform_ast as ast


class PojoGeneratorMixin(PojoBuilderMixin):
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
        block: 'ast.TransformBlockDef',
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
        block: 'ast.TransformBlockDef',
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
        fields: List['ast.FieldDecl'],
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

    def should_generate_input_pojo(self, block: 'ast.TransformBlockDef') -> bool:
        """Check if input POJO generation is needed."""
        return (
            block.input and
            block.input.fields and
            len(block.input.fields) > 1
        )

    def should_generate_output_pojo(self, block: 'ast.TransformBlockDef') -> bool:
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
