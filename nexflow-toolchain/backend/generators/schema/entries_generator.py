"""
Entries Generator Module

Generates Java reference data code from Schema AST definitions.
Supports reference_data pattern with static lookup tables.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class EntriesGeneratorMixin:
    """Mixin providing entries/reference data code generation capabilities.

    Generates:
    - Entry key enum constants
    - Static lookup map with entry data
    - Lookup methods (by key, with defaults)
    - Deprecation tracking for entries
    """

    def _generate_entries_class(self: BaseGenerator,
                                 schema: ast.SchemaDefinition,
                                 class_name: str,
                                 package: str) -> str:
        """Generate entries helper class for reference_data pattern.

        Returns complete Java class for static reference data lookup.
        """
        if not schema.entries:
            return ""

        entries_block = schema.entries

        header = self.generate_java_header(
            f"{class_name}Entries",
            f"Reference data entries for {schema.name} schema"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'java.util.Map',
            'java.util.HashMap',
            'java.util.Collections',
            'java.util.Optional',
            'java.util.Set',
            'java.util.HashSet',
            'java.util.logging.Logger',
        ])

        # Generate components
        key_enum = self._generate_entry_key_enum(entries_block, class_name)
        entry_class = self._generate_entry_record_class(entries_block, class_name)
        lookup_map = self._generate_entries_map(entries_block, class_name)
        lookup_methods = self._generate_lookup_methods(entries_block, class_name)
        deprecation_tracking = self._generate_deprecation_tracking(entries_block, class_name)

        return f'''{header}
{package_decl}
{imports}

/**
 * Reference data entries for {schema.name}.
 *
 * Pattern: reference_data
 * Purpose: Static lookup tables with typed access
 * Entries: {len(entries_block.entries)}
 */
public class {class_name}Entries {{

    private static final Logger LOGGER = Logger.getLogger({class_name}Entries.class.getName());

{key_enum}

{entry_class}

{lookup_map}

{lookup_methods}

{deprecation_tracking}
}}
'''

    def _generate_entry_key_enum(self: BaseGenerator,
                                  entries_block: ast.EntriesBlock,
                                  class_name: str) -> str:
        """Generate enum of entry keys.

        Returns Java enum with all entry keys.
        """
        enum_values = []
        for entry in entries_block.entries:
            key_const = self.to_java_constant(entry.key)
            if entry.deprecated:
                enum_values.append(f'        @Deprecated\n        {key_const}')
            else:
                enum_values.append(f'        {key_const}')

        enum_block = ',\n'.join(enum_values)

        return f'''    // =========================================================================
    // Entry Key Enum
    // =========================================================================

    /**
     * Enumeration of all entry keys in this reference data set.
     */
    public enum Key {{
{enum_block};

        /**
         * Parse key from string (case-insensitive).
         * @param name Key name
         * @return Matching Key or null if not found
         */
        public static Key fromString(String name) {{
            if (name == null) return null;
            String upper = name.toUpperCase().replace("-", "_").replace(" ", "_");
            try {{
                return Key.valueOf(upper);
            }} catch (IllegalArgumentException e) {{
                return null;
            }}
        }}
    }}'''

    def _generate_entry_record_class(self: BaseGenerator,
                                      entries_block: ast.EntriesBlock,
                                      class_name: str) -> str:
        """Generate inner class for entry records.

        Returns Java class representing a single entry.
        """
        # Collect all unique field names across entries
        all_fields = set()
        for entry in entries_block.entries:
            for field in entry.fields:
                all_fields.add(field.name)

        field_declarations = []
        getter_methods = []

        for field_name in sorted(all_fields):
            java_field = self.to_java_field_name(field_name)
            capitalized = java_field[0].upper() + java_field[1:]

            field_declarations.append(f'        private final Object {java_field};')
            getter_methods.append(f'''
        /**
         * Get {field_name} value.
         */
        public Object get{capitalized}() {{
            return this.{java_field};
        }}

        /**
         * Get {field_name} value as specific type.
         */
        @SuppressWarnings("unchecked")
        public <T> T get{capitalized}As(Class<T> type) {{
            return (T) this.{java_field};
        }}''')

        # Constructor parameters and assignments
        constructor_params = ', '.join(f'Object {self.to_java_field_name(f)}' for f in sorted(all_fields))
        constructor_assigns = '\n'.join(f'            this.{self.to_java_field_name(f)} = {self.to_java_field_name(f)};' for f in sorted(all_fields))

        fields_block = '\n'.join(field_declarations)
        getters_block = '\n'.join(getter_methods)

        return f'''    // =========================================================================
    // Entry Record Class
    // =========================================================================

    /**
     * Represents a single entry record with typed field access.
     */
    public static class Entry {{
        private final Key key;
        private final boolean deprecated;
        private final String deprecatedReason;
{fields_block}

        public Entry(Key key, boolean deprecated, String deprecatedReason, {constructor_params}) {{
            this.key = key;
            this.deprecated = deprecated;
            this.deprecatedReason = deprecatedReason;
{constructor_assigns}
        }}

        public Key getKey() {{
            return this.key;
        }}

        public boolean isDeprecated() {{
            return this.deprecated;
        }}

        public String getDeprecatedReason() {{
            return this.deprecatedReason;
        }}
{getters_block}
    }}'''

    def _generate_entries_map(self: BaseGenerator,
                               entries_block: ast.EntriesBlock,
                               class_name: str) -> str:
        """Generate static map of entries.

        Returns Java static initializer for entries map.
        """
        # Collect field names for constructor order
        all_fields = set()
        for entry in entries_block.entries:
            for field in entry.fields:
                all_fields.add(field.name)
        sorted_fields = sorted(all_fields)

        entry_puts = []
        for entry in entries_block.entries:
            key_const = self.to_java_constant(entry.key)
            deprecated = 'true' if entry.deprecated else 'false'
            deprecated_reason = f'"{entry.deprecated_reason}"' if entry.deprecated_reason else 'null'

            # Build field values in sorted order
            field_values = []
            field_map = {f.name: f.value for f in entry.fields}
            for field_name in sorted_fields:
                if field_name in field_map:
                    value = self._entry_value_to_java(field_map[field_name])
                else:
                    value = 'null'
                field_values.append(value)

            values_str = ', '.join(field_values)
            entry_puts.append(
                f'        ENTRIES.put(Key.{key_const}, new Entry(Key.{key_const}, {deprecated}, {deprecated_reason}, {values_str}));'
            )

        puts_block = '\n'.join(entry_puts)

        return f'''    // =========================================================================
    // Entries Map
    // =========================================================================

    private static final Map<Key, Entry> ENTRIES = new HashMap<>();

    static {{
{puts_block}
    }}'''

    def _generate_lookup_methods(self: BaseGenerator,
                                  entries_block: ast.EntriesBlock,
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
                                        entries_block: ast.EntriesBlock,
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

    # =========================================================================
    # Helper Methods
    # =========================================================================

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
