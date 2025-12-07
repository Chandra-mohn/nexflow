"""
Builder Generator Module

Generates Java Builder classes for immutable object construction.
"""

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class BuilderGeneratorMixin:
    """Mixin providing Builder pattern generation capabilities."""

    def generate_builder(self: BaseGenerator, schema: ast.SchemaDefinition,
                         class_name: str, package: str) -> str:
        """Generate builder class for immutable construction."""
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
        build_assignments = []

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

            setter_name = f"set{field_name[0].upper()}{field_name[1:]}"
            build_assignments.append(
                f"        instance.{setter_name}(this.{field_name});"
            )

        fields_block = '\n'.join(field_declarations)
        methods_block = '\n\n'.join(builder_methods)
        assignments_block = '\n'.join(build_assignments)

        return f'''{header}
{package_decl}
{imports}

public class {class_name}Builder {{

{fields_block}

{methods_block}

    public {class_name} build() {{
        {class_name} instance = new {class_name}();
{assignments_block}
        return instance;
    }}
}}
'''
