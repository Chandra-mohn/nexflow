"""
Builder Generator Module

Generates Java Builder classes for immutable Java Record construction.
Uses the canonical constructor pattern compatible with Java Records.
"""

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class BuilderGeneratorMixin:
    """Mixin providing Builder pattern generation capabilities for Java Records.

    Java Records are immutable and have:
    - Canonical constructor with all fields
    - Accessor methods: field() (not getField())
    - No setters (immutable)

    The builder collects field values and passes them to the canonical constructor.
    """

    def generate_builder(self: BaseGenerator, schema: ast.SchemaDefinition,
                         class_name: str, package: str) -> str:
        """Generate builder class for immutable Record construction.

        The generated builder uses the canonical constructor pattern:
        - Collects field values via fluent setter methods
        - build() passes all values to the Record's canonical constructor
        """
        header = self.generate_java_header(
            f"{class_name}Builder", f"Builder for {class_name}"
        )
        package_decl = self.generate_package_declaration(package)

        all_fields = self._collect_all_fields(schema)

        # Collect imports
        imports_set = set()
        for field_decl in all_fields:
            imports_set.update(self._get_field_imports(field_decl.field_type))

        imports = self.generate_imports(list(imports_set))

        # Field declarations
        field_declarations = []
        builder_methods = []
        constructor_args = []

        for field_decl in all_fields:
            field_name = self.to_java_field_name(field_decl.name)
            java_type = self._get_field_java_type(field_decl.field_type)

            field_declarations.append(f"    private {java_type} {field_name};")

            method_name = field_name
            builder_methods.append(
                f'''    public {class_name}Builder {method_name}({java_type} {field_name}) {{
        this.{field_name} = {field_name};
        return this;
    }}'''
            )

            # For canonical constructor, just pass the field values
            constructor_args.append(f"this.{field_name}")

        fields_block = '\n'.join(field_declarations)
        methods_block = '\n\n'.join(builder_methods)
        args_str = ', '.join(constructor_args)

        return f'''{header}
{package_decl}
{imports}

public class {class_name}Builder {{

{fields_block}

{methods_block}

    public {class_name} build() {{
        return new {class_name}({args_str});
    }}
}}
'''
