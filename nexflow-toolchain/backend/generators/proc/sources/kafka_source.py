# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Kafka Source Mixin

Generates Flink KafkaSource connectors for Kafka topics.
"""

from typing import List, Set

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case, duration_to_ms


class KafkaSourceMixin:
    """Mixin for generating Kafka source connectors."""

    def _generate_kafka_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate Kafka source code for a receive declaration."""
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get serialization configuration (process override > schema > team config > default)
        serialization = self._get_effective_serialization(receive, process)

        lines = []

        # Build Kafka source with format-specific deserializer
        deserializer_code = self._generate_deserializer(schema_class, serialization)
        lines.extend([
            f"// Source: {source_name}" + (f" (alias: {stream_alias})" if receive.alias else "") + f" [format: {serialization.format.value}]",
            f"KafkaSource<{schema_class}> {to_camel_case(source_name)}Source = KafkaSource",
            f"    .<{schema_class}>builder()",
            f"    .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)",
            f"    .setTopics(\"{source_name}\")",
            f"    .setGroupId(\"{process.name}-consumer\")",
            f"    .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))",
            f"    .setValueOnlyDeserializer({deserializer_code})",
            "    .build();",
            "",
        ])

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process, schema_class)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource(",
            f"        {to_camel_case(source_name)}Source,",
            f"        {watermark_strategy},",
            f"        \"{source_name}\"",
            f"    );",
            "",
        ])

        # Feature 2: Field projection
        if receive.project:
            projection_code, projected_var = self._generate_projection(
                receive, stream_var, schema_class, stream_alias
            )
            lines.append(projection_code)
            stream_var = projected_var

        # Feature 3a: Store action (buffer for later matching)
        if receive.store_action:
            store_code = self._generate_store_action(
                receive.store_action, stream_var, schema_class, stream_alias
            )
            lines.append(store_code)
            # Track this stored stream for match operations
            self._stored_streams[receive.store_action.state_name] = (stream_var, schema_class)

        # Feature 3b: Match action (join with buffered state)
        if receive.match_action:
            match_code, matched_var = self._generate_match_action(
                receive.match_action, stream_var, schema_class, stream_alias
            )
            lines.append(match_code)
            stream_var = matched_var

        return '\n'.join(lines)

    def _generate_watermark_strategy(self, process: ast.ProcessDefinition, schema_class: str) -> str:
        """Generate watermark strategy based on time configuration."""
        if not process.execution or not process.execution.time:
            return f"WatermarkStrategy.<{schema_class}>noWatermarks()"

        time_decl = process.execution.time
        time_field = time_decl.time_field.parts[-1]  # Get last part of field path

        if time_decl.watermark:
            delay_ms = duration_to_ms(time_decl.watermark.delay)
            return f'''WatermarkStrategy
                .<{schema_class}>forBoundedOutOfOrderness(Duration.ofMillis({delay_ms}))
                .withTimestampAssigner((event, timestamp) -> event.get{to_pascal_case(time_field)}().toEpochMilli())'''

        return f"WatermarkStrategy.<{schema_class}>noWatermarks()"

    def _generate_key_selector(self, schema_class: str, fields: List[str]) -> str:
        """Generate KeySelector for partitioning."""
        if len(fields) == 1:
            field = fields[0]
            return f"event -> event.get{to_pascal_case(field)}()"
        else:
            # Composite key - generate Tuple
            getters = ', '.join(f"event.get{to_pascal_case(f)}()" for f in fields)
            return f"event -> Tuple{len(fields)}.of({getters})"

    def get_kafka_imports(self) -> Set[str]:
        """Get required imports for Kafka source generation."""
        return {
            'org.apache.flink.api.common.eventtime.WatermarkStrategy',
            'org.apache.flink.connector.kafka.source.KafkaSource',
            'org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer',
            'org.apache.kafka.clients.consumer.OffsetResetStrategy',
            'org.apache.flink.streaming.api.datastream.DataStream',
            'org.apache.flink.streaming.api.datastream.KeyedStream',
            'java.time.Duration',
        }
