# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Migration Field Mapping Mixin

Generates field mapping and reflection-based migration utilities.
"""

from backend.generators.base import BaseGenerator


class MigrationFieldsMixin:
    """Mixin providing field mapping generation for migrations."""

    def _generate_field_mapping_methods(self: BaseGenerator,
                                         schema,
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

        # Add expression evaluation helpers
        methods.append(self._generate_expression_helpers(class_name))

        if not methods:
            return self._generate_identity_mapping(class_name)

        return '\n\n'.join(methods)

    def _generate_expression_helpers(self: BaseGenerator, class_name: str) -> str:
        """Generate helper methods for expression evaluation."""
        return f'''
    private static final java.util.logging.Logger LOGGER =
        java.util.logging.Logger.getLogger("{class_name}Migration");

    /**
     * Evaluate migration expression against source object.
     */
    private static Object evaluateMigrationExpression(Object source, String expression) {{
        if (expression.matches("^[a-zA-Z_][a-zA-Z0-9_]*(\\\\.[a-zA-Z_][a-zA-Z0-9_]*)*$")) {{
            return extractFieldValue(source, expression);
        }}
        LOGGER.fine("Complex expression not supported, requires parser: " + expression);
        return null;
    }}

    /**
     * Evaluate multi-field migration expression.
     */
    private static Object[] evaluateMultiFieldExpression(Object source, String expression) {{
        if (expression.contains(",")) {{
            String[] fields = expression.split("\\\\s*,\\\\s*");
            Object[] values = new Object[fields.length];
            for (int i = 0; i < fields.length; i++) {{
                values[i] = extractFieldValue(source, fields[i].trim());
            }}
            return values;
        }}
        LOGGER.fine("Multi-field expression not supported: " + expression);
        return new Object[0];
    }}

    /**
     * Extract field value using reflection.
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
     */
    private static void applyFieldValue(Object target, String setterName, Object value) {{
        if (target == null || setterName == null || value == null) {{
            return;
        }}
        try {{
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
    }}'''

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
