# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Source Generator Mixin

Generates Flink DataStream source connections from L1 receive declarations.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 Input Block Features:
- receive X from source (with optional alias)
- schema S (type-safe deserialization)
- project [fields] / project except [fields] (field projection)
- store in buffer (buffered storage for correlation)
- match from buffer on [fields] (stream matching)
─────────────────────────────────────────────────────────────────────
"""

from typing import Dict, List, Set, Tuple

from backend.ast import proc_ast as ast
from backend.generators.flow.source_projection import SourceProjectionMixin
from backend.generators.flow.source_correlation import SourceCorrelationMixin


class SourceGeneratorMixin(SourceProjectionMixin, SourceCorrelationMixin):
    """
    Mixin for generating Flink source connectors.

    Generates:
    - KafkaSource builders for Kafka topics
    - Schema deserialization setup
    - Watermark strategies
    - Field projection (map to subset of fields)
    - Store actions (buffer to ListState)
    - Match actions (join with buffered state)
    """

    # Track streams that are stored in buffers for later matching
    _stored_streams: Dict[str, Tuple[str, str]] = {}  # buffer_name -> (stream_var, schema_class)

    def generate_source_code(self, process: ast.ProcessDefinition) -> str:
        """Generate source connection code for a process."""
        # v0.5.0+: process.receives is direct list
        if not process.receives:
            return "// No input sources defined\n"

        # Reset stored streams for this process
        self._stored_streams = {}

        lines = []
        for receive in process.receives:
            source_code = self._generate_source(receive, process)
            lines.append(source_code)

        return '\n'.join(lines)

    def _generate_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate source code for a single receive declaration."""
        source_name = receive.source
        # Feature 1: Use alias if provided, otherwise use source name
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        lines = []

        # Build Kafka source
        lines.extend([
            f"// Source: {source_name}" + (f" (alias: {stream_alias})" if receive.alias else ""),
            f"KafkaSource<{schema_class}> {self._to_camel_case(source_name)}Source = KafkaSource",
            f"    .<{schema_class}>builder()",
            f"    .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)",
            f"    .setTopics(\"{source_name}\")",
            f"    .setGroupId(\"{process.name}-consumer\")",
            f"    .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))",
            f"    .setValueOnlyDeserializer(new JsonDeserializationSchema<>({schema_class}.class))",
            "    .build();",
            "",
        ])

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process, schema_class)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource(",
            f"        {self._to_camel_case(source_name)}Source,",
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
            delay_ms = self._duration_to_ms(time_decl.watermark.delay)
            return f'''WatermarkStrategy
                .<{schema_class}>forBoundedOutOfOrderness(Duration.ofMillis({delay_ms}))
                .withTimestampAssigner((event, timestamp) -> event.get{self._to_pascal_case(time_field)}().toEpochMilli())'''

        return f"WatermarkStrategy.<{schema_class}>noWatermarks()"

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
            return self.to_java_class_name(receive.schema.schema_name)
        # Default to source name as schema
        return self.to_java_class_name(receive.source)

    def _to_stream_var(self, name: str) -> str:
        """Convert source name to stream variable name."""
        return self._to_camel_case(name) + "Stream"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to PascalCase."""
        # Handle both underscores and hyphens
        name = name.replace('-', '_')
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to camelCase."""
        # Handle both underscores and hyphens
        name = name.replace('-', '_')
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _duration_to_ms(self, duration) -> int:
        """Convert Duration to milliseconds."""
        if hasattr(duration, 'to_milliseconds'):
            return duration.to_milliseconds()
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
            'org.apache.flink.streaming.api.datastream.KeyedStream',
            'org.apache.flink.formats.json.JsonDeserializationSchema',
            'java.time.Duration',
            'java.util.Map',
            'java.util.HashMap',
        }

    def get_match_imports(self) -> Set[str]:
        """Get additional imports needed for match operations."""
        return {
            'org.apache.flink.streaming.api.datastream.ConnectedStreams',
            'org.apache.flink.streaming.api.functions.co.KeyedCoProcessFunction',
        }
