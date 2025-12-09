"""
OnChange Generator Mixin

Generates Java code for L3 Transform on_change blocks.
Handles field change detection and recalculation logic.
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class OnChangeGeneratorMixin:
    """
    Mixin for generating Java on_change handling code.

    Generates:
    - Field change detection methods
    - Recalculation triggers
    - State tracking for changed fields
    - Conditional update logic
    """

    def generate_onchange_code(
        self,
        on_change: ast.OnChangeBlock,
        input_type: str = "Object"
    ) -> str:
        """Generate complete on_change handling code.

        Args:
            on_change: The on_change block AST node
            input_type: Java type for the input parameter

        Returns:
            Java code implementing on_change logic
        """
        if not on_change:
            return ""

        lines = []

        # Generate watched fields set
        lines.append(self._generate_watched_fields_constant(on_change.watched_fields))
        lines.append("")

        # Generate previous values state
        lines.append(self._generate_previous_values_state(on_change.watched_fields))
        lines.append("")

        # Generate change detection method
        lines.append(self._generate_change_detection_method(
            on_change.watched_fields, input_type
        ))
        lines.append("")

        # Generate recalculate method
        lines.append(self._generate_recalculate_method(
            on_change.recalculate, input_type
        ))
        lines.append("")

        # Generate update tracking method
        lines.append(self._generate_update_tracking_method(
            on_change.watched_fields, input_type
        ))

        return '\n'.join(lines)

    def _generate_watched_fields_constant(
        self,
        watched_fields: List[str]
    ) -> str:
        """Generate constant set of watched field names."""
        fields_str = ", ".join(f'"{f}"' for f in watched_fields)
        return f'''    /**
     * Fields being watched for changes.
     */
    private static final Set<String> WATCHED_FIELDS = Set.of({fields_str});'''

    def _generate_previous_values_state(
        self,
        watched_fields: List[str]
    ) -> str:
        """Generate Flink state for tracking previous field values."""
        lines = [
            "    /**",
            "     * State for tracking previous values of watched fields.",
            "     */",
            "    private transient MapState<String, Object> previousValues;",
            "",
            "    /**",
            "     * Initialize on_change state in open() method.",
            "     * Call this from your open() implementation.",
            "     */",
            "    protected void initOnChangeState() throws Exception {",
            "        MapStateDescriptor<String, Object> descriptor =",
            "            new MapStateDescriptor<>(\"previousValues\", String.class, Object.class);",
            "        previousValues = getRuntimeContext().getMapState(descriptor);",
            "    }",
        ]
        return '\n'.join(lines)

    def _generate_change_detection_method(
        self,
        watched_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to detect field changes."""
        use_map = input_type == "Object" or "Map<" in input_type

        lines = [
            "    /**",
            "     * Detect which watched fields have changed since last invocation.",
            "     *",
            f"     * @param input Current input record",
            "     * @return Set of field names that have changed",
            "     */",
            f"    private Set<String> detectChangedFields({input_type} input) throws Exception {{",
            "        Set<String> changedFields = new HashSet<>();",
            "",
        ]

        for field in watched_fields:
            if use_map:
                current_value = f'input.get("{field}")'
            else:
                getter = self.to_getter(field)
                current_value = f"input.{getter}"

            lines.extend([
                f"        // Check {field}",
                f"        Object current_{self.to_camel_case(field)} = {current_value};",
                f"        Object previous_{self.to_camel_case(field)} = previousValues.get(\"{field}\");",
                f"        if (!Objects.equals(current_{self.to_camel_case(field)}, previous_{self.to_camel_case(field)})) {{",
                f'            changedFields.add("{field}");',
                "        }",
                "",
            ])

        lines.extend([
            "        return changedFields;",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_recalculate_method(
        self,
        recalculate: ast.RecalculateBlock,
        input_type: str
    ) -> str:
        """Generate recalculation method for changed fields."""
        use_map = input_type == "Object" or "Map<" in input_type

        lines = [
            "    /**",
            "     * Recalculate derived values when watched fields change.",
            "     *",
            f"     * @param input Input record to update",
            "     * @param changedFields Fields that have changed",
            "     */",
            f"    private void recalculate({input_type} input, Set<String> changedFields) {{",
            "        if (changedFields.isEmpty()) {",
            "            return;",
            "        }",
            "",
        ]

        for assignment in recalculate.assignments:
            target_field = ".".join(assignment.target.parts)
            value_expr = self.generate_expression(assignment.value, use_map=use_map)

            if use_map:
                # Map-based assignment
                if len(assignment.target.parts) == 1:
                    lines.append(
                        f'        input.put("{assignment.target.parts[0]}", {value_expr});'
                    )
                else:
                    # Nested field - generate getter chain then put
                    lines.append(f"        // Update nested field: {target_field}")
                    parent_path = assignment.target.parts[:-1]
                    final_field = assignment.target.parts[-1]
                    getter_chain = self._generate_map_getter_chain(parent_path)
                    lines.append(
                        f'        ((Map<String, Object>){getter_chain}).put("{final_field}", {value_expr});'
                    )
            else:
                # POJO-based assignment with setter
                setter_chain = self._generate_setter_chain(assignment.target)
                lines.append(f"        input.{setter_chain}({value_expr});")

        lines.extend([
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_update_tracking_method(
        self,
        watched_fields: List[str],
        input_type: str
    ) -> str:
        """Generate method to update tracked previous values."""
        use_map = input_type == "Object" or "Map<" in input_type

        lines = [
            "    /**",
            "     * Update previous values state after processing.",
            "     *",
            f"     * @param input Processed input record",
            "     */",
            f"    private void updatePreviousValues({input_type} input) throws Exception {{",
        ]

        for field in watched_fields:
            if use_map:
                current_value = f'input.get("{field}")'
            else:
                getter = self.to_getter(field)
                current_value = f"input.{getter}"

            lines.append(f'        previousValues.put("{field}", {current_value});')

        lines.extend([
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_map_getter_chain(self, parts: List[str]) -> str:
        """Generate nested Map.get() chain."""
        result = "input"
        for part in parts:
            result = f'((Map<String, Object>){result}.get("{part}"))'
        return result

    def _generate_setter_chain(self, field_path: ast.FieldPath) -> str:
        """Generate setter method chain for POJO field path."""
        parts = field_path.parts
        if len(parts) == 1:
            return self.to_setter(parts[0])
        setters = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                setters.append(self.to_getter(part))
            else:
                setters.append(self.to_setter(part))
        return ".".join(setters)

    def generate_onchange_open_init(self) -> str:
        """Generate initialization call for open() method."""
        return "        initOnChangeState();"

    def generate_onchange_process_wrapper(
        self,
        input_type: str,
        output_type: str
    ) -> str:
        """Generate wrapper code for processElement with on_change handling.

        Returns code snippet to insert at start of processElement.
        """
        return f'''        // On-change detection and recalculation
        Set<String> changedFields = detectChangedFields(value);
        if (!changedFields.isEmpty()) {{
            recalculate(value, changedFields);
        }}'''

    def generate_onchange_post_process(self) -> str:
        """Generate code to call after processing to update tracking state."""
        return "        updatePreviousValues(value);"

    def get_onchange_imports(self) -> Set[str]:
        """Get required imports for on_change generation."""
        return {
            'java.util.Set',
            'java.util.HashSet',
            'java.util.Objects',
            'java.util.Map',
            'org.apache.flink.api.common.state.MapState',
            'org.apache.flink.api.common.state.MapStateDescriptor',
        }
