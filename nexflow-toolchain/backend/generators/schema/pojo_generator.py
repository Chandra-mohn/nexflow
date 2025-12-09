"""
POJO Generator Module

Generates Java POJO classes from Schema AST definitions.
Handles field declarations, getters/setters, toString(), and streaming metadata.
"""

from typing import Dict, List, Optional, Set

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class PojoGeneratorMixin:
    """Mixin providing POJO generation capabilities.

    Enhanced to include:
    - Streaming configuration constants (idle, watermark, retention)
    - Sparsity field annotations
    - Late data handling configuration
    - Version metadata
    """

    def generate_pojo(self: BaseGenerator, schema: ast.SchemaDefinition,
                      class_name: str, package: str) -> str:
        """Generate Java POJO class with streaming metadata."""
        self._imports: Set[str] = set()

        # Collect all fields
        all_fields = self._collect_all_fields(schema)

        # Build field declarations with sparsity annotations
        sparsity_hints = self._generate_sparsity_annotations(schema)
        field_declarations = []
        getter_setters = []
        for field_decl in all_fields:
            java_field = self._generate_field(field_decl, sparsity_hints)
            field_declarations.append(java_field['declaration'])
            getter_setters.append(java_field['getter'])
            getter_setters.append(java_field['setter'])
            self._imports.update(java_field['imports'])

        # Add common imports
        self._imports.add('java.io.Serializable')

        # Build class
        header = self.generate_java_header(class_name, f"POJO for {schema.name} schema")
        package_decl = self.generate_package_declaration(package)
        imports = self.generate_imports(list(self._imports))

        fields_block = self.indent('\n'.join(field_declarations))
        methods_block = self.indent('\n\n'.join(getter_setters))

        # Generate streaming constants (from StreamingGeneratorMixin)
        streaming_constants = self._generate_streaming_constants(schema)
        retention_constants = self._generate_retention_config(schema)
        sparsity_constants = self._generate_sparsity_constants(schema)
        version_constants = self._generate_version_constants(schema)

        # Generate correlation key method
        correlation_method = self._generate_correlation_key_method(all_fields)

        # Generate streaming utility methods (from StreamingGeneratorMixin)
        streaming_methods = self._generate_streaming_methods(schema)

        # Combine all constants
        all_constants = '\n'.join(filter(None, [
            version_constants,
            streaming_constants,
            retention_constants,
            sparsity_constants
        ]))

        return f'''{header}
{package_decl}
{imports}

public class {class_name} implements Serializable {{

    private static final long serialVersionUID = 1L;

{all_constants}
{fields_block}

    public {class_name}() {{
        // Default constructor
    }}

{methods_block}

{correlation_method}

{streaming_methods}
    @Override
    public String toString() {{
        return "{class_name}{{" +
{self._generate_to_string_body(all_fields)}
                "}}";
    }}
}}
'''

    def _generate_field(self: BaseGenerator, field_decl: ast.FieldDecl,
                         sparsity_hints: dict = None) -> Dict:
        """Generate field declaration, getter, and setter with sparsity annotations."""
        field_name = self.to_java_field_name(field_decl.name)
        java_type = self._get_field_java_type(field_decl.field_type)
        imports = self._get_field_imports(field_decl.field_type)

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

        comment_block = ""
        if comments:
            comment_block = f"    // {' | '.join(comments)}\n"

        declaration = f"{comment_block}    private {java_type} {field_name};"

        # Getter
        getter_name = f"get{field_name[0].upper()}{field_name[1:]}"
        getter = f'''public {java_type} {getter_name}() {{
    return this.{field_name};
}}'''

        # Setter
        setter_name = f"set{field_name[0].upper()}{field_name[1:]}"
        setter = f'''public void {setter_name}({java_type} {field_name}) {{
    this.{field_name} = {field_name};
}}'''

        return {
            'declaration': declaration,
            'getter': getter,
            'setter': setter,
            'imports': imports
        }

    def _generate_to_string_body(self: BaseGenerator,
                                  fields: List[ast.FieldDecl]) -> str:
        """Generate toString() body."""
        parts = []
        for i, field_decl in enumerate(fields):
            field_name = self.to_java_field_name(field_decl.name)
            separator = "" if i == 0 else ", "
            # Mask PII fields in toString
            if self._get_pii_profile(field_decl):
                parts.append(f'                "{separator}{field_name}=****" +')
            else:
                parts.append(f'                "{separator}{field_name}=" + {field_name} +')
        return '\n'.join(parts)

    def _generate_correlation_key_method(self: BaseGenerator,
                                          fields: List[ast.FieldDecl]) -> str:
        """Generate correlation key methods for Flink keying.

        These methods support:
        - getCorrelationKey(String[] fields): Dynamic key from specified fields
        - getBufferKey(String[] fields): Alias for correlation key (used in hold patterns)
        - getKey(): Simple key accessor for RoutedEvent compatibility
        """
        # Build field name to getter mapping
        field_getters = []
        for field_decl in fields:
            field_name = field_decl.name
            getter_name = f"get{self.to_java_field_name(field_name)[0].upper()}{self.to_java_field_name(field_name)[1:]}"
            field_getters.append((field_name, getter_name))

        # Build switch cases for correlation key method
        switch_cases = []
        for field_name, getter_name in field_getters:
            switch_cases.append(f'''                case "{field_name}":
                    sb.append({getter_name}());
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
{self._generate_default_key_body(field_getters)}
    }}'''

    def _generate_default_key_body(self: BaseGenerator,
                                    field_getters: List[tuple]) -> str:
        """Generate default key body for getKey() method."""
        if not field_getters:
            return '        return "default";'

        # Return first field value as string
        first_field, first_getter = field_getters[0]
        return f'''        Object val = {first_getter}();
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
