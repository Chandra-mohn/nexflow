# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
L5 Infrastructure AST Models

Defines the data structures for .infra YAML configuration files.
Supports Kafka, MongoDB, and Flink resource configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class InfraValidationError(Exception):
    """Error during infrastructure configuration validation."""
    pass


class SecurityProtocol(Enum):
    """Kafka security protocols."""
    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"


class SASLMechanism(Enum):
    """Kafka SASL mechanisms."""
    PLAIN = "PLAIN"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"
    GSSAPI = "GSSAPI"


class StartOffset(Enum):
    """Kafka consumer start offset."""
    EARLIEST = "earliest"
    LATEST = "latest"
    TIMESTAMP = "timestamp"


class WriteConcern(Enum):
    """MongoDB write concern levels."""
    ACKNOWLEDGED = "acknowledged"
    MAJORITY = "majority"
    UNACKNOWLEDGED = "unacknowledged"


class CalendarFallbackStrategy(Enum):
    """Calendar API fallback strategies."""
    LAST_KNOWN = "last_known"
    FAIL_FAST = "fail_fast"
    DEFAULT_TODAY = "default_today"


@dataclass
class CalendarCacheConfig:
    """Calendar API cache configuration.

    Attributes:
        ttl: Cache time-to-live (e.g., "300s", "5m")
        refresh_on_phase: Whether to refresh cache after phase transitions
    """
    ttl: str = "300s"
    refresh_on_phase: bool = True

    def ttl_seconds(self) -> int:
        """Convert ttl to seconds."""
        ttl = self.ttl.strip().lower()
        if ttl.endswith("ms"):
            return int(ttl[:-2]) // 1000
        elif ttl.endswith("s"):
            return int(ttl[:-1])
        elif ttl.endswith("m"):
            return int(ttl[:-1]) * 60
        elif ttl.endswith("h"):
            return int(ttl[:-1]) * 3600
        else:
            return int(ttl)


@dataclass
class CalendarFallbackConfig:
    """Calendar API fallback configuration.

    Attributes:
        strategy: Fallback strategy when API is unavailable
        max_stale: Maximum staleness allowed for cached values
        alert_channel: Alert channel for fallback activation
    """
    strategy: CalendarFallbackStrategy = CalendarFallbackStrategy.LAST_KNOWN
    max_stale: str = "1h"
    alert_channel: Optional[str] = None

    def max_stale_seconds(self) -> int:
        """Convert max_stale to seconds."""
        stale = self.max_stale.strip().lower()
        if stale.endswith("s"):
            return int(stale[:-1])
        elif stale.endswith("m"):
            return int(stale[:-1]) * 60
        elif stale.endswith("h"):
            return int(stale[:-1]) * 3600
        elif stale.endswith("d"):
            return int(stale[:-1]) * 86400
        else:
            return int(stale)


@dataclass
class CalendarConfig:
    """Calendar service configuration for business date resolution.

    Business date is resolved via external Calendar Service API.
    L5 only stores API endpoint and cache configuration.

    Attributes:
        name: Calendar name (e.g., "trading_calendar", "settlement_calendar")
        service: Service discovery name (for K8s/service mesh)
        endpoint: Direct API endpoint or env var reference
        cache: Cache configuration for reducing API calls
        fallback: Fallback configuration for API failures
        timeout: API call timeout (e.g., "5s")
        retry_attempts: Number of retry attempts
        properties: Additional properties for the calendar client
    """
    name: str
    service: Optional[str] = None
    endpoint: str = "${CALENDAR_API_URL:http://calendar-api:8080}"
    cache: CalendarCacheConfig = field(default_factory=CalendarCacheConfig)
    fallback: CalendarFallbackConfig = field(default_factory=CalendarFallbackConfig)
    timeout: str = "5s"
    retry_attempts: int = 3
    properties: Dict[str, str] = field(default_factory=dict)

    def timeout_ms(self) -> int:
        """Convert timeout to milliseconds."""
        timeout = self.timeout.strip().lower()
        if timeout.endswith("ms"):
            return int(timeout[:-2])
        elif timeout.endswith("s"):
            return int(timeout[:-1]) * 1000
        elif timeout.endswith("m"):
            return int(timeout[:-1]) * 60 * 1000
        else:
            return int(timeout) * 1000

    def get_endpoint(self) -> str:
        """Get the resolved endpoint (service takes priority)."""
        if self.service:
            return f"http://{self.service}"
        return self.endpoint


