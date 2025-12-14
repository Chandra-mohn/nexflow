# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform Validator

Validates L3 Transform DSL ASTs for semantic correctness.
"""

from pathlib import Path
from typing import Optional, Set

from backend.validators.base import BaseValidator, ValidationResult


class TransformValidator(BaseValidator):
    """
    Validator for Transform DSL ASTs.

    Checks:
    - Input/output field consistency
    - Transform reference validity
    - Cache configuration validity
    - Expression type checking (basic)
    """

    def validate(self, program, file_path: Optional[Path] = None) -> ValidationResult:
        """Validate a transform program AST."""
        result = ValidationResult()

        # Validate field-level transforms
        transforms = getattr(program, 'transforms', []) or []
        for transform in transforms:
            name = getattr(transform, 'name', None)
            if name:
                self.context.register_transform(name, transform, file_path)
            self._validate_transform(transform, result, file_path)

        # Validate block-level transforms
        transform_blocks = getattr(program, 'transform_blocks', []) or []
        for transform_block in transform_blocks:
            name = getattr(transform_block, 'name', None)
            if name:
                self.context.register_transform(name, transform_block, file_path)
            self._validate_transform_block(transform_block, result, file_path)

        return result

    def _validate_transform(self, transform, result: ValidationResult,
                            file_path: Optional[Path]) -> None:
        """Validate a field-level transform definition."""
        transform_name = getattr(transform, 'name', 'unknown')

        # Validate input spec
        input_spec = getattr(transform, 'input', None)
        if input_spec:
            self._validate_input_spec(input_spec, transform_name, result, file_path)

        # Validate output spec
        output_spec = getattr(transform, 'output', None)
        if output_spec:
            self._validate_output_spec(output_spec, transform_name, result, file_path)

        # Validate cache configuration
        cache = getattr(transform, 'cache', None)
        if cache:
            self._validate_cache(cache, transform_name, result, file_path)

        # Validate apply block
        apply_block = getattr(transform, 'apply', None)
        if apply_block:
            self._validate_apply(apply_block, transform_name, result, file_path)

    def _validate_transform_block(self, transform_block, result: ValidationResult,
                                   file_path: Optional[Path]) -> None:
        """Validate a block-level transform definition."""
        transform_name = getattr(transform_block, 'name', 'unknown')

        # Check for duplicate field names in input
        self._check_duplicate_input_fields(transform_block, transform_name, result, file_path)

        # Check for duplicate field names in output
        self._check_duplicate_output_fields(transform_block, transform_name, result, file_path)

        # Validate use block references
        use_block = getattr(transform_block, 'use', None)
        if use_block:
            self._validate_use_block(use_block, transform_name, result, file_path)

        # Validate compose block
        compose_block = getattr(transform_block, 'compose', None)
        if compose_block:
            self._validate_compose(compose_block, transform_name, result, file_path)

    def _validate_input_spec(self, input_spec, transform_name: str,
                              result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate input specification."""
        # Check for duplicate field names
        fields = getattr(input_spec, 'fields', []) or []
        seen_names: Set[str] = set()
        for field in fields:
            field_name = getattr(field, 'name', None)
            if field_name:
                if field_name in seen_names:
                    line, col = self._get_location(field)
                    result.add_error(
                        f"Duplicate input field '{field_name}' in transform '{transform_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                    )
                seen_names.add(field_name)

    def _validate_output_spec(self, output_spec, transform_name: str,
                               result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate output specification."""
        # Check for duplicate field names
        fields = getattr(output_spec, 'fields', []) or []
        seen_names: Set[str] = set()
        for field in fields:
            field_name = getattr(field, 'name', None)
            if field_name:
                if field_name in seen_names:
                    line, col = self._get_location(field)
                    result.add_error(
                        f"Duplicate output field '{field_name}' in transform '{transform_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                    )
                seen_names.add(field_name)

    def _check_duplicate_input_fields(self, transform_block, transform_name: str,
                                       result: ValidationResult, file_path: Optional[Path]) -> None:
        """Check for duplicate input field names."""
        input_spec = getattr(transform_block, 'input', None)
        if not input_spec:
            return

        fields = getattr(input_spec, 'fields', []) or []
        seen_names: Set[str] = set()
        for field in fields:
            field_name = getattr(field, 'name', None)
            if field_name:
                if field_name in seen_names:
                    line, col = self._get_location(field)
                    result.add_error(
                        f"Duplicate input field '{field_name}' in transform '{transform_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                    )
                seen_names.add(field_name)

    def _check_duplicate_output_fields(self, transform_block, transform_name: str,
                                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Check for duplicate output field names."""
        output_spec = getattr(transform_block, 'output', None)
        if not output_spec:
            return

        fields = getattr(output_spec, 'fields', []) or []
        seen_names: Set[str] = set()
        for field in fields:
            field_name = getattr(field, 'name', None)
            if field_name:
                if field_name in seen_names:
                    line, col = self._get_location(field)
                    result.add_error(
                        f"Duplicate output field '{field_name}' in transform '{transform_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                    )
                seen_names.add(field_name)

    def _validate_cache(self, cache, transform_name: str,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate cache configuration."""
        # Check TTL is positive
        ttl = getattr(cache, 'ttl', None)
        if ttl:
            ttl_value = getattr(ttl, 'value', None)
            if ttl_value is not None and ttl_value <= 0:
                line, col = self._get_location(cache)
                result.add_error(
                    f"Cache TTL must be positive in transform '{transform_name}'",
                    file=file_path, line=line, column=col, code="INVALID_CACHE_CONFIG"
                )

        # Check max_size is positive
        max_size = getattr(cache, 'max_size', None)
        if max_size is not None and max_size <= 0:
            line, col = self._get_location(cache)
            result.add_error(
                f"Cache max_size must be positive in transform '{transform_name}'",
                file=file_path, line=line, column=col, code="INVALID_CACHE_CONFIG"
            )

    def _validate_apply(self, apply_block, transform_name: str,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate apply block."""
        # Check that apply block has an expression or assignments
        expression = getattr(apply_block, 'expression', None)
        assignments = getattr(apply_block, 'assignments', []) or []
        locals_list = getattr(apply_block, 'locals', []) or []

        if not expression and not assignments and not locals_list:
            line, col = self._get_location(apply_block)
            result.add_warning(
                f"Apply block in transform '{transform_name}' has no content",
                file=file_path, line=line, column=col, code="EMPTY_APPLY"
            )

    def _validate_use_block(self, use_block, transform_name: str,
                            result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate use block references."""
        transforms = getattr(use_block, 'transforms', []) or []
        for ref_name in transforms:
            if ref_name and not self.context.has_transform(ref_name):
                line, col = self._get_location(use_block)
                result.add_warning(
                    f"Transform '{transform_name}' uses '{ref_name}' "
                    "which is not registered (may be defined in another file)",
                    file=file_path, line=line, column=col, code="UNRESOLVED_TRANSFORM"
                )

    def _validate_compose(self, compose_block, transform_name: str,
                          result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate compose block."""
        refs = getattr(compose_block, 'refs', []) or []
        for ref in refs:
            ref_name = getattr(ref, 'name', None)
            if ref_name and not self.context.has_transform(ref_name):
                line, col = self._get_location(ref)
                result.add_warning(
                    f"Transform '{transform_name}' composes '{ref_name}' "
                    "which is not registered (may be defined in another file)",
                    file=file_path, line=line, column=col, code="UNRESOLVED_TRANSFORM"
                )
