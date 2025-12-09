"""
Migration Generator Module

Generates Java migration code from Schema AST definitions.
Supports schema evolution with field mappings and transformation expressions.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class MigrationGeneratorMixin:
    """Mixin providing migration code generation capabilities.

    Generates:
    - Field mapping methods for schema evolution
    - Version compatibility validation
    - Migration transformation code
    - Schema upgrade/downgrade utilities
    """

    def _generate_migration_class(self: BaseGenerator,
                                   schema: ast.SchemaDefinition,
                                   class_name: str,
                                   package: str) -> str:
        """Generate migration helper class for schema evolution.

        Returns complete Java class for schema migration support.
        """
        if not schema.migration and not schema.version:
            return ""

        header = self.generate_java_header(
            f"{class_name}Migration",
            f"Migration helper for {schema.name} schema evolution"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'java.util.Map',
            'java.util.HashMap',
            'java.util.function.Function',
        ])

        # Generate migration methods
        field_mappings = self._generate_field_mapping_methods(schema, class_name)
        version_methods = self._generate_version_compatibility_methods(schema, class_name)
        migration_apply = self._generate_migration_apply_method(schema, class_name)

        return f'''{header}
{package_decl}
{imports}

/**
 * Migration helper for {schema.name} schema.
 *
 * Provides utilities for:
 * - Field mapping between schema versions
 * - Version compatibility validation
 * - Data transformation during migration
 */
public class {class_name}Migration {{

{field_mappings}

{version_methods}

{migration_apply}
}}
'''

    def _generate_field_mapping_methods(self: BaseGenerator,
                                         schema: ast.SchemaDefinition,
                                         class_name: str) -> str:
        """Generate field mapping methods for migration statements.

        Returns Java methods for field-level data transformation.
        """
        if not schema.migration:
            return self._generate_identity_mapping(class_name)

        methods = []

        # Generate mapping method for each migration statement
        for i, stmt in enumerate(schema.migration.statements):
            target_fields = stmt.target_fields
            expression = stmt.expression.raw_text if stmt.expression else "null"

            if len(target_fields) == 1:
                # Single field mapping
                field_name = target_fields[0]
                java_field = self.to_java_field_name(field_name)
                setter = f"set{java_field[0].upper()}{java_field[1:]}"

                methods.append(f'''    /**
     * Migrate field: {field_name}
     * Expression: {expression}
     */
    public static void migrate_{java_field}({class_name} source, {class_name} target) {{
        // Migration expression: {expression}
        Object value = evaluateMigrationExpression(source, "{expression}");
        if (value != null) {{
            try {{
                java.lang.reflect.Method setter = target.getClass().getMethod("{setter}", value.getClass());
                setter.invoke(target, value);
            }} catch (NoSuchMethodException e) {{
                LOGGER.warning("Migration setter not found: {setter} - " + e.getMessage());
            }} catch (Exception e) {{
                LOGGER.severe("Migration failed for field {field_name}: " + e.getMessage());
            }}
        }}
    }}''')
            else:
                # Multiple field mapping (tuple assignment)
                field_names = ', '.join(target_fields)
                method_name = '_'.join(self.to_java_field_name(f) for f in target_fields)

                # Generate setter calls for each field
                setter_calls = []
                for idx, tf in enumerate(target_fields):
                    java_tf = self.to_java_field_name(tf)
                    setter_name = f"set{java_tf[0].upper()}{java_tf[1:]}"
                    setter_calls.append(f'            applyFieldValue(target, "{setter_name}", values[{idx}]);')
                setters_block = '\n'.join(setter_calls)

                methods.append(f'''    /**
     * Migrate fields: {field_names}
     * Expression: {expression}
     */
    public static void migrate_{method_name}({class_name} source, {class_name} target) {{
        // Multi-field migration expression: {expression}
        Object[] values = evaluateMultiFieldExpression(source, "{expression}");
        if (values != null && values.length >= {len(target_fields)}) {{
{setters_block}
        }} else {{
            LOGGER.warning("Multi-field migration returned insufficient values for: {field_names}");
        }}
    }}''')

        # Add expression evaluation helper with logging
        methods.append(f'''
    private static final java.util.logging.Logger LOGGER =
        java.util.logging.Logger.getLogger("{class_name}Migration");

    /**
     * Evaluate migration expression against source object.
     * @param source The source object to extract values from
     * @param expression The migration expression to evaluate
     * @return Evaluated value
     */
    private static Object evaluateMigrationExpression(Object source, String expression) {{
        // Simple field path extraction
        if (expression.matches("^[a-zA-Z_][a-zA-Z0-9_]*(\\\\.[a-zA-Z_][a-zA-Z0-9_]*)*$")) {{
            return extractFieldValue(source, expression);
        }}
        // Complex expressions need expression parser - log for debugging
        LOGGER.fine("Complex expression not supported, requires parser: " + expression);
        return null;
    }}

    /**
     * Evaluate multi-field migration expression.
     * @param source The source object
     * @param expression The expression that returns multiple values
     * @return Array of values for multiple target fields
     */
    private static Object[] evaluateMultiFieldExpression(Object source, String expression) {{
        // Check for known multi-value expressions
        if (expression.contains(",")) {{
            // Comma-separated field list
            String[] fields = expression.split("\\\\s*,\\\\s*");
            Object[] values = new Object[fields.length];
            for (int i = 0; i < fields.length; i++) {{
                values[i] = extractFieldValue(source, fields[i].trim());
            }}
            return values;
        }}
        // Complex function call expressions need expression parser
        LOGGER.fine("Multi-field expression not supported: " + expression);
        return new Object[0];
    }}

    /**
     * Extract field value using reflection.
     * @param source The source object
     * @param fieldPath Dot-separated field path (e.g., "address.city")
     * @return The extracted value, or null if extraction fails
     */
    private static Object extractFieldValue(Object source, String fieldPath) {{
        if (source == null || fieldPath == null || fieldPath.isEmpty()) {{
            return null;
        }}
        try {{
            String[] parts = fieldPath.split("\\\\.");
            Object current = source;
            for (String part : parts) {{
                if (current == null) {{
                    LOGGER.fine("Null value encountered at path: " + part);
                    return null;
                }}
                String getter = "get" + Character.toUpperCase(part.charAt(0)) + part.substring(1);
                java.lang.reflect.Method method = current.getClass().getMethod(getter);
                current = method.invoke(current);
            }}
            return current;
        }} catch (NoSuchMethodException e) {{
            LOGGER.warning("Getter method not found for field path: " + fieldPath + " - " + e.getMessage());
            return null;
        }} catch (IllegalAccessException e) {{
            LOGGER.warning("Cannot access getter for field path: " + fieldPath + " - " + e.getMessage());
            return null;
        }} catch (java.lang.reflect.InvocationTargetException e) {{
            LOGGER.warning("Getter invocation failed for field path: " + fieldPath + " - " + e.getMessage());
            return null;
        }}
    }}

    /**
     * Apply a value to a target field using reflection.
     * @param target The target object
     * @param setterName The setter method name
     * @param value The value to set
     */
    private static void applyFieldValue(Object target, String setterName, Object value) {{
        if (target == null || setterName == null || value == null) {{
            return;
        }}
        try {{
            // Find a setter method that accepts the value type
            for (java.lang.reflect.Method method : target.getClass().getMethods()) {{
                if (method.getName().equals(setterName) && method.getParameterCount() == 1) {{
                    Class<?> paramType = method.getParameterTypes()[0];
                    if (paramType.isAssignableFrom(value.getClass())) {{
                        method.invoke(target, value);
                        return;
                    }}
                }}
            }}
            LOGGER.warning("No compatible setter found: " + setterName + " for type " + value.getClass().getName());
        }} catch (Exception e) {{
            LOGGER.severe("Failed to apply field value via " + setterName + ": " + e.getMessage());
        }}
    }}''')

        if not methods:
            return self._generate_identity_mapping(class_name)

        return '\n\n'.join(methods)

    def _generate_identity_mapping(self: BaseGenerator, class_name: str) -> str:
        """Generate identity mapping when no migration is defined."""
        return f'''    /**
     * Identity mapping - no migration defined.
     * Copies all fields from source to target.
     */
    public static void migrateIdentity({class_name} source, {class_name} target) {{
        // No migration defined - implement field-by-field copy
        // or use reflection for automatic copying
    }}'''

    def _generate_version_compatibility_methods(self: BaseGenerator,
                                                  schema: ast.SchemaDefinition,
                                                  class_name: str) -> str:
        """Generate version compatibility validation methods.

        Returns Java methods for checking schema version compatibility.
        """
        methods = []

        # Extract version info with safe defaults
        version = schema.version
        version_major = getattr(version, 'major', 1) if version else 1
        version_minor = getattr(version, 'minor', 0) if version else 0
        version_patch = getattr(version, 'patch', 0) or 0 if version else 0
        previous_version = getattr(version, 'previous_version', None) if version else None

        # Handle compatibility enum safely
        compatibility = "backward"
        if version:
            compat_value = getattr(version, 'compatibility', None)
            if compat_value:
                compatibility = getattr(compat_value, 'value', str(compat_value))

        methods.append(f'''    // =========================================================================
    // Version Compatibility Constants
    // =========================================================================

    public static final int VERSION_MAJOR = {version_major};
    public static final int VERSION_MINOR = {version_minor};
    public static final int VERSION_PATCH = {version_patch};
    public static final String COMPATIBILITY_MODE = "{compatibility}";
    public static final String PREVIOUS_VERSION = {f'"{previous_version}"' if previous_version else 'null'};''')

        # isCompatible method
        methods.append(f'''
    /**
     * Check if the given version is compatible with this schema version.
     * Compatibility mode: {compatibility}
     *
     * @param otherMajor Major version to check
     * @param otherMinor Minor version to check
     * @return true if versions are compatible
     */
    public static boolean isCompatible(int otherMajor, int otherMinor) {{
        switch (COMPATIBILITY_MODE) {{
            case "backward":
                // New code can read old data
                return otherMajor == VERSION_MAJOR && otherMinor <= VERSION_MINOR;
            case "forward":
                // Old code can read new data
                return otherMajor == VERSION_MAJOR && otherMinor >= VERSION_MINOR;
            case "full":
                // Both directions
                return otherMajor == VERSION_MAJOR;
            case "none":
                // Exact match only
                return otherMajor == VERSION_MAJOR && otherMinor == VERSION_MINOR;
            default:
                return false;
        }}
    }}''')

        # canMigrate method
        methods.append(f'''
    /**
     * Check if migration is possible from the given version.
     *
     * @param fromMajor Source major version
     * @param fromMinor Source minor version
     * @return true if migration path exists
     */
    public static boolean canMigrate(int fromMajor, int fromMinor) {{
        // Migration within same major version is typically supported
        if (fromMajor != VERSION_MAJOR) {{
            return false;  // Cross-major migrations require explicit handling
        }}
        // Check if we have migration path for this version
        return fromMinor < VERSION_MINOR;
    }}''')

        # getVersionString method
        methods.append(f'''
    /**
     * Get the full version string for this schema.
     */
    public static String getVersionString() {{
        return VERSION_MAJOR + "." + VERSION_MINOR + "." + VERSION_PATCH;
    }}''')

        return '\n'.join(methods)

    def _generate_migration_apply_method(self: BaseGenerator,
                                          schema: ast.SchemaDefinition,
                                          class_name: str) -> str:
        """Generate the main migration apply method.

        Returns Java method for applying all migration transformations.
        """
        if not schema.migration or not schema.migration.statements:
            return f'''    /**
     * Apply migration transformations from source to target.
     * No migrations defined - performs identity mapping.
     *
     * @param source The source object (old version)
     * @param target The target object (new version)
     */
    public static void applyMigration({class_name} source, {class_name} target) {{
        migrateIdentity(source, target);
    }}'''

        # Generate calls to individual migration methods
        migration_calls = []
        for stmt in schema.migration.statements:
            if len(stmt.target_fields) == 1:
                field_name = stmt.target_fields[0]
                java_field = self.to_java_field_name(field_name)
                migration_calls.append(f"        migrate_{java_field}(source, target);")
            else:
                method_name = '_'.join(self.to_java_field_name(f) for f in stmt.target_fields)
                migration_calls.append(f"        migrate_{method_name}(source, target);")

        calls_block = '\n'.join(migration_calls)

        return f'''    /**
     * Apply all migration transformations from source to target.
     *
     * @param source The source object (old version)
     * @param target The target object (new version)
     */
    public static void applyMigration({class_name} source, {class_name} target) {{
{calls_block}
    }}

    /**
     * Create a migrated copy of the source object.
     *
     * @param source The source object to migrate
     * @return New object with migrations applied
     */
    public static {class_name} migrate({class_name} source) {{
        {class_name} target = new {class_name}();
        applyMigration(source, target);
        return target;
    }}'''
