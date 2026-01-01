# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Function Generator Mixin

Generates Java function class structure for L3 Transforms.
"""

from typing import Set

from backend.ast import transform_ast as ast
from backend.generators.transform.function_process import FunctionProcessMixin


class FunctionGeneratorMixin(FunctionProcessMixin):
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
        class_name = self.to_pascal_case(transform.name) + "Function"

        imports = self._collect_transform_imports(transform)

        # Map Object types to Map<String, Object> for dynamic access
        actual_input_type = "Map<String, Object>" if input_type == "Object" else input_type
        actual_output_type = "Map<String, Object>" if output_type == "Object" else output_type

        # Use RichMapFunction if caching is needed
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
        ]

        # Add pure annotation if applicable
        if transform.pure:
            lines.append("    // Pure function - no side effects")

        # Add idempotent annotation if applicable
        if transform.idempotent:
            lines.append("    // Idempotent function - repeated calls produce same result")

        lines.append("")

        # Add params declarations if defined
        if transform.params:
            lines.append(self.generate_params_declarations(transform.params))
            lines.append(self.generate_params_accessor_object(transform.params))

        # Add lookups declarations if defined
        if transform.lookups:
            lines.append(self.generate_lookups_declarations(transform.lookups))
            lines.append(self.generate_lookups_object_field(transform.lookups))

        # Add cache if defined
        if transform.cache:
            lines.append(self.generate_cache_code(transform.cache, transform.name))
            lines.append("")

        # Add map method
        lines.extend([
            "    @Override",
            f"    public {actual_output_type} map({actual_input_type} input) throws Exception {{",
        ])

        if transform.cache:
            lines.append("        return transformWithCache(input);")
        else:
            lines.append("        return transform(input);")

        lines.extend([
            "    }",
            "",
        ])

        # Add internal transform method
        lines.append(self.generate_transform_function_method(
            transform, actual_input_type, actual_output_type
        ))
        lines.append("")

        # Add validation methods if needed
        if transform.validate_input or transform.validate_output:
            lines.append(self.generate_validation_code(
                transform.validate_input,
                transform.validate_output,
                None,
                use_map=True
            ))
            lines.append(self._generate_validation_exception_class())
            lines.append("")

        # Add cached wrapper if cache is defined
        if transform.cache:
            lines.append(self.generate_cached_transform_wrapper(
                transform.name, transform.cache, actual_input_type, actual_output_type
            ))
            lines.append("")

        # Add error handling if defined
        if transform.on_error:
            lines.append(self.generate_error_handling_code(
                transform.on_error, transform.name
            ))
            lines.append(self.generate_exception_classes())
            lines.append("")

        # Add params accessor class and methods if defined
        if transform.params:
            lines.append(self.generate_params_accessor_class(transform.params))
            lines.append(self.generate_params_setters(transform.params))
            lines.append(self.generate_params_validation(transform.params))
            lines.append(self.generate_params_from_config(transform.params))

        # Add lookups accessor class and methods if defined
        if transform.lookups:
            lines.append(self.generate_lookups_accessor_class(transform.lookups))
            lines.append(self.generate_lookup_accessor_methods(transform.lookups))
            lines.append(self.generate_async_lookup_methods(transform.lookups))

        lines.append("}")

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
        imports.add('java.util.Map')
        imports.add('java.util.HashMap')

        if transform.validate_input or transform.validate_output:
            imports.update(self.get_validation_imports())

        if transform.cache:
            imports.update(self.get_cache_imports())

        if transform.on_error:
            imports.update(self.get_error_imports())

        if transform.lookups:
            imports.update(self.get_lookups_imports())

        if transform.params:
            imports.update(self.get_params_imports())

        return imports

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
