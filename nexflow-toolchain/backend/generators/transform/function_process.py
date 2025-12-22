# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Function Process Mixin

Generates ProcessFunction implementations for block-level transforms.
"""

from typing import Set

from backend.ast import transform_ast as ast


class FunctionProcessMixin:
    """Mixin providing ProcessFunction generation for block transforms."""

    def generate_process_function_class(
        self,
        block: ast.TransformBlockDef,
        package: str,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate ProcessFunction implementation for block-level transform."""
        class_name = self.to_pascal_case(block.name) + "ProcessFunction"

        imports = self._collect_block_imports(block)

        lines = [
            self.generate_java_header(
                class_name, f"ProcessFunction for {block.name}"
            ),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name}",
            f"        extends KeyedProcessFunction<String, {input_type}, {output_type}> {{",
            "",
            "    private static final Logger LOG = LoggerFactory.getLogger("
            f"{class_name}.class);",
            "",
        ]

        # Add params declarations if defined
        if block.params:
            lines.append(self.generate_params_declarations(block.params))
            lines.append(self.generate_params_accessor_object(block.params))

        # Add lookups declarations if defined
        if block.lookups:
            lines.append(self.generate_lookups_declarations(block.lookups))
            lines.append(self.generate_lookups_object_field(block.lookups))

        # Collect all transform references (deduplicated)
        all_transform_refs = self._collect_all_transform_refs(block)
        if all_transform_refs:
            lines.append(self._generate_transform_fields(all_transform_refs))
            lines.append("")

        # Add open method for initialization (includes lookups init)
        lines.append(self._generate_open_method_with_refs(block, all_transform_refs))
        lines.append("")

        # Add processElement method
        lines.append(self._generate_process_element_method(
            block, input_type, output_type
        ))
        lines.append("")

        # Add internal transform method
        lines.append(self.generate_block_transform_method(
            block, input_type, output_type
        ))
        lines.append("")

        # Add validation methods
        if block.validate_input or block.validate_output or block.invariant:
            lines.append(self.generate_validation_code(
                block.validate_input,
                block.validate_output,
                block.invariant,
                use_map=False,
                invariant_context="result"
            ))
            lines.append(self._generate_validation_exception_class())
            lines.append(self._generate_invariant_exception_class())
            lines.append("")

        # Add error handling
        if block.on_error:
            lines.append(self.generate_error_handling_code(
                block.on_error, block.name
            ))
            lines.append(self.generate_error_record_class())
            lines.append(self.generate_exception_classes())
            lines.append("")

        # Add on_change handling
        if block.on_change:
            lines.append(self._generate_on_change_handler(block.on_change))
            lines.append("")

        # Add params accessor class and methods if defined
        if block.params:
            lines.append(self.generate_params_accessor_class(block.params))
            lines.append(self.generate_params_setters(block.params))
            lines.append(self.generate_params_validation(block.params))
            lines.append(self.generate_params_from_config(block.params))

        # Add lookups accessor class and methods if defined
        if block.lookups:
            lines.append(self.generate_lookups_accessor_class(block.lookups))
            lines.append(self.generate_lookup_accessor_methods(block.lookups))
            lines.append(self.generate_async_lookup_methods(block.lookups))

        lines.append("}")

        return '\n'.join(lines)

    def _collect_all_transform_refs(self, block: ast.TransformBlockDef) -> list:
        """Collect all transform references from use and compose blocks (deduplicated).

        Returns list of (transform_name, class_name, field_name) tuples.
        """
        seen = set()
        refs = []

        # Collect from use block
        if block.use:
            for transform_name in block.use.transforms:
                if transform_name not in seen:
                    seen.add(transform_name)
                    refs.append((
                        transform_name,
                        self.to_pascal_case(transform_name) + "Function",
                        self.to_camel_case(transform_name) + "Transform"
                    ))

        # Collect from compose block
        if block.compose:
            for ref in block.compose.refs:
                if ref.transform_name not in seen:
                    seen.add(ref.transform_name)
                    refs.append((
                        ref.transform_name,
                        self.to_pascal_case(ref.transform_name) + "Function",
                        self.to_camel_case(ref.transform_name) + "Transform"
                    ))
            # Also collect from then_refs
            for ref in block.compose.then_refs:
                if ref.transform_name not in seen:
                    seen.add(ref.transform_name)
                    refs.append((
                        ref.transform_name,
                        self.to_pascal_case(ref.transform_name) + "Function",
                        self.to_camel_case(ref.transform_name) + "Transform"
                    ))

        return refs

    def _generate_transform_fields(self, refs: list) -> str:
        """Generate field declarations for all transform references."""
        if not refs:
            return ""

        lines = ["    // Transform references"]
        for _, class_name, field_name in refs:
            lines.append(f"    private transient {class_name} {field_name};")

        return '\n'.join(lines)

    def _generate_open_method_with_refs(self, block: ast.TransformBlockDef, refs: list) -> str:
        """Generate open method that initializes all transform references."""
        lines = [
            "    @Override",
            "    public void open(Configuration parameters) throws Exception {",
        ]

        # Initialize all transform references
        for _, class_name, field_name in refs:
            lines.append(f"        {field_name} = new {class_name}();")

        # Initialize lookups if present
        if block.lookups:
            lines.append(self.generate_lookups_init(block.lookups))

        lines.append("    }")
        return '\n'.join(lines)

    def _generate_open_method(self, block: ast.TransformBlockDef) -> str:
        """Generate open method for initialization."""
        lines = [
            "    @Override",
            "    public void open(Configuration parameters) throws Exception {",
        ]

        # Initialize used transforms
        if block.use:
            for transform_name in block.use.transforms:
                class_name = self.to_pascal_case(transform_name) + "Function"
                field_name = self.to_camel_case(transform_name) + "Transform"
                lines.append(f"        {field_name} = new {class_name}();")

        # Initialize composed transforms
        if block.compose:
            compose_init = self.generate_compose_init(block.compose)
            if compose_init:
                lines.append(compose_init)

        lines.append("    }")
        return '\n'.join(lines)

    def _generate_process_element_method(
        self,
        block: ast.TransformBlockDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate processElement method."""
        lines = [
            "    @Override",
            f"    public void processElement({input_type} value, Context ctx,",
            f"            Collector<{output_type}> out) throws Exception {{",
        ]

        if block.on_error:
            lines.append("        try {")
            lines.append(f"            {output_type} result = transform(value);")
            lines.append("            out.collect(result);")
            lines.append("        } catch (Exception e) {")
            lines.append("            handleError(e, value);")
            lines.append("        }")
        else:
            lines.append(f"        {output_type} result = transform(value);")
            lines.append("        out.collect(result);")

        lines.append("    }")
        return '\n'.join(lines)

    def _generate_on_change_handler(self, on_change: ast.OnChangeBlock) -> str:
        """Generate on_change handler for reactive updates."""
        watched = ", ".join(f'"{f}"' for f in on_change.watched_fields)

        lines = [
            "    /**",
            f"     * Recalculate on change of: {', '.join(on_change.watched_fields)}",
            "     */",
            f"    private static final Set<String> WATCHED_FIELDS = Set.of({watched});",
            "",
            "    private boolean shouldRecalculate(Set<String> changedFields) {",
            "        return !Collections.disjoint(WATCHED_FIELDS, changedFields);",
            "    }",
            "",
            "    private void recalculate(Object input) {",
        ]

        for assignment in on_change.recalculate.assignments:
            target = self._generate_setter_chain(assignment.target)
            value = self.generate_expression(assignment.value)
            lines.append(f"        input.{target}({value});")

        lines.append("    }")
        return '\n'.join(lines)

    def _collect_block_imports(self, block: ast.TransformBlockDef) -> Set[str]:
        """Collect all imports needed for a transform block."""
        imports = {
            'org.apache.flink.streaming.api.functions.KeyedProcessFunction',
            'org.apache.flink.util.Collector',
            'org.apache.flink.configuration.Configuration',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }

        imports.update(self.get_expression_imports())
        imports.update(self.get_mapping_imports())

        if block.validate_input or block.validate_output or block.invariant:
            imports.update(self.get_validation_imports())

        if block.on_error:
            imports.update(self.get_error_imports())

        if block.on_change:
            imports.add('java.util.Set')
            imports.add('java.util.Collections')

        # Add compose imports (for parallel composition with CompletableFuture)
        if block.compose:
            imports.update(self.get_compose_imports())

        # Add lookups imports if lookups block is present
        if block.lookups:
            imports.update(self.get_lookups_imports())

        # Add params imports if params block is present
        if block.params:
            imports.update(self.get_params_imports())

        return imports

    def _generate_setter_chain(self, field_path: ast.FieldPath) -> str:
        """Generate setter method chain for field path."""
        parts = field_path.parts
        if len(parts) == 1:
            return self.to_setter(parts[0])
        setters = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                setters.append(self.to_getter(part))
            else:
                setters.append(self.to_setter(part))
        return ".".join(setters)
