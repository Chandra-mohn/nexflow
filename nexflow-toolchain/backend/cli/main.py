# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Command Line Interface

Build tool for Nexflow projects. Compiles DSL files to target runtime code.

Usage:
    nexflow build [--target TARGET] [--output DIR]
    nexflow validate [PATH]
    nexflow parse FILE [--format FORMAT]
    nexflow init [--name NAME]
    nexflow clean
"""
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .project import Project, ProjectError
from .commands import build_project, validate_project, parse_file, init_project, clean_project

console = Console()

# Version
__version__ = "0.1.0"


@click.group()
@click.version_option(version=__version__, prog_name="nexflow")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool):
    """
    Nexflow Build Tool

    Compile DSL files (.proc, .schema, .transform, .rules) to target runtime code.

    \b
    Example:
        nexflow init --name my-project
        nexflow build --target flink
        nexflow validate
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--target", "-t", type=click.Choice(["flink", "spark", "all"]),
              default="flink", help="Target runtime (default: flink)")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output directory (default: from nexflow.toml)")
@click.option("--dry-run", is_flag=True, help="Validate and show what would be generated")
@click.option("--verify", is_flag=True, help="Verify generated code compiles with Maven")
@click.pass_context
def build(ctx: click.Context, target: str, output: Optional[str], dry_run: bool, verify: bool):
    """
    Build the project - compile DSL files to target code.

    Performs full pipeline: parse → validate → generate → verify (optional).

    \b
    Example:
        nexflow build                    # Build with defaults from nexflow.toml
        nexflow build --target spark     # Build for Apache Spark
        nexflow build --dry-run          # Validate only, show what would be generated
        nexflow build --verify           # Build and verify Java compilation
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        project = Project.load()
        result = build_project(project, target, output, dry_run, verbose, verify)

        if result.success:
            if dry_run:
                console.print("[green]✓[/green] Validation passed. Files that would be generated:")
                for f in result.files:
                    console.print(f"  • {f}")
            else:
                console.print(f"[green]✓[/green] Build successful. Generated {len(result.files)} files.")
                if verbose:
                    for f in result.files:
                        console.print(f"  • {f}")
        else:
            console.print("[red]✗[/red] Build failed.")
            for error in result.errors:
                console.print(f"  [red]•[/red] {error}")
            sys.exit(1)

    except ProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.pass_context
def validate(ctx: click.Context, path: Optional[str]):
    """
    Validate DSL files without generating code.

    If PATH is provided, validates that file/directory only.
    Otherwise validates entire project based on nexflow.toml.

    \b
    Example:
        nexflow validate                     # Validate entire project
        nexflow validate src/rules/          # Validate rules directory
        nexflow validate src/rules/credit.rules  # Validate single file
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        if path:
            result = validate_project(Path(path), verbose)
        else:
            project = Project.load()
            result = validate_project(project.src_dir, verbose, project)

        if result.success:
            console.print(f"[green]✓[/green] Validation passed. {result.file_count} files checked.")
        else:
            console.print(f"[red]✗[/red] Validation failed. {len(result.errors)} errors found.")
            for error in result.errors:
                loc = f"{error.file}:{error.line}:{error.column}" if error.line else error.file
                console.print(f"  [red]•[/red] {loc}: {error.message}")
            sys.exit(1)

    except ProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "-f", "output_format", type=click.Choice(["json", "tree", "summary"]),
              default="summary", help="Output format (default: summary)")
@click.pass_context
def parse(ctx: click.Context, file: str, output_format: str):
    """
    Parse a single DSL file and show AST.

    Useful for debugging and understanding DSL structure.

    \b
    Example:
        nexflow parse src/rules/credit.rules
        nexflow parse src/rules/credit.rules --format json
        nexflow parse src/rules/credit.rules --format tree
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        result = parse_file(Path(file), output_format, verbose)

        if result.success:
            console.print(result.output)
        else:
            console.print(f"[red]✗[/red] Parse failed.")
            for error in result.errors:
                console.print(f"  [red]•[/red] Line {error.line}: {error.message}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--name", "-n", default="my-project", help="Project name")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing nexflow.toml")
def init(name: str, force: bool):
    """
    Initialize a new Nexflow project.

    Creates nexflow.toml and standard directory structure.

    \b
    Example:
        nexflow init --name order-processing
    """
    try:
        result = init_project(name, force)

        if result.success:
            console.print(f"[green]✓[/green] Initialized project '{name}'")
            console.print("  Created:")
            for item in result.created:
                console.print(f"    • {item}")
            console.print("\n  Next steps:")
            console.print("    1. Add DSL files to src/")
            console.print("    2. Run: nexflow build")
        else:
            console.print(f"[red]Error:[/red] {result.message}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--all", "-a", "clean_all", is_flag=True, help="Also remove build artifacts")
def clean(clean_all: bool):
    """
    Remove generated files.

    \b
    Example:
        nexflow clean         # Remove generated/ directory
        nexflow clean --all   # Also remove .nexflow-cache/
    """
    try:
        project = Project.load()
        result = clean_project(project, clean_all)

        if result.success:
            console.print(f"[green]✓[/green] Cleaned {result.removed_count} items.")
        else:
            console.print(f"[yellow]![/yellow] Nothing to clean.")

    except ProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def info():
    """
    Show project information.
    """
    try:
        project = Project.load()

        table = Table(title="Nexflow Project Info")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name", project.name)
        table.add_row("Version", project.version)
        table.add_row("Source Dir", str(project.src_dir))
        table.add_row("Output Dir", str(project.output_dir))
        table.add_row("Targets", ", ".join(project.targets))

        console.print(table)

        # Show file counts
        console.print("\nDSL Files:")
        for lang, count in project.file_counts.items():
            console.print(f"  • {lang}: {count} files")

    except ProjectError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
