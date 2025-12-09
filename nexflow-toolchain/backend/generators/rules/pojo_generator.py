"""
POJO Generator Mixin for Rules

Generates Java POJO classes for L4 Rules input/output types with multiple fields.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 POJO generates: Input/Output POJOs with builders, complete types
L4 POJO NEVER generates: Incomplete classes, missing methods
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import List, TYPE_CHECKING

from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    get_java_type,
)
from backend.generators.rules.pojo_builder import RulesPojoBuilderMixin

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class RulesPojoGeneratorMixin(RulesPojoBuilderMixin):
    """
    Mixin for generating Java POJO classes for rules input/output.

    Generates:
    - Output POJOs when multiple return parameters
    - Builder pattern for POJOs
    - Serializable implementations
    """

    def generate_output_pojo(
        self,
        table: 'ast.DecisionTableDef',
        package: str
    ) -> str:
        """Generate Output POJO class for decision table with multiple returns.

        Args:
            table: Decision table definition
            package: Java package name

        Returns:
            Complete Java class for output POJO
        """
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return ""

        params = getattr(return_spec, 'params', None) or []
        if len(params) <= 1:
            return ""

        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Output"

        lines = [
            self.generate_java_header(
                class_name, f"Output POJO for {table_name} decision table"
            ),
            f"package {package};",
            "",
            "import java.io.Serializable;",
            "import java.math.BigDecimal;",
            "import java.time.LocalDate;",
            "import java.time.Instant;",
            "import java.util.Objects;",
            "",
            f"/**",
            f" * Output data class for {table_name} decision table.",
            f" * Contains {len(params)} fields from return specification.",
            f" */",
            f"public class {class_name} implements Serializable {{",
            "",
            "    private static final long serialVersionUID = 1L;",
            "",
        ]

        # Generate fields
        for param in params:
            param_type = getattr(param, 'param_type', None)
            param_name = getattr(param, 'name', 'unknown')
            java_type = get_java_type(param_type)
            field_name = to_camel_case(param_name)
            lines.append(f"    private {java_type} {field_name};")

        lines.append("")

        # No-args constructor
        lines.append(f"    public {class_name}() {{}}")
        lines.append("")

        # All-args constructor
        lines.extend(self._generate_all_args_constructor(class_name, params))
        lines.append("")

        # Getters and setters
        for param in params:
            param_type = getattr(param, 'param_type', None)
            param_name = getattr(param, 'name', 'unknown')
            java_type = get_java_type(param_type)
            field_name = to_camel_case(param_name)
            pascal_name = to_pascal_case(param_name)

            lines.append(f"    public {java_type} get{pascal_name}() {{")
            lines.append(f"        return {field_name};")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    public void set{pascal_name}({java_type} {field_name}) {{")
            lines.append(f"        this.{field_name} = {field_name};")
            lines.append(f"    }}")
            lines.append("")

        # Builder
        lines.extend(self._generate_builder(class_name, params))
        lines.append("")

        # equals, hashCode, toString
        lines.extend(self._generate_equals_hashcode(class_name, params))
        lines.append("")
        lines.extend(self._generate_to_string(class_name, params))
        lines.append("")

        lines.append("}")

        return '\n'.join(lines)

    def should_generate_output_pojo(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if table needs an output POJO (multiple return params)."""
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return False
        params = getattr(return_spec, 'params', None) or []
        return len(params) > 1

    def get_output_type(self, table: 'ast.DecisionTableDef') -> str:
        """Get the appropriate output type for the table.

        Returns:
            - Simple type if single return param
            - POJO class name if multiple return params
            - "Object" if no return spec
        """
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return "Object"

        params = getattr(return_spec, 'params', None) or []
        if len(params) == 0:
            return "Object"

        if len(params) == 1:
            param_type = getattr(params[0], 'param_type', None)
            return get_java_type(param_type)

        table_name = getattr(table, 'name', 'unknown')
        return to_pascal_case(table_name) + "Output"

    def generate_java_header(self, class_name: str, description: str) -> str:
        """Generate Java file header comment."""
        return f'''/**
 * {description}
 *
 * Auto-generated by Nexflow L4 Rules Generator.
 * DO NOT EDIT - Changes will be overwritten.
 */'''
