"""
Java Record Generator Module

Generates immutable Java Record classes from Schema AST definitions.
Records provide compact syntax with automatic accessors, equals, hashCode, and toString.

Key differences from POJOs:
- Immutable: no setters, use withField() methods for modified copies
- Accessor methods: field() instead of getField()
- Compact constructor for validation of required fields
- 80% less boilerplate code
"""

from typing import Dict, List, Optional, Set

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class PojoGeneratorMixin:
    """Mixin providing Java Record generation capabilities.

    Generates Java Records with:
    - Streaming configuration constants (idle, watermark, retention)
    - Compact constructor for required field validation
    - withField() methods for immutable updates
    - Utility methods for Flink compatibility
    - Version metadata
    """

    def generate_pojo(self: BaseGenerator, schema: ast.SchemaDefinition,
                      class_name: str, package: str) -> str:
        """Generate Java Record class with streaming metadata."""
        self._imports: Set[str] = set()
        self._current_class_name = class_name

        # Collect all fields
        all_fields = self._collect_all_fields(schema)

        # Build record components (constructor parameters)
        sparsity_hints = self._generate_sparsity_annotations(schema)
        record_components = []
        field_infos = []
        required_fields = []

        for field_decl in all_fields:
            field_info = self._generate_record_component(field_decl, sparsity_hints)
            record_components.append(field_info['component'])
            field_infos.append(field_info)
            self._imports.update(field_info['imports'])
            if field_info['required']:
                required_fields.append(field_info)

        # Generate with methods now that we have all field info
        with_methods = self._generate_with_methods(field_infos, class_name)

        # Add common imports
        self._imports.add('java.io.Serializable')
        if required_fields:
            self._imports.add('java.util.Objects')

        # Build class
        header = self.generate_java_header(class_name, f"Record for {schema.name} schema")
        package_decl = self.generate_package_declaration(package)
        imports = self.generate_imports(list(self._imports))

        # Format record components with line breaks for readability
        components_str = self._format_record_components(record_components)

        # Generate streaming constants (from StreamingGeneratorMixin)
        streaming_constants = self._generate_streaming_constants(schema)
        retention_constants = self._generate_retention_config(schema)
        sparsity_constants = self._generate_sparsity_constants(schema)
        version_constants = self._generate_version_constants(schema)

        # Generate compact constructor for required field validation
        compact_constructor = self._generate_compact_constructor(required_fields, class_name)

        # Generate correlation key method (updated for record accessor pattern)
        correlation_method = self._generate_correlation_key_method_record(all_fields)

        # Generate streaming utility methods (from StreamingGeneratorMixin)
        streaming_methods = self._generate_streaming_methods_record(schema)

        # Generate computed property methods (from ComputedGeneratorMixin)
        computed_methods = self._generate_computed_methods(schema, class_name)

        # Combine all constants
        all_constants = '\n'.join(filter(None, [
            version_constants,
            streaming_constants,
            retention_constants,
            sparsity_constants
        ]))

        # Format with methods
        with_methods_block = self.indent('\n\n'.join(with_methods))

        return f'''{header}
{package_decl}
{imports}

public record {class_name}(
{components_str}
) implements Serializable {{

    private static final long serialVersionUID = 1L;

{all_constants}
{compact_constructor}
{with_methods_block}

{correlation_method}

{streaming_methods}

{computed_methods}
}}
'''

    def _generate_record_component(self: BaseGenerator, field_decl: ast.FieldDecl,
                                    sparsity_hints: dict = None) -> Dict:
        """Generate record component (constructor parameter) with annotations."""
        field_name = self.to_java_field_name(field_decl.name)
        java_type = self._get_field_java_type(field_decl.field_type)
        imports = self._get_field_imports(field_decl.field_type)

        # Check if field is required
        is_required = any(q.qualifier_type == ast.FieldQualifierType.REQUIRED
                         for q in field_decl.qualifiers)

        # Build field comment with annotations
        comments = []

        # Check for PII annotation
        pii_profile = self._get_pii_profile(field_decl)
        if pii_profile:
            comments.append(f"PII: encrypted with '{pii_profile}' profile")

        # Check for sparsity annotation
        if sparsity_hints and field_decl.name in sparsity_hints:
            sparsity = sparsity_hints[field_decl.name]
            comments.append(f"Sparsity: {sparsity}")

        if is_required:
            comments.append("Required")

        comment_block = ""
        if comments:
            comment_block = f"    // {' | '.join(comments)}\n"

        component = f"{comment_block}    {java_type} {field_name}"

        return {
            'component': component,
            'imports': imports,
            'required': is_required,
            'field_name': field_name,
            'java_type': java_type,
            'original_name': field_decl.name
        }

    def _format_record_components(self: BaseGenerator, components: List[str]) -> str:
        """Format record components with proper indentation and commas."""
        if not components:
            return ""
        # Join with comma and newline, last component has no comma
        formatted = []
        for i, comp in enumerate(components):
            if i < len(components) - 1:
                formatted.append(comp + ",")
            else:
                formatted.append(comp)
        return '\n'.join(formatted)

    def _generate_with_methods(self: BaseGenerator, field_infos: List[Dict],
                                class_name: str) -> List[str]:
        """Generate all withField() methods for creating modified copies.

        Each withField method creates a new record instance with one field modified.
        Uses record accessor pattern: fieldName() to access other fields.
        """
        methods = []
        all_field_names = [info['field_name'] for info in field_infos]

        for field_info in field_infos:
            field_name = field_info['field_name']
            java_type = field_info['java_type']
            method_name = f"with{field_name[0].upper()}{field_name[1:]}"

            # Build constructor arguments - use accessor for existing fields,
            # parameter for the modified field
            args = []
            for fn in all_field_names:
                if fn == field_name:
                    args.append(field_name)  # Use the new parameter value
                else:
                    args.append(f"{fn}()")  # Use accessor for existing value
            args_str = ', '.join(args)

            method = f'''/**
 * Create a copy with modified {field_name}.
 * @param {field_name} The new value
 * @return New record instance with updated value
 */
public {class_name} {method_name}({java_type} {field_name}) {{
    return new {class_name}({args_str});
}}'''
            methods.append(method)

        return methods

    def _generate_compact_constructor(self: BaseGenerator, required_fields: List[Dict],
                                       class_name: str) -> str:
        """Generate compact constructor for required field validation."""
        if not required_fields:
            return ""

        validations = []
        for field_info in required_fields:
            field_name = field_info['field_name']
            validations.append(
                f'        Objects.requireNonNull({field_name}, "{field_info["original_name"]} is required");'
            )

        return f'''    /**
     * Compact constructor - validates required fields.
     */
    public {class_name} {{
{chr(10).join(validations)}
    }}
'''

    def _generate_correlation_key_method_record(self: BaseGenerator,
                                                   fields: List[ast.FieldDecl]) -> str:
        """Generate correlation key methods for Flink keying (record accessor pattern).

        These methods support:
        - getCorrelationKey(String[] fields): Dynamic key from specified fields
        - getBufferKey(String[] fields): Alias for correlation key (used in hold patterns)
        - getKey(): Simple key accessor for RoutedEvent compatibility

        Note: Uses record accessor pattern - field() instead of getField()
        """
        # Build field name to accessor mapping (record pattern: fieldName() instead of getFieldName())
        field_accessors = []
        for field_decl in fields:
            field_name = field_decl.name
            accessor_name = self.to_java_field_name(field_name)  # Record uses field name directly
            field_accessors.append((field_name, accessor_name))

        # Build switch cases for correlation key method
        switch_cases = []
        for field_name, accessor_name in field_accessors:
            switch_cases.append(f'''                case "{field_name}":
                    sb.append({accessor_name}());
                    break;''')
        switch_block = '\n'.join(switch_cases)

        return f'''    /**
     * Generate correlation key from specified fields.
     * Used by Flink keying operations for event correlation.
     *
     * @param fields Array of field names to include in the key
     * @return Concatenated string key from field values
     */
    public String getCorrelationKey(String[] fields) {{
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < fields.length; i++) {{
            if (i > 0) sb.append(":");
            switch (fields[i]) {{
{switch_block}
                default:
                    sb.append("null");
            }}
        }}
        return sb.toString();
    }}

    /**
     * Alias for getCorrelationKey - used by hold patterns for buffer keying.
     */
    public String getBufferKey(String[] fields) {{
        return getCorrelationKey(fields);
    }}

    /**
     * Get simple key for this record (first identity field or fallback).
     * Used by window operations and RoutedEvent compatibility.
     */
    public String getKey() {{
        // Return first non-null identity field as default key
{self._generate_default_key_body_record(field_accessors)}
    }}'''

    def _generate_default_key_body_record(self: BaseGenerator,
                                           field_accessors: List[tuple]) -> str:
        """Generate default key body for getKey() method (record accessor pattern)."""
        if not field_accessors:
            return '        return "default";'

        # Return first field value as string (record uses fieldName() accessor)
        first_field, first_accessor = field_accessors[0]
        return f'''        Object val = {first_accessor}();
        return val != null ? val.toString() : "null";'''

    def _generate_version_constants(self: BaseGenerator,
                                     schema: ast.SchemaDefinition) -> str:
        """Generate version metadata constants for schema evolution support.

        Returns Java constants block for version information.
        """
        constants = []

        # Schema version from version block
        if schema.version:
            version = schema.version
            if hasattr(version, 'major') and hasattr(version, 'minor'):
                constants.append(f"    public static final int SCHEMA_VERSION_MAJOR = {version.major};")
                constants.append(f"    public static final int SCHEMA_VERSION_MINOR = {version.minor};")
                if hasattr(version, 'patch') and version.patch is not None:
                    constants.append(f"    public static final int SCHEMA_VERSION_PATCH = {version.patch};")
                constants.append(f'    public static final String SCHEMA_VERSION = "{version.major}.{version.minor}' +
                               (f'.{version.patch}";' if hasattr(version, 'patch') and version.patch is not None else '";'))
            elif hasattr(version, 'version'):
                constants.append(f'    public static final String SCHEMA_VERSION = "{version.version}";')

        # Schema name constant
        constants.append(f'    public static final String SCHEMA_NAME = "{schema.name}";')

        if not constants:
            return ""

        return f'''    // =========================================================================
    // Schema Version Metadata
    // =========================================================================

{chr(10).join(constants)}
'''
