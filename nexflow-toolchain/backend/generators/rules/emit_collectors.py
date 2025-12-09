"""
Emit Collectors Mixin

Collects emit targets from decision tables and procedural rules.
"""

import logging
from typing import List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class EmitCollectorsMixin:
    """
    Mixin for collecting emit targets from rule definitions.

    Provides:
    - Decision table emit target collection
    - Procedural rule emit target collection
    - Recursive block item traversal
    """

    def collect_emit_targets(
        self,
        table: 'ast.DecisionTableDef'
    ) -> List[str]:
        """Collect all unique emit targets from a decision table.

        Args:
            table: The decision table definition

        Returns:
            List of unique emit target names
        """
        from backend.ast import rules_ast as ast

        targets = set()

        decide = getattr(table, 'decide', None)
        if not decide:
            return sorted(list(targets))

        matrix = getattr(decide, 'matrix', None)
        if not matrix:
            return sorted(list(targets))

        rows = getattr(matrix, 'rows', None) or []
        for row in rows:
            cells = getattr(row, 'cells', None) or []
            for cell in cells:
                content = getattr(cell, 'content', None)
                if isinstance(content, ast.EmitAction):
                    target = getattr(content, 'target', None)
                    if target:
                        targets.add(target)

        return sorted(list(targets))

    def collect_emit_targets_from_procedural(
        self,
        rule: 'ast.ProceduralRuleDef'
    ) -> List[str]:
        """Collect all unique emit targets from a procedural rule.

        Args:
            rule: The procedural rule definition

        Returns:
            List of unique emit target names
        """
        targets: Set[str] = set()
        items = getattr(rule, 'items', None) or []
        self._collect_emit_targets_from_block_items(items, targets)
        return sorted(list(targets))

    def _collect_emit_targets_from_block_items(
        self,
        items: List,
        targets: Set[str]
    ) -> None:
        """Recursively collect emit targets from block items."""
        from backend.ast import rules_ast as ast

        if not items:
            return

        for item in items:
            if isinstance(item, ast.RuleStep):
                # Check then block
                then_block = getattr(item, 'then_block', None)
                if then_block:
                    block_items = getattr(then_block, 'items', None) or []
                    self._collect_emit_targets_from_block_items(block_items, targets)

                # Check elseif branches
                elseif_branches = getattr(item, 'elseif_branches', None) or []
                for branch in elseif_branches:
                    block = getattr(branch, 'block', None)
                    if block:
                        block_items = getattr(block, 'items', None) or []
                        self._collect_emit_targets_from_block_items(block_items, targets)

                # Check else block
                else_block = getattr(item, 'else_block', None)
                if else_block:
                    block_items = getattr(else_block, 'items', None) or []
                    self._collect_emit_targets_from_block_items(block_items, targets)

            elif isinstance(item, ast.ActionSequence):
                # Check actions for EmitAction
                actions = getattr(item, 'actions', None) or []
                for action in actions:
                    if isinstance(action, ast.EmitAction):
                        target = getattr(action, 'target', None)
                        if target:
                            targets.add(target)

            elif isinstance(item, ast.EmitAction):
                # Direct EmitAction item
                target = getattr(item, 'target', None)
                if target:
                    targets.add(target)

    def has_emit_actions(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table contains any emit actions."""
        return len(self.collect_emit_targets(table)) > 0

    def requires_process_function(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if table requires ProcessFunction (for side outputs).

        Decision tables with emit actions need ProcessFunction instead of
        simple Function to access the Context for side outputs.
        """
        return self.has_emit_actions(table)
