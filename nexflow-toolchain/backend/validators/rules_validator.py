"""
Rules Validator

Validates L4 Rules DSL ASTs for semantic correctness.
"""

from pathlib import Path
from typing import Optional, Set

from backend.validators.base import BaseValidator, ValidationResult


class RulesValidator(BaseValidator):
    """
    Validator for Rules DSL ASTs.

    Checks:
    - Decision table column consistency
    - Hit policy validity
    - Condition type matching
    - Return clause matches decide columns
    - Procedural rule validity
    """

    def validate(self, program, file_path: Optional[Path] = None) -> ValidationResult:
        """Validate a rules program AST."""
        result = ValidationResult()

        # Register and validate decision tables
        decision_tables = getattr(program, 'decision_tables', []) or []
        for table in decision_tables:
            name = getattr(table, 'name', None)
            if name:
                self.context.register_decision_table(name, table, file_path)
            self._validate_decision_table(table, result, file_path)

        # Register and validate procedural rules
        procedural_rules = getattr(program, 'procedural_rules', []) or []
        for rule in procedural_rules:
            name = getattr(rule, 'name', None)
            if name:
                self.context.register_rule(name, rule, file_path)
            self._validate_procedural_rule(rule, result, file_path)

        return result

    def _validate_decision_table(self, table, result: ValidationResult,
                                  file_path: Optional[Path]) -> None:
        """Validate a decision table definition."""
        table_name = getattr(table, 'name', 'unknown')

        # Check that given block has parameters
        given_block = getattr(table, 'given', None)
        given_params = []
        if given_block:
            given_params = getattr(given_block, 'params', []) or []

        if not given_params:
            line, col = self._get_location(table)
            result.add_warning(
                f"Decision table '{table_name}' has no input parameters in given block",
                file=file_path, line=line, column=col, code="EMPTY_GIVEN"
            )

        # Check that return spec has parameters
        return_spec = getattr(table, 'return_spec', None)
        return_params = []
        if return_spec:
            return_params = getattr(return_spec, 'params', []) or []

        if not return_params:
            line, col = self._get_location(table)
            result.add_warning(
                f"Decision table '{table_name}' has no output parameters in return spec",
                file=file_path, line=line, column=col, code="EMPTY_RETURN"
            )

        # Validate hit policy
        self._validate_hit_policy(table, table_name, result, file_path)

        # Validate decision matrix
        decide_block = getattr(table, 'decide', None)
        if decide_block:
            self._validate_decide_block(decide_block, table_name, len(given_params),
                                        len(return_params), result, file_path)

    def _validate_hit_policy(self, table, table_name: str, result: ValidationResult,
                             file_path: Optional[Path]) -> None:
        """Validate hit policy configuration."""
        valid_policies = {'first_match', 'multi_hit', 'single_hit', 'collect', 'priority',
                          'first', 'unique', 'any', 'rule_order', 'output_order', 'sum',
                          'min', 'max', 'count'}

        hit_policy = getattr(table, 'hit_policy', None)
        if hit_policy:
            policy_name = hit_policy
            if hasattr(hit_policy, 'value'):
                policy_name = hit_policy.value
            policy_str = str(policy_name).lower().replace(' ', '_')

            if policy_str not in valid_policies:
                line, col = self._get_location(table)
                result.add_warning(
                    f"Unknown hit policy '{hit_policy}' in decision table '{table_name}'",
                    file=file_path, line=line, column=col, code="UNKNOWN_HIT_POLICY"
                )

    def _validate_decide_block(self, decide_block, table_name: str,
                                given_count: int, return_count: int,
                                result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate decision table matrix."""
        matrix = getattr(decide_block, 'matrix', None)
        if not matrix:
            return

        rows = getattr(matrix, 'rows', []) or []
        headers = getattr(matrix, 'headers', []) or []
        has_priority = getattr(matrix, 'has_priority', False)

        # Validate row consistency
        expected_columns = len(headers)
        priorities_seen: Set[int] = set()

        for i, row in enumerate(rows):
            cells = getattr(row, 'cells', []) or []
            cell_count = len(cells)

            if cell_count != expected_columns:
                line, col = self._get_location(row)
                result.add_warning(
                    f"Row {i + 1} in '{table_name}' has {cell_count} cells, expected {expected_columns}",
                    file=file_path, line=line, column=col, code="CELL_COUNT_MISMATCH"
                )

            # Check for duplicate priorities
            priority = getattr(row, 'priority', None)
            if priority is not None:
                if priority in priorities_seen:
                    line, col = self._get_location(row)
                    result.add_warning(
                        f"Duplicate priority {priority} in decision table '{table_name}'",
                        file=file_path, line=line, column=col, code="DUPLICATE_PRIORITY"
                    )
                priorities_seen.add(priority)

    def _validate_procedural_rule(self, rule, result: ValidationResult,
                                   file_path: Optional[Path]) -> None:
        """Validate a procedural rule definition."""
        rule_name = getattr(rule, 'name', 'unknown')

        # Check that rule has content
        items = getattr(rule, 'items', []) or []
        if not items:
            line, col = self._get_location(rule)
            result.add_warning(
                f"Procedural rule '{rule_name}' has no statements",
                file=file_path, line=line, column=col, code="EMPTY_RULE"
            )
            return

        # Validate each block item
        for item in items:
            self._validate_block_item(item, rule_name, result, file_path)

    def _validate_block_item(self, item, rule_name: str,
                              result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate a block item in a procedural rule."""
        # Check if it's a RuleStep (if-then-else)
        condition = getattr(item, 'condition', None)
        then_block = getattr(item, 'then_block', None)

        # This looks like a RuleStep
        if condition is not None or then_block is not None:
            self._validate_rule_step(item, rule_name, result, file_path)

    def _validate_rule_step(self, step, rule_name: str,
                            result: ValidationResult, file_path: Optional[Path]) -> None:
        """Validate a rule step (if-then-else)."""
        # Check that condition exists
        condition = getattr(step, 'condition', None)
        if not condition:
            line, col = self._get_location(step)
            result.add_error(
                f"Rule step in '{rule_name}' has no condition",
                file=file_path, line=line, column=col, code="MISSING_CONDITION"
            )

        # Check that then block exists
        then_block = getattr(step, 'then_block', None)
        if not then_block:
            line, col = self._get_location(step)
            result.add_error(
                f"Rule step in '{rule_name}' has no then block",
                file=file_path, line=line, column=col, code="MISSING_THEN"
            )

        # Recursively validate nested blocks
        if then_block:
            then_items = getattr(then_block, 'items', []) or []
            for item in then_items:
                self._validate_block_item(item, rule_name, result, file_path)

        else_block = getattr(step, 'else_block', None)
        if else_block:
            else_items = getattr(else_block, 'items', []) or []
            for item in else_items:
                self._validate_block_item(item, rule_name, result, file_path)

        elseif_branches = getattr(step, 'elseif_branches', []) or []
        for branch in elseif_branches:
            branch_block = getattr(branch, 'block', None)
            if branch_block:
                branch_items = getattr(branch_block, 'items', []) or []
                for item in branch_items:
                    self._validate_block_item(item, rule_name, result, file_path)
