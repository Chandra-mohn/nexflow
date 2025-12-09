"""
Emit Generator Mixin

Generates Java code for L4 Rules emit actions - Flink side output emission.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Emit generates: OutputTag declarations, side output collection, emit helpers
L4 Emit NEVER generates: Incomplete stubs, placeholder code
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List, Optional, TYPE_CHECKING

from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class EmitGeneratorMixin:
    """
    Mixin for generating Java emit action code for Flink side outputs.

    Generates:
    - OutputTag declarations for emit targets
    - Side output emission via ProcessFunction.Context
    - Helper methods for type-safe emission
    """

    def generate_emit_action(
        self,
        action: 'ast.EmitAction',
        value_expr: str = "result"
    ) -> str:
        """Generate Java code for an emit action.

        Args:
            action: The EmitAction AST node
            value_expr: Expression for the value to emit

        Returns:
            Java code for the emit operation
        """
        if action is None:
            LOG.warning("Null EmitAction provided")
            return "        // ERROR: null emit action"

        target = getattr(action, 'target', None)
        if not target:
            LOG.warning("EmitAction missing target")
            return "        // ERROR: emit action missing target"

        tag_name = to_camel_case(target) + "OutputTag"
        return f"        ctx.output({tag_name}, {value_expr});"

    def generate_output_tag_declaration(
        self,
        target_name: str,
        output_type: str = "Object"
    ) -> str:
        """Generate OutputTag constant declaration.

        Args:
            target_name: Name of the emit target
            output_type: Java type for the output

        Returns:
            Java OutputTag declaration
        """
        if not target_name:
            LOG.warning("Empty target_name for OutputTag declaration")
            return "    // ERROR: empty target name for OutputTag"

        tag_name = to_camel_case(target_name) + "OutputTag"
        tag_id = target_name.lower().replace('_', '-')

        return f'''    /**
     * Side output tag for {target_name} emissions.
     */
    public static final OutputTag<{output_type}> {tag_name} =
        new OutputTag<{output_type}>("{tag_id}") {{}};'''

    def generate_emit_helper_method(
        self,
        target_name: str,
        output_type: str = "Object"
    ) -> str:
        """Generate type-safe emit helper method.

        Args:
            target_name: Name of the emit target
            output_type: Java type for the output

        Returns:
            Java helper method for emission
        """
        if not target_name:
            LOG.warning("Empty target_name for emit helper method")
            return "    // ERROR: empty target name for emit helper"

        method_name = "emitTo" + to_pascal_case(target_name)
        tag_name = to_camel_case(target_name) + "OutputTag"

        return f'''    /**
     * Emit a value to the {target_name} side output.
     *
     * @param ctx ProcessFunction context
     * @param value The value to emit
     */
    protected void {method_name}(Context ctx, {output_type} value) {{
        ctx.output({tag_name}, value);
    }}'''

    def generate_all_output_tags(
        self,
        table: 'ast.DecisionTableDef',
        output_types: Optional[dict] = None
    ) -> str:
        """Generate all OutputTag declarations for a decision table.

        Args:
            table: Decision table definition
            output_types: Optional mapping of target names to Java types

        Returns:
            Java code for all OutputTag declarations
        """
        emit_targets = self.collect_emit_targets(table)

        if not emit_targets:
            return ""

        output_types = output_types or {}
        lines = ["    // Side output tags for emit actions"]

        for target in emit_targets:
            output_type = output_types.get(target, "Object")
            lines.append(self.generate_output_tag_declaration(target, output_type))
            lines.append("")

        return '\n'.join(lines)

    def generate_all_emit_helpers(
        self,
        table: 'ast.DecisionTableDef',
        output_types: Optional[dict] = None
    ) -> str:
        """Generate all emit helper methods for a decision table.

        Args:
            table: Decision table definition
            output_types: Optional mapping of target names to Java types

        Returns:
            Java code for all emit helper methods
        """
        emit_targets = self.collect_emit_targets(table)

        if not emit_targets:
            return ""

        output_types = output_types or {}
        lines = []

        for target in emit_targets:
            output_type = output_types.get(target, "Object")
            lines.append(self.generate_emit_helper_method(target, output_type))
            lines.append("")

        return '\n'.join(lines)

    def generate_side_output_getters(
        self,
        table: 'ast.DecisionTableDef'
    ) -> str:
        """Generate public getters for OutputTags (for downstream consumption).

        Args:
            table: Decision table definition

        Returns:
            Java code for OutputTag getter methods
        """
        emit_targets = self.collect_emit_targets(table)

        if not emit_targets:
            return ""

        lines = []
        for target in emit_targets:
            tag_name = to_camel_case(target) + "OutputTag"
            getter_name = "get" + to_pascal_case(target) + "OutputTag"

            lines.append(f'''    /**
     * Get the OutputTag for {target} side output.
     * Use this to collect side outputs from the ProcessFunction result.
     */
    public static OutputTag<Object> {getter_name}() {{
        return {tag_name};
    }}''')
            lines.append("")

        return '\n'.join(lines)

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

    def get_emit_imports(self) -> Set[str]:
        """Get required imports for emit generation."""
        return {
            'org.apache.flink.util.OutputTag',
            'org.apache.flink.streaming.api.functions.ProcessFunction',
        }
