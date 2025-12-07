"""
Source Generator Mixin

Generates Flink DataStream source connections from L1 receive declarations.
"""

from typing import List, Set

from backend.ast import proc_ast as ast


class SourceGeneratorMixin:
    """
    Mixin for generating Flink source connectors.

    Generates:
    - KafkaSource builders for Kafka topics
    - Schema deserialization setup
    - Watermark strategies
    """

    def generate_source_code(self, process: ast.ProcessDefinition) -> str:
        """Generate source connection code for a process."""
        if not process.input or not process.input.receives:
            return "// No input sources defined\n"

        lines = []
        for receive in process.input.receives:
            lines.append(self._generate_source(receive, process))

        return '\n'.join(lines)

    def _generate_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate source code for a single receive declaration."""
        source_name = receive.source
        stream_var = self._to_stream_var(source_name)
        schema_class = self._get_schema_class(receive)

        # Build Kafka source
        lines = [
            f"// Source: {source_name}",
            f"KafkaSource<{schema_class}> {source_name}Source = KafkaSource",
            f"    .<{schema_class}>builder()",
            f"    .setBootstrapServers(kafkaBootstrapServers)",
            f"    .setTopics(\"{source_name}\")",
            f"    .setGroupId(\"{process.name}-consumer\")",
            f"    .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))",
            f"    .setDeserializer(new {schema_class}Deserializer())",
            "    .build();",
            "",
        ]

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource({source_name}Source, {watermark_strategy}, \"{source_name}\")",
        ])

        # Add partitioning if specified
        if process.execution and process.execution.partition_by:
            partition_fields = process.execution.partition_by
            key_selector = self._generate_key_selector(schema_class, partition_fields)
            lines.append(f"    .keyBy({key_selector})")

        lines.append("    ;")
        lines.append("")

        return '\n'.join(lines)

    def _generate_watermark_strategy(self, process: ast.ProcessDefinition) -> str:
        """Generate watermark strategy based on time configuration."""
        if not process.execution or not process.execution.time:
            return "WatermarkStrategy.noWatermarks()"

        time_decl = process.execution.time
        time_field = time_decl.time_field.parts[-1]  # Get last part of field path

        if time_decl.watermark:
            delay_ms = time_decl.watermark.delay.to_milliseconds() if hasattr(time_decl.watermark.delay, 'to_milliseconds') else self._duration_to_ms(time_decl.watermark.delay)
            return f'''WatermarkStrategy
            .<{self._current_schema_class}>forBoundedOutOfOrderness(Duration.ofMillis({delay_ms}))
            .withTimestampAssigner((event, timestamp) -> event.get{self._to_pascal_case(time_field)}().toEpochMilli())'''

        return "WatermarkStrategy.noWatermarks()"

    def _generate_key_selector(self, schema_class: str, fields: List[str]) -> str:
        """Generate KeySelector for partitioning."""
        if len(fields) == 1:
            field = fields[0]
            return f"event -> event.get{self._to_pascal_case(field)}()"
        else:
            # Composite key - generate Tuple
            getters = ', '.join(f"event.get{self._to_pascal_case(f)}()" for f in fields)
            return f"event -> Tuple{len(fields)}.of({getters})"

    def _get_schema_class(self, receive: ast.ReceiveDecl) -> str:
        """Get the schema class name for a receive declaration."""
        if receive.schema and receive.schema.schema_name:
            return self._to_pascal_case(receive.schema.schema_name)
        # Default to source name as schema
        return self._to_pascal_case(receive.source)

    def _to_stream_var(self, name: str) -> str:
        """Convert source name to stream variable name."""
        return self._to_camel_case(name) + "Stream"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _duration_to_ms(self, duration: ast.Duration) -> int:
        """Convert Duration to milliseconds."""
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return duration.value * multipliers.get(duration.unit, 1)

    def get_source_imports(self) -> Set[str]:
        """Get required imports for source generation."""
        return {
            'org.apache.flink.api.common.eventtime.WatermarkStrategy',
            'org.apache.flink.connector.kafka.source.KafkaSource',
            'org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer',
            'org.apache.kafka.clients.consumer.OffsetResetStrategy',
            'org.apache.flink.streaming.api.datastream.DataStream',
            'java.time.Duration',
        }
