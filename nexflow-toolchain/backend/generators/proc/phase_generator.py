# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Phase Generator Mixin

Generates Flink code for business date and phase-based execution from L1 declarations.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 Markers & Phases Features:
- markers block (EOD marker definitions)
- phase before/between/after marker(s)
- business_date from calendar
- on complete signal
─────────────────────────────────────────────────────────────────────
"""

from typing import Set, List, Dict

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_camel_case, to_pascal_case


class PhaseGeneratorMixin:
    """
    Mixin for generating Flink phase orchestration code.

    Generates:
    - Marker state management (ValueState for each marker)
    - Phase condition evaluation
    - Signal emission on phase completion
    - Business date calendar integration
    """

    def generate_marker_state_declarations(self, process: ast.ProcessDefinition) -> str:
        """Generate ValueState declarations for each marker."""
        if not hasattr(process, 'markers') or not process.markers:
            return ""

        markers_block = process.markers
        lines = [
            "// EOD Marker State",
        ]

        for marker in markers_block.markers:
            state_name = to_camel_case(marker.name) + "State"
            lines.append(f"private transient ValueState<Boolean> {state_name};")

        lines.append("")
        return '\n'.join(lines)

    def generate_marker_state_init(self, process: ast.ProcessDefinition) -> str:
        """Generate marker state initialization in open() method."""
        if not hasattr(process, 'markers') or not process.markers:
            return ""

        markers_block = process.markers
        lines = [
            "// Initialize marker state descriptors",
        ]

        for marker in markers_block.markers:
            state_name = to_camel_case(marker.name) + "State"
            descriptor_name = to_camel_case(marker.name) + "Descriptor"
            lines.extend([
                f"ValueStateDescriptor<Boolean> {descriptor_name} = new ValueStateDescriptor<>(",
                f"    \"{marker.name}\",",
                f"    Boolean.class,",
                f"    false);",
                f"{state_name} = getRuntimeContext().getState({descriptor_name});",
            ])

        lines.append("")
        return '\n'.join(lines)

    def generate_marker_check_method(self, marker: ast.MarkerDef) -> str:
        """Generate a method that checks if a marker condition is satisfied."""
        method_name = f"check{to_pascal_case(marker.name)}Condition"
        condition_code = self._generate_condition_code(marker.condition)

        lines = [
            f"/** Check if marker {marker.name} condition is satisfied. */",
            f"private boolean {method_name}() throws Exception {{",
            f"    return {condition_code};",
            f"}}",
            "",
        ]

        return '\n'.join(lines)

    def generate_marker_check_methods(self, process: ast.ProcessDefinition) -> str:
        """Generate check methods for all markers."""
        if not hasattr(process, 'markers') or not process.markers:
            return ""

        lines = []
        for marker in process.markers.markers:
            lines.append(self.generate_marker_check_method(marker))

        return '\n'.join(lines)

    def generate_phase_filter(self, phase: ast.PhaseBlock, input_stream: str, input_type: str) -> str:
        """Generate a filter/branch for a phase based on marker conditions.

        Returns code that filters the stream based on phase activation conditions.
        """
        spec = phase.spec
        phase_var = to_camel_case(self._get_phase_name(spec))
        output_stream = f"{phase_var}Stream"

        lines = [
            f"// Phase: {self._format_phase_spec(spec)}",
        ]

        if spec.phase_type == ast.PhaseType.ANYTIME:
            # Anytime phase - no filtering needed
            lines.append(f"DataStream<{input_type}> {output_stream} = {input_stream};")
        elif spec.phase_type == ast.PhaseType.BEFORE:
            # Before marker - filter records where marker is NOT yet satisfied
            marker_state = to_camel_case(spec.end_marker) + "State"
            lines.extend([
                f"DataStream<{input_type}> {output_stream} = {input_stream}",
                f"    .filter(value -> !{marker_state}.value())",
                f"    .name(\"Phase: before {spec.end_marker}\");",
            ])
        elif spec.phase_type == ast.PhaseType.AFTER:
            # After marker - filter records where marker IS satisfied
            marker_state = to_camel_case(spec.start_marker) + "State"
            lines.extend([
                f"DataStream<{input_type}> {output_stream} = {input_stream}",
                f"    .filter(value -> {marker_state}.value())",
                f"    .name(\"Phase: after {spec.start_marker}\");",
            ])
        elif spec.phase_type == ast.PhaseType.BETWEEN:
            # Between markers - filter where start IS satisfied but end is NOT
            start_state = to_camel_case(spec.start_marker) + "State"
            end_state = to_camel_case(spec.end_marker) + "State"
            lines.extend([
                f"DataStream<{input_type}> {output_stream} = {input_stream}",
                f"    .filter(value -> {start_state}.value() && !{end_state}.value())",
                f"    .name(\"Phase: between {spec.start_marker} and {spec.end_marker}\");",
            ])

        lines.append("")
        return '\n'.join(lines)

    def generate_on_complete_handler(self, on_complete: ast.OnCompleteClause) -> str:
        """Generate code for on complete signal emission."""
        signal_name = on_complete.signal_name
        target = on_complete.target

        # Build target argument if present
        target_arg = f', "{target}"' if target else ''

        if on_complete.condition:
            # Conditional signal
            return f'''if ({on_complete.condition}) {{
    emitSignal("{signal_name}"{target_arg});
}}'''
        else:
            # Unconditional signal
            return f'emitSignal("{signal_name}"{target_arg});'

    def generate_signal_emission_method(self, process: ast.ProcessDefinition) -> str:
        """Generate the emitSignal helper method."""
        lines = [
            "/** Emit a signal to trigger marker transitions. */",
            "private void emitSignal(String signalName, String... targets) {",
            "    // Signal emission via side output or state update",
            "    SignalEvent signal = new SignalEvent(signalName, System.currentTimeMillis());",
            "    ctx.output(signalOutputTag, signal);",
            "    LOG.info(\"Emitted signal: {}\", signalName);",
            "}",
            "",
        ]
        return '\n'.join(lines)

    def generate_business_date_code(self, business_date: ast.BusinessDateDecl) -> str:
        """Generate code for business date calendar lookup."""
        calendar_name = business_date.calendar_name
        calendar_var = to_camel_case(calendar_name)

        lines = [
            f"// Business date from calendar: {calendar_name}",
            f"private transient TradingCalendar {calendar_var}Calendar;",
            "",
            f"// In open():",
            f"{calendar_var}Calendar = TradingCalendarFactory.getCalendar(\"{calendar_name}\");",
            "",
            f"// Business date accessor",
            f"private LocalDate getBusinessDate() {{",
            f"    return {calendar_var}Calendar.getCurrentBusinessDate();",
            f"}}",
            "",
        ]
        return '\n'.join(lines)

    def _generate_condition_code(self, condition: ast.AnyMarkerCondition) -> str:
        """Generate Java code for evaluating a marker condition."""
        if isinstance(condition, ast.SignalCondition):
            # Check if signal was received (via state)
            signal_state = to_camel_case(condition.signal_name) + "SignalReceived"
            return f"{signal_state}.value()"

        elif isinstance(condition, ast.MarkerRefCondition):
            # Check if referenced marker is complete
            marker_state = to_camel_case(condition.marker_name) + "State"
            return f"{marker_state}.value()"

        elif isinstance(condition, ast.StreamDrainedCondition):
            # Check if stream has no pending messages
            return f"isStreamDrained(\"{condition.stream_name}\")"

        elif isinstance(condition, ast.CountThresholdCondition):
            # Check count threshold
            count_var = to_camel_case(condition.stream_name) + "Count"
            return f"{count_var}.value() {condition.operator} {condition.threshold}L"

        elif isinstance(condition, ast.TimeBasedCondition):
            # Check time condition
            return f"isTimeReached(\"{condition.time_spec}\")"

        elif isinstance(condition, ast.ApiCheckCondition):
            # Check API service status
            return f'checkApiStatus("{condition.api_name}", "{condition.service_name}", "{condition.check_name}")'

        elif isinstance(condition, ast.CompoundCondition):
            # Combine sub-conditions with AND/OR
            sub_conditions = [self._generate_condition_code(c) for c in condition.conditions]
            joiner = " && " if condition.operator == "and" else " || "
            return f"({joiner.join(sub_conditions)})"

        else:
            return "true /* unknown condition */"

    def _get_phase_name(self, spec: ast.PhaseSpec) -> str:
        """Generate a name for a phase based on its spec."""
        if spec.phase_type == ast.PhaseType.ANYTIME:
            return "anytimePhase"
        elif spec.phase_type == ast.PhaseType.BEFORE:
            return f"before{to_pascal_case(spec.end_marker)}Phase"
        elif spec.phase_type == ast.PhaseType.AFTER:
            return f"after{to_pascal_case(spec.start_marker)}Phase"
        elif spec.phase_type == ast.PhaseType.BETWEEN:
            return f"between{to_pascal_case(spec.start_marker)}And{to_pascal_case(spec.end_marker)}Phase"
        return "phase"

    def _format_phase_spec(self, spec: ast.PhaseSpec) -> str:
        """Format phase spec for comments."""
        if spec.phase_type == ast.PhaseType.ANYTIME:
            return "anytime"
        elif spec.phase_type == ast.PhaseType.BEFORE:
            return f"before {spec.end_marker}"
        elif spec.phase_type == ast.PhaseType.AFTER:
            return f"after {spec.start_marker}"
        elif spec.phase_type == ast.PhaseType.BETWEEN:
            return f"between {spec.start_marker} and {spec.end_marker}"
        return "unknown phase"

    def get_phase_imports(self) -> Set[str]:
        """Get required imports for phase generation."""
        return {
            'org.apache.flink.api.common.state.ValueState',
            'org.apache.flink.api.common.state.ValueStateDescriptor',
            'io.nexflow.calendar.TradingCalendar',
            'io.nexflow.calendar.TradingCalendarFactory',
            'io.nexflow.signals.SignalEvent',
            'java.time.LocalDate',
        }
