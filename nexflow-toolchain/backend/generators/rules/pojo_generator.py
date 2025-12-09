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

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class RulesPojoGeneratorMixin:
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

    def _generate_all_args_constructor(
        self,
        class_name: str,
        params: List['ast.ReturnParam']
    ) -> List[str]:
        """Generate all-arguments constructor."""
        lines = []

        # Constructor signature
        constructor_params = ", ".join(
            f"{get_java_type(getattr(p, 'param_type', None))} {to_camel_case(getattr(p, 'name', 'unknown'))}"
            for p in params
        )
        lines.append(f"    public {class_name}({constructor_params}) {{")

        # Assignments
        for param in params:
            param_name = getattr(param, 'name', 'unknown')
            field_name = to_camel_case(param_name)
            lines.append(f"        this.{field_name} = {field_name};")

        lines.append("    }")

        return lines

    def _generate_builder(
        self,
        class_name: str,
        params: List['ast.ReturnParam']
    ) -> List[str]:
        """Generate Builder inner class."""
        lines = [
            f"    /**",
            f"     * Builder for {class_name}.",
            f"     */",
            f"    public static class Builder {{",
        ]

        # Builder fields
        for param in params:
            param_type = getattr(param, 'param_type', None)
            param_name = getattr(param, 'name', 'unknown')
            java_type = get_java_type(param_type)
            field_name = to_camel_case(param_name)
            lines.append(f"        private {java_type} {field_name};")

        lines.append("")

        # Builder setters (returning this for chaining)
        for param in params:
            param_type = getattr(param, 'param_type', None)
            param_name = getattr(param, 'name', 'unknown')
            java_type = get_java_type(param_type)
            field_name = to_camel_case(param_name)

            lines.append(f"        public Builder {field_name}({java_type} {field_name}) {{")
            lines.append(f"            this.{field_name} = {field_name};")
            lines.append(f"            return this;")
            lines.append(f"        }}")
            lines.append("")

        # Build method
        lines.append(f"        public {class_name} build() {{")
        args = ", ".join(to_camel_case(getattr(p, 'name', 'unknown')) for p in params)
        lines.append(f"            return new {class_name}({args});")
        lines.append(f"        }}")

        lines.append("    }")
        lines.append("")

        # Static builder() method
        lines.append(f"    public static Builder builder() {{")
        lines.append(f"        return new Builder();")
        lines.append(f"    }}")

        return lines

    def _generate_equals_hashcode(
        self,
        class_name: str,
        params: List['ast.ReturnParam']
    ) -> List[str]:
        """Generate equals and hashCode methods."""
        field_names = [to_camel_case(getattr(p, 'name', 'unknown')) for p in params]

        lines = [
            f"    @Override",
            f"    public boolean equals(Object o) {{",
            f"        if (this == o) return true;",
            f"        if (o == null || getClass() != o.getClass()) return false;",
            f"        {class_name} that = ({class_name}) o;",
        ]

        # Generate equals comparisons
        comparisons = " && ".join(
            f"Objects.equals({fn}, that.{fn})" for fn in field_names
        )
        lines.append(f"        return {comparisons};")
        lines.append(f"    }}")
        lines.append("")

        # hashCode
        lines.append(f"    @Override")
        lines.append(f"    public int hashCode() {{")
        hash_args = ", ".join(field_names)
        lines.append(f"        return Objects.hash({hash_args});")
        lines.append(f"    }}")

        return lines

    def _generate_to_string(
        self,
        class_name: str,
        params: List['ast.ReturnParam']
    ) -> List[str]:
        """Generate toString method."""
        field_names = [to_camel_case(getattr(p, 'name', 'unknown')) for p in params]

        lines = [
            f"    @Override",
            f"    public String toString() {{",
            f'        return "{class_name}{{" +',
        ]

        for i, fn in enumerate(field_names):
            if i == 0:
                lines.append(f'            "{fn}=" + {fn} +')
            else:
                lines.append(f'            ", {fn}=" + {fn} +')

        lines.append(f'            "}}";')
        lines.append(f"    }}")

        return lines

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
