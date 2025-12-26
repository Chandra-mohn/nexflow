# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Alternative Sources Mixin

Generates Flink connectors for non-Kafka sources:
- Redis (Pub/Sub, Streams, Scan)
- StateStore
- MongoDB
- Scheduler (Cron-based)
"""

from typing import List, Set

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_camel_case


class AlternativeSourcesMixin:
    """Mixin for generating alternative (non-Kafka) source connectors."""

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
                f"RedisSource<{schema_class}> {to_camel_case(source_name)}Source = RedisSource",
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
                f"RedisStreamSource<{schema_class}> {to_camel_case(source_name)}Source = RedisStreamSource",
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
                f"RedisScanSource<{schema_class}> {to_camel_case(source_name)}Source = RedisScanSource",
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
            f"        {to_camel_case(source_name)}Source,",
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
            f"StateStoreSource<{key_type}, {value_type}> {to_camel_case(source_name)}Source = StateStoreSource",
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
            f"        {to_camel_case(source_name)}Source,",
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
            f"MongoSource<{schema_class}> {to_camel_case(source_name)}Source = MongoSource",
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
            f"        {to_camel_case(source_name)}Source,",
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
            f"SchedulerSource<{schema_class}> {to_camel_case(source_name)}Source = SchedulerSource",
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
            f"        {to_camel_case(source_name)}Source,",
            f"        {watermark_strategy},",
            f"        \"{source_name}\"",
            f"    );",
            "",
        ])

        return '\n'.join(lines)

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
