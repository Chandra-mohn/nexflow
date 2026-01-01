# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Cache Generator Mixin

Generates Java caching code from L3 Transform cache declarations.
Uses Flink native state with TTL for cache semantics.
Supports both TTL-based and key-based caching strategies.
"""

from typing import Set

from backend.ast import transform_ast as ast


class CacheGeneratorMixin:
    """
    Mixin for generating Java caching code using Flink state.

    Generates:
    - Flink ValueState with TTL configuration
    - Cache key generation for multi-field keys
    - State-based lookup and populate logic
    - MapState for key-based caching (multiple entries)
    """

    def generate_cache_code(self, cache: ast.CacheDecl, transform_name: str) -> str:
        """Generate Flink state-based caching infrastructure code.

        Supports two caching modes:
        1. Simple TTL cache (ValueState) - when no key_fields specified
        2. Key-based cache (MapState) - when key_fields are specified
        """
        if not cache:
            return ""

        ttl_ms = self._duration_to_ms(cache.ttl)

        # Use MapState for key-based caching, ValueState for simple TTL
        if cache.key_fields:
            return self._generate_keyed_cache_code(cache, transform_name, ttl_ms)
        else:
            return self._generate_simple_cache_code(cache, transform_name, ttl_ms)

    def _generate_simple_cache_code(
        self,
        cache: ast.CacheDecl,
        transform_name: str,
        ttl_ms: int
    ) -> str:
        """Generate simple TTL-based cache using ValueState."""
        state_var = f"{self.to_camel_case(transform_name)}CacheState"
        state_desc = f"{self.to_camel_case(transform_name)}CacheStateDesc"

        lines = [
            "    // Flink State-based Cache Configuration (TTL-only)",
            f"    private transient ValueState<Object> {state_var};",
            "",
            "    @Override",
            "    public void open(Configuration parameters) throws Exception {",
            "        super.open(parameters);",
            "",
            "        // Configure state TTL for cache expiration",
            "        StateTtlConfig ttlConfig = StateTtlConfig",
            f"            .newBuilder(Time.milliseconds({ttl_ms}L))",
            "            .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)",
            "            .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)",
            "            .build();",
            "",
            f"        ValueStateDescriptor<Object> {state_desc} =",
            f"            new ValueStateDescriptor<>(\"{transform_name}_cache\", Object.class);",
            f"        {state_desc}.enableTimeToLive(ttlConfig);",
            f"        {state_var} = getRuntimeContext().getState({state_desc});",
            "    }",
            "",
        ]

        return '\n'.join(lines)

    def _generate_keyed_cache_code(
        self,
        cache: ast.CacheDecl,
        transform_name: str,
        ttl_ms: int
    ) -> str:
        """Generate key-based cache using MapState with TTL."""
        state_var = f"{self.to_camel_case(transform_name)}CacheMap"
        state_desc = f"{self.to_camel_case(transform_name)}CacheMapDesc"

        lines = [
            "    // Flink State-based Cache Configuration (Key-based with TTL)",
            f"    private transient MapState<String, Object> {state_var};",
            "",
            "    @Override",
            "    public void open(Configuration parameters) throws Exception {",
            "        super.open(parameters);",
            "",
            "        // Configure state TTL for cache expiration",
            "        StateTtlConfig ttlConfig = StateTtlConfig",
            f"            .newBuilder(Time.milliseconds({ttl_ms}L))",
            "            .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)",
            "            .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)",
            "            .build();",
            "",
            f"        MapStateDescriptor<String, Object> {state_desc} =",
            f"            new MapStateDescriptor<>(\"{transform_name}_cache\", String.class, Object.class);",
            f"        {state_desc}.enableTimeToLive(ttlConfig);",
            f"        {state_var} = getRuntimeContext().getMapState({state_desc});",
            "    }",
            "",
        ]

        # Generate cache key builder for multi-field keys
        lines.extend(self._generate_cache_key_builder(cache.key_fields, transform_name))
        lines.append("")

        return '\n'.join(lines)

    def _generate_cache_key_builder(
        self,
        key_fields: list,
        transform_name: str,
        use_map: bool = True
    ) -> list:
        """Generate cache key builder method.

        Args:
            key_fields: List of field names to include in cache key
            transform_name: Name of the transform
            use_map: If True, use Map.get() access; otherwise use getter methods
        """
        method_name = f"build{self.to_pascal_case(transform_name)}CacheKey"

        # For simple transforms, input is Map<String, Object>
        input_type = "Map<String, Object>" if use_map else "Object"

        lines = [
            "    /**",
            f"     * Build cache key from {', '.join(key_fields)}",
            "     */",
            f"    private String {method_name}({input_type} input) {{",
            "        StringBuilder keyBuilder = new StringBuilder();",
        ]

        for i, field in enumerate(key_fields):
            if i > 0:
                lines.append('        keyBuilder.append("::");')
            if use_map:
                # Use Map.get() for simple transforms
                lines.append(f'        keyBuilder.append(String.valueOf(input.get("{field}")));')
            else:
                # Use getter for typed POJOs
                getter = self.to_getter(field)
                lines.append(f"        keyBuilder.append(String.valueOf(input.{getter}));")

        lines.extend([
            "        return keyBuilder.toString();",
            "    }",
        ])

        return lines

    def generate_cached_transform_wrapper(
        self,
        transform_name: str,
        cache: ast.CacheDecl,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate cached wrapper for transform method using Flink state.

        Supports two caching modes:
        1. Simple TTL cache - uses ValueState for single cached value
        2. Key-based cache - uses MapState with composite key lookup
        """
        if not cache:
            return ""

        if cache.key_fields:
            return self._generate_keyed_cache_wrapper(
                transform_name, cache, input_type, output_type
            )
        else:
            return self._generate_simple_cache_wrapper(
                transform_name, input_type, output_type
            )

    def _generate_simple_cache_wrapper(
        self,
        transform_name: str,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate simple TTL-based cache wrapper using ValueState."""
        state_var = f"{self.to_camel_case(transform_name)}CacheState"

        return f'''    /**
     * Cached version of {transform_name} transform using Flink state (TTL-only).
     */
    public {output_type} transformWithCache({input_type} input) throws Exception {{
        // Try state lookup
        Object cached = {state_var}.value();
        if (cached != null) {{
            return ({output_type}) cached;
        }}

        // Execute transform and cache result in state
        {output_type} result = transform(input);
        {state_var}.update(result);

        return result;
    }}'''

    def _generate_keyed_cache_wrapper(
        self,
        transform_name: str,
        cache: ast.CacheDecl,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate key-based cache wrapper using MapState."""
        state_var = f"{self.to_camel_case(transform_name)}CacheMap"
        key_method = f"build{self.to_pascal_case(transform_name)}CacheKey"

        return f'''    /**
     * Cached version of {transform_name} transform using key-based Flink state.
     * Cache key composed from: {', '.join(cache.key_fields)}
     */
    public {output_type} transformWithCache({input_type} input) throws Exception {{
        // Build cache key from specified fields
        String cacheKey = {key_method}(input);

        // Try state lookup by key
        Object cached = {state_var}.get(cacheKey);
        if (cached != null) {{
            return ({output_type}) cached;
        }}

        // Execute transform and cache result by key
        {output_type} result = transform(input);
        {state_var}.put(cacheKey, result);

        return result;
    }}

    /**
     * Invalidate cache entry for the given input's key.
     */
    public void invalidateCache({input_type} input) throws Exception {{
        String cacheKey = {key_method}(input);
        {state_var}.remove(cacheKey);
    }}

    /**
     * Clear all cached entries.
     */
    public void clearCache() throws Exception {{
        {state_var}.clear();
    }}'''

    def _duration_to_ms(self, duration: ast.Duration) -> int:
        """Convert Duration to milliseconds."""
        multipliers = {
            'ms': 1,
            's': 1000,
            'm': 60000,
            'h': 3600000,
            'd': 86400000
        }
        return duration.value * multipliers.get(duration.unit, 1)

    # Note: _to_getter, _to_camel_case, _to_pascal_case are inherited from BaseGenerator
    # as to_getter(), to_camel_case(), to_pascal_case() - use those instead

    def get_cache_imports(self) -> Set[str]:
        """Get required imports for Flink state-based cache generation."""
        return {
            'org.apache.flink.api.common.state.ValueState',
            'org.apache.flink.api.common.state.ValueStateDescriptor',
            'org.apache.flink.api.common.state.MapState',
            'org.apache.flink.api.common.state.MapStateDescriptor',
            'org.apache.flink.api.common.state.StateTtlConfig',
            'org.apache.flink.api.common.time.Time',
            'org.apache.flink.configuration.Configuration',
        }
