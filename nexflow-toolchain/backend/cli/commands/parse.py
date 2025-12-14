# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Parse Command Implementation

Parses a single DSL file and returns AST in requested format.
"""

import json
from pathlib import Path
from typing import Any

from ..project import DSL_EXTENSIONS
from .types import ParseResult, ValidationError


def get_language_from_file(file_path: Path) -> str | None:
    """Determine DSL language from file extension."""
    return DSL_EXTENSIONS.get(file_path.suffix)


def parse_file(file_path: Path, output_format: str, verbose: bool) -> ParseResult:
    """
    Parse a single DSL file and return AST in requested format.
    """
    from ...parser import parse as parse_dsl, PARSERS

    result = ParseResult(success=True)

    lang = get_language_from_file(file_path)
    if not lang:
        result.success = False
        result.errors.append(ValidationError(
            file=str(file_path),
            line=None,
            column=None,
            message=f"Unknown file type: {file_path.suffix}"
        ))
        return result

    if lang not in PARSERS:
        result.success = False
        result.errors.append(ValidationError(
            file=str(file_path),
            line=None,
            column=None,
            message=f"Parser for '{lang}' not yet implemented"
        ))
        return result

    try:
        content = file_path.read_text()
        parse_result = parse_dsl(content, lang)

        if not parse_result.success:
            result.success = False
            for error in parse_result.errors:
                result.errors.append(ValidationError(
                    file=str(file_path),
                    line=error.location.line if error.location else None,
                    column=error.location.column if error.location else None,
                    message=error.message
                ))
            return result

        # Format output
        if output_format == "json":
            result.output = ast_to_json(parse_result.ast)
        elif output_format == "tree":
            result.output = ast_to_tree(parse_result.ast)
        else:  # summary
            result.output = ast_to_summary(parse_result.ast, file_path)

    except Exception as e:
        result.success = False
        result.errors.append(ValidationError(
            file=str(file_path),
            line=None,
            column=None,
            message=str(e)
        ))

    return result


def ast_to_json(ast: Any) -> str:
    """Convert AST to JSON string."""
    import dataclasses

    def serialize(obj: Any) -> Any:
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            result = {"_type": obj.__class__.__name__}
            for f in dataclasses.fields(obj):
                value = getattr(obj, f.name)
                result[f.name] = serialize(value)
            return result
        elif isinstance(obj, list):
            return [serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: serialize(v) for k, v in obj.items()}
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        else:
            return obj

    return json.dumps(serialize(ast), indent=2)


def ast_to_tree(ast: Any, indent: int = 0) -> str:
    """Convert AST to tree representation."""
    import dataclasses

    lines = []
    prefix = "  " * indent

    if dataclasses.is_dataclass(ast) and not isinstance(ast, type):
        lines.append(f"{prefix}{ast.__class__.__name__}")
        for f in dataclasses.fields(ast):
            value = getattr(f, f.name) if hasattr(f, f.name) else getattr(ast, f.name)
            if value is None:
                continue
            if dataclasses.is_dataclass(value) or isinstance(value, list):
                lines.append(f"{prefix}  {f.name}:")
                if isinstance(value, list):
                    for item in value:
                        lines.append(ast_to_tree(item, indent + 2))
                else:
                    lines.append(ast_to_tree(value, indent + 2))
            else:
                val_str = value.value if hasattr(value, 'value') else str(value)
                lines.append(f"{prefix}  {f.name}: {val_str}")

    return "\n".join(lines)


def ast_to_summary(ast: Any, file_path: Path) -> str:
    """Convert AST to human-readable summary."""
    lines = [f"File: {file_path.name}", f"Type: {type(ast).__name__}", ""]

    # Get counts based on AST type
    if hasattr(ast, 'decision_tables'):
        lines.append(f"Decision Tables: {len(ast.decision_tables)}")
        for dt in ast.decision_tables:
            lines.append(f"  • {dt.name}")

    if hasattr(ast, 'procedural_rules'):
        lines.append(f"Procedural Rules: {len(ast.procedural_rules)}")
        for rule in ast.procedural_rules:
            lines.append(f"  • {rule.name}")

    if hasattr(ast, 'processes'):
        lines.append(f"Processes: {len(ast.processes)}")
        for proc in ast.processes:
            lines.append(f"  • {proc.name}")

    if hasattr(ast, 'schemas'):
        lines.append(f"Schemas: {len(ast.schemas)}")
        for schema in ast.schemas:
            lines.append(f"  • {schema.name}")

    if hasattr(ast, 'transforms'):
        lines.append(f"Transforms: {len(ast.transforms)}")
        for t in ast.transforms:
            lines.append(f"  • {t.name}")

    return "\n".join(lines)
