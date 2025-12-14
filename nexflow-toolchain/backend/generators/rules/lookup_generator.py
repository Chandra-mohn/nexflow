# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Lookup Generator Mixin

Generates Java code for L4 Rules lookup actions - external data enrichment.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Lookup generates: Async lookup methods, default fallbacks, temporal lookups
L4 Lookup NEVER generates: Placeholder stubs, incomplete implementations
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List, Optional, TYPE_CHECKING

from backend.generators.rules.utils import (
    to_camel_case,
    to_setter,
    generate_value_expr,
    get_concurrent_imports,
    get_time_imports,
)
from backend.generators.rules.lookup_cache import LookupCacheMixin

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class LookupGeneratorMixin(LookupCacheMixin):
    """
    Mixin for generating Java lookup action code.

    Generates:
    - Async lookup method calls for external data sources
    - Default value fallback handling
    - Temporal (as_of) lookup support
    - Lookup result caching
    """

    def generate_lookup_action(
        self,
        action: 'ast.LookupAction',
        output_var: str,
        output_field: Optional[str] = None
    ) -> str:
        """Generate Java code for a lookup action.

        Args:
            action: The LookupAction AST node
            output_var: Variable to store result
            output_field: Optional field to set on output

        Returns:
            Java code for the lookup operation
        """
        if action is None:
            LOG.warning("Null LookupAction provided")
            return "        // ERROR: null lookup action"

        table_name = getattr(action, 'table_name', None)
        if not table_name:
            LOG.warning("LookupAction missing table_name")
            return "        // ERROR: lookup action missing table_name"

        lookup_method = to_camel_case(table_name) + "Lookup"

        # Generate key arguments with null safety
        keys = getattr(action, 'keys', None) or []
        key_args = ", ".join(generate_value_expr(key) for key in keys)

        lines = []

        # Check for temporal (as_of) lookup
        as_of = getattr(action, 'as_of', None)
        if as_of:
            as_of_expr = generate_value_expr(as_of)
            lines.append(f"        // Temporal lookup: {table_name} as of {as_of_expr}")
            lines.append(f"        var lookupResult = {lookup_method}AsOf({key_args}, {as_of_expr});")
        else:
            lines.append(f"        // Lookup: {table_name}")
            lines.append(f"        var lookupResult = {lookup_method}({key_args});")

        # Handle default value fallback
        default_value = getattr(action, 'default_value', None)
        if default_value:
            default_expr = generate_value_expr(default_value)
            lines.append(f"        if (lookupResult == null) {{")
            lines.append(f"            lookupResult = {default_expr};")
            lines.append(f"        }}")

        # Set result on output if field specified
        if output_field:
            setter = to_setter(output_field)
            lines.append(f"        {output_var}.{setter}(lookupResult);")

        return '\n'.join(lines)

    def generate_lookup_method_signature(
        self,
        table_name: str,
        key_types: List[str],
        return_type: str = "Object"
    ) -> str:
        """Generate lookup method signature for interface/abstract class.

        Args:
            table_name: Name of the lookup table
            key_types: Java types for lookup keys
            return_type: Java return type

        Returns:
            Method signature string
        """
        method_name = to_camel_case(table_name) + "Lookup"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types or []))

        return f"    protected abstract {return_type} {method_name}({params});"

    def generate_temporal_lookup_method_signature(
        self,
        table_name: str,
        key_types: List[str],
        return_type: str = "Object"
    ) -> str:
        """Generate temporal lookup method signature with as_of parameter.

        Args:
            table_name: Name of the lookup table
            key_types: Java types for lookup keys
            return_type: Java return type

        Returns:
            Method signature string
        """
        method_name = to_camel_case(table_name) + "LookupAsOf"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types or []))
        if params:
            params += ", "
        params += "Instant asOfTime"

        return f"    protected abstract {return_type} {method_name}({params});"

    def collect_lookup_actions(
        self,
        table: 'ast.DecisionTableDef'
    ) -> List['ast.LookupAction']:
        """Collect all lookup actions from a decision table.

        Args:
            table: The decision table definition

        Returns:
            List of LookupAction nodes found in the table
        """
        from backend.ast import rules_ast as ast

        lookups = []

        decide = getattr(table, 'decide', None)
        if not decide:
            return lookups

        matrix = getattr(decide, 'matrix', None)
        if not matrix:
            return lookups

        rows = getattr(matrix, 'rows', None) or []
        for row in rows:
            cells = getattr(row, 'cells', None) or []
            for cell in cells:
                content = getattr(cell, 'content', None)
                if isinstance(content, ast.LookupAction):
                    lookups.append(content)

        return lookups

    def has_lookup_actions(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table contains any lookup actions."""
        return len(self.collect_lookup_actions(table)) > 0

    def has_temporal_lookups(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table contains temporal (as_of) lookups."""
        lookups = self.collect_lookup_actions(table)
        return any(getattr(lookup, 'as_of', None) is not None for lookup in lookups)

    def has_async_lookups(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table should use async lookups.

        Tables with multiple lookup actions benefit from async execution.
        """
        return len(self.collect_lookup_actions(table)) > 1

    def get_lookup_imports(self) -> Set[str]:
        """Get required imports for lookup generation."""
        imports = set()
        imports.add('java.util.Map')
        imports.add('java.util.HashMap')
        imports.update(get_concurrent_imports())
        imports.update(get_time_imports())
        return imports
