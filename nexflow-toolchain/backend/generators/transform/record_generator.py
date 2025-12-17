# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform Record Generator Mixin

Generates Java Record classes for L3 Transform input/output schemas.
Used when block transforms define structured input/output fields.
Replaces the older POJO generator with modern Java 17+ Records.
"""

from typing import TYPE_CHECKING

from backend.generators.common.record_builder import RecordBuilderMixin

if TYPE_CHECKING:
    from backend.ast import transform_ast as ast


class TransformRecordGeneratorMixin(RecordBuilderMixin):
    """
    Mixin for generating Java Record classes for transform input/output.

    Generates:
    - Input Record classes for block transforms
    - Output Record classes for block transforms
    - Builder patterns for step-by-step construction
    - withField() methods for immutable updates
    - Serializable implementations for Flink
    """

    def generate_input_record(
        self,
        block: 'ast.TransformBlockDef',
        package: str
    ) -> str:
        """Generate Input Record class for a block transform.

        Args:
            block: The transform block AST node
            package: Java package name

        Returns:
            Java Record class code
        """
        if not block.input or not block.input.fields:
            return ""

        # Only generate if multiple fields (single field uses primitive type)
        if len(block.input.fields) == 1:
            return ""

        class_name = self.to_pascal_case(block.name) + "Input"
        return self.generate_record_class(
            class_name=class_name,
            fields=block.input.fields,
            package=package,
            description=f"Input record for {block.name} transform",
            field_name_accessor=lambda f: f.name,
            field_type_accessor=lambda f: self._field_type_to_java(f.field_type),
        )

    def generate_output_record(
        self,
        block: 'ast.TransformBlockDef',
        package: str
    ) -> str:
        """Generate Output Record class for a block transform.

        Args:
            block: The transform block AST node
            package: Java package name

        Returns:
            Java Record class code
        """
        if not block.output or not block.output.fields:
            return ""

        # Only generate if multiple fields (single field uses primitive type)
        if len(block.output.fields) == 1:
            return ""

        class_name = self.to_pascal_case(block.name) + "Output"
        return self.generate_record_class(
            class_name=class_name,
            fields=block.output.fields,
            package=package,
            description=f"Output record for {block.name} transform",
            field_name_accessor=lambda f: f.name,
            field_type_accessor=lambda f: self._field_type_to_java(f.field_type),
        )

    def should_generate_input_record(self, block: 'ast.TransformBlockDef') -> bool:
        """Check if input Record generation is needed."""
        return (
            block.input and
            block.input.fields and
            len(block.input.fields) > 1
        )

    def should_generate_output_record(self, block: 'ast.TransformBlockDef') -> bool:
        """Check if output Record generation is needed."""
        return (
            block.output and
            block.output.fields and
            len(block.output.fields) > 1
        )

    # Backwards compatibility aliases
    def generate_input_pojo(self, block: 'ast.TransformBlockDef', package: str) -> str:
        """Deprecated: Use generate_input_record() instead."""
        return self.generate_input_record(block, package)

    def generate_output_pojo(self, block: 'ast.TransformBlockDef', package: str) -> str:
        """Deprecated: Use generate_output_record() instead."""
        return self.generate_output_record(block, package)

    def should_generate_input_pojo(self, block: 'ast.TransformBlockDef') -> bool:
        """Deprecated: Use should_generate_input_record() instead."""
        return self.should_generate_input_record(block)

    def should_generate_output_pojo(self, block: 'ast.TransformBlockDef') -> bool:
        """Deprecated: Use should_generate_output_record() instead."""
        return self.should_generate_output_record(block)
