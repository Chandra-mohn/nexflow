# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Migration Generator Module

Generates Java migration code from Schema AST definitions.
Supports schema evolution with field mappings and transformation expressions.
"""


from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator
from backend.generators.schema.migration_fields import MigrationFieldsMixin


class MigrationGeneratorMixin(MigrationFieldsMixin):
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

    def _generate_version_compatibility_methods(self: BaseGenerator,
                                                  schema: ast.SchemaDefinition,
                                                  class_name: str) -> str:
        """Generate version compatibility validation methods."""
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
     */
    public static boolean isCompatible(int otherMajor, int otherMinor) {{
        switch (COMPATIBILITY_MODE) {{
            case "backward":
                return otherMajor == VERSION_MAJOR && otherMinor <= VERSION_MINOR;
            case "forward":
                return otherMajor == VERSION_MAJOR && otherMinor >= VERSION_MINOR;
            case "full":
                return otherMajor == VERSION_MAJOR;
            case "none":
                return otherMajor == VERSION_MAJOR && otherMinor == VERSION_MINOR;
            default:
                return false;
        }}
    }}''')

        # canMigrate method
        methods.append(f'''
    /**
     * Check if migration is possible from the given version.
     */
    public static boolean canMigrate(int fromMajor, int fromMinor) {{
        if (fromMajor != VERSION_MAJOR) {{
            return false;
        }}
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
        """Generate the main migration apply method."""
        if not schema.migration or not schema.migration.statements:
            return f'''    /**
     * Apply migration transformations from source to target.
     * No migrations defined - performs identity mapping.
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
     */
    public static void applyMigration({class_name} source, {class_name} target) {{
{calls_block}
    }}

    /**
     * Create a migrated copy of the source object.
     */
    public static {class_name} migrate({class_name} source) {{
        {class_name} target = new {class_name}();
        applyMigration(source, target);
        return target;
    }}'''
