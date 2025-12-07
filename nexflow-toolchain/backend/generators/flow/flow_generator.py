"""
Flow Generator Module

Main generator class for L1 Process DSL → Apache Flink Java code.
Orchestrates mixin classes for modular generation.
"""

from pathlib import Path
from typing import Set

from backend.ast import proc_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
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
        ]

        # Add state declarations
        if process.state:
            lines.append(self.generate_state_code(process))
            lines.append("")

        # Add processElement method
        lines.append(self._generate_process_element_method(process, input_type, output_type))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_process_element_method(self, process: ast.ProcessDefinition,
                                         input_type: str, output_type: str) -> str:
        """Generate processElement method."""
        lines = [
            "    @Override",
            f"    public void processElement({input_type} value, Context ctx, Collector<{output_type}> out)",
            "            throws Exception {",
            "        try {",
            "            // Process the record",
        ]

        # Add processing logic based on operators
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.TransformDecl):
                    lines.append(f"            // Apply transform: {op.transform_name}")
                elif isinstance(op, ast.EnrichDecl):
                    lines.append(f"            // Enrich from: {op.lookup_name}")
                elif isinstance(op, ast.RouteDecl):
                    lines.append(f"            // Route using: {op.rule_name}")

        lines.extend([
            "            ",
            "            // Emit result",
            "            out.collect(result);",
            "        } catch (Exception e) {",
        ])

        # Add error handling
        if process.resilience and process.resilience.error:
            lines.append("            // Error handling")
            lines.append("            handleError(e, value, ctx);")
        else:
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
