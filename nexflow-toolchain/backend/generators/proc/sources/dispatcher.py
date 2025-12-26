# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Source Generator Dispatcher

Main mixin that composes all source sub-mixins and provides the unified
source generation interface for routing to appropriate connector handlers.
"""

from typing import Dict, List, Set, Tuple

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case

from backend.generators.proc.source_projection import SourceProjectionMixin
from backend.generators.proc.source_correlation import SourceCorrelationMixin
from .kafka_source import KafkaSourceMixin
from .alternative_sources import AlternativeSourcesMixin
from .file_sources import FileSourcesMixin
from .serialization import SerializationMixin


class SourceGeneratorMixin(
    SourceProjectionMixin,
    SourceCorrelationMixin,
    KafkaSourceMixin,
    AlternativeSourcesMixin,
    FileSourcesMixin,
    SerializationMixin
):
    """Unified mixin for generating Flink source connectors.

    Composes all source sub-mixins:
    - SourceProjectionMixin: Field projection (project [fields])
    - SourceCorrelationMixin: Store/match correlation patterns
    - KafkaSourceMixin: Kafka source connectors
    - AlternativeSourcesMixin: Redis, StateStore, MongoDB, Scheduler
    - FileSourcesMixin: Parquet, CSV file sources
    - SerializationMixin: Format detection and deserializer generation
    """

    # Track streams that are stored in buffers for later matching
    _stored_streams: Dict[str, Tuple[str, str]] = {}  # buffer_name -> (stream_var, schema_class)

    def generate_source_code(self, process: ast.ProcessDefinition) -> str:
        """Generate source connection code for a process."""
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
        """Generate source code for a single receive declaration.

        Routes to connector-specific generators based on connector_type.
        """
        # Route to appropriate connector generator
        connector_type = receive.connector_type if hasattr(receive, 'connector_type') else ast.ConnectorType.KAFKA

        if connector_type == ast.ConnectorType.REDIS:
            return self._generate_redis_source(receive, process)
        elif connector_type == ast.ConnectorType.STATE_STORE:
            return self._generate_state_store_source(receive, process)
        elif connector_type == ast.ConnectorType.MONGODB:
            return self._generate_mongodb_source(receive, process)
        elif connector_type == ast.ConnectorType.SCHEDULER:
            return self._generate_scheduler_source(receive, process)
        elif connector_type == ast.ConnectorType.PARQUET:
            return self._generate_parquet_source(receive, process)
        elif connector_type == ast.ConnectorType.CSV:
            return self._generate_csv_source(receive, process)
        else:
            # Default: Kafka source
            return self._generate_kafka_source(receive, process)

    def _get_schema_class(self, receive: ast.ReceiveDecl) -> str:
        """Get the schema class name for a receive declaration."""
        if receive.schema and receive.schema.schema_name:
            return self.to_java_class_name(receive.schema.schema_name)
        # Default to source name as schema
        return self.to_java_class_name(receive.source)

    def _to_stream_var(self, name: str) -> str:
        """Convert source name to stream variable name."""
        return to_camel_case(name) + "Stream"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to PascalCase."""
        return to_pascal_case(name)

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to camelCase."""
        return to_camel_case(name)

    def _apply_source_options(self, receive: ast.ReceiveDecl, stream_var: str,
                              schema_class: str, stream_alias: str) -> List[str]:
        """Apply common source options (projection, store, match) to a stream."""
        lines = []

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

        return lines

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

    def get_all_source_imports(self, process: ast.ProcessDefinition) -> Set[str]:
        """Get all imports needed based on sources used in process."""
        imports = self.get_source_imports()

        if not process.receives:
            return imports

        for receive in process.receives:
            connector_type = receive.connector_type if hasattr(receive, 'connector_type') else ast.ConnectorType.KAFKA

            if connector_type == ast.ConnectorType.REDIS:
                imports.update(self.get_redis_imports())
            elif connector_type == ast.ConnectorType.STATE_STORE:
                imports.update(self.get_state_store_imports())
            elif connector_type == ast.ConnectorType.MONGODB:
                imports.update(self.get_mongodb_imports())
            elif connector_type == ast.ConnectorType.SCHEDULER:
                imports.update(self.get_scheduler_imports())
            elif connector_type == ast.ConnectorType.PARQUET:
                imports.update(self.get_parquet_imports())
            elif connector_type == ast.ConnectorType.CSV:
                imports.update(self.get_csv_imports())
            else:
                imports.update(self.get_kafka_imports())

            # Check for match operations
            if receive.match_action:
                imports.update(self.get_match_imports())

            # Add serialization imports
            serialization = self._get_effective_serialization(receive, process)
            imports.update(self.get_serialization_imports(serialization))

        return imports
