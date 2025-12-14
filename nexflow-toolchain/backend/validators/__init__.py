# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Nexflow Validators Module
# Semantic validation for DSL constructs

from pathlib import Path
from typing import Dict, Any, Optional

from .base import (
    BaseValidator,
    ValidationResult,
    ValidationContext,
    ValidationError,
    Severity,
)
from .schema_validator import SchemaValidator
from .transform_validator import TransformValidator
from .rules_validator import RulesValidator
from .flow_validator import FlowValidator

# Validator registry - maps DSL type to validator class
VALIDATORS = {
    'schema': SchemaValidator,
    'transform': TransformValidator,
    'rules': RulesValidator,
    'flow': FlowValidator,
}


def get_validator(lang: str, context: Optional[ValidationContext] = None) -> Optional[BaseValidator]:
    """
    Factory function to get a validator instance for a DSL type.

    Args:
        lang: DSL type ('schema', 'flow', 'transform', 'rules')
        context: Optional shared validation context

    Returns:
        Validator instance or None if not found
    """
    validator_class = VALIDATORS.get(lang)
    if validator_class:
        return validator_class(context)
    return None


def validate_project_asts(
    asts: Dict[str, Dict[Path, Any]],
    verbose: bool = False,
    return_context: bool = False
) -> ValidationResult:
    """
    Validate all parsed ASTs in a project.

    Performs two-pass validation:
    1. First pass: Register all definitions in context
    2. Second pass: Validate with full cross-reference context

    Args:
        asts: Dictionary mapping DSL type to dict of file_path -> AST
        verbose: Enable verbose output
        return_context: If True, attaches validation_context to result for type flow

    Returns:
        Combined ValidationResult for all files
        If return_context=True, result.context contains the ValidationContext
    """
    result = ValidationResult()
    context = ValidationContext()

    # Validation order matters for cross-references:
    # 1. Schema (no dependencies)
    # 2. Transform (may reference schemas)
    # 3. Rules (may reference schemas)
    # 4. Flow (references schemas, transforms, rules)
    validation_order = ['schema', 'transform', 'rules', 'flow']

    for lang in validation_order:
        if lang not in asts or not asts[lang]:
            continue

        validator = get_validator(lang, context)
        if not validator:
            if verbose:
                print(f"  No validator for '{lang}', skipping validation")
            continue

        for file_path, ast in asts[lang].items():
            if ast is None:
                continue

            if verbose:
                print(f"  Validating {file_path.name}...")

            try:
                file_result = validator.validate(ast, file_path)
                result.merge(file_result)

                if verbose:
                    if file_result.errors:
                        for err in file_result.errors:
                            print(f"    ✗ {err}")
                    if file_result.warnings:
                        for warn in file_result.warnings:
                            print(f"    ⚠ {warn}")

            except Exception as e:
                result.add_error(
                    f"Validation failed: {e}",
                    file=file_path,
                    code="VALIDATION_EXCEPTION"
                )
                if verbose:
                    print(f"    ✗ Exception: {e}")

    # Attach context to result for type flow in code generation
    if return_context:
        result.context = context

    return result


__all__ = [
    'BaseValidator',
    'ValidationResult',
    'ValidationContext',
    'ValidationError',
    'Severity',
    'SchemaValidator',
    'TransformValidator',
    'RulesValidator',
    'FlowValidator',
    'VALIDATORS',
    'get_validator',
    'validate_project_asts',
]
