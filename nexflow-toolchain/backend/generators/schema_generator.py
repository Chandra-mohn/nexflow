"""
Schema Generator Module

Orchestrates Java code generation from L2 Schema DSL definitions.
Uses mixin classes for modular generation of POJOs, Builders, and PII helpers.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L2 generates: POJOs, builders, validators
L2 NEVER generates: Processing logic, business rules

Generated POJOs must:
- Compile independently
- Include all fields with correct Java types
- Be complete and production-ready
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import List, Optional, Set

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult
from backend.generators.voltage import VoltageProfilesConfig
from backend.generators.schema.pojo_generator import PojoGeneratorMixin
from backend.generators.schema.builder_generator import BuilderGeneratorMixin
from backend.generators.schema.pii_helper_generator import PiiHelperGeneratorMixin
from backend.generators.schema.streaming_generator import StreamingGeneratorMixin
from backend.generators.schema.migration_generator import MigrationGeneratorMixin
from backend.generators.schema.statemachine_generator import StateMachineGeneratorMixin
from backend.generators.schema.parameters_generator import ParametersGeneratorMixin
from backend.generators.schema.entries_generator import EntriesGeneratorMixin
from backend.generators.schema.rule_generator import RuleGeneratorMixin
from backend.generators.schema.computed_generator import ComputedGeneratorMixin


class SchemaGenerator(
    PojoGeneratorMixin,
    BuilderGeneratorMixin,
    PiiHelperGeneratorMixin,
    StreamingGeneratorMixin,
    MigrationGeneratorMixin,
    StateMachineGeneratorMixin,
    ParametersGeneratorMixin,
    EntriesGeneratorMixin,
    RuleGeneratorMixin,
    ComputedGeneratorMixin,
    BaseGenerator
):
    """
    Generator for L2 Schema DSL.

    Generates:
    - Java POJO classes with getters/setters
    - Builder pattern for immutable construction
    - Voltage SDK encryption/decryption methods for PII fields
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        self.voltage_profiles = VoltageProfilesConfig(config.voltage_profiles_path)
        self._imports: Set[str] = set()

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate Java code from Schema AST."""
        for schema in program.schemas:
            self._generate_schema(schema)
        return self.result

    def _generate_schema(self, schema: ast.SchemaDefinition) -> None:
        """Generate all files for a single schema definition."""
        class_name = self.to_java_class_name(schema.name)
        package = f"{self.config.package_prefix}.schema"
        java_src_path = Path("src/main/java") / self.get_package_path(package)

        # Generate main POJO class
        pojo_content = self.generate_pojo(schema, class_name, package)
        self.result.add_file(java_src_path / f"{class_name}.java", pojo_content, "java")

        # Generate builder class
        builder_content = self.generate_builder(schema, class_name, package)
        self.result.add_file(java_src_path / f"{class_name}Builder.java", builder_content, "java")

        # Generate Voltage helper if schema has PII fields
        if self._has_pii_fields(schema):
            voltage_content = self.generate_pii_helper(schema, class_name, package)
            self.result.add_file(java_src_path / f"{class_name}PiiHelper.java", voltage_content, "java")

        # Generate Migration helper if schema has migration or version block
        if schema.migration or schema.version:
            migration_content = self._generate_migration_class(schema, class_name, package)
            if migration_content:
                self.result.add_file(java_src_path / f"{class_name}Migration.java", migration_content, "java")

        # Generate State Machine helper if schema has state_machine block
        if schema.state_machine:
            statemachine_content = self._generate_state_machine_class(schema, class_name, package)
            if statemachine_content:
                self.result.add_file(java_src_path / f"{class_name}StateMachine.java", statemachine_content, "java")

        # Generate Parameters helper if schema has parameters block (operational_parameters pattern)
        if schema.parameters:
            parameters_content = self._generate_parameters_class(schema, class_name, package)
            if parameters_content:
                self.result.add_file(java_src_path / f"{class_name}Parameters.java", parameters_content, "java")

        # Generate Entries helper if schema has entries block (reference_data pattern)
        if schema.entries:
            entries_content = self._generate_entries_class(schema, class_name, package)
            if entries_content:
                self.result.add_file(java_src_path / f"{class_name}Entries.java", entries_content, "java")

        # Generate Rules helper if schema has rules block (business_logic pattern)
        if schema.rules:
            rules_content = self._generate_rules_class(schema, class_name, package)
            if rules_content:
                self.result.add_file(java_src_path / f"{class_name}Rules.java", rules_content, "java")

    # =========================================================================
    # Field Utilities (shared by mixins)
    # =========================================================================

    def _collect_all_fields(self, schema: ast.SchemaDefinition) -> List[ast.FieldDecl]:
        """Collect all fields from identity and fields blocks, deduplicating by name."""
        seen_names = set()
        all_fields = []

        # Identity fields take precedence
        if schema.identity:
            for field in schema.identity.fields:
                if field.name not in seen_names:
                    seen_names.add(field.name)
                    all_fields.append(field)

        # Then add fields from fields block (skip duplicates)
        if schema.fields:
            for field in schema.fields.fields:
                if field.name not in seen_names:
                    seen_names.add(field.name)
                    all_fields.append(field)

        return all_fields

    def _get_field_java_type(self, field_type: ast.FieldType) -> str:
        """Map Nexflow field type to Java type."""
        if field_type.base_type:
            return self.get_java_type(field_type.base_type.value)
        if field_type.collection_type:
            coll = field_type.collection_type
            # collection_kind is a string: 'list', 'set', 'map'
            if coll.collection_kind == 'list':
                element_type = self._get_field_java_type(coll.element_type)
                return f"List<{element_type}>"
            elif coll.collection_kind == 'set':
                element_type = self._get_field_java_type(coll.element_type)
                return f"Set<{element_type}>"
            elif coll.collection_kind == 'map':
                key_type = self._get_field_java_type(coll.key_type)
                value_type = self._get_field_java_type(coll.element_type)
                return f"Map<{key_type}, {value_type}>"
        if field_type.custom_type:
            return self.to_java_class_name(field_type.custom_type)
        return "Object"

    def _get_field_imports(self, field_type: ast.FieldType) -> Set[str]:
        """Get required imports for a field type."""
        imports = set()
        if field_type.base_type:
            imports.update(self.get_java_imports_for_type(field_type.base_type.value))
        if field_type.collection_type:
            coll = field_type.collection_type
            # collection_kind is a string: 'list', 'set', 'map'
            if coll.collection_kind == 'list':
                imports.add('java.util.List')
            elif coll.collection_kind == 'set':
                imports.add('java.util.Set')
            elif coll.collection_kind == 'map':
                imports.add('java.util.Map')
            imports.update(self._get_field_imports(coll.element_type))
            if coll.key_type:
                imports.update(self._get_field_imports(coll.key_type))
        return imports

    def _get_pii_profile(self, field_decl: ast.FieldDecl) -> Optional[str]:
        """Get PII profile name if field is marked as PII."""
        for qualifier in field_decl.qualifiers:
            if qualifier.qualifier_type == ast.FieldQualifierType.PII:
                return qualifier.pii_profile or 'full'
        return None

    def _has_pii_fields(self, schema: ast.SchemaDefinition) -> bool:
        """Check if schema has any PII fields."""
        return any(self._get_pii_profile(f) for f in self._collect_all_fields(schema))
