# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema Validator

Validates L2 Schema DSL ASTs for semantic correctness.
"""

from pathlib import Path
from typing import Optional, Set

from backend.validators.base import BaseValidator, ValidationResult


class SchemaValidator(BaseValidator):
    """
    Validator for Schema DSL ASTs.

    Checks:
    - Field type constraints validity
    - Required field presence
    - State machine validity (states exist for transitions)
    - Version format
    - Streaming configuration validity
    - Unique field names
    """

    def validate(self, program, file_path: Optional[Path] = None) -> ValidationResult:
        """Validate a schema program AST."""
        result = ValidationResult()

        schemas = getattr(program, 'schemas', []) or []
        for schema in schemas:
            self._validate_schema(schema, result, file_path)
            # Register for cross-file validation
            name = getattr(schema, 'name', None)
            if name:
                self.context.register_schema(name, schema, file_path)

        return result

    def _validate_schema(self, schema, result: ValidationResult,
                         file_path: Optional[Path]) -> None:
        """Validate a single schema definition."""
        schema_name = getattr(schema, 'name', 'unknown')

        # Check for duplicate field names
        self._check_duplicate_fields(schema, schema_name, result, file_path)

        # Validate version format
        version = getattr(schema, 'version', None)
        if version:
            self._validate_version(version, result, file_path)

        # Validate streaming configuration
        streaming = getattr(schema, 'streaming', None)
        if streaming:
            self._validate_streaming(schema, schema_name, result, file_path)

        # Validate state machine
        state_machine = getattr(schema, 'state_machine', None)
        if state_machine:
            self._validate_state_machine(state_machine, schema_name, result, file_path)

        # Validate field types
        fields_block = getattr(schema, 'fields', None)
        if fields_block:
            fields = getattr(fields_block, 'fields', []) or []
            for field in fields:
                self._validate_field(field, schema_name, result, file_path)

        # Validate identity fields
        identity = getattr(schema, 'identity', None)
        if identity:
            self._validate_identity(schema, schema_name, result, file_path)

    def _check_duplicate_fields(self, schema, schema_name: str, result: ValidationResult,
                                 file_path: Optional[Path]) -> None:
        """Check for duplicate field names."""
        seen_names: Set[str] = set()

        # Get fields from FieldsBlock
        fields_block = getattr(schema, 'fields', None)
        if fields_block:
            fields = getattr(fields_block, 'fields', []) or []
            for field in fields:
                field_name = getattr(field, 'name', None)
                if field_name:
                    if field_name in seen_names:
                        line, col = self._get_location(field)
                        result.add_error(
                            f"Duplicate field name '{field_name}' in schema '{schema_name}'",
                            file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                        )
                    seen_names.add(field_name)

        # Also check nested objects
        nested_objects = getattr(schema, 'nested_objects', []) or []
        for obj in nested_objects:
            obj_name = getattr(obj, 'name', None)
            if obj_name:
                if obj_name in seen_names:
                    line, col = self._get_location(obj)
                    result.add_error(
                        f"Duplicate field/object name '{obj_name}' in schema '{schema_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_FIELD"
                    )
                seen_names.add(obj_name)

    def _validate_version(self, version, result: ValidationResult,
                          file_path: Optional[Path]) -> None:
        """Validate version format (semver)."""
        version_string = getattr(version, 'version_string', None)
        if version_string:
            parts = version_string.split('.')
            if len(parts) != 3:
                line, col = self._get_location(version)
                result.add_warning(
                    f"Version '{version_string}' does not follow semver format (X.Y.Z)",
                    file=file_path, line=line, column=col, code="INVALID_VERSION"
                )
            else:
                for part in parts:
                    if not part.isdigit():
                        line, col = self._get_location(version)
                        result.add_warning(
                            f"Version '{version_string}' contains non-numeric parts",
                            file=file_path, line=line, column=col, code="INVALID_VERSION"
                        )
                        break

    def _validate_streaming(self, schema, schema_name: str, result: ValidationResult,
                            file_path: Optional[Path]) -> None:
        """Validate streaming configuration."""
        streaming = getattr(schema, 'streaming', None)
        if not streaming:
            return

        # Get all field names from both fields block and identity block
        all_field_names = set()

        # Add fields from fields block
        fields_block = getattr(schema, 'fields', None)
        if fields_block:
            fields = getattr(fields_block, 'fields', []) or []
            for f in fields:
                name = getattr(f, 'name', None)
                if name:
                    all_field_names.add(name)

        # Add fields from identity block
        identity = getattr(schema, 'identity', None)
        if identity:
            identity_fields = getattr(identity, 'fields', []) or []
            for f in identity_fields:
                name = getattr(f, 'name', None)
                if name:
                    all_field_names.add(name)

        # Check that key_fields reference existing fields
        key_fields = getattr(streaming, 'key_fields', None)
        if key_fields:
            for key_field in key_fields:
                if key_field not in all_field_names:
                    line, col = self._get_location(streaming)
                    result.add_error(
                        f"Streaming key_field '{key_field}' not found in schema fields",
                        file=file_path, line=line, column=col, code="UNKNOWN_FIELD"
                    )

        # Check that time_field references an existing field
        time_field = getattr(streaming, 'time_field', None)
        if time_field:
            # time_field might be a FieldPath object
            time_field_name = time_field
            if hasattr(time_field, 'path'):
                time_field_name = time_field.path
            elif hasattr(time_field, 'parts'):
                time_field_name = time_field.parts[0] if time_field.parts else None

            if time_field_name and time_field_name not in all_field_names:
                line, col = self._get_location(streaming)
                result.add_error(
                    f"Streaming time_field '{time_field_name}' not found in schema fields",
                    file=file_path, line=line, column=col, code="UNKNOWN_FIELD"
                )

    def _validate_state_machine(self, sm, schema_name: str, result: ValidationResult,
                                file_path: Optional[Path]) -> None:
        """Validate state machine configuration."""
        states = getattr(sm, 'states', None) or []
        initial_state = getattr(sm, 'initial_state', None)

        # Check that initial state is in states list
        if states and initial_state:
            if initial_state not in states:
                line, col = self._get_location(sm)
                result.add_error(
                    f"Initial state '{initial_state}' not found in states list",
                    file=file_path, line=line, column=col, code="INVALID_STATE"
                )

        # Check that all transition states exist
        # Note: '*' is a wildcard meaning "any state"
        transitions = getattr(sm, 'transitions', None) or []
        if transitions and states:
            valid_states = set(states)
            for transition in transitions:
                from_state = getattr(transition, 'from_state', None)
                # '*' is wildcard for "any state"
                if from_state and from_state != '*' and from_state not in valid_states:
                    line, col = self._get_location(transition)
                    result.add_error(
                        f"Transition from unknown state '{from_state}'",
                        file=file_path, line=line, column=col, code="INVALID_STATE"
                    )
                to_states = getattr(transition, 'to_states', None) or []
                for to_state in to_states:
                    # '*' is wildcard for "any state"
                    if to_state != '*' and to_state not in valid_states:
                        line, col = self._get_location(transition)
                        result.add_error(
                            f"Transition to unknown state '{to_state}'",
                            file=file_path, line=line, column=col, code="INVALID_STATE"
                        )

    def _validate_field(self, field, schema_name: str,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate a field definition."""
        field_name = getattr(field, 'name', 'unknown')
        field_type = getattr(field, 'field_type', None)

        if not field_type:
            return

        base_type = getattr(field_type, 'base_type', None)
        constraints = getattr(field_type, 'constraints', None) or []

        # Check decimal precision/scale
        if base_type and str(base_type).lower() == 'decimal':
            precision = None
            scale = None
            for constraint in constraints:
                p = getattr(constraint, 'precision', None)
                s = getattr(constraint, 'scale', None)
                if p is not None:
                    precision = p
                if s is not None:
                    scale = s

            if precision is not None and scale is not None:
                if scale > precision:
                    line, col = self._get_location(field)
                    result.add_error(
                        f"Field '{field_name}': scale ({scale}) cannot exceed precision ({precision})",
                        file=file_path, line=line, column=col, code="INVALID_CONSTRAINT"
                    )

        # Check string length constraint
        if base_type and str(base_type).lower() == 'string':
            for constraint in constraints:
                length_spec = getattr(constraint, 'length_spec', None)
                if length_spec:
                    max_val = getattr(length_spec, 'max', None)
                    if max_val is not None and max_val <= 0:
                        line, col = self._get_location(field)
                        result.add_error(
                            f"Field '{field_name}': string length must be positive",
                            file=file_path, line=line, column=col, code="INVALID_CONSTRAINT"
                        )

    def _validate_identity(self, schema, schema_name: str, result: ValidationResult,
                           file_path: Optional[Path]) -> None:
        """Validate identity block fields exist."""
        identity = getattr(schema, 'identity', None)
        if not identity:
            return

        identity_fields = getattr(identity, 'fields', None) or []
        if not identity_fields:
            return

        # Get all field names
        all_field_names = set()
        fields_block = getattr(schema, 'fields', None)
        if fields_block:
            fields = getattr(fields_block, 'fields', []) or []
            for f in fields:
                name = getattr(f, 'name', None)
                if name:
                    all_field_names.add(name)

        for id_field in identity_fields:
            id_field_name = getattr(id_field, 'name', None)
            if id_field_name and id_field_name not in all_field_names:
                # Identity fields might be declared in identity block itself
                # Check if it's a self-contained declaration
                field_type = getattr(id_field, 'field_type', None)
                if not field_type:
                    line, col = self._get_location(id_field)
                    result.add_warning(
                        f"Identity field '{id_field_name}' not found in main fields block",
                        file=file_path, line=line, column=col, code="UNKNOWN_FIELD"
                    )
