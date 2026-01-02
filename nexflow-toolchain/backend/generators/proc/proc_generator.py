# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Proc Generator Module

Main generator class for L1 Process DSL -> Apache Flink Java code.
Orchestrates mixin classes for modular generation.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 is the "RAILROAD" - it orchestrates data flow, NOT business logic.

L1 generates: Pipeline DAG, operator wiring, source/sink connections
L1 NEVER generates: Business logic, transformation code, rule evaluation
─────────────────────────────────────────────────────────────────────

L5 INTEGRATION:
When an InfraConfig is provided, the generator uses BindingResolver to:
- Resolve logical stream names to physical Kafka topics
- Use configured broker servers, security settings
- Generate MongoDB async sinks when persist clause is present
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import Optional

from backend.ast import proc_ast as ast
from backend.ast.infra import InfraConfig
from backend.generators.base import BaseGenerator, GenerationResult, GeneratorConfig
from backend.generators.infra import BindingResolver
from backend.generators.proc.job_generator import JobGeneratorMixin
from backend.generators.proc.metrics_generator import MetricsGeneratorMixin
from backend.generators.proc.mongo_sink_generator import MongoSinkGeneratorMixin
from backend.generators.proc.operator_generator import OperatorGeneratorMixin
from backend.generators.proc.phase_generator import PhaseGeneratorMixin
from backend.generators.proc.proc_process_function import ProcProcessFunctionMixin
from backend.generators.proc.resilience_generator import ResilienceGeneratorMixin
from backend.generators.proc.sink_generator import SinkGeneratorMixin
from backend.generators.proc.source_generator import SourceGeneratorMixin
from backend.generators.proc.state_context_generator import StateContextGeneratorMixin
from backend.generators.proc.state_generator import StateGeneratorMixin
from backend.generators.proc.window_generator import WindowGeneratorMixin
from backend.generators.scaffold_generator import ScaffoldGenerator


class ProcGenerator(
    SourceGeneratorMixin,
    OperatorGeneratorMixin,
    WindowGeneratorMixin,
    SinkGeneratorMixin,
    StateGeneratorMixin,
    StateContextGeneratorMixin,
    ResilienceGeneratorMixin,
    JobGeneratorMixin,
    ProcProcessFunctionMixin,
    MongoSinkGeneratorMixin,
    MetricsGeneratorMixin,
    PhaseGeneratorMixin,
    BaseGenerator,
):
    """
    Generator for L1 Process DSL.

    Generates Apache Flink streaming jobs:
    - Main job class with StreamExecutionEnvironment
    - Kafka/Redis/StateStore/MongoDB/Scheduler source configurations
    - Processing operators (transform, enrich, route, validate, evaluate, lookup, parallel)
    - Windowing and aggregation
    - State management with TTL
    - Checkpointing and error handling
    - MongoDB async sinks (L5 integration)
    - Flink metrics (counter, gauge, histogram, meter)
    - Business date and phase-based execution (EOD markers)
    """

    def __init__(
        self, config: GeneratorConfig, infra_config: Optional[InfraConfig] = None
    ):
        super().__init__(config)
        self._current_schema_class = "Object"
        self._infra_config = infra_config
        self._binding_resolver = BindingResolver(infra_config)

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate Flink code from Process AST."""
        for process in program.processes:
            self._generate_process(process)

        # Generate scaffold classes (L3/L4 stubs)
        scaffold_generator = ScaffoldGenerator(self.config)
        scaffold_result = scaffold_generator.generate(program)

        # Merge scaffold files into our result
        for gen_file in scaffold_result.files:
            self.result.add_file(gen_file.path, gen_file.content, gen_file.file_type)

        return self.result

    def _generate_process(self, process: ast.ProcessDefinition) -> None:
        """Generate all files for a single process definition."""
        class_name = self.to_java_class_name(process.name)
        package = f"{self.config.package_prefix}.proc"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Generate main job class
        job_content = self.generate_job_class(process, package)
        self.result.add_file(
            java_src_path / f"{class_name}Job.java", job_content, "java"
        )

        # Generate ProcessFunction if there's complex processing
        if self._needs_process_function(process):
            process_func_content = self._generate_process_function(process, package)
            self.result.add_file(
                java_src_path / f"{class_name}ProcessFunction.java",
                process_func_content,
                "java",
            )

        # Generate ProcessContext if there's state (L1 State Accessors)
        if process.state and (process.state.locals or process.state.buffers):
            context_content = self.generate_process_context(process, package)
            self.result.add_file(
                java_src_path / f"{class_name}Context.java", context_content, "java"
            )

    def _needs_process_function(self, process: ast.ProcessDefinition) -> bool:
        """Check if process needs a custom ProcessFunction."""
        if process.state and (process.state.locals or process.state.buffers):
            return True
        if process.resilience and process.resilience.error:
            return True
        if len(process.emits) > 1:
            return True
        return False

    def _get_input_type(self, process: ast.ProcessDefinition) -> str:
        """Get the input type for the process."""
        # process.receives is direct list
        if process.receives:
            receive = process.receives[0]
            if receive.schema and receive.schema.schema_name:
                return self.to_java_class_name(receive.schema.schema_name)
        return "Object"

    def _get_output_type(self, process: ast.ProcessDefinition) -> str:
        """Get the output type for the process."""
        # process.emits is direct list
        if process.emits:
            for emit in process.emits:
                if isinstance(emit, ast.EmitDecl) and emit.schema:
                    return self.to_java_class_name(emit.schema.schema_name)
        return "Object"
