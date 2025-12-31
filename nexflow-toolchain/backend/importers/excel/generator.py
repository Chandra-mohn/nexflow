"""
Schema DSL generator from parsed Excel data.

Generates Nexflow .schema files from the parsed ServiceDomain model.
"""

from pathlib import Path
from typing import Optional
import logging

from .models import (
    ServiceDomain,
    Entity,
    Attribute,
    Relationship,
    EnumValue,
    EntityQualifier,
    PersistencePattern,
    RelationshipType,
    to_pascal_case,
    to_camel_case,
    to_upper_snake,
)
from .graph import DomainGraph

logger = logging.getLogger(__name__)


# Datatype mapping from Excel to Nexflow Schema DSL
DATATYPE_MAP = {
    "string": "string",
    "varchar": "string",
    "char": "string",
    "text": "string",
    "integer": "int",
    "int": "int",
    "number": "int",  # May be decimal if has precision
    "long": "long",
    "bigint": "long",
    "decimal": "decimal",
    "float": "decimal",
    "double": "decimal",
    "numeric": "decimal",
    "boolean": "boolean",
    "bool": "boolean",
    "date": "date",
    "datetime": "timestamp",
    "timestamp": "timestamp",
    "blob": "bytes",
    "binary": "bytes",
    "bytes": "bytes",
}


