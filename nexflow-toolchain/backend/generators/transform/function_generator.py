"""
Function Generator Mixin

Generates Java function class structure for L3 Transforms.
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class FunctionGeneratorMixin:
    """
    Mixin for generating Java transform function classes.

    Generates:
    - MapFunction implementations for simple transforms
    - ProcessFunction implementations for complex transforms
    - Flink UDF wrappers
    """

    def generate_map_function_class(
        self,
        transform: ast.TransformDef,
        package: str,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate MapFunction implementation for a simple transform."""
        class_name = self._to_pascal_case(transform.name) + "Function"

        imports = self._collect_transform_imports(transform)

        # Map Object types to Map<String, Object> for dynamic access
        actual_input_type = "Map<String, Object>" if input_type == "Object" else input_type
        actual_output_type = "Map<String, Object>" if output_type == "Object" else output_type

        # Use RichMapFunction if caching is needed (requires open() and getRuntimeContext())
        if transform.cache:
            base_class = f"extends RichMapFunction<{actual_input_type}, {actual_output_type}>"
        else:
            base_class = f"implements MapFunction<{actual_input_type}, {actual_output_type}>"

        lines = [
            self.generate_java_header(class_name, f"MapFunction for {transform.name}"),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name} {base_class} {{",
            "",
            "    private static final Logger LOG = LoggerFactory.getLogger("
            f"{class_name}.class);",
            "",
        ]

        # Add pure annotation if applicable
        if transform.pure:
            lines.insert(-1, "    // Pure function - no side effects")

        # Add cache if defined
        if transform.cache:
            lines.append(self.generate_cache_code(transform.cache, transform.name))
            lines.append("")

        # Add map method
        lines.extend([
            "    @Override",
            f"    public {actual_output_type} map({actual_input_type} value) throws Exception {{",
        ])

        if transform.cache:
            lines.append("        return transformWithCache(value);")
        else:
            lines.append("        return transform(value);")

        lines.extend([
            "    }",
            "",
        ])

        # Add internal transform method
        lines.append(self.generate_transform_function_method(
            transform, input_type, output_type
        ))
        lines.append("")

        # Add validation methods if needed
        if transform.validate_input or transform.validate_output:
            lines.append(self.generate_validation_code(
                transform.validate_input,
                transform.validate_output,
                None
            ))
            lines.append(self._generate_validation_exception_class())
            lines.append("")

        # Add cached wrapper if cache is defined
        if transform.cache:
            lines.append(self.generate_cached_transform_wrapper(
                transform.name, transform.cache, input_type, output_type
            ))
            lines.append("")

        # Add error handling if defined
        if transform.on_error:
            lines.append(self.generate_error_handling_code(
                transform.on_error, transform.name
            ))
            lines.append(self.generate_exception_classes())
            lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def generate_process_function_class(
        self,
        block: ast.TransformBlockDef,
        package: str,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate ProcessFunction implementation for block-level transform."""
        class_name = self._to_pascal_case(block.name) + "ProcessFunction"

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

        # Add used transforms references
        if block.use:
            lines.append(self._generate_use_block(block.use))
            lines.append("")

        # Add open method for initialization
        lines.append(self._generate_open_method(block))
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
                block.invariant
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

        lines.append("}")

        return '\n'.join(lines)

    def _generate_use_block(self, use: ast.UseBlock) -> str:
        """Generate field references for used transforms."""
        lines = ["    // Referenced transforms"]
        for transform_name in use.transforms:
            class_name = self._to_pascal_case(transform_name) + "Function"
            field_name = self._to_camel_case(transform_name) + "Transform"
            lines.append(
                f"    private transient {class_name} {field_name};"
            )
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
                class_name = self._to_pascal_case(transform_name) + "Function"
                field_name = self._to_camel_case(transform_name) + "Transform"
                lines.append(f"        {field_name} = new {class_name}();")

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
            "    private void recalculate(Object context) {",
        ]

        for assignment in on_change.recalculate.assignments:
            target = self._generate_setter_chain(assignment.target)
            value = self.generate_expression(assignment.value)
            lines.append(f"        context.{target}({value});")

        lines.append("    }")
        return '\n'.join(lines)

    def _collect_transform_imports(self, transform: ast.TransformDef) -> Set[str]:
        """Collect all imports needed for a transform."""
        imports = {
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }

        # Use RichMapFunction if caching is needed, otherwise use MapFunction
        if transform.cache:
            imports.add('org.apache.flink.api.common.functions.RichMapFunction')
        else:
            imports.add('org.apache.flink.api.common.functions.MapFunction')

        imports.update(self.get_expression_imports())

        # Add Map/HashMap imports for simple transforms with Object types
        # (simple transforms without explicit schema types use Map<String, Object>)
        imports.add('java.util.Map')
        imports.add('java.util.HashMap')

        if transform.validate_input or transform.validate_output:
            imports.update(self.get_validation_imports())

        if transform.cache:
            imports.update(self.get_cache_imports())

        if transform.on_error:
            imports.update(self.get_error_imports())

        return imports

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

        return imports

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _generate_setter_chain(self, field_path: ast.FieldPath) -> str:
        """Generate setter method chain for field path."""
        parts = field_path.parts
        if len(parts) == 1:
            return self._to_setter(parts[0])
        setters = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                setters.append(self._to_getter(part))
            else:
                setters.append(self._to_setter(part))
        return ".".join(setters)

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _to_setter(self, field_name: str) -> str:
        """Convert field name to setter method name."""
        camel = self._to_camel_case(field_name)
        return f"set{camel[0].upper()}{camel[1:]}"

    def get_function_imports(self) -> Set[str]:
        """Get base imports for function generation."""
        return {
            'org.apache.flink.api.common.functions.MapFunction',
            'org.apache.flink.streaming.api.functions.KeyedProcessFunction',
            'org.apache.flink.util.Collector',
            'org.apache.flink.configuration.Configuration',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }
