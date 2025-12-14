# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Window Generator Mixin

Generates Flink windowing code from L1 window declarations.
"""

from typing import Set

from backend.ast import proc_ast as ast


class WindowGeneratorMixin:
    """
    Mixin for generating Flink windowing operations.

    Generates:
    - Tumbling windows
    - Sliding windows
    - Session windows
    - Allowed lateness and late data handling
    """

    def generate_window_code(self, process: ast.ProcessDefinition, input_stream: str) -> tuple:
        """Generate windowing code for a process."""
        window_decl = self._find_window_decl(process)
        if not window_decl:
            return "", input_stream

        return self._generate_window(window_decl, input_stream)

    def _find_window_decl(self, process: ast.ProcessDefinition) -> ast.WindowDecl:
        """Find window declaration in processing steps."""
        if not process.processing:
            return None
        for op in process.processing:
            if isinstance(op, ast.WindowDecl):
                return op
        return None

    def _generate_window(self, window: ast.WindowDecl, input_stream: str) -> tuple:
        """Generate window operator code."""
        output_stream = f"windowed{input_stream[0].upper()}{input_stream[1:]}"

        window_assigner = self._get_window_assigner(window)
        lateness_code = self._get_lateness_code(window)
        late_data_code = self._get_late_data_code(window)

        lines = [
            f"// Window: {window.window_type.value} {self._format_duration(window.size)}",
            f"WindowedStream<?, ?, TimeWindow> {output_stream} = {input_stream}",
            f"    .window({window_assigner})",
        ]

        if lateness_code:
            lines.append(f"    .allowedLateness({lateness_code})")

        if late_data_code:
            lines.append(f"    .sideOutputLateData({late_data_code})")

        lines.append("    ;")
        lines.append("")

        return '\n'.join(lines), output_stream

    def _get_window_assigner(self, window: ast.WindowDecl) -> str:
        """Get the appropriate window assigner."""
        size_str = self._duration_to_time(window.size)

        if window.window_type == ast.WindowType.TUMBLING:
            return f"TumblingEventTimeWindows.of({size_str})"
        elif window.window_type == ast.WindowType.SLIDING:
            slide_str = self._duration_to_time(window.slide) if window.slide else "Time.seconds(10)"
            return f"SlidingEventTimeWindows.of({size_str}, {slide_str})"
        elif window.window_type == ast.WindowType.SESSION:
            return f"EventTimeSessionWindows.withGap({size_str})"
        else:
            return f"TumblingEventTimeWindows.of({size_str})"

    def _get_lateness_code(self, window: ast.WindowDecl) -> str:
        """Get allowed lateness code if specified."""
        if window.options and window.options.lateness:
            duration = window.options.lateness.duration
            return self._duration_to_time(duration)
        return None

    def _get_late_data_code(self, window: ast.WindowDecl) -> str:
        """Get late data side output code if specified."""
        if window.options and window.options.late_data:
            target = window.options.late_data.target
            tag_name = self._to_camel_case(target) + "Tag"
            return f"{tag_name}"
        return None

    def _duration_to_time(self, duration: ast.Duration) -> str:
        """Convert Duration to Flink Time call."""
        unit_map = {
            'ms': 'milliseconds',
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
        }
        method = unit_map.get(duration.unit, 'seconds')
        return f"Time.{method}({duration.value})"

    def _format_duration(self, duration: ast.Duration) -> str:
        """Format duration for comments."""
        unit_names = {
            'ms': 'milliseconds',
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
        }
        unit = unit_names.get(duration.unit, duration.unit)
        return f"{duration.value} {unit}"

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_window_imports(self) -> Set[str]:
        """Get required imports for window generation."""
        return {
            'org.apache.flink.streaming.api.datastream.WindowedStream',
            'org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows',
            'org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows',
            'org.apache.flink.streaming.api.windowing.assigners.EventTimeSessionWindows',
            'org.apache.flink.streaming.api.windowing.windows.TimeWindow',
            'org.apache.flink.streaming.api.windowing.time.Time',
        }
