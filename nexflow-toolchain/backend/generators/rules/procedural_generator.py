"""
Procedural Generator Mixin

Generates Java code from L4 Rules procedural rule definitions.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Procedural generates: Complete rule execution methods, all conditionals
L4 Procedural NEVER generates: Placeholder stubs, incomplete rules
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    generate_value_expr,
    get_common_imports,
    get_logging_imports,
)
from backend.generators.rules.procedural_expressions import ProceduralExpressionsMixin

LOG = logging.getLogger(__name__)


class ProceduralGeneratorMixin(ProceduralExpressionsMixin):
    """
    Mixin for generating Java procedural rule classes.

    Generates:
    - Rule evaluation methods with conditionals
    - If-then-else chains
    - Action sequences
    """

    def generate_procedural_rule_class(
        self,
        rule: ast.ProceduralRuleDef,
        package: str
    ) -> str:
        """Generate complete procedural rule class."""
        rule_name = getattr(rule, 'name', 'unknown')
        class_name = to_pascal_case(rule_name) + "Rule"

        imports = self._collect_procedural_imports(rule)

        lines = [
            self.generate_java_header(
                class_name, f"Procedural Rule: {rule_name}"
            ),
            f"package {package};",
            "",
            self.generate_imports(list(imports)),
            "",
            f"public class {class_name} {{",
            "",
            "    private static final Logger LOG = LoggerFactory.getLogger("
            f"{class_name}.class);",
            "",
        ]

        lines.append(self._generate_execute_method(rule))
        lines.append("")

        action_stubs = self._generate_action_stubs(rule)
        if action_stubs:
            lines.append(action_stubs)
            lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_action_stubs(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate stub methods for all action calls in the rule."""
        actions = set()
        self._collect_action_calls(getattr(rule, 'items', None) or [], actions)

        if not actions:
            return ""

        lines = [
            "    // =========================================================================",
            "    // Action Method Stubs - Implement these methods for rule execution",
            "    // =========================================================================",
            "",
        ]

        for action_name, arg_count in sorted(actions):
            method_name = to_camel_case(action_name)
            params = ", ".join(f"Object arg{i}" for i in range(arg_count)) if arg_count > 0 else ""
            lines.extend([
                f"    /**",
                f"     * Action: {action_name}",
                f"     * TODO: Implement this action method.",
                f"     */",
                f"    protected void {method_name}({params}) {{",
                f'        throw new UnsupportedOperationException("Action {action_name} not implemented");',
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def _collect_action_calls(self, items, actions: set):
        """Recursively collect all action calls from block items."""
        for item in items:
            if isinstance(item, ast.RuleStep):
                then_block = getattr(item, 'then_block', None)
                if then_block:
                    self._collect_action_calls(getattr(then_block, 'items', None) or [], actions)

                elseif_branches = getattr(item, 'elseif_branches', None) or []
                for branch in elseif_branches:
                    branch_block = getattr(branch, 'block', None)
                    if branch_block:
                        self._collect_action_calls(getattr(branch_block, 'items', None) or [], actions)

                else_block = getattr(item, 'else_block', None)
                if else_block:
                    self._collect_action_calls(getattr(else_block, 'items', None) or [], actions)

            elif isinstance(item, ast.ActionSequence):
                action_list = getattr(item, 'actions', None) or []
                for action in action_list:
                    name = getattr(action, 'name', None)
                    args = getattr(action, 'arguments', None) or []
                    if name:
                        actions.add((name, len(args)))

    def _generate_execute_method(self, rule: ast.ProceduralRuleDef) -> str:
        """Generate main execute method for procedural rule."""
        rule_name = getattr(rule, 'name', 'unknown')
        lines = [
            "    /**",
            f"     * Execute rule: {rule_name}",
            "     */",
            "    public void execute(Object context) {",
        ]

        items = getattr(rule, 'items', None) or []
        for item in items:
            lines.append(self._generate_block_item(item, 2))

        lines.append("    }")

        return '\n'.join(lines)

    def _generate_block_item(self, item, indent: int) -> str:
        """Generate code for a block item."""
        prefix = "    " * indent

        if item is None:
            LOG.warning("Null block item provided")
            return f"{prefix}// ERROR: null block item"

        if isinstance(item, ast.RuleStep):
            return self._generate_rule_step(item, indent)

        if isinstance(item, ast.ActionSequence):
            return self._generate_action_sequence(item, indent)

        if isinstance(item, ast.ReturnStatement):
            return f"{prefix}return;"

        if isinstance(item, ast.SetStatement):
            variable = to_camel_case(getattr(item, 'variable', 'unknown'))
            value = generate_value_expr(getattr(item, 'value', None))
            return f"{prefix}{variable} = {value};"

        if isinstance(item, ast.LetStatement):
            variable = to_camel_case(getattr(item, 'variable', 'unknown'))
            value = generate_value_expr(getattr(item, 'value', None))
            # For now, use Object type for let statements (could be improved with type inference)
            return f"{prefix}var {variable} = {value};"

        LOG.warning(f"Unknown block item type: {type(item).__name__}")
        return f"{prefix}// UNSUPPORTED: {type(item).__name__}"

    def _generate_rule_step(self, step: ast.RuleStep, indent: int) -> str:
        """Generate if-then-elseif-else structure."""
        prefix = "    " * indent
        lines = []

        condition = getattr(step, 'condition', None)
        condition_str = self._generate_boolean_expr(condition, "context")
        lines.append(f"{prefix}if ({condition_str}) {{")

        then_block = getattr(step, 'then_block', None)
        if then_block:
            then_items = getattr(then_block, 'items', None) or []
            for item in then_items:
                lines.append(self._generate_block_item(item, indent + 1))

        elseif_branches = getattr(step, 'elseif_branches', None) or []
        for branch in elseif_branches:
            branch_condition = getattr(branch, 'condition', None)
            branch_cond = self._generate_boolean_expr(branch_condition, "context")
            lines.append(f"{prefix}}} else if ({branch_cond}) {{")
            branch_block = getattr(branch, 'block', None)
            if branch_block:
                branch_items = getattr(branch_block, 'items', None) or []
                for item in branch_items:
                    lines.append(self._generate_block_item(item, indent + 1))

        else_block = getattr(step, 'else_block', None)
        if else_block:
            lines.append(f"{prefix}}} else {{")
            else_items = getattr(else_block, 'items', None) or []
            for item in else_items:
                lines.append(self._generate_block_item(item, indent + 1))

        lines.append(f"{prefix}}}")

        return '\n'.join(lines)

    def _generate_action_sequence(
        self,
        seq: ast.ActionSequence,
        indent: int
    ) -> str:
        """Generate action sequence."""
        prefix = "    " * indent
        lines = []

        actions = getattr(seq, 'actions', None) or []
        for action in actions:
            action_name = getattr(action, 'name', 'unknown')
            func_name = to_camel_case(action_name)
            arguments = getattr(action, 'arguments', None) or []
            args = ", ".join(generate_value_expr(a) for a in arguments)
            lines.append(f"{prefix}{func_name}({args});")

        return '\n'.join(lines)

    def _collect_procedural_imports(self, rule: ast.ProceduralRuleDef) -> Set[str]:
        """Collect imports for procedural rule class."""
        imports = set()
        imports.update(get_common_imports())
        imports.update(get_logging_imports())
        return imports

    def generate_java_header(self, class_name: str, description: str) -> str:
        """Generate Java file header comment."""
        return f'''/**
 * {description}
 *
 * Auto-generated by Nexflow L4 Rules Generator.
 * DO NOT EDIT - Changes will be overwritten.
 */'''

    def generate_imports(self, imports: List[str]) -> str:
        """Generate import statements."""
        sorted_imports = sorted(imports)
        return '\n'.join(f'import {imp};' for imp in sorted_imports)
