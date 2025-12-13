"""
L5 Binding Resolver

Resolves logical names (from L1 DSL) to physical infrastructure configurations (from L5 .infra).
This is the bridge between the process DSL and actual infrastructure.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from backend.ast.infra import (
    InfraConfig,
    StreamDefinition,
    PersistenceTarget,
    KafkaConfig,
    MongoDBConfig,
    ResourceConfig,
    InfraValidationError,
)


class BindingError(Exception):
    """Error during binding resolution."""

    def __init__(self, message: str, logical_name: Optional[str] = None):
        self.message = message
        self.logical_name = logical_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.logical_name:
            return f"Binding error for '{self.logical_name}': {self.message}"
        return f"Binding error: {self.message}"


@dataclass
class ResolvedKafkaSource:
    """Resolved Kafka source configuration for code generation."""
    topic: str
    brokers: str
    consumer_group: str
    parallelism: int
    start_offset: str  # "earliest" or "latest"
    is_secure: bool
    security_protocol: str
    sasl_mechanism: Optional[str]
    sasl_username: Optional[str]
    sasl_password: Optional[str]
    properties: Dict[str, str]


@dataclass
class ResolvedKafkaSink:
    """Resolved Kafka sink configuration for code generation."""
    topic: str
    brokers: str
    parallelism: int
    is_secure: bool
    security_protocol: str
    sasl_mechanism: Optional[str]
    sasl_username: Optional[str]
    sasl_password: Optional[str]
    properties: Dict[str, str]


@dataclass
class ResolvedMongoDBPersistence:
    """Resolved MongoDB persistence configuration for code generation."""
    uri: str
    database: str
    collection: str
    batch_size: int
    flush_interval_ms: int
    parallelism: int
    write_concern: str
    ordered: bool
    upsert_key: Optional[list]
    auth_source: str
    tls_enabled: bool
    properties: Dict[str, str]


@dataclass
class ResolvedResources:
    """Resolved Flink job resources for code generation."""
    job_parallelism: int
    task_slots: int
    heap_memory_mb: int
    managed_memory: float
    checkpoint_interval_ms: int
    checkpoint_storage: Optional[str]
    checkpoint_mode: str
    state_backend: str
    restart_attempts: int
    restart_delay_ms: int


class BindingResolver:
    """Resolves logical names to physical infrastructure configurations.

    The resolver takes an InfraConfig (parsed from .infra YAML) and provides
    methods to resolve logical names (used in L1 DSL) to physical configurations
    ready for code generation.

    Example usage:
        infra = InfraParser().parse_file("prod.infra")
        resolver = BindingResolver(infra)

        # Resolve a source stream
        source = resolver.resolve_source("auth_events")
        # -> ResolvedKafkaSource with topic, brokers, etc.

        # Resolve a sink stream
        sink = resolver.resolve_sink("processed_events")
        # -> ResolvedKafkaSink with topic, brokers, etc.

        # Resolve a persistence target
        persistence = resolver.resolve_persistence("transaction_store")
        # -> ResolvedMongoDBPersistence with uri, database, collection, etc.
    """

    def __init__(self, infra_config: Optional[InfraConfig] = None):
        """Initialize the resolver.

        Args:
            infra_config: Optional L5 infrastructure configuration.
                         If None, uses default/stub configurations.
        """
        self._config = infra_config
        self._default_kafka = self._create_default_kafka()
        self._default_mongodb = self._create_default_mongodb()
        self._default_resources = self._create_default_resources()

    def _create_default_kafka(self) -> KafkaConfig:
        """Create default Kafka configuration for development."""
        from backend.ast.infra import SecurityProtocol
        return KafkaConfig(
            brokers="localhost:9092",
            security_protocol=SecurityProtocol.PLAINTEXT,
        )

    def _create_default_mongodb(self) -> MongoDBConfig:
        """Create default MongoDB configuration for development."""
        return MongoDBConfig(uri="mongodb://localhost:27017")

    def _create_default_resources(self) -> ResourceConfig:
        """Create default resource configuration for development."""
        return ResourceConfig(
            job_parallelism=1,
            task_slots=1,
            heap_memory="1g",
            checkpoint_interval="60s",
        )

    @property
    def has_config(self) -> bool:
        """Check if infrastructure configuration is available."""
        return self._config is not None

    @property
    def environment(self) -> str:
        """Get the environment name."""
        return self._config.environment if self._config else "default"

    def resolve_source(self, logical_name: str) -> ResolvedKafkaSource:
        """Resolve a source stream (Kafka consumer) by logical name.

        Args:
            logical_name: The logical name used in L1 'receive from X'

        Returns:
            ResolvedKafkaSource with all physical configuration

        Raises:
            BindingError: If the stream is not defined or invalid
        """
        stream = self._get_stream(logical_name)
        kafka = self._get_kafka_config()

        if not stream.consumer_group:
            # Default consumer group based on logical name
            consumer_group = f"nexflow-{logical_name}"
        else:
            consumer_group = stream.consumer_group

        return ResolvedKafkaSource(
            topic=stream.topic,
            brokers=kafka.brokers,
            consumer_group=consumer_group,
            parallelism=stream.parallelism,
            start_offset=stream.start_offset.value,
            is_secure=kafka.is_secure(),
            security_protocol=kafka.security_protocol.value,
            sasl_mechanism=kafka.sasl_mechanism.value if kafka.sasl_mechanism else None,
            sasl_username=kafka.sasl_username,
            sasl_password=kafka.sasl_password,
            properties={**kafka.properties, **stream.properties},
        )

    def resolve_sink(self, logical_name: str) -> ResolvedKafkaSink:
        """Resolve a sink stream (Kafka producer) by logical name.

        Args:
            logical_name: The logical name used in L1 'emit to X'

        Returns:
            ResolvedKafkaSink with all physical configuration

        Raises:
            BindingError: If the stream is not defined or invalid
        """
        stream = self._get_stream(logical_name)
        kafka = self._get_kafka_config()

        return ResolvedKafkaSink(
            topic=stream.topic,
            brokers=kafka.brokers,
            parallelism=stream.parallelism,
            is_secure=kafka.is_secure(),
            security_protocol=kafka.security_protocol.value,
            sasl_mechanism=kafka.sasl_mechanism.value if kafka.sasl_mechanism else None,
            sasl_username=kafka.sasl_username,
            sasl_password=kafka.sasl_password,
            properties={**kafka.properties, **stream.properties},
        )

    def resolve_persistence(
        self,
        logical_name: str,
        batch_size_override: Optional[int] = None,
        flush_interval_override: Optional[str] = None,
    ) -> ResolvedMongoDBPersistence:
        """Resolve a MongoDB persistence target by logical name.

        Args:
            logical_name: The logical name used in L1 'persist to X'
            batch_size_override: Optional batch size override from DSL
            flush_interval_override: Optional flush interval override from DSL

        Returns:
            ResolvedMongoDBPersistence with all physical configuration

        Raises:
            BindingError: If the persistence target is not defined or invalid
        """
        target = self._get_persistence(logical_name)
        mongodb = self._get_mongodb_config()

        # Apply overrides from DSL
        batch_size = batch_size_override if batch_size_override else target.batch_size
        flush_interval_ms = (
            self._parse_duration_ms(flush_interval_override)
            if flush_interval_override
            else target.flush_interval_ms()
        )

        return ResolvedMongoDBPersistence(
            uri=mongodb.uri,
            database=target.database,
            collection=target.collection,
            batch_size=batch_size,
            flush_interval_ms=flush_interval_ms,
            parallelism=target.parallelism,
            write_concern=target.write_concern.value,
            ordered=target.ordered,
            upsert_key=target.upsert_key,
            auth_source=mongodb.auth_source,
            tls_enabled=mongodb.tls_enabled,
            properties={**mongodb.properties, **target.properties},
        )

    def resolve_resources(self) -> ResolvedResources:
        """Resolve Flink job resource configuration.

        Returns:
            ResolvedResources with all physical configuration
        """
        resources = self._get_resources()

        # Parse restart strategy
        restart_strategy = resources.restart_strategy
        restart_attempts = restart_strategy.get("attempts", 3)
        restart_delay = restart_strategy.get("delay", "10s")
        restart_delay_ms = self._parse_duration_ms(restart_delay)

        return ResolvedResources(
            job_parallelism=resources.job_parallelism,
            task_slots=resources.task_slots,
            heap_memory_mb=resources.heap_memory_mb(),
            managed_memory=resources.managed_memory,
            checkpoint_interval_ms=resources.checkpoint_interval_ms(),
            checkpoint_storage=resources.checkpoint_storage,
            checkpoint_mode=resources.checkpoint_mode,
            state_backend=resources.state_backend,
            restart_attempts=restart_attempts,
            restart_delay_ms=restart_delay_ms,
        )

    def _get_stream(self, logical_name: str) -> StreamDefinition:
        """Get stream definition, with fallback to stub."""
        if self._config and logical_name in self._config.streams:
            return self._config.streams[logical_name]

        # Create stub stream for development
        from backend.ast.infra import StartOffset
        return StreamDefinition(
            name=logical_name,
            topic=logical_name,  # Use logical name as topic
            parallelism=1,
            start_offset=StartOffset.LATEST,
        )

    def _get_persistence(self, logical_name: str) -> PersistenceTarget:
        """Get persistence target, with fallback to stub."""
        if self._config and logical_name in self._config.persistence:
            return self._config.persistence[logical_name]

        # Create stub persistence for development
        from backend.ast.infra import WriteConcern
        return PersistenceTarget(
            name=logical_name,
            database="nexflow",
            collection=logical_name,
            batch_size=100,
            flush_interval="5s",
            write_concern=WriteConcern.MAJORITY,
        )

    def _get_kafka_config(self) -> KafkaConfig:
        """Get Kafka config with fallback to default."""
        if self._config and self._config.kafka:
            return self._config.kafka
        return self._default_kafka

    def _get_mongodb_config(self) -> MongoDBConfig:
        """Get MongoDB config with fallback to default."""
        if self._config and self._config.mongodb:
            return self._config.mongodb
        return self._default_mongodb

    def _get_resources(self) -> ResourceConfig:
        """Get resources config with fallback to default."""
        if self._config:
            return self._config.resources
        return self._default_resources

    def _parse_duration_ms(self, duration: str) -> int:
        """Parse duration string to milliseconds."""
        duration = duration.strip().lower()
        if duration.endswith("ms"):
            return int(duration[:-2])
        elif duration.endswith("s"):
            return int(duration[:-1]) * 1000
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60 * 1000
        else:
            return int(duration) * 1000

    def list_streams(self) -> list:
        """List all defined stream names."""
        if self._config:
            return list(self._config.streams.keys())
        return []

    def list_persistence_targets(self) -> list:
        """List all defined persistence target names."""
        if self._config:
            return list(self._config.persistence.keys())
        return []

    def validate_bindings(self, stream_refs: list, persistence_refs: list) -> list:
        """Validate that all referenced bindings exist.

        Args:
            stream_refs: List of stream names referenced in L1
            persistence_refs: List of persistence names referenced in L1

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self._config:
            # No config = development mode, allow all references
            return errors

        for ref in stream_refs:
            if ref not in self._config.streams:
                errors.append(f"Stream '{ref}' not defined in infrastructure config")

        for ref in persistence_refs:
            if ref not in self._config.persistence:
                errors.append(f"Persistence target '{ref}' not defined in infrastructure config")

        return errors
