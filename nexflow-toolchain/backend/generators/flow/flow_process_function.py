# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Flow Process Function Mixin

Generates ProcessFunction implementations for complex processing logic.
"""

from typing import Set

from backend.ast import proc_ast as ast
from backend.generators.base import BaseGenerator


class FlowProcessFunctionMixin:
    """Mixin providing ProcessFunction generation for complex processes."""

    def _generate_process_function(self: BaseGenerator,
                                    process: ast.ProcessDefinition,
                                    package: str) -> str:
        """Generate a ProcessFunction for complex processing logic."""
        class_name = self.to_java_class_name(process.name)
        input_type = self._get_input_type(process)
        output_type = self._get_output_type(process)

        # Collect all imports
        imports = self._collect_process_function_imports(process)

        lines = [
            self.generate_java_header(f"{class_name}ProcessFunction",
                                      f"ProcessFunction for {process.name}"),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name}ProcessFunction",
            f"        extends KeyedProcessFunction<String, {input_type}, {output_type}> {{",
            "",
            "    private static final long serialVersionUID = 1L;",
            "",
        ]

        # Add state declarations
        if process.state:
            lines.append(self.generate_state_code(process))
            lines.append("")

        # Add processElement method
        lines.append(self._generate_process_element_method(process, input_type, output_type))
        lines.append("")

        # Add helper methods based on what's used
        lines.append(self._generate_helper_methods(process, input_type, output_type))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_helper_methods(self: BaseGenerator,
                                  process: ast.ProcessDefinition,
                                  input_type: str, output_type: str) -> str:
        """Generate helper methods needed by processElement."""
        methods = []

        # Check which helpers are needed
        has_enrich = False
        has_transform = False
        has_route = False

        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    has_enrich = True
                elif isinstance(op, ast.TransformDecl):
                    has_transform = True
                elif isinstance(op, ast.RouteDecl):
                    has_route = True

        # Generate enrichSync helper if needed
        if has_enrich:
            methods.append(f'''    /**
     * Synchronous enrichment helper for ProcessFunction context.
     */
    private {output_type} enrichSync({input_type} input) {{
        {output_type} enriched = new {output_type}();
        return enriched;
    }}''')

        # Generate transform helper if needed
        if has_transform:
            methods.append(f'''    /**
     * Transform helper for applying field transformations.
     */
    private Map<String, Object> transform(Object input) {{
        Map<String, Object> result = new HashMap<>();
        result.put("_original", input);
        return result;
    }}''')

        # Generate route evaluation helper if needed
        if has_route:
            methods.append(f'''    /**
     * Route evaluation helper for determining routing decision.
     */
    private String evaluateRoute(Object input) {{
        return "approve";
    }}''')

        # Generate createOutput helper if output type differs
        if output_type != input_type and output_type != f"Enriched{input_type}":
            methods.append(f'''    /**
     * Create output record from processed data.
     */
    @SuppressWarnings("unchecked")
    private {output_type} createOutput(Object processed) {{
        if (processed instanceof {output_type}) {{
            return ({output_type}) processed;
        }}
        throw new RuntimeException("Cannot convert " + processed.getClass() + " to {output_type}");
    }}''')

        # Generate handleError if resilience is configured
        if process.resilience and process.resilience.error:
            error_handlers = []
            for handler in process.resilience.error.handlers:
                action_type = handler.action.action_type.value if handler.action else "skip"
                error_handlers.append(f"        // {handler.error_type.value}: {action_type}")

            methods.append(f'''    /**
     * Error handling based on resilience configuration.
     */
    private void handleError(Exception e, {input_type} value, Context ctx) {{
        // Error handling strategies:
{chr(10).join(error_handlers)}

        String errorType = e.getClass().getSimpleName();
        System.err.println("Error processing record: " + errorType + " - " + e.getMessage());
    }}''')

        return '\n\n'.join(methods)

    def _generate_process_element_method(self: BaseGenerator,
                                         process: ast.ProcessDefinition,
                                         input_type: str, output_type: str) -> str:
        """Generate processElement method with complete implementation."""
        lines = [
            "    @Override",
            f"    public void processElement({input_type} value, Context ctx, Collector<{output_type}> out)",
            "            throws Exception {",
            "        try {",
            "            // Process the record through the pipeline",
        ]

        # Track current variable for chaining
        current_var = "value"
        current_type = input_type
        var_counter = 0

        # Add processing logic based on operators
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    var_counter += 1
                    new_var = f"enriched{var_counter}"
                    lines.append(f"")
                    lines.append(f"            // Enrich from: {op.lookup_name}")
                    lines.append(f"            Enriched{input_type} {new_var} = enrichSync({current_var});")
                    current_var = new_var
                    current_type = f"Enriched{input_type}"

                elif isinstance(op, ast.TransformDecl):
                    var_counter += 1
                    new_var = f"transformed{var_counter}"
                    lines.append(f"")
                    lines.append(f"            // Apply transform: {op.transform_name}")
                    lines.append(f"            Map<String, Object> {new_var} = transform({current_var});")
                    current_var = new_var
                    current_type = "Map<String, Object>"

                elif isinstance(op, ast.RouteDecl):
                    lines.append(f"")
                    if op.rule_name:
                        lines.append(f"            // Route using: {op.rule_name}")
                    else:
                        lines.append(f"            // Route when: {op.condition}")
                    lines.append(f"            String routeDecision = evaluateRoute({current_var});")

        # Create result and emit
        lines.append(f"")
        lines.append(f"            // Create and emit result")
        if output_type == input_type:
            lines.append(f"            {output_type} result = value;")
        elif current_type == output_type:
            lines.append(f"            {output_type} result = {current_var};")
        else:
            has_enrich_in_pipeline = any(isinstance(op, ast.EnrichDecl) for op in (process.processing or []))
            if has_enrich_in_pipeline:
                lines.append(f"            {output_type} result = enrichSync(value);")
            else:
                lines.append(f"            {output_type} result = createOutput({current_var});")

        lines.extend([
            "            out.collect(result);",
            "",
            "        } catch (Exception e) {",
        ])

        # Add error handling
        if process.resilience and process.resilience.error:
            lines.append("            handleError(e, value, ctx);")
        else:
            lines.append("            throw e;")

        lines.extend([
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _collect_process_function_imports(self: BaseGenerator,
                                           process: ast.ProcessDefinition) -> Set[str]:
        """Collect all imports needed for ProcessFunction."""
        imports = {
            'org.apache.flink.streaming.api.functions.KeyedProcessFunction',
            'org.apache.flink.util.Collector',
            'org.apache.flink.configuration.Configuration',
        }

        if process.state:
            imports.update(self.get_state_imports())

        if process.resilience:
            imports.update(self.get_resilience_imports())

        # Add schema type imports for input/output
        input_type = self._get_input_type(process)
        output_type = self._get_output_type(process)
        schema_package = f"{self.config.package_prefix}.schema"

        if input_type and input_type != "Object":
            imports.add(f"{schema_package}.{input_type}")
        if output_type and output_type != "Object" and output_type != input_type:
            imports.add(f"{schema_package}.{output_type}")

        # Check what helper methods are needed and add their imports
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    imports.add(f"{schema_package}.Enriched{input_type}")
                elif isinstance(op, ast.TransformDecl):
                    imports.add('java.util.Map')
                    imports.add('java.util.HashMap')

        return imports
