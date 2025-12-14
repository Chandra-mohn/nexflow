# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Entries Lookup Methods Mixin

Generates lookup and deprecation tracking methods for reference data entries.
"""

from backend.generators.base import BaseGenerator


class EntriesLookupMixin:
    """Mixin providing entries lookup method generation."""

    def _generate_lookup_methods(self: BaseGenerator,
                                  entries_block,
                                  class_name: str) -> str:
        """Generate lookup methods for entries.

        Returns Java methods for entry retrieval.
        """
        return f'''    // =========================================================================
    // Lookup Methods
    // =========================================================================

    /**
     * Get entry by key.
     * @param key The entry key
     * @return Optional containing the entry if found
     */
    public static Optional<Entry> get(Key key) {{
        Entry entry = ENTRIES.get(key);
        if (entry != null && entry.isDeprecated()) {{
            LOGGER.warning("Accessing deprecated entry: " + key +
                (entry.getDeprecatedReason() != null ? " - " + entry.getDeprecatedReason() : ""));
        }}
        return Optional.ofNullable(entry);
    }}

    /**
     * Get entry by key string (case-insensitive).
     * @param keyName The entry key name
     * @return Optional containing the entry if found
     */
    public static Optional<Entry> get(String keyName) {{
        Key key = Key.fromString(keyName);
        return key != null ? get(key) : Optional.empty();
    }}

    /**
     * Get entry by key, returning default if not found.
     * @param key The entry key
     * @param defaultEntry Default entry to return if not found
     * @return The entry or default
     */
    public static Entry getOrDefault(Key key, Entry defaultEntry) {{
        return get(key).orElse(defaultEntry);
    }}

    /**
     * Check if an entry exists for the given key.
     * @param key The entry key
     * @return true if entry exists
     */
    public static boolean contains(Key key) {{
        return ENTRIES.containsKey(key);
    }}

    /**
     * Get all entry keys.
     * @return Unmodifiable set of all keys
     */
    public static Set<Key> keys() {{
        return Collections.unmodifiableSet(ENTRIES.keySet());
    }}

    /**
     * Get count of entries.
     * @return Number of entries
     */
    public static int size() {{
        return ENTRIES.size();
    }}'''

    def _generate_deprecation_tracking(self: BaseGenerator,
                                        entries_block,
                                        class_name: str) -> str:
        """Generate deprecation tracking methods.

        Returns Java methods for handling deprecated entries.
        """
        deprecated_entries = [e for e in entries_block.entries if e.deprecated]

        if not deprecated_entries:
            return '''    // =========================================================================
    // Deprecation Tracking (no deprecated entries)
    // =========================================================================

    /**
     * Check if any entries are deprecated.
     */
    public static boolean hasDeprecatedEntries() {
        return false;
    }

    /**
     * Get set of deprecated keys.
     */
    public static Set<Key> getDeprecatedKeys() {
        return Collections.emptySet();
    }
'''

        deprecated_keys = ', '.join(f'Key.{self.to_java_constant(e.key)}' for e in deprecated_entries)

        return f'''    // =========================================================================
    // Deprecation Tracking
    // =========================================================================

    private static final Set<Key> DEPRECATED_KEYS = new HashSet<>();

    static {{
        Collections.addAll(DEPRECATED_KEYS, {deprecated_keys});
    }}

    /**
     * Check if any entries are deprecated.
     */
    public static boolean hasDeprecatedEntries() {{
        return true;
    }}

    /**
     * Get set of deprecated keys.
     */
    public static Set<Key> getDeprecatedKeys() {{
        return Collections.unmodifiableSet(DEPRECATED_KEYS);
    }}

    /**
     * Check if a specific key is deprecated.
     * @param key The key to check
     * @return true if the key is deprecated
     */
    public static boolean isDeprecated(Key key) {{
        return DEPRECATED_KEYS.contains(key);
    }}
'''

    def _entry_value_to_java(self: BaseGenerator, value) -> str:
        """Convert entry field value to Java literal."""
        if value is None:
            return 'null'
        if hasattr(value, 'value'):
            value = value.value

        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, (int, float)):
            return str(value)

        return f'"{value}"'