@dataclass
class KafkaConfig:
    """Kafka cluster configuration.

    Attributes:
        brokers: Comma-separated broker addresses or env var reference
        security_protocol: Security protocol (PLAINTEXT, SSL, SASL_SSL, etc.)
        sasl_mechanism: SASL mechanism if using SASL
        sasl_username: SASL username or env var reference
        sasl_password: SASL password or env var reference
        ssl_truststore_location: Path to SSL truststore
        ssl_truststore_password: Truststore password or env var reference
        properties: Additional Kafka properties
    """
    brokers: str
    security_protocol: SecurityProtocol = SecurityProtocol.PLAINTEXT
    sasl_mechanism: Optional[SASLMechanism] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    ssl_truststore_location: Optional[str] = None
    ssl_truststore_password: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

    def is_secure(self) -> bool:
        """Check if security is enabled."""
        return self.security_protocol != SecurityProtocol.PLAINTEXT


@dataclass
class MongoDBConfig:
    """MongoDB cluster configuration.

    Attributes:
        uri: MongoDB connection URI or env var reference
        auth_source: Authentication database
        auth_mechanism: Authentication mechanism
        tls_enabled: Whether TLS is enabled
        tls_ca_file: Path to CA certificate file
        properties: Additional connection properties
    """
    uri: str
    auth_source: str = "admin"
    auth_mechanism: Optional[str] = None
    tls_enabled: bool = False
    tls_ca_file: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class StreamDefinition:
    """Kafka stream definition (source or sink).

    Attributes:
        name: Logical name used in L1 DSL
        topic: Physical Kafka topic name
        parallelism: Stream-specific parallelism
        consumer_group: Consumer group ID (for sources)
        start_offset: Where to start consuming (earliest/latest)
        timestamp_field: Field to use for event time (optional)
        properties: Additional Kafka properties for this stream
    """
    name: str
    topic: str
    parallelism: int = 1
    consumer_group: Optional[str] = None
    start_offset: StartOffset = StartOffset.LATEST
    timestamp_field: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

    def is_source(self) -> bool:
        """Check if this is a source stream (has consumer group)."""
        return self.consumer_group is not None


@dataclass
class PersistenceTarget:
    """MongoDB async persistence target.

    Attributes:
        name: Logical name used in L1 DSL
        database: MongoDB database name
        collection: MongoDB collection name
        batch_size: Number of records to batch before writing
        flush_interval: Time interval to flush (e.g., "5s", "1m")
        parallelism: Writer parallelism
        write_concern: MongoDB write concern
        ordered: Whether to use ordered bulk writes
        upsert_key: Field(s) for upsert operations (optional)
        properties: Additional MongoDB properties
    """
    name: str
    database: str
    collection: str
    batch_size: int = 100
    flush_interval: str = "5s"
    parallelism: int = 1
    write_concern: WriteConcern = WriteConcern.MAJORITY
    ordered: bool = False
    upsert_key: Optional[List[str]] = None
    properties: Dict[str, str] = field(default_factory=dict)

    def flush_interval_ms(self) -> int:
        """Convert flush_interval to milliseconds."""
        interval = self.flush_interval.strip().lower()
        if interval.endswith("ms"):
            return int(interval[:-2])
        elif interval.endswith("s"):
            return int(interval[:-1]) * 1000
        elif interval.endswith("m"):
            return int(interval[:-1]) * 60 * 1000
        else:
            # Assume seconds if no unit
            return int(interval) * 1000


@dataclass
class ResourceConfig:
    """Flink job resource configuration.

    Attributes:
        job_parallelism: Default parallelism for the job
        task_slots: Number of task slots per TaskManager
        heap_memory: Heap memory per TaskManager (e.g., "4g")
        managed_memory: Managed memory fraction
        checkpoint_interval: Checkpoint interval (e.g., "60s")
        checkpoint_storage: Checkpoint storage path
        checkpoint_mode: Checkpoint mode (exactly_once/at_least_once)
        state_backend: State backend type (rocksdb/hashmap)
        restart_strategy: Restart strategy configuration
    """
    job_parallelism: int = 1
    task_slots: int = 1
    heap_memory: str = "1g"
    managed_memory: float = 0.4
    checkpoint_interval: str = "60s"
    checkpoint_storage: Optional[str] = None
    checkpoint_mode: str = "exactly_once"
    state_backend: str = "rocksdb"
    restart_strategy: Dict[str, Any] = field(default_factory=lambda: {
        "type": "fixed-delay",
        "attempts": 3,
        "delay": "10s"
    })

    def checkpoint_interval_ms(self) -> int:
        """Convert checkpoint_interval to milliseconds."""
        interval = self.checkpoint_interval.strip().lower()
        if interval.endswith("ms"):
            return int(interval[:-2])
        elif interval.endswith("s"):
            return int(interval[:-1]) * 1000
        elif interval.endswith("m"):
            return int(interval[:-1]) * 60 * 1000
        else:
            return int(interval) * 1000

    def heap_memory_mb(self) -> int:
        """Convert heap_memory to megabytes."""
        mem = self.heap_memory.strip().lower()
        if mem.endswith("g"):
            return int(mem[:-1]) * 1024
        elif mem.endswith("m"):
            return int(mem[:-1])
        else:
            return int(mem)


