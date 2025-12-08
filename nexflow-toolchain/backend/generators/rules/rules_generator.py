"""
Rules Generator Module

Main generator class for L4 Rules DSL → Java rule evaluators.
Orchestrates mixin classes for modular generation.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 generates: ProcessFunction, decision tables, procedural rules
L4 NEVER generates: Data structure definitions, schema types

Generated rules must:
- Return ACTUAL decision values (never null placeholders)
- Generate REAL conditions (never "if (true)")
- Compile and execute correctly
- Map all actions to executable code
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import Set

from backend.ast import rules_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
from backend.generators.rules.condition_generator import ConditionGeneratorMixin
from backend.generators.rules.action_generator import ActionGeneratorMixin
from backend.generators.rules.decision_table_generator import DecisionTableGeneratorMixin
from backend.generators.rules.procedural_generator import ProceduralGeneratorMixin


class RulesGenerator(
    ConditionGeneratorMixin,
    ActionGeneratorMixin,
    DecisionTableGeneratorMixin,
    ProceduralGeneratorMixin,
    BaseGenerator
):
    """
    Generator for L4 Rules DSL.

    Generates Java rule evaluator classes:
    - Decision table evaluators with hit policies
    - Procedural rule executors with conditionals
    - Condition matching and action execution
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate Java code from Rules AST."""
        # Generate decision tables
        for table in program.decision_tables:
            self._generate_decision_table(table)

        # Generate procedural rules
        for rule in program.procedural_rules:
            self._generate_procedural_rule(rule)

        return self.result

    def _generate_decision_table(self, table: ast.DecisionTableDef) -> None:
        """Generate files for a decision table definition."""
        class_name = self.to_java_class_name(table.name) + "Table"
        package = f"{self.config.package_prefix}.rules"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Generate decision table class
        content = self.generate_decision_table_class(table, package)

        self.result.add_file(
            java_src_path / f"{class_name}.java",
            content,
            "java"
        )

    def _generate_procedural_rule(self, rule: ast.ProceduralRuleDef) -> None:
        """Generate files for a procedural rule definition."""
        class_name = self.to_java_class_name(rule.name) + "Rule"
        package = f"{self.config.package_prefix}.rules"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Generate procedural rule class
        content = self.generate_procedural_rule_class(rule, package)

        self.result.add_file(
            java_src_path / f"{class_name}.java",
            content,
            "java"
        )

    def _collect_all_imports(self, program: ast.Program) -> Set[str]:
        """Collect all imports needed for rules generation."""
        imports = set()

        imports.update(self.get_condition_imports())
        imports.update(self.get_action_imports())

        return imports
