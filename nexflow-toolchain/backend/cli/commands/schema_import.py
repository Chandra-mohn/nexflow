# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema Import CLI Command

Import enterprise data models from Excel workbooks into Nexflow Schema DSL.
"""

from pathlib import Path
from typing import Optional
import click
from rich.console import Console

console = Console(force_terminal=False, legacy_windows=True)


@click.command("import")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), required=True,
              help="Output directory for generated schema files")
@click.option("--domain", "-d", type=str, default=None,
              help="Override domain name (single file only)")
@click.option("--resolve-shortcuts", is_flag=True,
              help="Validate and resolve cross-domain shortcut references")
@click.option("--managed-only", is_flag=True,
              help="Only import entities with BIMEntityName (managed aggregates)")
@click.option("--exclude-qualifiers", type=str, default=None,
              help="Comma-separated qualifiers to exclude (e.g., 'CR')")
@click.option("--patterns", type=str, default=None,
              help="Comma-separated patterns to include (e.g., 'Event,Ledger')")
@click.option("--dry-run", is_flag=True,
              help="Preview without writing files")
@click.option("--verbose", "-v", is_flag=True,
              help="Enable verbose output")
@click.option("--manifest", is_flag=True,
              help="Generate dependency manifest file")
@click.option("--report", is_flag=True,
              help="Generate domain summary report")
@click.pass_context
def schema_import(
    ctx: click.Context,
    files: tuple,
    output: str,
    domain: Optional[str],
    resolve_shortcuts: bool,
    managed_only: bool,
    exclude_qualifiers: Optional[str],
    patterns: Optional[str],
    dry_run: bool,
    verbose: bool,
    manifest: bool,
    report: bool,
):
    """
    Import Excel workbooks into Nexflow Schema DSL.

    Parses enterprise data models from Excel and generates .schema files
    with proper entity relationships, enums, and cross-domain references.

    \b
    Excel Workbook Structure (per service domain):
        ServiceDomain  - Domain metadata
        Entities       - Schema/type definitions
        Attributes     - Field definitions
        Relationships  - Parent-child composition
        Enumerations   - Enum values

    \b
    Example:
        nexflow schema import Orders.xlsx -o ./schemas/orders/
        nexflow schema import Orders.xlsx Customers.xlsx -o ./schemas/ --resolve-shortcuts
        nexflow schema import Orders.xlsx -o ./schemas/ --managed-only
        nexflow schema import Orders.xlsx -o ./schemas/ --exclude-qualifiers CR
        nexflow schema import Orders.xlsx -o ./schemas/ --dry-run
    """
    try:
        # Import here to avoid loading openpyxl when not needed
        from backend.importers.excel import ExcelSchemaImporter
    except ImportError as e:
        console.print("[red]Error:[/red] Excel import requires openpyxl.")
        console.print("  Install with: pip install openpyxl")
        ctx.exit(1)

    # Parse filter options
    exclude_list = None
    if exclude_qualifiers:
        exclude_list = [q.strip() for q in exclude_qualifiers.split(",")]

    pattern_list = None
    if patterns:
        pattern_list = [p.strip() for p in patterns.split(",")]

    output_dir = Path(output)
    file_paths = [Path(f) for f in files]

    # Validate files are Excel
    for fp in file_paths:
        if not fp.suffix.lower() in (".xlsx", ".xls"):
            console.print(f"[red]Error:[/red] {fp} is not an Excel file (.xlsx or .xls)")
            ctx.exit(1)

    importer = ExcelSchemaImporter()

    try:
        if len(file_paths) == 1:
            # Single file import
            result = importer.import_workbook(
                file_paths[0],
                output_dir,
                dry_run=dry_run,
                managed_only=managed_only,
                exclude_qualifiers=exclude_list,
                patterns=pattern_list,
                verbose=verbose,
            )

            if not result.success():
                console.print("[red][FAIL][/red] Import failed.")
                for error in result.errors:
                    console.print(f"  [red]-[/red] {error}")
                ctx.exit(1)

            if dry_run:
                console.print("[green][OK][/green] Dry run complete. No files written.")
            else:
                console.print(
                    f"[green][OK][/green] Imported {result.entity_count} entities, "
                    f"generated {len(result.generated_files)} files."
                )

            if result.warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    console.print(f"  [yellow]![/yellow] {warning}")

        else:
            # Multiple files import
            results = importer.import_multiple(
                file_paths,
                output_dir,
                resolve_shortcuts=resolve_shortcuts,
                dry_run=dry_run,
                managed_only=managed_only,
                exclude_qualifiers=exclude_list,
                patterns=pattern_list,
                verbose=verbose,
            )

            total_files = 0
            total_entities = 0
            all_warnings = []
            has_errors = False

            for domain_name, result in results.items():
                if not result.success():
                    has_errors = True
                    console.print(f"[red][FAIL][/red] {domain_name}: Import failed.")
                    for error in result.errors:
                        console.print(f"  [red]-[/red] {error}")
                else:
                    total_files += len(result.generated_files)
                    total_entities += result.entity_count
                    all_warnings.extend(result.warnings)

            if has_errors:
                ctx.exit(1)

            if dry_run:
                console.print("[green][OK][/green] Dry run complete. No files written.")
            else:
                console.print(
                    f"[green][OK][/green] Imported {total_entities} entities across "
                    f"{len(results)} domains, generated {total_files} files."
                )

            if all_warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in all_warnings[:10]:  # Limit warning output
                    console.print(f"  [yellow]![/yellow] {warning}")
                if len(all_warnings) > 10:
                    console.print(f"  ... and {len(all_warnings) - 10} more warnings")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        ctx.exit(1)
