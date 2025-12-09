"""
Lookup Generator Mixin

Generates Java code for L4 Rules lookup actions - external data enrichment.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Lookup generates: Async lookup methods, default fallbacks, temporal lookups
L4 Lookup NEVER generates: Placeholder stubs, incomplete implementations
─────────────────────────────────────────────────────────────────────
"""

from typing import Set, List, Optional

from backend.ast import rules_ast as ast


class LookupGeneratorMixin:
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
        action: ast.LookupAction,
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
        lookup_method = self._to_camel_case(action.table_name) + "Lookup"

        # Generate key arguments
        key_args = ", ".join(
            self._generate_value_expr(key) for key in action.keys
        )

        lines = []

        # Check for temporal (as_of) lookup
        if action.as_of:
            as_of_expr = self._generate_value_expr(action.as_of)
            lines.append(f"        // Temporal lookup: {action.table_name} as of {as_of_expr}")
            lines.append(f"        var lookupResult = {lookup_method}AsOf({key_args}, {as_of_expr});")
        else:
            lines.append(f"        // Lookup: {action.table_name}")
            lines.append(f"        var lookupResult = {lookup_method}({key_args});")

        # Handle default value fallback
        if action.default_value:
            default_expr = self._generate_value_expr(action.default_value)
            lines.append(f"        if (lookupResult == null) {{")
            lines.append(f"            lookupResult = {default_expr};")
            lines.append(f"        }}")

        # Set result on output if field specified
        if output_field:
            setter = self._to_setter(output_field)
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
        method_name = self._to_camel_case(table_name) + "Lookup"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))

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
        method_name = self._to_camel_case(table_name) + "LookupAsOf"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))
        if params:
            params += ", "
        params += "Instant asOfTime"

        return f"    protected abstract {return_type} {method_name}({params});"

    def generate_async_lookup_wrapper(
        self,
        table_name: str,
        key_types: List[str],
        return_type: str = "Object"
    ) -> str:
        """Generate async lookup wrapper for Flink AsyncDataStream integration.

        Args:
            table_name: Name of the lookup table
            key_types: Java types for lookup keys
            return_type: Java return type

        Returns:
            Java code for async lookup wrapper
        """
        method_name = self._to_camel_case(table_name) + "Lookup"
        async_method_name = self._to_camel_case(table_name) + "LookupAsync"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))
        args = ", ".join(f"key{i}" for i in range(len(key_types)))

        return f'''    /**
     * Async lookup for {table_name} - for use with AsyncDataStream.
     *
     * @return CompletableFuture with lookup result
     */
    protected CompletableFuture<{return_type}> {async_method_name}({params}) {{
        return CompletableFuture.supplyAsync(() -> {method_name}({args}), lookupExecutor);
    }}'''

    def generate_cached_lookup_wrapper(
        self,
        table_name: str,
        key_types: List[str],
        return_type: str = "Object",
        cache_ttl_seconds: int = 300
    ) -> str:
        """Generate cached lookup wrapper with TTL.

        Args:
            table_name: Name of the lookup table
            key_types: Java types for lookup keys
            return_type: Java return type
            cache_ttl_seconds: Cache TTL in seconds

        Returns:
            Java code for cached lookup wrapper
        """
        method_name = self._to_camel_case(table_name) + "Lookup"
        cached_method_name = self._to_camel_case(table_name) + "LookupCached"
        cache_name = self._to_camel_case(table_name) + "Cache"
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))

        # Build cache key
        if len(key_types) == 1:
            cache_key = "String.valueOf(key0)"
        else:
            key_parts = " + \":\" + ".join(f"String.valueOf(key{i})" for i in range(len(key_types)))
            cache_key = key_parts

        args = ", ".join(f"key{i}" for i in range(len(key_types)))

        return f'''    // Cache for {table_name} lookups
    private transient Map<String, CacheEntry<{return_type}>> {cache_name};
    private static final long {table_name.upper()}_CACHE_TTL_MS = {cache_ttl_seconds * 1000}L;

    /**
     * Cached lookup for {table_name} with {cache_ttl_seconds}s TTL.
     */
    protected {return_type} {cached_method_name}({params}) {{
        if ({cache_name} == null) {{
            {cache_name} = new HashMap<>();
        }}

        String cacheKey = {cache_key};
        CacheEntry<{return_type}> entry = {cache_name}.get(cacheKey);

        if (entry != null && !entry.isExpired()) {{
            return entry.getValue();
        }}

        {return_type} result = {method_name}({args});
        {cache_name}.put(cacheKey, new CacheEntry<>(result, {table_name.upper()}_CACHE_TTL_MS));
        return result;
    }}'''

    def generate_lookup_cache_entry_class(self) -> str:
        """Generate CacheEntry helper class for lookup caching."""
        return '''    /**
     * Cache entry with TTL support for lookup results.
     */
    private static class CacheEntry<T> {
        private final T value;
        private final long expirationTime;

        public CacheEntry(T value, long ttlMs) {
            this.value = value;
            this.expirationTime = System.currentTimeMillis() + ttlMs;
        }

        public T getValue() {
            return value;
        }

        public boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }'''

    def generate_lookup_executor_field(self) -> str:
        """Generate executor service field for async lookups."""
        return '''    // Executor for async lookup operations
    private transient ExecutorService lookupExecutor;

    private ExecutorService getLookupExecutor() {
        if (lookupExecutor == null) {
            lookupExecutor = Executors.newFixedThreadPool(
                Runtime.getRuntime().availableProcessors(),
                r -> {
                    Thread t = new Thread(r, "lookup-executor");
                    t.setDaemon(true);
                    return t;
                }
            );
        }
        return lookupExecutor;
    }'''

    def collect_lookup_actions(
        self,
        table: 'ast.DecisionTableDef'
    ) -> List[ast.LookupAction]:
        """Collect all lookup actions from a decision table.

        Args:
            table: The decision table definition

        Returns:
            List of LookupAction nodes found in the table
        """
        lookups = []

        if table.decide and table.decide.matrix:
            for row in table.decide.matrix.rows:
                for cell in row.cells:
                    if isinstance(cell.content, ast.LookupAction):
                        lookups.append(cell.content)

        return lookups

    def has_lookup_actions(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table contains any lookup actions."""
        return len(self.collect_lookup_actions(table)) > 0

    def has_temporal_lookups(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table contains temporal (as_of) lookups."""
        lookups = self.collect_lookup_actions(table)
        return any(lookup.as_of is not None for lookup in lookups)

    def has_async_lookups(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table should use async lookups.

        Tables with multiple lookup actions benefit from async execution.
        """
        return len(self.collect_lookup_actions(table)) > 1

    def get_lookup_imports(self) -> Set[str]:
        """Get required imports for lookup generation."""
        return {
            'java.util.Map',
            'java.util.HashMap',
            'java.util.concurrent.CompletableFuture',
            'java.util.concurrent.ExecutorService',
            'java.util.concurrent.Executors',
            'java.time.Instant',
        }

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _to_setter(self, field_name: str) -> str:
        """Convert field name to setter method name."""
        camel = self._to_camel_case(field_name)
        return f"set{camel[0].upper()}{camel[1:]}"

    def _generate_value_expr(self, expr) -> str:
        """Generate Java code for a value expression.

        Note: This method should be provided by the parent class or another mixin.
        """
        if isinstance(expr, ast.FieldPath):
            parts = expr.parts
            if len(parts) == 1:
                camel = self._to_camel_case(parts[0])
                return f"get{camel[0].upper()}{camel[1:]}()"
            return ".".join(
                f"get{self._to_camel_case(p)[0].upper()}{self._to_camel_case(p)[1:]}()"
                for p in parts
            )
        if isinstance(expr, ast.StringLiteral):
            return f'"{expr.value}"'
        if isinstance(expr, ast.IntegerLiteral):
            return f'{expr.value}L'
        if isinstance(expr, ast.DecimalLiteral):
            return f'new BigDecimal("{expr.value}")'
        if isinstance(expr, ast.BooleanLiteral):
            return 'true' if expr.value else 'false'
        if isinstance(expr, ast.NullLiteral):
            return 'null'
        return str(expr)
