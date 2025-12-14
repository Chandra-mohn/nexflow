# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Decision Table Generator Mixin

Generates Java decision table evaluators from L4 Rules decision tables.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Decision Table generates: Complete evaluators with hit policies
L4 Decision Table NEVER generates: Placeholder stubs, incomplete evaluators
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List

from backend.ast import rules_ast as ast
from backend.generators.rules.utils import (
    to_pascal_case,
    get_java_type,
    get_common_imports,
    get_logging_imports,
    get_collection_imports,
    get_runtime_imports,
)
from backend.generators.rules.decision_table_rows import DecisionTableRowsMixin

LOG = logging.getLogger(__name__)


class DecisionTableGeneratorMixin(DecisionTableRowsMixin):
    """
    Mixin for generating Java decision table evaluator classes.

    Generates:
    - Rule evaluation methods with hit policies
    - Row matching logic
    - Result collection based on hit policy
    """

    def generate_decision_table_class(
        self,
        table: ast.DecisionTableDef,
        package: str
    ) -> str:
        """Generate complete decision table evaluator class."""
        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Table"
        input_type = class_name + "Input"
        output_type = self._get_output_type(table)

        # Derive package prefix for runtime imports (remove .rules suffix)
        package_prefix = package.rsplit('.', 1)[0] if '.rules' in package else package

        imports = self._collect_decision_table_imports(table, package_prefix)

        lines = [
            self.generate_java_header(
                class_name, f"Decision Table: {table_name}"
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

        lines.append(self._generate_evaluate_method(table, input_type, output_type))
        lines.append("")

        lines.append(self._generate_row_methods(table, input_type))
        lines.append("")

        lines.append(self._generate_input_class(table, input_type))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def _generate_evaluate_method(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate main evaluate method based on hit policy."""
        hit_policy = getattr(table, 'hit_policy', None) or ast.HitPolicyType.FIRST_MATCH

        if hit_policy == ast.HitPolicyType.FIRST_MATCH:
            return self._generate_first_match_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.MULTI_HIT:
            return self._generate_multi_hit_evaluate(table, input_type, output_type)
        if hit_policy == ast.HitPolicyType.SINGLE_HIT:
            return self._generate_single_hit_evaluate(table, input_type, output_type)

        LOG.warning(f"Unknown hit policy: {hit_policy}, defaulting to FIRST_MATCH")
        return self._generate_first_match_evaluate(table, input_type, output_type)

    def _generate_first_match_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate first-match hit policy evaluate method."""
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: FIRST_MATCH - returns first matching row's result",
            "     */",
            f"    public Optional<{output_type}> evaluate({input_type} input) {{",
        ]

        for i, row in enumerate(rows or []):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            return Optional.of(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "        // No matching rule",
            "        return Optional.empty();",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_multi_hit_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate multi-hit hit policy evaluate method."""
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: MULTI_HIT - returns all matching rows' results",
            "     */",
            f"    public List<{output_type}> evaluate({input_type} input) {{",
            f"        List<{output_type}> results = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows or []):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            results.add(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "",
            "        return results;",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_single_hit_evaluate(
        self,
        table: ast.DecisionTableDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate single-hit hit policy evaluate method."""
        table_name = getattr(table, 'name', 'unknown')
        decide = getattr(table, 'decide', None)
        matrix = getattr(decide, 'matrix', None) if decide else None
        rows = getattr(matrix, 'rows', None) if matrix else []

        lines = [
            "    /**",
            f"     * Evaluate decision table: {table_name}",
            "     * Hit Policy: SINGLE_HIT - validates exactly one row matches",
            "     */",
            f"    public {output_type} evaluate({input_type} input) {{",
            f"        List<{output_type}> matches = new ArrayList<>();",
            "",
        ]

        for i, row in enumerate(rows or []):
            method_name = f"matchRow{i + 1}"
            lines.append(f"        if ({method_name}(input)) {{")
            lines.append(f"            matches.add(getRow{i + 1}Result(input));")
            lines.append("        }")

        lines.extend([
            "",
            "        if (matches.isEmpty()) {",
            '            throw new IllegalStateException("No rule matched");',
            "        }",
            "        if (matches.size() > 1) {",
            '            throw new IllegalStateException("Multiple rules matched: " + matches.size());',
            "        }",
            "",
            "        return matches.get(0);",
            "    }",
        ])

        return '\n'.join(lines)

    def _get_output_type(self, table: ast.DecisionTableDef) -> str:
        """Get Java type for decision table output.

        Returns Output POJO class name if multiple return params,
        otherwise returns the Java type of the single return param.
        """
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return "String"

        params = getattr(return_spec, 'params', None) or []
        if len(params) == 0:
            return "String"

        # Multiple return params → use Output POJO
        if len(params) > 1:
            table_name = getattr(table, 'name', 'unknown')
            return to_pascal_case(table_name) + "Output"

        # Single return param → use its Java type
        param_type = getattr(params[0], 'param_type', None)
        return get_java_type(param_type)

    def _collect_decision_table_imports(
        self,
        table: ast.DecisionTableDef,
        package_prefix: str = None
    ) -> Set[str]:
        """Collect imports for decision table class.

        Args:
            table: DecisionTableDef AST node
            package_prefix: Package prefix for runtime imports (e.g., 'nexflow.flink')
        """
        imports = set()
        imports.update(get_collection_imports())
        imports.update(get_common_imports())
        imports.update(get_logging_imports())

        imports.update(self.get_condition_imports())
        imports.update(self.get_action_imports())

        # Add static import for NexflowRuntime built-in functions
        if package_prefix:
            imports.update(get_runtime_imports(package_prefix))

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
