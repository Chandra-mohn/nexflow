# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Metrics Generator Mixin

Generates Flink metrics registration and update code from L1 metrics declarations.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 Metrics Block Features:
- counter name (increment/decrement counters)
- gauge name (current value metrics)
- histogram name window duration (distribution metrics)
- meter name (throughput/rate metrics)
─────────────────────────────────────────────────────────────────────
"""

from typing import Set

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_camel_case, to_pascal_case


class MetricsGeneratorMixin:
    """
    Mixin for generating Flink metrics code.

    Generates:
    - Metric field declarations
    - Metric registration in open()
    - Metric update helper methods
    - Metric group configuration
    """

    def generate_metrics_declarations(self, process: ast.ProcessDefinition) -> str:
        """Generate metric field declarations for the class."""
        if not hasattr(process, 'metrics') or not process.metrics:
            return ""

        metrics_block = process.metrics
        lines = [
            "// Metrics declarations",
        ]

        for metric in metrics_block.metrics:
            java_type = self._get_metric_java_type(metric.metric_type)
            field_name = to_camel_case(metric.name) + "Metric"

            lines.append(f"private transient {java_type} {field_name};")

        lines.append("")
        return '\n'.join(lines)

    def generate_metrics_init(self, process: ast.ProcessDefinition) -> str:
        """Generate metric registration code for open() method."""
        if not hasattr(process, 'metrics') or not process.metrics:
            return ""

        metrics_block = process.metrics
        group_name = metrics_block.group_name if metrics_block.group_name else process.name

        lines = [
            "// Initialize Flink metrics",
            f"MetricGroup metricGroup = getRuntimeContext().getMetricGroup().addGroup(\"{group_name}\");",
            "",
        ]

        for metric in metrics_block.metrics:
            field_name = to_camel_case(metric.name) + "Metric"
            metric_name = metric.name

            if metric.metric_type == ast.MetricType.COUNTER:
                lines.append(f"{field_name} = metricGroup.counter(\"{metric_name}\");")
            elif metric.metric_type == ast.MetricType.GAUGE:
                # Gauge requires a value holder
                holder_name = to_camel_case(metric.name) + "Value"
                lines.extend([
                    f"final AtomicLong {holder_name} = new AtomicLong(0L);",
                    f"{field_name} = metricGroup.gauge(\"{metric_name}\", () -> {holder_name}.get());",
                ])
            elif metric.metric_type == ast.MetricType.HISTOGRAM:
                lines.append(f"{field_name} = metricGroup.histogram(\"{metric_name}\", new DescriptiveStatisticsHistogram(1000));")
            elif metric.metric_type == ast.MetricType.METER:
                lines.append(f"{field_name} = metricGroup.meter(\"{metric_name}\", new MeterView(60));")

        lines.append("")
        return '\n'.join(lines)

    def generate_metric_update_methods(self, process: ast.ProcessDefinition) -> str:
        """Generate helper methods for updating metrics."""
        if not hasattr(process, 'metrics') or not process.metrics:
            return ""

        metrics_block = process.metrics
        lines = []

        for metric in metrics_block.metrics:
            method_base = to_camel_case(metric.name)
            field_name = method_base + "Metric"

            if metric.metric_type == ast.MetricType.COUNTER:
                lines.extend([
                    f"/** Increment the {metric.name} counter. */",
                    f"protected void increment{to_pascal_case(metric.name)}() {{",
                    f"    if ({field_name} != null) {field_name}.inc();",
                    f"}}",
                    "",
                    f"/** Increment the {metric.name} counter by n. */",
                    f"protected void increment{to_pascal_case(metric.name)}(long n) {{",
                    f"    if ({field_name} != null) {field_name}.inc(n);",
                    f"}}",
                    "",
                ])
            elif metric.metric_type == ast.MetricType.GAUGE:
                holder_name = method_base + "Value"
                lines.extend([
                    f"/** Set the {metric.name} gauge value. */",
                    f"protected void set{to_pascal_case(metric.name)}(long value) {{",
                    f"    {holder_name}.set(value);",
                    f"}}",
                    "",
                ])
            elif metric.metric_type == ast.MetricType.HISTOGRAM:
                lines.extend([
                    f"/** Record a value in the {metric.name} histogram. */",
                    f"protected void record{to_pascal_case(metric.name)}(long value) {{",
                    f"    if ({field_name} != null) {field_name}.update(value);",
                    f"}}",
                    "",
                ])
            elif metric.metric_type == ast.MetricType.METER:
                lines.extend([
                    f"/** Mark an event in the {metric.name} meter. */",
                    f"protected void mark{to_pascal_case(metric.name)}() {{",
                    f"    if ({field_name} != null) {field_name}.markEvent();",
                    f"}}",
                    "",
                    f"/** Mark n events in the {metric.name} meter. */",
                    f"protected void mark{to_pascal_case(metric.name)}(long n) {{",
                    f"    if ({field_name} != null) {field_name}.markEvent(n);",
                    f"}}",
                    "",
                ])

        return '\n'.join(lines)

    def generate_metric_update_code(self, update: ast.MetricUpdateDecl) -> str:
        """Generate code for a single metric update operation."""
        field_name = to_camel_case(update.metric_name) + "Metric"

        if update.operation == "increment":
            if update.value_expression:
                return f"{field_name}.inc({update.value_expression});"
            return f"{field_name}.inc();"
        elif update.operation == "decrement":
            if update.value_expression:
                return f"{field_name}.dec({update.value_expression});"
            return f"{field_name}.dec();"
        elif update.operation == "set":
            holder_name = to_camel_case(update.metric_name) + "Value"
            return f"{holder_name}.set({update.value_expression});"
        elif update.operation == "record":
            return f"{field_name}.update({update.value_expression});"
        elif update.operation == "mark":
            if update.value_expression:
                return f"{field_name}.markEvent({update.value_expression});"
            return f"{field_name}.markEvent();"
        else:
            return f"// Unknown metric operation: {update.operation}"

    def _get_metric_java_type(self, metric_type: ast.MetricType) -> str:
        """Get the Java type for a metric type."""
        type_map = {
            ast.MetricType.COUNTER: "Counter",
            ast.MetricType.GAUGE: "Gauge<Long>",
            ast.MetricType.HISTOGRAM: "Histogram",
            ast.MetricType.METER: "Meter",
        }
        return type_map.get(metric_type, "Counter")

    def get_metrics_imports(self) -> Set[str]:
        """Get required imports for metrics generation."""
        return {
            'org.apache.flink.metrics.Counter',
            'org.apache.flink.metrics.Gauge',
            'org.apache.flink.metrics.Histogram',
            'org.apache.flink.metrics.Meter',
            'org.apache.flink.metrics.MetricGroup',
            'org.apache.flink.metrics.MeterView',
            'org.apache.flink.runtime.metrics.DescriptiveStatisticsHistogram',
            'java.util.concurrent.atomic.AtomicLong',
        }
