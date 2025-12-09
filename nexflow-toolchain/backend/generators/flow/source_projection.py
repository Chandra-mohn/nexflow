"""
Source Projection Mixin

Generates field projection code for Flink DataStream sources.
"""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.ast import proc_ast as ast


class SourceProjectionMixin:
    """
    Mixin for generating field projection code.

    Generates:
    - Include-only field projection
    - Exclude-field projection with reflection
    """

    def _generate_projection(
        self,
        receive: 'ast.ReceiveDecl',
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """
        Generate field projection code.

        Feature 2: project [fields] / project except [fields]

        Strategy: Post-deserialization projection using Map<String, Object>
        - Deserialize full schema first
        - Map to only needed fields
        - Reduces memory footprint for downstream operators
        """
        project = receive.project
        projected_var = f"projected{self.to_java_class_name(stream_alias)}Stream"

        if project.is_except:
            return self._generate_except_projection(
                project, stream_var, schema_class, projected_var, stream_alias
            )
        else:
            return self._generate_include_projection(
                project, stream_var, projected_var, stream_alias
            )

    def _generate_except_projection(
        self,
        project,
        stream_var: str,
        schema_class: str,
        projected_var: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """Generate projection that excludes specified fields."""
        excluded_fields = ', '.join(f'"{f}"' for f in project.fields)
        lines = [
            f"// Projection: exclude [{', '.join(project.fields)}]",
            f"DataStream<Map<String, Object>> {projected_var} = {stream_var}",
            f"    .map(event -> {{",
            f"        Map<String, Object> projected = new HashMap<>();",
            f"        java.util.Set<String> excluded = java.util.Set.of({excluded_fields});",
            f"        // Copy all fields except excluded ones",
            f"        // Note: For production, use reflection or generated field list",
            f"        java.lang.reflect.Method[] methods = event.getClass().getMethods();",
            f"        for (java.lang.reflect.Method method : methods) {{",
            f"            String name = method.getName();",
            f"            if (name.startsWith(\"get\") && !name.equals(\"getClass\") && method.getParameterCount() == 0) {{",
            f"                String fieldName = Character.toLowerCase(name.charAt(3)) + name.substring(4);",
            f"                // Convert camelCase to snake_case for DSL field names",
            f"                String snakeCase = fieldName.replaceAll(\"([a-z])([A-Z])\", \"$1_$2\").toLowerCase();",
            f"                if (!excluded.contains(snakeCase)) {{",
            f"                    try {{",
            f"                        projected.put(snakeCase, method.invoke(event));",
            f"                    }} catch (Exception e) {{ /* skip */ }}",
            f"                }}",
            f"            }}",
            f"        }}",
            f"        return projected;",
            f"    }})",
            f"    .name(\"project-except-{stream_alias}\");",
            "",
        ]
        return '\n'.join(lines), projected_var

    def _generate_include_projection(
        self,
        project,
        stream_var: str,
        projected_var: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """Generate projection that includes only specified fields."""
        field_mappings = []
        for field in project.fields:
            getter = f"event.get{self._to_pascal_case(field)}()"
            field_mappings.append(f'        projected.put("{field}", {getter});')

        lines = [
            f"// Projection: include only [{', '.join(project.fields)}]",
            f"DataStream<Map<String, Object>> {projected_var} = {stream_var}",
            f"    .map(event -> {{",
            f"        Map<String, Object> projected = new HashMap<>({len(project.fields)});",
            '\n'.join(field_mappings),
            f"        return projected;",
            f"    }})",
            f"    .name(\"project-{stream_alias}\");",
            "",
        ]
        return '\n'.join(lines), projected_var

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
