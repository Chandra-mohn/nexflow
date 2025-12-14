# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Mapping Generator Mixin

Generates Java mapping code from L3 Transform mappings blocks.
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class MappingGeneratorMixin:
    """
    Mixin for generating Java field mapping code.

    Generates:
    - Field-to-field mappings
    - Expression-based mappings
    - Null-safe mapping chains
    - Nested object construction
    """

    def generate_mappings_code(self, mappings: ast.MappingsBlock, output_type: str) -> str:
        """Generate mapping method code."""
        if not mappings or not mappings.mappings:
            return "        // No mappings defined"

        lines = [
            "    /**",
            "     * Apply field mappings to build output object.",
            "     */",
            f"    private {output_type} applyMappings(Object input) {{",
            f"        {output_type} result = new {output_type}();",
            "",
        ]

        for mapping in mappings.mappings:
            lines.append(self._generate_mapping(mapping))

        lines.extend([
            "",
            "        return result;",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_mapping(self, mapping: ast.Mapping) -> str:
        """Generate code for a single field mapping."""
        target = self._generate_setter_chain(mapping.target)
        value = self.generate_expression(mapping.expression)

        return f"        result.{target}({value});"

    def _generate_setter_chain(self, field_path: ast.FieldPath) -> str:
        """Generate setter method chain for field path."""
        parts = field_path.parts

        if len(parts) == 1:
            return self.to_setter(parts[0])

        # For nested paths like enriched.transaction_id
        # Generate: getEnriched().setTransactionId
        setters = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                setters.append(self.to_getter(part))
            else:
                setters.append(self.to_setter(part))

        return ".".join(setters)

    def generate_apply_block_code(self, apply: ast.ApplyBlock, use_map: bool = False) -> str:
        """Generate code for apply block (simple transforms).

        Handles local variables and output field assignments, tracking which
        fields have been assigned so later expressions can reference them.
        """
        if not apply or not apply.statements:
            return "        // No apply logic defined"

        lines = []
        local_vars = []
        # Track output fields that have been assigned (for result.get() access)
        assigned_output_fields = []

        for stmt in apply.statements:
            if isinstance(stmt, ast.LocalAssignment):
                # Local variable assignment - creates a Java local var
                var_name = self.to_camel_case(stmt.name)
                value = self.generate_expression(
                    stmt.value, use_map, local_vars, assigned_output_fields
                )
                lines.append(f"        var {var_name} = {value};")
                local_vars.append(var_name)

            elif isinstance(stmt, ast.Assignment):
                # Output field assignment - stores in result map/object
                target_field = stmt.target.parts[-1] if stmt.target.parts else "result"
                value = self.generate_expression(
                    stmt.value, use_map, local_vars, assigned_output_fields
                )
                if use_map:
                    lines.append(f'        result.put("{target_field}", {value});')
                    # Track this field as assigned for later reference
                    assigned_output_fields.append(target_field)
                else:
                    target = self._generate_setter_chain(stmt.target)
                    lines.append(f"        result.{target}({value});")

        return '\n'.join(lines)

    def generate_transform_function_method(
        self,
        transform: ast.TransformDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate the main transform function method."""
        # Use Map for Object or Map<String, Object> types to allow dynamic field access
        use_map = output_type in ("Object", "Map<String, Object>")
        actual_output_type = "Map<String, Object>" if output_type == "Object" else output_type
        actual_input_type = "Map<String, Object>" if input_type == "Object" else input_type

        lines = [
            "    /**",
            f"     * Transform: {transform.name}",
            f"     * {transform.metadata.description if transform.metadata else ''}",
            "     */",
            f"    public {actual_output_type} transform({actual_input_type} input) throws Exception {{",
        ]

        # Add input validation if defined
        if transform.validate_input:
            lines.append("        validateInput(input);")
            lines.append("")

        # Generate result initialization
        if use_map:
            lines.append("        Map<String, Object> result = new HashMap<>();")
        else:
            lines.append(f"        {output_type} result = new {output_type}();")
        lines.append("")

        # Add apply logic
        if transform.apply:
            lines.append("        // Apply transformation logic")
            lines.append(self.generate_apply_block_code(transform.apply, use_map))
            lines.append("")

        # Add output validation if defined
        if transform.validate_output:
            lines.append("        validateOutput(result);")
            lines.append("")

        lines.extend([
            "        return result;",
            "    }",
        ])

        return '\n'.join(lines)

    def generate_block_transform_method(
        self,
        block: ast.TransformBlockDef,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate method for block-level transform."""
        lines = [
            "    /**",
            f"     * Transform Block: {block.name}",
            f"     * {block.metadata.description if block.metadata else ''}",
            "     */",
            f"    public {output_type} transform({input_type} input) throws Exception {{",
        ]

        # Add input validation
        if block.validate_input:
            lines.append("        validateInput(input);")
            lines.append("")

        # Check if we have compose - if so, the compose code handles result generation
        if block.compose:
            # Generate composition code which handles result construction
            lines.append("        // Transform composition")
            compose_code = self.generate_compose_code(block.compose, input_type, output_type)
            lines.append(compose_code)
        else:
            # Standard mappings-based result construction
            # Generate result initialization
            lines.append(f"        {output_type} result = new {output_type}();")
            lines.append("")

            # Add mappings
            if block.mappings:
                lines.append("        // Apply field mappings")
                for mapping in block.mappings.mappings:
                    lines.append(self._generate_mapping(mapping))
                lines.append("")

            # Add invariant checks
            if block.invariant:
                lines.append("        checkInvariants(result);")
                lines.append("")

            # Add output validation
            if block.validate_output:
                lines.append("        validateOutput(result);")
                lines.append("")

            lines.extend([
                "        return result;",
            ])

        lines.append("    }")

        return '\n'.join(lines)

    # Note: _to_getter, _to_setter, _to_camel_case are inherited from BaseGenerator
    # as to_getter(), to_setter(), to_camel_case() - use those instead

    def get_mapping_imports(self) -> Set[str]:
        """Get required imports for mapping generation."""
        return {
            'java.util.Objects',
        }
