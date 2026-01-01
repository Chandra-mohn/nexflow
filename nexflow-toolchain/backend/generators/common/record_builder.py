# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Java Record Builder Module

Shared utilities for generating Java Record classes across Rules and Transform generators.
Provides a unified approach to generating immutable data classes using Java 17+ Records.

Key features:
- Immutable by default (no setters)
- Automatic equals(), hashCode(), toString()
- Compact constructor for validation
- withField() methods for creating modified copies
- 80% less boilerplate than POJOs
"""

from typing import List, Dict, Set, Callable, Any
from backend.generators.common.java_utils import to_camel_case


class RecordBuilderMixin:
    """
    Mixin for generating Java Record classes.

    Used by both Rules and Transform generators for output data types.
    Replaces the older POJO generators with modern Java Records.
    """

    def generate_record_class(
        self,
        class_name: str,
        fields: List[Any],
        package: str,
        description: str,
        field_name_accessor: Callable[[Any], str],
        field_type_accessor: Callable[[Any], str],
    ) -> str:
        """Generate a complete Java Record class.

        Args:
            class_name: Name of the record class
            fields: List of field definitions (AST nodes)
            package: Java package name
            description: Class description for Javadoc
            field_name_accessor: Function to extract field name from AST node
            field_type_accessor: Function to extract Java type from AST node

        Returns:
            Complete Java record class source code
        """
        # Build field info list
        field_infos = []
        imports: Set[str] = {'java.io.Serializable'}

        for field in fields:
            field_name = to_camel_case(field_name_accessor(field))
            java_type = field_type_accessor(field)
            field_infos.append({
                'field_name': field_name,
                'java_type': java_type,
                'original_name': field_name_accessor(field),
            })
            # Collect imports based on type
            imports.update(self._get_type_imports(java_type))

        if field_infos:
            imports.add('java.util.Objects')

        # Generate components
        record_components = self._format_record_components(field_infos)
        with_methods = self._generate_with_methods(field_infos, class_name)
        builder_class = self._generate_builder_class(field_infos, class_name)

        # Build imports string
        imports_str = '\n'.join(f'import {imp};' for imp in sorted(imports))

        # Format with methods
        with_methods_str = '\n\n'.join(with_methods)

        return f'''// Nexflow DSL Toolchain - Auto-generated
// DO NOT EDIT - Generated from Nexflow DSL specification

package {package};

{imports_str}

/**
 * {description}
 *
 * <p>This is an immutable Java Record. Use withField() methods to create
 * modified copies, or use the Builder for step-by-step construction.</p>
 */
public record {class_name}(
{record_components}
) implements Serializable {{

    private static final long serialVersionUID = 1L;

{with_methods_str}

{builder_class}
}}
'''

    def _format_record_components(self, field_infos: List[Dict]) -> str:
        """Format record components (constructor parameters)."""
        if not field_infos:
            return ""

        components = []
        for i, info in enumerate(field_infos):
            comma = "," if i < len(field_infos) - 1 else ""
            components.append(f"    {info['java_type']} {info['field_name']}{comma}")

        return '\n'.join(components)

    def _generate_with_methods(
        self,
        field_infos: List[Dict],
        class_name: str
    ) -> List[str]:
        """Generate withField() methods for creating modified copies."""
        methods = []
        all_field_names = [info['field_name'] for info in field_infos]

        for field_info in field_infos:
            field_name = field_info['field_name']
            java_type = field_info['java_type']
            method_name = f"with{field_name[0].upper()}{field_name[1:]}"

            # Build constructor arguments
            args = []
            for fn in all_field_names:
                if fn == field_name:
                    args.append(field_name)  # Use new parameter value
                else:
                    args.append(f"{fn}()")  # Use accessor for existing value
            args_str = ', '.join(args)

            method = f'''    /**
     * Create a copy with modified {field_name}.
     *
     * @param {field_name} The new value
     * @return New record instance with updated {field_name}
     */
    public {class_name} {method_name}({java_type} {field_name}) {{
        return new {class_name}({args_str});
    }}'''
            methods.append(method)

        return methods

    def _generate_builder_class(
        self,
        field_infos: List[Dict],
        class_name: str
    ) -> str:
        """Generate Builder inner class for step-by-step construction."""
        if not field_infos:
            return ""

        # Builder fields
        builder_fields = []
        for info in field_infos:
            builder_fields.append(
                f"        private {info['java_type']} {info['field_name']};"
            )

        # Builder setters
        builder_setters = []
        for info in field_infos:
            field_name = info['field_name']
            java_type = info['java_type']
            builder_setters.append(f'''        /**
         * Set {field_name}.
         */
        public Builder {field_name}({java_type} {field_name}) {{
            this.{field_name} = {field_name};
            return this;
        }}''')

        # Build method
        args = ', '.join(info['field_name'] for info in field_infos)

        return f'''    /**
     * Builder for {class_name}.
     *
     * <p>Use for step-by-step construction when not all values are available at once.</p>
     */
    public static class Builder {{

{chr(10).join(builder_fields)}

{chr(10).join(builder_setters)}

        /**
         * Build the {class_name} record.
         *
         * @return New {class_name} instance
         */
        public {class_name} build() {{
            return new {class_name}({args});
        }}
    }}

    /**
     * Create a new Builder for {class_name}.
     *
     * @return New Builder instance
     */
    public static Builder builder() {{
        return new Builder();
    }}'''

    def _get_type_imports(self, java_type: str) -> Set[str]:
        """Get required imports for a Java type."""
        imports = set()

        type_imports = {
            'BigDecimal': 'java.math.BigDecimal',
            'LocalDate': 'java.time.LocalDate',
            'Instant': 'java.time.Instant',
            'List': 'java.util.List',
            'Map': 'java.util.Map',
            'Set': 'java.util.Set',
            'UUID': 'java.util.UUID',
        }

        for type_name, import_path in type_imports.items():
            if type_name in java_type:
                imports.add(import_path)

        return imports
