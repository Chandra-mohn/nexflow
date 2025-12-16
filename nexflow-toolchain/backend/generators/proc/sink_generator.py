# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Sink Generator Mixin

Generates Flink sink connections from L1 emit declarations.
"""

from typing import Set, List

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case


class SinkGeneratorMixin:
    """
    Mixin for generating Flink sink connectors.

    Generates:
    - KafkaSink builders for Kafka topics
    - Schema serialization setup
    - Side outputs for multiple emit targets
    """

    def generate_sink_code(self, process: ast.ProcessDefinition, input_stream: str) -> str:
        """Generate sink connection code for a process."""
        # v0.5.0+: process.emits is direct list
        if not process.emits:
            return "// No output sinks defined\n"

        lines = []
        emits = [e for e in process.emits if isinstance(e, ast.EmitDecl)]

        # Generate side output tags if multiple emits
        if len(emits) > 1:
            lines.append(self._generate_output_tags(emits))
            lines.append("")

        # Generate sink for each emit
        for emit in emits:
            lines.append(self._generate_sink(emit, input_stream, process))

        return '\n'.join(lines)

    def _generate_output_tags(self, emits: List[ast.EmitDecl]) -> str:
        """Generate OutputTag declarations for side outputs."""
        lines = ["// Side output tags"]
        for emit in emits:
            tag_name = self._to_camel_case(emit.target) + "Tag"
            schema_class = self._get_emit_schema_class(emit)
            lines.append(
                f"private static final OutputTag<{schema_class}> {tag_name} = "
                f"new OutputTag<{schema_class}>(\"{emit.target}\") {{}};"
            )
        return '\n'.join(lines)

    def _generate_sink(self, emit: ast.EmitDecl, input_stream: str, process: ast.ProcessDefinition) -> str:
        """Generate sink code for a single emit declaration.

        Supports fanout strategies:
        - broadcast: Send to all partitions (BroadcastPartitioner)
        - round_robin: Load-balanced distribution (RebalancePartitioner)
        """
        target = emit.target
        schema_class = self._get_emit_schema_class(emit)
        sink_name = self._to_camel_case(target) + "Sink"

        # Determine stream transformation based on fanout strategy
        fanout_transform = ""
        fanout_comment = ""
        if emit.fanout:
            if emit.fanout.strategy == ast.FanoutType.BROADCAST:
                fanout_transform = f".broadcast()"
                fanout_comment = " (BROADCAST to all partitions)"
            elif emit.fanout.strategy == ast.FanoutType.ROUND_ROBIN:
                fanout_transform = f".rebalance()"
                fanout_comment = " (ROUND_ROBIN load balanced)"

        lines = [
            f"// Sink: {target}{fanout_comment}",
            f"KafkaSink<{schema_class}> {sink_name} = KafkaSink",
            f"    .<{schema_class}>builder()",
            f"    .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)",
            f"    .setRecordSerializer(",
            f"        KafkaRecordSerializationSchema.<{schema_class}>builder()",
            f"            .setTopic(\"{target}\")",
            f"            .setValueSerializationSchema(new JsonSerializationSchema<{schema_class}>())",
            "            .build()",
            "    )",
            "    .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)",
            "    .build();",
            "",
        ]

        # Apply fanout transformation before sink
        if fanout_transform:
            lines.extend([
                f"{input_stream}{fanout_transform}.sinkTo({sink_name})",
                f"    .name(\"sink-{target}\");",
                "",
            ])
        else:
            lines.extend([
                f"{input_stream}.sinkTo({sink_name})",
                f"    .name(\"sink-{target}\");",
                "",
            ])

        return '\n'.join(lines)

    def _get_emit_schema_class(self, emit: ast.EmitDecl) -> str:
        """Get the schema class name for an emit declaration."""
        if emit.schema and emit.schema.schema_name:
            return self._to_pascal_case(emit.schema.schema_name)
        # Default to target name as schema
        return self._to_pascal_case(emit.target)

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return to_pascal_case(name)

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        return to_camel_case(name)

    def get_sink_imports(self) -> Set[str]:
        """Get required imports for sink generation."""
        return {
            'org.apache.flink.connector.kafka.sink.KafkaSink',
            'org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema',
            'org.apache.flink.connector.base.DeliveryGuarantee',
            'org.apache.flink.streaming.api.functions.ProcessFunction.Context',
            'org.apache.flink.util.OutputTag',
        }
