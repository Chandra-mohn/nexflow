# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules Record Generator Mixin

Generates Java Record classes for L4 Rules output types with multiple fields.
Replaces the older POJO generator with modern Java 17+ Records.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Record generates: Output Records with withField(), builders, complete types
L4 Record NEVER generates: Incomplete classes, mutable state
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import TYPE_CHECKING

from backend.generators.common.record_builder import RecordBuilderMixin
from backend.generators.rules.utils import (
    to_pascal_case,
    get_java_type,
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class RulesRecordGeneratorMixin(RecordBuilderMixin):
    """
    Mixin for generating Java Record classes for rules output.

    Generates:
    - Output Records when multiple return parameters
    - Builder pattern for step-by-step construction
    - withField() methods for immutable updates
    - Serializable implementations for Flink
    """

    def generate_output_record(
        self,
        table: 'ast.DecisionTableDef',
        package: str
    ) -> str:
        """Generate Output Record class for decision table with multiple returns.

        Args:
            table: Decision table definition
            package: Java package name

        Returns:
            Complete Java record for output
        """
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return ""

        params = getattr(return_spec, 'params', None) or []
        if len(params) <= 1:
            return ""

        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Output"

        return self.generate_record_class(
            class_name=class_name,
            fields=params,
            package=package,
            description=f"Output record for {table_name} decision table. Contains {len(params)} fields from return specification.",
            field_name_accessor=lambda p: getattr(p, 'name', 'unknown'),
            field_type_accessor=lambda p: get_java_type(getattr(p, 'param_type', None)),
        )

    def should_generate_output_record(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if table needs an output Record (multiple return params)."""
        return_spec = getattr(table, 'return_spec', None)
        if not return_spec:
            return False

        params = getattr(return_spec, 'params', None) or []
        return len(params) > 1

    # Backwards compatibility aliases
    def generate_output_pojo(self, table: 'ast.DecisionTableDef', package: str) -> str:
        """Deprecated: Use generate_output_record() instead."""
        LOG.warning("generate_output_pojo is deprecated, use generate_output_record")
        return self.generate_output_record(table, package)

    def should_generate_output_pojo(self, table: 'ast.DecisionTableDef') -> bool:
        """Deprecated: Use should_generate_output_record() instead."""
        return self.should_generate_output_record(table)
