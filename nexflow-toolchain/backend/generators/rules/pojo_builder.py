"""
Rules POJO Builder Mixin

Generates builder pattern and utility methods for rules POJOs.
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


class RulesPojoBuilderMixin:
    """
    Mixin for generating builder and utility methods for rules POJOs.

    Generates:
    - Builder inner class
    - equals and hashCode methods
    - toString method
    """

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
