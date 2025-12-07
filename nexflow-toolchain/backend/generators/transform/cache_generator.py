"""
Cache Generator Mixin

Generates Java caching code from L3 Transform cache declarations.
Uses Flink native state with TTL for cache semantics.
"""

from typing import Set

from backend.ast import transform_ast as ast


class CacheGeneratorMixin:
    """
    Mixin for generating Java caching code using Flink state.

    Generates:
    - Flink ValueState with TTL configuration
    - Cache key generation
    - State-based lookup and populate logic
    """

    def generate_cache_code(self, cache: ast.CacheDecl, transform_name: str) -> str:
        """Generate Flink state-based caching infrastructure code."""
        if not cache:
            return ""

        ttl_ms = self._duration_to_ms(cache.ttl)
        state_var = f"{self._to_camel_case(transform_name)}CacheState"
        state_desc = f"{self._to_camel_case(transform_name)}CacheStateDesc"

        lines = [
            "    // Flink State-based Cache Configuration",
            f"    private transient ValueState<Object> {state_var};",
            "",
            "    @Override",
            "    public void open(Configuration parameters) throws Exception {",
            "        super.open(parameters);",
            "",
            "        // Configure state TTL for cache expiration",
            "        StateTtlConfig ttlConfig = StateTtlConfig",
            "            .newBuilder(Time.milliseconds(" + str(ttl_ms) + "L))",
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

        # Generate cache key builder
        if cache.key_fields:
            lines.extend(self._generate_cache_key_builder(cache.key_fields, transform_name))
            lines.append("")

        return '\n'.join(lines)

    def _generate_cache_key_builder(self, key_fields: list, transform_name: str) -> list:
        """Generate cache key builder method."""
        method_name = f"build{self._to_pascal_case(transform_name)}CacheKey"

        lines = [
            "    /**",
            f"     * Build cache key from {', '.join(key_fields)}",
            "     */",
            f"    private String {method_name}(Object input) {{",
            "        StringBuilder keyBuilder = new StringBuilder();",
        ]

        for i, field in enumerate(key_fields):
            getter = self._to_getter(field)
            if i > 0:
                lines.append('        keyBuilder.append("::");')
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
        """Generate cached wrapper for transform method using Flink state."""
        if not cache:
            return ""

        state_var = f"{self._to_camel_case(transform_name)}CacheState"
        key_method = f"build{self._to_pascal_case(transform_name)}CacheKey"

        return f'''    /**
     * Cached version of {transform_name} transform using Flink state.
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

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method call."""
        camel = self._to_camel_case(field_name)
        return f"get{camel[0].upper()}{camel[1:]}()"

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def get_cache_imports(self) -> Set[str]:
        """Get required imports for Flink state-based cache generation."""
        return {
            'org.apache.flink.api.common.state.ValueState',
            'org.apache.flink.api.common.state.ValueStateDescriptor',
            'org.apache.flink.api.common.state.StateTtlConfig',
            'org.apache.flink.api.common.time.Time',
            'org.apache.flink.configuration.Configuration',
        }
