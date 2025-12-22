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
from backend.generators.common.java_utils import to_pascal_case, to_camel_case, duration_to_ms
from backend.generators.proc.source_projection import SourceProjectionMixin
from backend.generators.proc.source_correlation import SourceCorrelationMixin


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
        else:
            # Default: Kafka source
            return self._generate_kafka_source(receive, process)

    def _generate_kafka_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate Kafka source code for a receive declaration."""
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
        return to_pascal_case(name)

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case or kebab-case to camelCase."""
        return to_camel_case(name)

    def _duration_to_ms(self, duration) -> int:
        """Convert Duration to milliseconds."""
        return duration_to_ms(duration)

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

    # =========================================================================
    # Alternative Source Generators
    # =========================================================================

    def _generate_redis_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate Redis source code for a receive declaration.

        Generates Flink source for Redis Pub/Sub, Streams, or scan-based sources.
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get Redis config or use defaults
        redis_config = receive.redis_config
        pattern = redis_config.pattern if redis_config else source_name
        mode = redis_config.mode if redis_config else "subscribe"
        batch_size = redis_config.batch_size if redis_config else 100

        lines = [
            f"// Redis Source: {source_name} (pattern: {pattern}, mode: {mode})",
        ]

        if mode == "subscribe":
            # Redis Pub/Sub mode
            lines.extend([
                f"RedisSource<{schema_class}> {self._to_camel_case(source_name)}Source = RedisSource",
                f"    .<{schema_class}>builder()",
                f"    .setRedisHost(REDIS_HOST)",
                f"    .setRedisPort(REDIS_PORT)",
                f"    .setChannelPattern(\"{pattern}\")",
                f"    .setDeserializer(new JsonRedisDeserializer<>({schema_class}.class))",
                f"    .build();",
                "",
            ])
        elif mode == "stream":
            # Redis Streams mode (XREAD)
            lines.extend([
                f"RedisStreamSource<{schema_class}> {self._to_camel_case(source_name)}Source = RedisStreamSource",
                f"    .<{schema_class}>builder()",
                f"    .setRedisHost(REDIS_HOST)",
                f"    .setRedisPort(REDIS_PORT)",
                f"    .setStreamKey(\"{pattern}\")",
                f"    .setConsumerGroup(\"{process.name}-consumer\")",
                f"    .setBatchSize({batch_size})",
                f"    .setDeserializer(new JsonRedisDeserializer<>({schema_class}.class))",
                f"    .build();",
                "",
            ])
        else:
            # Redis SCAN mode for batch-like ingestion
            lines.extend([
                f"RedisScanSource<{schema_class}> {self._to_camel_case(source_name)}Source = RedisScanSource",
                f"    .<{schema_class}>builder()",
                f"    .setRedisHost(REDIS_HOST)",
                f"    .setRedisPort(REDIS_PORT)",
                f"    .setKeyPattern(\"{pattern}\")",
                f"    .setBatchSize({batch_size})",
                f"    .setDeserializer(new JsonRedisDeserializer<>({schema_class}.class))",
                f"    .build();",
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

        # Apply projections and actions
        lines.extend(self._apply_source_options(receive, stream_var, schema_class, stream_alias))

        return '\n'.join(lines)

    def _generate_state_store_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate StateStore source code for a receive declaration.

        Generates Flink source that reads from an external state store (e.g., RocksDB, Redis state).
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get state store config or use defaults
        ss_config = receive.state_store_config
        store_name = ss_config.store_name if ss_config else source_name
        key_type = ss_config.key_type if ss_config and ss_config.key_type else "String"
        value_type = ss_config.value_type if ss_config and ss_config.value_type else schema_class

        lines = [
            f"// StateStore Source: {source_name} (store: {store_name})",
            f"StateStoreSource<{key_type}, {value_type}> {self._to_camel_case(source_name)}Source = StateStoreSource",
            f"    .<{key_type}, {value_type}>builder()",
            f"    .setStoreName(\"{store_name}\")",
            f"    .setKeyType({key_type}.class)",
            f"    .setValueType({value_type}.class)",
            f"    .setStateBackend(stateBackend)",
            f"    .build();",
            "",
        ]

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

        # Apply projections and actions
        lines.extend(self._apply_source_options(receive, stream_var, schema_class, stream_alias))

        return '\n'.join(lines)

    def _generate_mongodb_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate MongoDB source code for a receive declaration.

        Generates Flink MongoDB connector for change stream or batch reads.
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        lines = [
            f"// MongoDB Source: {source_name}",
            f"MongoSource<{schema_class}> {self._to_camel_case(source_name)}Source = MongoSource",
            f"    .<{schema_class}>builder()",
            f"    .setUri(MONGODB_URI)",
            f"    .setDatabase(MONGODB_DATABASE)",
            f"    .setCollection(\"{source_name}\")",
            f"    .setDeserializationSchema(new MongoDeserializationSchema<>({schema_class}.class))",
            f"    .build();",
            "",
        ]

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

        # Apply projections and actions
        lines.extend(self._apply_source_options(receive, stream_var, schema_class, stream_alias))

        return '\n'.join(lines)

    def _generate_scheduler_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate Scheduler/Cron source code for a receive declaration.

        Generates a source that emits events on a cron schedule.
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get scheduler config or use defaults
        sched_config = receive.scheduler_config
        cron_expr = sched_config.cron_expression if sched_config else "0 * * * *"
        timezone = sched_config.timezone if sched_config else "UTC"

        lines = [
            f"// Scheduler Source: {source_name} (cron: {cron_expr})",
            f"SchedulerSource<{schema_class}> {self._to_camel_case(source_name)}Source = SchedulerSource",
            f"    .<{schema_class}>builder()",
            f"    .setCronExpression(\"{cron_expr}\")",
            f"    .setTimezone(\"{timezone}\")",
            f"    .setEventGenerator(() -> new {schema_class}())",
            f"    .build();",
            "",
        ]

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

        return '\n'.join(lines)

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

    def get_redis_imports(self) -> Set[str]:
        """Get imports needed for Redis sources."""
        return {
            'io.nexflow.connectors.redis.RedisSource',
            'io.nexflow.connectors.redis.RedisStreamSource',
            'io.nexflow.connectors.redis.RedisScanSource',
            'io.nexflow.connectors.redis.JsonRedisDeserializer',
        }

    def get_state_store_imports(self) -> Set[str]:
        """Get imports needed for StateStore sources."""
        return {
            'io.nexflow.state.StateStoreSource',
        }

    def get_mongodb_imports(self) -> Set[str]:
        """Get imports needed for MongoDB sources."""
        return {
            'org.apache.flink.connector.mongodb.source.MongoSource',
            'io.nexflow.connectors.mongodb.MongoDeserializationSchema',
        }

    def get_scheduler_imports(self) -> Set[str]:
        """Get imports needed for Scheduler sources."""
        return {
            'io.nexflow.connectors.scheduler.SchedulerSource',
        }
