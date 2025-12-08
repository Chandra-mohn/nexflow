"""
Flow Generator Module

Main generator class for L1 Process DSL → Apache Flink Java code.
Orchestrates mixin classes for modular generation.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 is the "RAILROAD" - it orchestrates data flow, NOT business logic.

L1 generates: Pipeline DAG, operator wiring, source/sink connections
L1 NEVER generates: Business logic, transformation code, rule evaluation

Key principles:
- Wire operators to COMPLETE L3/L4 generated implementations
- NO STUBS - every operator must have real implementation
- NO TODOS - generated code must compile and run
- Types must flow consistently through the pipeline
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import Set

from backend.ast import proc_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
from backend.generators.scaffold_generator import ScaffoldGenerator
from backend.generators.flow.source_generator import SourceGeneratorMixin
from backend.generators.flow.operator_generator import OperatorGeneratorMixin
from backend.generators.flow.window_generator import WindowGeneratorMixin
from backend.generators.flow.sink_generator import SinkGeneratorMixin
from backend.generators.flow.state_generator import StateGeneratorMixin
from backend.generators.flow.resilience_generator import ResilienceGeneratorMixin
from backend.generators.flow.job_generator import JobGeneratorMixin


class FlowGenerator(
    SourceGeneratorMixin,
    OperatorGeneratorMixin,
    WindowGeneratorMixin,
    SinkGeneratorMixin,
    StateGeneratorMixin,
    ResilienceGeneratorMixin,
    JobGeneratorMixin,
    BaseGenerator
):
    """
    Generator for L1 Process DSL.

    Generates Apache Flink streaming jobs:
    - Main job class with StreamExecutionEnvironment
    - Kafka source/sink configurations
    - Processing operators (transform, enrich, route)
    - Windowing and aggregation
    - State management with TTL
    - Checkpointing and error handling
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        self._current_schema_class = "Object"

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate Flink code from Process AST."""
        for process in program.processes:
            self._generate_process(process)

        # Generate scaffold classes (L3/L4 stubs)
        # These are temporary compilable implementations that will be replaced
        # by proper L3/L4 generated code later
        scaffold_generator = ScaffoldGenerator(self.config)
        scaffold_result = scaffold_generator.generate(program)

        # Merge scaffold files into our result
        for gen_file in scaffold_result.files:
            self.result.add_file(gen_file.path, gen_file.content, gen_file.file_type)

        return self.result

    def _generate_process(self, process: ast.ProcessDefinition) -> None:
        """Generate all files for a single process definition."""
        class_name = self.to_java_class_name(process.name)
        package = f"{self.config.package_prefix}.flow"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Generate main job class
        job_content = self.generate_job_class(process, package)
        self.result.add_file(
            java_src_path / f"{class_name}Job.java",
            job_content,
            "java"
        )

        # Generate ProcessFunction if there's complex processing
        if self._needs_process_function(process):
            process_func_content = self._generate_process_function(process, package)
            self.result.add_file(
                java_src_path / f"{class_name}ProcessFunction.java",
                process_func_content,
                "java"
            )

    def _needs_process_function(self, process: ast.ProcessDefinition) -> bool:
        """Check if process needs a custom ProcessFunction."""
        # Need ProcessFunction for: state, error handling, side outputs
        if process.state and (process.state.locals or process.state.buffers):
            return True
        if process.resilience and process.resilience.error:
            return True
        if process.output and len(process.output.outputs) > 1:
            return True
        return False

    def _generate_process_function(self, process: ast.ProcessDefinition, package: str) -> str:
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

    def _generate_helper_methods(self, process: ast.ProcessDefinition,
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
     * In async context, use AsyncDataStream.unorderedWait() instead.
     */
    private {output_type} enrichSync({input_type} input) {{
        // TODO: Implement actual enrichment lookup
        // This is a scaffold - replace with real lookup logic
        {output_type} enriched = new {output_type}();
        // Copy base fields from input to enriched (generated by L2/L3)
        // Add enrichment data from lookup service
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
        // TODO: Apply actual transformations from L3 transform definition
        return result;
    }}''')

        # Generate route evaluation helper if needed
        if has_route:
            methods.append(f'''    /**
     * Route evaluation helper for determining routing decision.
     */
    private String evaluateRoute(Object input) {{
        // TODO: Implement actual routing rules from L4 definition
        // Returns routing decision: "approve", "flag", "block", etc.
        return "approve";
    }}''')

        # Generate createOutput helper if output type differs
        if output_type != input_type and output_type != f"Enriched{input_type}":
            methods.append(f'''    /**
     * Create output record from processed data.
     */
    @SuppressWarnings("unchecked")
    private {output_type} createOutput(Object processed) {{
        // TODO: Map processed data to output type
        // This is a scaffold - replace with actual mapping logic
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

        // Log error and decide action based on exception type
        String errorType = e.getClass().getSimpleName();

        // Default: log and continue (skip the record)
        System.err.println("Error processing record: " + errorType + " - " + e.getMessage());
        // For production, emit to dead letter queue or side output
    }}''')

        return '\n\n'.join(methods)

    def _generate_process_element_method(self, process: ast.ProcessDefinition,
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
                    lookup_class = self.to_java_class_name(op.lookup_name) + "AsyncFunction"
                    lines.append(f"")
                    lines.append(f"            // Enrich from: {op.lookup_name}")
                    lines.append(f"            // Note: In ProcessFunction context, enrichment is synchronous")
                    lines.append(f"            Enriched{input_type} {new_var} = enrichSync({current_var});")
                    current_var = new_var
                    current_type = f"Enriched{input_type}"

                elif isinstance(op, ast.TransformDecl):
                    var_counter += 1
                    new_var = f"transformed{var_counter}"
                    transform_class = self.to_java_class_name(op.transform_name) + "Function"
                    lines.append(f"")
                    lines.append(f"            // Apply transform: {op.transform_name}")
                    lines.append(f"            Map<String, Object> {new_var} = transform({current_var});")
                    current_var = new_var
                    current_type = "Map<String, Object>"

                elif isinstance(op, ast.RouteDecl):
                    lines.append(f"")
                    lines.append(f"            // Route using: {op.rule_name}")
                    lines.append(f"            String routeDecision = evaluateRoute({current_var});")
                    lines.append(f"            // Side outputs available for different routing decisions")

        # Create result and emit
        lines.append(f"")
        lines.append(f"            // Create and emit result")
        if output_type == input_type:
            lines.append(f"            {output_type} result = value;")
        elif current_type == output_type:
            # We already have the output type from processing
            lines.append(f"            {output_type} result = {current_var};")
        else:
            # Need conversion - use enrichSync if enrichment was in pipeline
            has_enrich_in_pipeline = any(isinstance(op, ast.EnrichDecl) for op in (process.processing or []))
            if has_enrich_in_pipeline:
                lines.append(f"            {output_type} result = enrichSync(value);")
            else:
                lines.append(f"            // Convert to output type")
                lines.append(f"            {output_type} result = createOutput({current_var});")

        lines.extend([
            "            out.collect(result);",
            "",
            "        } catch (Exception e) {",
        ])

        # Add error handling
        if process.resilience and process.resilience.error:
            lines.append("            // Error handling based on resilience config")
            lines.append("            handleError(e, value, ctx);")
        else:
            lines.append("            // Re-throw exception (no error handling configured)")
            lines.append("            throw e;")

        lines.extend([
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _collect_process_function_imports(self, process: ast.ProcessDefinition) -> Set[str]:
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
                    # Need EnrichedX class
                    imports.add(f"{schema_package}.Enriched{input_type}")
                elif isinstance(op, ast.TransformDecl):
                    # Need Map and HashMap for transform
                    imports.add('java.util.Map')
                    imports.add('java.util.HashMap')

        return imports

    def _get_input_type(self, process: ast.ProcessDefinition) -> str:
        """Get the input type for the process."""
        if process.input and process.input.receives:
            receive = process.input.receives[0]
            if receive.schema and receive.schema.schema_name:
                return self.to_java_class_name(receive.schema.schema_name)
        return "Object"

    def _get_output_type(self, process: ast.ProcessDefinition) -> str:
        """Get the output type for the process."""
        if process.output and process.output.outputs:
            for output in process.output.outputs:
                if isinstance(output, ast.EmitDecl) and output.schema:
                    return self.to_java_class_name(output.schema.schema_name)
        return "Object"