class SchemaGenerator:
    """Generate Schema DSL files from ServiceDomain."""

    def __init__(
        self,
        domain: ServiceDomain,
        graph: DomainGraph,
        shortcut_resolutions: Optional[dict[str, str]] = None,
    ):
        self.domain = domain
        self.graph = graph
        self.shortcut_resolutions = shortcut_resolutions or {}

    def generate_all(self, output_dir: Path, dry_run: bool = False) -> list[Path]:
        """
        Generate all schema files for the domain.

        Args:
            output_dir: Directory to write schema files
            dry_run: If True, don't write files

        Returns:
            List of generated file paths
        """
        generated_files: list[Path] = []

        # Ensure output directory exists
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "enums").mkdir(exist_ok=True)

        # Generate in topological order (children before parents)
        for entity_name in self.graph.generation_order:
            entity = self.domain.entities.get(entity_name)
            if not entity:
                continue

            # Generate entity schema
            schema_content = self.generate_entity_schema(entity)
            schema_name = entity.get_schema_name()
            schema_path = output_dir / f"{schema_name}.schema"

            if dry_run:
                logger.info(f"Would generate: {schema_path}")
                print(f"\n=== {schema_path} ===")
                print(schema_content)
            else:
                schema_path.write_text(schema_content)
                logger.info(f"Generated: {schema_path}")

            generated_files.append(schema_path)

            # Generate enum schemas for this entity
            for attr_name, enum_values in entity.enum_values.items():
                enum_content = self.generate_enum_schema(entity, attr_name, enum_values)
                enum_name = f"{schema_name}{to_pascal_case(attr_name)}"
                enum_path = output_dir / "enums" / f"{enum_name}.schema"

                if dry_run:
                    logger.info(f"Would generate: {enum_path}")
                    print(f"\n=== {enum_path} ===")
                    print(enum_content)
                else:
                    enum_path.write_text(enum_content)
                    logger.info(f"Generated: {enum_path}")

                generated_files.append(enum_path)

        # Generate domain metadata
        domain_yaml = self.generate_domain_yaml()
        domain_path = output_dir / "_domain.yaml"

        if dry_run:
            logger.info(f"Would generate: {domain_path}")
            print(f"\n=== {domain_path} ===")
            print(domain_yaml)
        else:
            domain_path.write_text(domain_yaml)

        generated_files.append(domain_path)

        return generated_files

    def generate_entity_schema(self, entity: Entity) -> str:
        """Generate schema DSL for a single entity."""
        lines: list[str] = []
        schema_name = entity.get_schema_name()

        # Schema header
        lines.append(f"schema {schema_name}")

        # Annotations
        lines.append('    @version "1.0.0"')
        lines.append(f'    @entity "{entity.entity_name}"')

        if entity.collection_name:
            lines.append(f'    @collection "{entity.collection_name}"')

        if entity.pattern != PersistencePattern.NONE:
            lines.append(f"    @pattern {entity.pattern.value}")

        if entity.qualifier != EntityQualifier.NONE:
            lines.append(f"    @qualifier {entity.qualifier.value}")

        if entity.is_managed():
            lines.append("    @managed")

        if entity.is_shortcut():
            source = self.shortcut_resolutions.get(entity.entity_name)
            if source:
                lines.append(f'    @external "{source}/{schema_name}"')
            else:
                lines.append("    @external")
                lines.append("    # WARNING: Shortcut entity - source domain unknown")
                lines.append("    # Run with --resolve-shortcuts to validate")

        if entity.comment:
            lines.append(f'    @description "{self._escape_string(entity.comment)}"')

        lines.append("")

        # For shortcut entities, don't generate fields
        if entity.is_shortcut():
            lines.append("end")
            return "\n".join(lines)

        # Generate fields
        for attr in entity.attributes:
            field_lines = self._generate_field(entity, attr)
            lines.extend(field_lines)
            lines.append("")

        # Generate composition fields from relationships
        for rel in entity.child_relationships:
            rel_lines = self._generate_relationship_field(rel)
            lines.extend(rel_lines)
            lines.append("")

        lines.append("end")

        return "\n".join(lines)

    def _generate_field(self, entity: Entity, attr: Attribute) -> list[str]:
        """Generate field definition for an attribute."""
        lines: list[str] = []

        field_name = to_camel_case(attr.name)
        field_type = self._map_datatype(attr)

        # Check if this attribute is an enum
        if attr.is_enum() and attr.name in entity.enum_values:
            schema_name = entity.get_schema_name()
            field_type = f"{schema_name}{to_pascal_case(attr.name)}"

        # Check if this is a foreign key reference
        if attr.foreign_identifier and attr.foreign_parent_entity:
            ref_entity = self.domain.entities.get(attr.foreign_parent_entity)
            if ref_entity:
                # Keep as original type but add @foreign annotation
                pass

        # Required modifier
        required = " required" if attr.mandatory else ""

        lines.append(f"    {field_name}: {field_type}{required}")

        # Field annotations
        if attr.primary_identifier:
            lines.append("        @primary")

        if attr.foreign_identifier and attr.foreign_parent_entity:
            ref_name = to_pascal_case(attr.foreign_parent_entity)
            lines.append(f"        @foreign {ref_name}")

        if attr.json_name and attr.json_name != attr.name:
            lines.append(f'        @json "{attr.json_name}"')

        if attr.length:
            # Handle precision format like "18,2" for decimals
            if "," in attr.length:
                lines.append(f"        @precision {attr.length}")
            else:
                lines.append(f"        @length {attr.length}")

        if attr.pii_pci_indicator:
            indicator = attr.pii_pci_indicator.upper()
            if "PII" in indicator:
                lines.append("        @pii")
            if "PCI" in indicator:
                lines.append("        @pci")

        if attr.comment:
            lines.append(f'        @description "{self._escape_string(attr.comment)}"')

        return lines

    def _generate_relationship_field(self, rel: Relationship) -> list[str]:
        """Generate field definition for a composition relationship."""
        lines: list[str] = []

        # Field name derived from child entity
        child_entity = self.domain.entities.get(rel.child_entity)
        if not child_entity:
            return lines

        child_schema = child_entity.get_schema_name()
        field_name = to_camel_case(rel.child_entity)

        # Pluralize for 1:n relationships
        if rel.is_array():
            if not field_name.endswith("s"):
                field_name = field_name + "s"
            field_type = f"array of {child_schema}"
        else:
            field_type = child_schema

        lines.append(f"    {field_name}: {field_type}")
        lines.append("        @composition")

        if rel.join_attributes:
            lines.append(f'        @join "{rel.join_attributes}"')

        if rel.comment:
            lines.append(f'        @description "{self._escape_string(rel.comment)}"')

        return lines

    def _map_datatype(self, attr: Attribute) -> str:
        """Map Excel datatype to Nexflow type."""
        datatype = attr.datatype.lower() if attr.datatype else "string"

        # Check for decimal with precision
        if datatype == "number" and attr.length and "," in attr.length:
            return "decimal"

        return DATATYPE_MAP.get(datatype, "string")

    def generate_enum_schema(
        self, entity: Entity, attr_name: str, values: list[EnumValue]
    ) -> str:
        """Generate enum schema for an attribute."""
        lines: list[str] = []

        schema_name = entity.get_schema_name()
        enum_name = f"{schema_name}{to_pascal_case(attr_name)}"

        lines.append(f"enum {enum_name}")
        lines.append('    @version "1.0.0"')
        lines.append("")

        for enum_val in values:
            const_name = to_upper_snake(enum_val.value)
            label = self._escape_string(enum_val.label)
            lines.append(f'    {const_name} = "{label}"')

        lines.append("end")

        return "\n".join(lines)

    def generate_domain_yaml(self) -> str:
        """Generate domain metadata YAML file."""
        from datetime import datetime

        lines: list[str] = []

        lines.append(f"name: {self.domain.name}")
        lines.append(f"source_file: {self.domain.source_file}")
        lines.append(f"generated_at: {datetime.now().isoformat()}")
        lines.append("")

        lines.append("managed_entities:")
        for entity_name in self.domain.managed_entities:
            entity = self.domain.entities.get(entity_name)
            if entity:
                lines.append(f"  - {entity.get_schema_name()}")

        lines.append("")
        lines.append("external_references:")
        for entity_name in self.domain.external_references:
            entity = self.domain.entities.get(entity_name)
            if entity:
                source = self.shortcut_resolutions.get(entity_name, "unknown")
                lines.append(f"  - entity: {entity.get_schema_name()}")
                lines.append(f"    source: {source}")

        return "\n".join(lines)

    def _escape_string(self, s: str) -> str:
        """Escape string for DSL output."""
        if not s:
            return ""
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
