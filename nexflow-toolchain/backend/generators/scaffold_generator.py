"""
Scaffold Generator Module

Generates dummy/template L3 and L4 classes for L1 to compile against.
These are intentionally simple implementations that can be replaced
by proper L3/L4 generated code later.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
This is a TEMPORARY measure to allow L1 to compile while L3/L4 are
being completed. The generated scaffolds are REAL, COMPILABLE code
that provides minimal but correct implementations.

NOT STUBS: These compile and run (with minimal functionality)
NOT PLACEHOLDERS: They have actual method bodies
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path

from backend.ast import proc_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
from backend.generators.common.java_utils import to_pascal_case
from backend.generators.scaffold.scaffold_operators import ScaffoldOperatorsMixin
from backend.generators.scaffold.scaffold_correlation import ScaffoldCorrelationMixin
from backend.generators.scaffold.scaffold_completion import ScaffoldCompletionMixin


class ScaffoldGenerator(
    BaseGenerator,
    ScaffoldOperatorsMixin,
    ScaffoldCorrelationMixin,
    ScaffoldCompletionMixin
):
    """
    Generator for L3/L4 scaffold classes.

    Generates minimal but compilable implementations for:
    - AsyncFunction (for enrich operators)
    - ProcessFunction/Router (for route operators)
    - AggregateFunction (for aggregate operators)
    - RoutedEvent wrapper class
    - Enriched schema wrappers
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate scaffold classes from Process AST."""
        for process in program.processes:
            self._generate_scaffolds_for_process(process)
        return self.result

    def _generate_scaffolds_for_process(self, process: ast.ProcessDefinition) -> None:
        """Generate all scaffold classes needed by a process."""
        transform_package = f"{self.config.package_prefix}.transform"
        rules_package = f"{self.config.package_prefix}.rules"
        schema_package = f"{self.config.package_prefix}.schema"
        correlation_package = f"{self.config.package_prefix}.correlation"

        transform_path = Path("src/main/java") / self.get_package_path(transform_package)
        rules_path = Path("src/main/java") / self.get_package_path(rules_package)
        schema_path = Path("src/main/java") / self.get_package_path(schema_package)
        correlation_path = Path("src/main/java") / self.get_package_path(correlation_package)

        # Track what we need to generate
        input_type = self._get_input_type(process)
        needs_routed_event = False

        # Generate processing operator scaffolds
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    self._generate_enrich_scaffold(
                        op, transform_package, transform_path, schema_package, schema_path, input_type
                    )
                elif isinstance(op, ast.TransformDecl):
                    self._generate_transform_scaffold(
                        op, transform_package, transform_path, input_type
                    )
                elif isinstance(op, ast.RouteDecl):
                    self._generate_route_scaffold(
                        op, rules_package, rules_path, input_type
                    )
                    needs_routed_event = True
                elif isinstance(op, ast.AggregateDecl):
                    self._generate_aggregate_scaffold(
                        op, transform_package, transform_path, input_type
                    )

        # Generate RoutedEvent if needed
        if needs_routed_event:
            routed_content = self._generate_routed_event(rules_package)
            self.result.add_file(rules_path / "RoutedEvent.java", routed_content, "java")

        # Generate correlation scaffolds
        if process.correlation:
            self._generate_correlation_scaffold(
                process.correlation, correlation_package, correlation_path, input_type
            )

        # Generate completion scaffolds
        if process.completion:
            self._generate_completion_scaffold(process)

    def _get_input_type(self, process: ast.ProcessDefinition) -> str:
        """Get the input type for the process."""
        if process.input and process.input.receives:
            receive = process.input.receives[0]
            if receive.schema and receive.schema.schema_name:
                return to_pascal_case(receive.schema.schema_name)
        return "Object"

    def _generate_routed_event(self, package: str) -> str:
        """Generate RoutedEvent wrapper class."""
        return f'''/**
 * RoutedEvent
 *
 * Wrapper class containing original event data and routing decision.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

public class RoutedEvent {{

    private final Object originalEvent;
    private final String decision;

    public RoutedEvent(Object originalEvent, String decision) {{
        this.originalEvent = originalEvent;
        this.decision = decision;
    }}

    public Object getOriginalEvent() {{
        return originalEvent;
    }}

    public String getDecision() {{
        return decision;
    }}

    @SuppressWarnings("unchecked")
    public <T> T getOriginalAs(Class<T> clazz) {{
        return (T) originalEvent;
    }}

    public String getKey() {{
        return originalEvent.toString();
    }}

    @Override
    public String toString() {{
        return "RoutedEvent{{decision='" + decision + "', event=" + originalEvent + "}}";
    }}
}}
'''
