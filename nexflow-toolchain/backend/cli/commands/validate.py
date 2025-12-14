# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Validate Command Implementation

Validates DSL files without code generation.
"""

from pathlib import Path
from typing import Optional, List

from ..project import Project, DSL_EXTENSIONS
from .types import ValidateResult, ValidationError


def get_language_from_file(file_path: Path) -> Optional[str]:
    """Determine DSL language from file extension."""
    return DSL_EXTENSIONS.get(file_path.suffix)


def validate_project(path: Path, verbose: bool,
                     project: Optional[Project] = None) -> ValidateResult:
    """
    Validate DSL files without code generation.
    """
    from ...parser import parse as parse_dsl, PARSERS

    result = ValidateResult(success=True)

    # Collect files to validate
    files_to_validate: List[Path] = []

    if path.is_file():
        files_to_validate = [path]
    elif path.is_dir():
        for ext in DSL_EXTENSIONS.keys():
            files_to_validate.extend(path.rglob(f"*{ext}"))
    else:
        result.success = False
        result.errors.append(ValidationError(
            file=str(path),
            line=None,
            column=None,
            message="Path does not exist"
        ))
        return result

    result.file_count = len(files_to_validate)

    # Validate each file
    for file_path in sorted(files_to_validate):
        lang = get_language_from_file(file_path)
        if not lang:
            continue

        if lang not in PARSERS:
            if verbose:
                print(f"  Skipping {file_path.name} (parser not implemented)")
            continue

        if verbose:
            print(f"  Validating {file_path.name}...")

        try:
            content = file_path.read_text()
            parse_result = parse_dsl(content, lang)

            if not parse_result.success:
                for error in parse_result.errors:
                    result.errors.append(ValidationError(
                        file=str(file_path),
                        line=error.location.line if error.location else None,
                        column=error.location.column if error.location else None,
                        message=error.message,
                        severity=error.severity.value
                    ))
                result.success = False

        except Exception as e:
            result.errors.append(ValidationError(
                file=str(file_path),
                line=None,
                column=None,
                message=str(e)
            ))
            result.success = False

    return result
