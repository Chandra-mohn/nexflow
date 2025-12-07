"""
POJO Generator Module

Generates Java POJO classes from Schema AST definitions.
Handles field declarations, getters/setters, and toString().
"""

from typing import Dict, List, Optional, Set

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class PojoGeneratorMixin:
    """Mixin providing POJO generation capabilities."""

    def generate_pojo(self: BaseGenerator, schema: ast.SchemaDefinition,
                      class_name: str, package: str) -> str:
        """Generate Java POJO class."""
        self._imports: Set[str] = set()

        # Collect all fields
        all_fields = self._collect_all_fields(schema)

        # Build field declarations
        field_declarations = []
        getter_setters = []
        for field_decl in all_fields:
            java_field = self._generate_field(field_decl)
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

        return f'''{header}
{package_decl}
{imports}

public class {class_name} implements Serializable {{

    private static final long serialVersionUID = 1L;

{fields_block}

    public {class_name}() {{
        // Default constructor
    }}

{methods_block}

    @Override
    public String toString() {{
        return "{class_name}{{" +
{self._generate_to_string_body(all_fields)}
                "}}";
    }}
}}
'''

    def _generate_field(self: BaseGenerator, field_decl: ast.FieldDecl) -> Dict:
        """Generate field declaration, getter, and setter."""
        field_name = self.to_java_field_name(field_decl.name)
        java_type = self._get_field_java_type(field_decl.field_type)
        imports = self._get_field_imports(field_decl.field_type)

        # Check for PII annotation
        pii_profile = self._get_pii_profile(field_decl)
        pii_comment = ""
        if pii_profile:
            pii_comment = f"    // PII: encrypted with '{pii_profile}' profile\n"

        declaration = f"{pii_comment}    private {java_type} {field_name};"

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
