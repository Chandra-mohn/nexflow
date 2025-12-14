# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Lookup Cache Mixin

Generates caching and async support for lookup actions.
"""

import logging
from typing import List

from backend.generators.rules.utils import (
    to_camel_case,
    DEFAULT_CACHE_TTL_SECONDS,
)

LOG = logging.getLogger(__name__)


class LookupCacheMixin:
    """
    Mixin for generating lookup caching and async support.

    Generates:
    - Async lookup wrappers for Flink AsyncDataStream
    - Cached lookup wrappers with TTL
    - CacheEntry helper class
    - Executor service for async operations
    """

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
        method_name = to_camel_case(table_name) + "Lookup"
        async_method_name = to_camel_case(table_name) + "LookupAsync"
        key_types = key_types or []
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))
        args = ", ".join(f"key{i}" for i in range(len(key_types)))

        return f'''    /**
     * Async lookup for {table_name} - for use with AsyncDataStream.
     *
     * @return CompletableFuture with lookup result
     */
    protected CompletableFuture<{return_type}> {async_method_name}({params}) {{
        return CompletableFuture.supplyAsync(() -> {method_name}({args}), getLookupExecutor());
    }}'''

    def generate_cached_lookup_wrapper(
        self,
        table_name: str,
        key_types: List[str],
        return_type: str = "Object",
        cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS
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
        method_name = to_camel_case(table_name) + "Lookup"
        cached_method_name = to_camel_case(table_name) + "LookupCached"
        cache_name = to_camel_case(table_name) + "Cache"
        cache_ttl_const = table_name.upper() + "_CACHE_TTL_MS"
        key_types = key_types or []
        params = ", ".join(f"{kt} key{i}" for i, kt in enumerate(key_types))

        # Build cache key
        if len(key_types) == 1:
            cache_key = "String.valueOf(key0)"
        else:
            key_parts = " + \":\" + ".join(f"String.valueOf(key{i})" for i in range(len(key_types)))
            cache_key = key_parts if key_parts else '""'

        args = ", ".join(f"key{i}" for i in range(len(key_types)))
        cache_ttl_ms = cache_ttl_seconds * 1000

        return f'''    // Cache for {table_name} lookups
    private transient Map<String, CacheEntry<{return_type}>> {cache_name};
    private static final long {cache_ttl_const} = {cache_ttl_ms}L;

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
        {cache_name}.put(cacheKey, new CacheEntry<>(result, {cache_ttl_const}));
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
