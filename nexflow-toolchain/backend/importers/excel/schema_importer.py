"""
Excel Schema Importer - Main orchestrator.

Import enterprise data models from Excel workbooks into Nexflow Schema DSL.
"""

from pathlib import Path
from typing import Optional
import logging
import yaml

from .parser import ExcelParser, ExcelParseError
from .graph import GraphBuilder, CrossDomainResolver, DomainGraph
from .generator import SchemaGenerator
from .validator import SchemaValidator, ValidationSeverity
from .models import ServiceDomain

logger = logging.getLogger(__name__)


class ImportResult:
    """Result of a schema import operation."""

    def __init__(self):
        self.generated_files: list[Path] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.domain_name: str = ""
        self.entity_count: int = 0
        self.managed_count: int = 0
        self.external_count: int = 0

    def success(self) -> bool:
        """Check if import was successful (no errors)."""
        return len(self.errors) == 0


class ExcelSchemaImporter:
    """
    Import Excel workbooks into Nexflow Schema DSL.

    Usage:
        importer = ExcelSchemaImporter()
        result = importer.import_workbook(
            Path("Orders.xlsx"),
            output_dir=Path("./schemas/orders/")
        )
    """

    def __init__(self):
        self.resolver = CrossDomainResolver()
        self.imported_domains: dict[str, DomainGraph] = {}

    def import_workbook(
        self,
        file_path: Path,
        output_dir: Path,
        dry_run: bool = False,
        managed_only: bool = False,
        exclude_qualifiers: Optional[list[str]] = None,
        patterns: Optional[list[str]] = None,
        verbose: bool = False,
    ) -> ImportResult:
        """
        Import a single Excel workbook.

        Args:
            file_path: Path to Excel workbook
            output_dir: Directory to write schema files
            dry_run: If True, don't write files
            managed_only: Only import entities with BIMEntityName
            exclude_qualifiers: Exclude entities with these qualifiers (e.g., ["CR"])
            patterns: Only include entities with these patterns
            verbose: Enable verbose logging

        Returns:
            ImportResult with generated files and any warnings/errors
        """
        result = ImportResult()

        if verbose:
            logging.basicConfig(level=logging.DEBUG)

        try:
            # Parse Excel workbook
            logger.info(f"Importing: {file_path}")
            parser = ExcelParser(file_path)
            domain = parser.parse()

            result.warnings.extend(parser.warnings)
            result.domain_name = domain.name

            # Apply filters
            if managed_only:
                domain = self._filter_managed_only(domain)

            if exclude_qualifiers:
                domain = self._filter_exclude_qualifiers(domain, exclude_qualifiers)

            if patterns:
                domain = self._filter_patterns(domain, patterns)

            # Build relationship graph
            graph_builder = GraphBuilder(domain)
            graph = graph_builder.build()

            result.warnings.extend(graph_builder.warnings)

            # Validate before generation
            validator = SchemaValidator(domain, graph)
            validation = validator.validate()

            for issue in validation.issues:
                if issue.severity == ValidationSeverity.ERROR:
                    result.errors.append(f"{issue.code}: {issue.message}")
                else:
                    result.warnings.append(f"{issue.code}: {issue.message}")

            # Abort if validation errors
            if validation.has_errors():
                return result

            # Store for cross-domain resolution
            self.imported_domains[domain.name] = graph
            self.resolver.add_domain(graph)

            # Generate schema files
            generator = SchemaGenerator(domain, graph)
            generated = generator.generate_all(output_dir, dry_run=dry_run)

            result.generated_files = generated
            result.entity_count = len(domain.entities)
            result.managed_count = len(domain.managed_entities)
            result.external_count = len(domain.external_references)

            # Print summary
            self._print_summary(result, domain)

        except ExcelParseError as e:
            result.errors.append(str(e))
            logger.error(f"Parse error: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error: {e}")
            logger.exception("Import failed")

        return result

    def import_multiple(
        self,
        file_paths: list[Path],
        output_dir: Path,
        resolve_shortcuts: bool = False,
        dry_run: bool = False,
        **kwargs,
    ) -> dict[str, ImportResult]:
        """
        Import multiple Excel workbooks with optional cross-reference resolution.

        Args:
            file_paths: List of workbook paths
            output_dir: Base output directory (subdirs created per domain)
            resolve_shortcuts: Validate and resolve cross-domain references
            dry_run: If True, don't write files
            **kwargs: Additional arguments passed to import_workbook

        Returns:
            Dict mapping domain name to ImportResult
        """
        results: dict[str, ImportResult] = {}

        # First pass: import all workbooks
        for file_path in file_paths:
            domain_name = file_path.stem.lower()
            domain_output = output_dir / domain_name

            result = self.import_workbook(
                file_path,
                domain_output,
                dry_run=dry_run,
                **kwargs,
            )
            results[result.domain_name or domain_name] = result

        # Second pass: resolve shortcuts if requested
        if resolve_shortcuts:
            resolutions = self.resolver.resolve_shortcuts()

            # Regenerate with resolved shortcuts
            for domain_name, graph in self.imported_domains.items():
                domain_output = output_dir / domain_name.lower()
                domain_resolutions = resolutions.get(domain_name, {})

                generator = SchemaGenerator(
                    graph.domain,
                    graph,
                    shortcut_resolutions=domain_resolutions,
                )
                generator.generate_all(domain_output, dry_run=dry_run)

            # Generate dependencies manifest
            if not dry_run:
                dependencies = self.resolver.get_dependencies()
                manifest_path = output_dir / "_dependencies.yaml"
                with open(manifest_path, "w") as f:
                    yaml.dump(dependencies, f, default_flow_style=False)
                logger.info(f"Generated: {manifest_path}")

            # Report unresolved shortcuts
            for domain, entity in self.resolver.unresolved:
                for result in results.values():
                    if result.domain_name == domain:
                        result.warnings.append(
                            f"SHORTCUT_UNRESOLVED: Entity '{entity}' source domain unknown"
                        )

        return results

    def _filter_managed_only(self, domain: ServiceDomain) -> ServiceDomain:
        """Filter to only managed entities (with BIMEntityName)."""
        filtered_entities = {
            name: entity
            for name, entity in domain.entities.items()
            if entity.is_managed() or entity.is_shortcut()
        }

        domain.entities = filtered_entities
        return domain

    def _filter_exclude_qualifiers(
        self, domain: ServiceDomain, qualifiers: list[str]
    ) -> ServiceDomain:
        """Exclude entities with specified qualifiers."""
        qualifier_set = {q.upper() for q in qualifiers}

        filtered_entities = {
            name: entity
            for name, entity in domain.entities.items()
            if entity.qualifier.value not in qualifier_set
        }

        domain.entities = filtered_entities
        return domain

    def _filter_patterns(
        self, domain: ServiceDomain, patterns: list[str]
    ) -> ServiceDomain:
        """Include only entities with specified patterns."""
        pattern_set = {p.lower() for p in patterns}

        filtered_entities = {
            name: entity
            for name, entity in domain.entities.items()
            if entity.pattern.value.lower() in pattern_set or entity.is_shortcut()
        }

        domain.entities = filtered_entities
        return domain

    def _print_summary(self, result: ImportResult, domain: ServiceDomain):
        """Print import summary."""
        print()
        print("=" * 60)
        print(f"Service Domain: {domain.name}")
        print("=" * 60)
        print()

        print("Managed Aggregates (BIM Entities):")
        for entity_name in domain.managed_entities:
            entity = domain.entities.get(entity_name)
            if entity:
                pattern = f" - Pattern: {entity.pattern.value}" if entity.pattern.value else ""
                print(f"  + {entity.get_schema_name()} ({entity.collection_name}){pattern}")

        print()
        print("Child Entities:")
        for entity_name, entity in domain.entities.items():
            if not entity.is_managed() and not entity.is_shortcut():
                # Find parent
                parent = None
                for rel in domain.relationships:
                    if rel.child_entity == entity_name:
                        parent = rel.parent_entity
                        break
                parent_info = f" - composition of {parent}" if parent else ""
                print(f"  - {entity.get_schema_name()} ({entity.collection_name}){parent_info}")

        print()
        print("External References (Shortcuts):")
        for entity_name in domain.external_references:
            entity = domain.entities.get(entity_name)
            if entity:
                print(f"  ! {entity.get_schema_name()} - source domain: unknown")

        print()
        print(f"Generated: {len(result.generated_files)} schema files")

        if result.warnings:
            print()
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        print("=" * 60)