@dataclass
class InfraConfig:
    """Complete L5 infrastructure configuration.

    Represents a parsed .infra file with all bindings and definitions.

    Attributes:
        version: Configuration version
        environment: Environment name (dev/staging/prod)
        kafka: Kafka cluster configuration
        mongodb: MongoDB cluster configuration
        calendar: Calendar service configuration (for business date)
        streams: Stream definitions by logical name
        persistence: Persistence targets by logical name
        resources: Flink job resource configuration
        source_file: Path to source .infra file
    """
    version: str = "1.0"
    environment: str = "default"
    kafka: Optional[KafkaConfig] = None
    mongodb: Optional[MongoDBConfig] = None
    calendar: Optional[CalendarConfig] = None
    streams: Dict[str, StreamDefinition] = field(default_factory=dict)
    persistence: Dict[str, PersistenceTarget] = field(default_factory=dict)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    source_file: Optional[str] = None

    def get_stream(self, name: str) -> StreamDefinition:
        """Get stream definition by logical name.

        Raises:
            InfraValidationError: If stream not found
        """
        if name not in self.streams:
            available = ", ".join(self.streams.keys()) if self.streams else "none"
            raise InfraValidationError(
                f"Stream '{name}' not defined in infrastructure config. "
                f"Available streams: {available}"
            )
        return self.streams[name]

    def get_persistence(self, name: str) -> PersistenceTarget:
        """Get persistence target by logical name.

        Raises:
            InfraValidationError: If persistence target not found
        """
        if name not in self.persistence:
            available = ", ".join(self.persistence.keys()) if self.persistence else "none"
            raise InfraValidationError(
                f"Persistence target '{name}' not defined in infrastructure config. "
                f"Available targets: {available}"
            )
        return self.persistence[name]

    def validate(self) -> List[str]:
        """Validate the infrastructure configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check that streams have required fields
        for name, stream in self.streams.items():
            if not stream.topic:
                errors.append(f"Stream '{name}' missing required 'topic' field")

        # Check that persistence targets have required fields
        for name, target in self.persistence.items():
            if not target.database:
                errors.append(f"Persistence target '{name}' missing required 'database' field")
            if not target.collection:
                errors.append(f"Persistence target '{name}' missing required 'collection' field")

        # Check that Kafka is configured if streams are defined
        if self.streams and not self.kafka:
            errors.append("Streams defined but no Kafka configuration provided")

        # Check that MongoDB is configured if persistence is defined
        if self.persistence and not self.mongodb:
            errors.append("Persistence targets defined but no MongoDB configuration provided")

        return errors

    def has_streams(self) -> bool:
        """Check if any streams are defined."""
        return bool(self.streams)

    def has_persistence(self) -> bool:
        """Check if any persistence targets are defined."""
        return bool(self.persistence)

    def has_calendar(self) -> bool:
        """Check if calendar service is configured."""
        return self.calendar is not None

    def get_calendar(self, name: str) -> CalendarConfig:
        """Get calendar configuration by name.

        Raises:
            InfraValidationError: If calendar not found or name doesn't match
        """
        if not self.calendar:
            raise InfraValidationError(
                f"Calendar '{name}' not configured. No calendar defined in infrastructure config."
            )
        if self.calendar.name != name:
            raise InfraValidationError(
                f"Calendar '{name}' not found. Available calendar: {self.calendar.name}"
            )
        return self.calendar

    def source_streams(self) -> Dict[str, StreamDefinition]:
        """Get all source streams (those with consumer groups)."""
        return {k: v for k, v in self.streams.items() if v.is_source()}

    def sink_streams(self) -> Dict[str, StreamDefinition]:
        """Get all sink streams (those without consumer groups)."""
        return {k: v for k, v in self.streams.items() if not v.is_source()}
