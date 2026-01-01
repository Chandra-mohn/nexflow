# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Proc Validator

Validates L1 Proc DSL ASTs for semantic correctness.
"""

from pathlib import Path
from typing import Optional, Set

from backend.validators.base import BaseValidator, ValidationResult


class ProcValidator(BaseValidator):
    """
    Validator for Proc DSL ASTs.

    Checks:
    - Schema references exist (or will be provided)
    - Transform references exist
    - Rule references exist
    - State references valid
    - Emit targets are consistent
    - Windowing configuration validity
    """

    def validate(self, program, file_path: Optional[Path] = None) -> ValidationResult:
        """Validate a proc program AST."""
        result = ValidationResult()

        for process in program.processes:
            self.context.register_flow(process.name, process, file_path)
            self._validate_process(process, result, file_path)

        return result

    def _validate_process(self, process, result: ValidationResult,
                          file_path: Optional[Path]) -> None:
        """Validate a single process definition."""
        # Validate inputs
        if hasattr(process, 'inputs') and process.inputs:
            for input_decl in process.inputs:
                self._validate_input(input_decl, process, result, file_path)

        # Validate processing operators
        if hasattr(process, 'processing') and process.processing:
            self._validate_processing(process.processing, process, result, file_path)

        # Validate outputs
        if hasattr(process, 'outputs') and process.outputs:
            for output_decl in process.outputs:
                self._validate_output(output_decl, process, result, file_path)

        # Validate state configuration
        if hasattr(process, 'state') and process.state:
            self._validate_state(process.state, process, result, file_path)

        # Validate windowing
        if hasattr(process, 'window') and process.window:
            self._validate_window(process.window, process, result, file_path)

        # Validate error handling
        if hasattr(process, 'error_handling') and process.error_handling:
            self._validate_error_handling(process.error_handling, process, result, file_path)

        # Check parallelism hint
        if hasattr(process, 'parallelism') and process.parallelism:
            if process.parallelism <= 0:
                line, col = self._get_location(process)
                result.add_error(
                    f"Process '{process.name}' has invalid parallelism: {process.parallelism}",
                    file=file_path, line=line, column=col, code="INVALID_PARALLELISM"
                )

    def _validate_input(self, input_decl, process,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate an input declaration."""
        # Check schema reference (warning only - might be defined elsewhere)
        schema_name = getattr(input_decl, 'schema_name', None) or getattr(input_decl, 'schema', None)
        if schema_name:
            if isinstance(schema_name, str) and not self.context.has_schema(schema_name):
                line, col = self._get_location(input_decl)
                result.add_warning(
                    f"Process '{process.name}' references schema '{schema_name}' "
                    "which is not registered (may be defined in another file)",
                    file=file_path, line=line, column=col, code="UNRESOLVED_SCHEMA"
                )

        # Check source name is provided
        source_name = getattr(input_decl, 'source_name', None) or getattr(input_decl, 'source', None)
        if not source_name:
            line, col = self._get_location(input_decl)
            result.add_warning(
                f"Input in process '{process.name}' has no source name",
                file=file_path, line=line, column=col, code="MISSING_SOURCE"
            )

    def _validate_processing(self, processing, process,
                             result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate processing operators."""
        # Validate enrich declarations
        enrichments = getattr(processing, 'enrichments', None) or getattr(processing, 'enrich', None)
        if enrichments:
            for enrich in enrichments:
                self._validate_enrich(enrich, process, result, file_path)

        # Validate transform declarations
        transforms = getattr(processing, 'transforms', None) or getattr(processing, 'transform', None)
        if transforms:
            for transform in (transforms if isinstance(transforms, list) else [transforms]):
                self._validate_transform_ref(transform, process, result, file_path)

        # Validate route declarations
        routes = getattr(processing, 'routes', None) or getattr(processing, 'route', None)
        if routes:
            for route in (routes if isinstance(routes, list) else [routes]):
                self._validate_route(route, process, result, file_path)

    def _validate_enrich(self, enrich, process,
                         result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate an enrich declaration."""
        lookup_name = getattr(enrich, 'lookup_name', None) or getattr(enrich, 'lookup', None)
        if not lookup_name:
            line, col = self._get_location(enrich)
            result.add_warning(
                f"Enrich in process '{process.name}' has no lookup name",
                file=file_path, line=line, column=col, code="MISSING_LOOKUP"
            )

    def _validate_transform_ref(self, transform, process,
                                result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate a transform reference."""
        transform_name = getattr(transform, 'transform_name', None) or getattr(transform, 'name', None)
        if transform_name:
            if isinstance(transform_name, str) and not self.context.has_transform(transform_name):
                line, col = self._get_location(transform)
                result.add_warning(
                    f"Process '{process.name}' references transform '{transform_name}' "
                    "which is not registered (may be defined in another file)",
                    file=file_path, line=line, column=col, code="UNRESOLVED_TRANSFORM"
                )

    def _validate_route(self, route, process,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate a route declaration."""
        rule_name = getattr(route, 'rule_name', None) or getattr(route, 'rules', None)
        if rule_name:
            if isinstance(rule_name, str) and not self.context.has_rule(rule_name):
                line, col = self._get_location(route)
                result.add_warning(
                    f"Process '{process.name}' references rule '{rule_name}' "
                    "which is not registered (may be defined in another file)",
                    file=file_path, line=line, column=col, code="UNRESOLVED_RULE"
                )

    def _validate_output(self, output_decl, process,
                         result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate an output declaration."""
        # Check schema reference
        schema_name = getattr(output_decl, 'schema_name', None) or getattr(output_decl, 'schema', None)
        if schema_name:
            if isinstance(schema_name, str) and not self.context.has_schema(schema_name):
                line, col = self._get_location(output_decl)
                result.add_warning(
                    f"Output in process '{process.name}' references schema '{schema_name}' "
                    "which is not registered",
                    file=file_path, line=line, column=col, code="UNRESOLVED_SCHEMA"
                )

    def _validate_state(self, state, process,
                        result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate state configuration."""
        # Check state references
        uses = getattr(state, 'uses', None)
        if uses:
            for state_name in (uses if isinstance(uses, list) else [uses]):
                if not state_name:
                    line, col = self._get_location(state)
                    result.add_error(
                        f"Empty state reference in process '{process.name}'",
                        file=file_path, line=line, column=col, code="EMPTY_STATE_REF"
                    )

        # Validate local state declarations
        local_states = getattr(state, 'local_states', None) or getattr(state, 'locals', None)
        if local_states:
            seen_names: Set[str] = set()
            for local_state in local_states:
                name = getattr(local_state, 'name', None)
                if name:
                    if name in seen_names:
                        line, col = self._get_location(local_state)
                        result.add_error(
                            f"Duplicate local state name '{name}' in process '{process.name}'",
                            file=file_path, line=line, column=col, code="DUPLICATE_STATE"
                        )
                    seen_names.add(name)

    def _validate_window(self, window, process,
                         result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate windowing configuration."""
        # Check window type
        valid_types = {'tumbling', 'sliding', 'session', 'global'}
        window_type = getattr(window, 'window_type', None) or getattr(window, 'type', None)
        if window_type:
            wtype = str(window_type).lower()
            if hasattr(window_type, 'value'):
                wtype = window_type.value.lower()
            if wtype not in valid_types:
                line, col = self._get_location(window)
                result.add_warning(
                    f"Unknown window type '{window_type}' in process '{process.name}'",
                    file=file_path, line=line, column=col, code="UNKNOWN_WINDOW_TYPE"
                )

        # Check window size is positive
        size = getattr(window, 'size', None)
        if size:
            if hasattr(size, 'value') and size.value <= 0:
                line, col = self._get_location(window)
                result.add_error(
                    f"Window size must be positive in process '{process.name}'",
                    file=file_path, line=line, column=col, code="INVALID_WINDOW_SIZE"
                )

    def _validate_error_handling(self, error_handling, process,
                                  result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate error handling configuration."""
        valid_actions = {'dead_letter', 'retry', 'skip', 'fail'}

        handlers = getattr(error_handling, 'handlers', None)
        if handlers:
            for handler in handlers:
                action = getattr(handler, 'action', None)
                if action:
                    action_str = str(action).lower()
                    if hasattr(action, 'value'):
                        action_str = action.value.lower()
                    if action_str not in valid_actions:
                        line, col = self._get_location(handler)
                        result.add_warning(
                            f"Unknown error action '{action}' in process '{process.name}'",
                            file=file_path, line=line, column=col, code="UNKNOWN_ERROR_ACTION"
                        )
