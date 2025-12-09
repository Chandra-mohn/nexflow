"""
Transform Generator Module

Main generator class for L3 Transform DSL → Java transform functions.
Orchestrates mixin classes for modular generation.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L3 generates: MapFunction implementations with complete logic
L3 NEVER generates: Routing decisions, rule evaluations

Generated transforms must:
- Compile and run without modification
- NO placeholder returns (return null)
- NO stub methods
- Complete expression evaluation code
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import Set

from backend.ast import transform_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
from backend.generators.transform.expression_generator import ExpressionGeneratorMixin
from backend.generators.transform.validation_generator import ValidationGeneratorMixin
from backend.generators.transform.mapping_generator import MappingGeneratorMixin
from backend.generators.transform.cache_generator import CacheGeneratorMixin
from backend.generators.transform.error_generator import ErrorGeneratorMixin
from backend.generators.transform.function_generator import FunctionGeneratorMixin
from backend.generators.transform.compose_generator import ComposeGeneratorMixin
from backend.generators.transform.onchange_generator import OnChangeGeneratorMixin
from backend.generators.transform.pojo_generator import PojoGeneratorMixin
from backend.generators.transform.metadata_generator import MetadataGeneratorMixin


class TransformGenerator(
    ExpressionGeneratorMixin,
    ValidationGeneratorMixin,
    MappingGeneratorMixin,
    CacheGeneratorMixin,
    ErrorGeneratorMixin,
    FunctionGeneratorMixin,
    ComposeGeneratorMixin,
    OnChangeGeneratorMixin,
    PojoGeneratorMixin,
    MetadataGeneratorMixin,
    BaseGenerator
):
    """
    Generator for L3 Transform DSL.

    Generates Java transform functions:
    - MapFunction implementations for simple transforms
    - ProcessFunction implementations for block transforms
    - Validation, caching, and error handling
    - Expression evaluation code
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate Java code from Transform AST."""
        # Generate simple transforms
        for transform in program.transforms:
            self._generate_transform(transform)

        # Generate block transforms
        for block in program.transform_blocks:
            self._generate_transform_block(block)

        return self.result

    def _generate_transform(self, transform: ast.TransformDef) -> None:
        """Generate files for a simple transform definition."""
        class_name = self.to_java_class_name(transform.name) + "Function"
        package = f"{self.config.package_prefix}.transform"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Determine input/output types from transform specs
        input_type = self._get_input_type(transform)
        output_type = self._get_output_type(transform)

        # Generate MapFunction class
        content = self.generate_map_function_class(
            transform, package, input_type, output_type
        )

        self.result.add_file(
            java_src_path / f"{class_name}.java",
            content,
            "java"
        )

    def _generate_transform_block(self, block: ast.TransformBlockDef) -> None:
        """Generate files for a block-level transform definition."""
        class_name = self.to_java_class_name(block.name) + "ProcessFunction"
        package = f"{self.config.package_prefix}.transform"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Determine input/output types from block specs
        input_type = self._get_block_input_type(block)
        output_type = self._get_block_output_type(block)

        # Generate Input POJO if needed (multiple input fields)
        if self.should_generate_input_pojo(block):
            input_pojo_content = self.generate_input_pojo(block, package)
            input_pojo_name = self.to_pascal_case(block.name) + "Input"
            self.result.add_file(
                java_src_path / f"{input_pojo_name}.java",
                input_pojo_content,
                "java"
            )

        # Generate Output POJO if needed (multiple output fields)
        if self.should_generate_output_pojo(block):
            output_pojo_content = self.generate_output_pojo(block, package)
            output_pojo_name = self.to_pascal_case(block.name) + "Output"
            self.result.add_file(
                java_src_path / f"{output_pojo_name}.java",
                output_pojo_content,
                "java"
            )

        # Generate ProcessFunction class
        content = self.generate_process_function_class(
            block, package, input_type, output_type
        )

        self.result.add_file(
            java_src_path / f"{class_name}.java",
            content,
            "java"
        )

    def _get_input_type(self, transform: ast.TransformDef) -> str:
        """Get input type for a transform."""
        if transform.input:
            if transform.input.is_single and transform.input.single_type:
                return self._field_type_to_java(transform.input.single_type)
            # For transforms with multiple input fields, use Object for now
            # TODO: Generate Input POJO classes in future
        return "Object"

    def _get_output_type(self, transform: ast.TransformDef) -> str:
        """Get output type for a transform."""
        if transform.output:
            if transform.output.is_single and transform.output.single_type:
                return self._field_type_to_java(transform.output.single_type)
            # For transforms with multiple output fields, use Object for now
            # TODO: Generate Output POJO classes in future
        return "Object"

    def _get_block_input_type(self, block: ast.TransformBlockDef) -> str:
        """Get input type for a transform block."""
        if block.input and block.input.fields:
            # For blocks with multiple input fields, typically a combined type
            field_names = [f.name for f in block.input.fields]
            if len(field_names) == 1:
                return self._field_type_to_java(block.input.fields[0].field_type)
            return self.to_java_class_name(block.name) + "Input"
        return "Object"

    def _get_block_output_type(self, block: ast.TransformBlockDef) -> str:
        """Get output type for a transform block."""
        if block.output and block.output.fields:
            if len(block.output.fields) == 1:
                return self._field_type_to_java(block.output.fields[0].field_type)
            return self.to_java_class_name(block.name) + "Output"
        return "Object"

    def _field_type_to_java(self, field_type: ast.FieldType) -> str:
        """Convert field type to Java type string."""
        if not field_type:
            return "Object"

        base_type = field_type.base_type
        if isinstance(base_type, ast.BaseType):
            return self.get_java_type(base_type.value)

        # Custom type (reference to schema)
        if isinstance(base_type, str):
            return self.to_java_class_name(base_type)

        return "Object"

    def _collect_all_imports(
        self,
        transform: ast.TransformDef | ast.TransformBlockDef
    ) -> Set[str]:
        """Collect all imports needed for a transform."""
        imports = set()

        imports.update(self.get_expression_imports())

        if isinstance(transform, ast.TransformDef):
            if transform.validate_input or transform.validate_output:
                imports.update(self.get_validation_imports())
                # Add structured validation imports if needed
                if self.has_structured_validation(
                    transform.validate_input,
                    transform.validate_output
                ):
                    imports.update(self.get_structured_validation_imports())
            if transform.cache:
                imports.update(self.get_cache_imports())
            if transform.on_error:
                imports.update(self.get_error_imports())
                # Add side output imports if emit_to is used
                if any(action.emit_to for action in transform.on_error.actions):
                    imports.update(self.get_side_output_imports())

        elif isinstance(transform, ast.TransformBlockDef):
            imports.update(self.get_mapping_imports())
            if transform.validate_input or transform.validate_output:
                imports.update(self.get_validation_imports())
                # Add structured validation imports if needed
                if self.has_structured_validation(
                    transform.validate_input,
                    transform.validate_output
                ):
                    imports.update(self.get_structured_validation_imports())
            if transform.invariant:
                imports.update(self.get_validation_imports())
            if transform.on_error:
                imports.update(self.get_error_imports())
                # Add side output imports if emit_to is used
                if any(action.emit_to for action in transform.on_error.actions):
                    imports.update(self.get_side_output_imports())
            # Add compose imports if compose block is present
            if transform.compose:
                imports.update(self.get_compose_imports())
            # Add on_change imports if on_change block is present
            if transform.on_change:
                imports.update(self.get_onchange_imports())

        return imports
