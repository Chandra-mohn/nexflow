# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
L5 Infrastructure YAML Parser

Parses .infra YAML files into InfraConfig AST.
Supports:
- Environment variable substitution with ${VAR} syntax
- Default values with ${VAR:-default} syntax
- Validation of required fields
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import yaml

from backend.ast.infra import (
    InfraConfig,
    KafkaConfig,
    MongoDBConfig,
    CalendarConfig,
    CalendarCacheConfig,
    CalendarFallbackConfig,
    CalendarFallbackStrategy,
    StreamDefinition,
    PersistenceTarget,
    ResourceConfig,
    SecurityProtocol,
    SASLMechanism,
    StartOffset,
    WriteConcern,
    InfraValidationError,
)


class InfraParseError(Exception):
    """Error during infrastructure file parsing."""

    def __init__(self, message: str, file: Optional[str] = None, line: Optional[int] = None):
        self.message = message
        self.file = file
        self.line = line
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = []
        if self.file:
            parts.append(f"{self.file}")
        if self.line:
            parts.append(f"line {self.line}")
        if parts:
            return f"{': '.join(parts)}: {self.message}"
        return self.message


class InfraParser:
    """Parser for L5 .infra YAML files.

    Example usage:
        parser = InfraParser()
        config = parser.parse_file("prod.infra")
        # or
        config = parser.parse_string(yaml_content)
    """

    # Pattern for environment variable substitution: ${VAR} or ${VAR:-default}
    ENV_VAR_PATTERN = re.compile(r'\$\{([^}:]+)(?::-([^}]*))?\}')

    def __init__(self, resolve_env_vars: bool = True):
        """Initialize the parser.

        Args:
            resolve_env_vars: Whether to resolve ${VAR} patterns from environment
        """
        self.resolve_env_vars = resolve_env_vars

    def parse_file(self, file_path: Union[str, Path]) -> InfraConfig:
        """Parse an infrastructure configuration file.

        Args:
            file_path: Path to .infra file

        Returns:
            InfraConfig AST

        Raises:
            InfraParseError: If parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise InfraParseError(f"File not found: {path}")

        try:
            content = path.read_text()
            config = self.parse_string(content, source_file=str(path))
            return config
        except yaml.YAMLError as e:
            raise InfraParseError(f"YAML parse error: {e}", file=str(path))

    def parse_string(self, content: str, source_file: Optional[str] = None) -> InfraConfig:
        """Parse infrastructure configuration from a string.

        Args:
            content: YAML content
            source_file: Optional source file path for error messages

        Returns:
            InfraConfig AST

        Raises:
            InfraParseError: If parsing fails
        """
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise InfraParseError(f"YAML parse error: {e}", file=source_file)

        if not data:
            raise InfraParseError("Empty configuration file", file=source_file)

        if not isinstance(data, dict):
            raise InfraParseError("Configuration must be a YAML mapping", file=source_file)

        # Resolve environment variables if enabled
        if self.resolve_env_vars:
            data = self._resolve_env_vars(data)

        return self._build_config(data, source_file)

    def _resolve_env_vars(self, data: Any) -> Any:
        """Recursively resolve ${VAR} patterns in the data.

        Supports:
        - ${VAR}: Substitute with environment variable value
        - ${VAR:-default}: Use default if VAR is not set
        """
        if isinstance(data, str):
            return self._substitute_string(data)
        elif isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        else:
            return data

    def _substitute_string(self, value: str) -> str:
        """Substitute environment variables in a string."""
        def replace_match(match):
            var_name = match.group(1)
            default_value = match.group(2)
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            elif default_value is not None:
                return default_value
            else:
                # Keep the original pattern if not resolved
                return match.group(0)

        return self.ENV_VAR_PATTERN.sub(replace_match, value)

    def _build_config(self, data: Dict[str, Any], source_file: Optional[str]) -> InfraConfig:
        """Build InfraConfig from parsed YAML data."""
        config = InfraConfig(source_file=source_file)

        # Version and environment
        config.version = str(data.get("version", "1.0"))
        config.environment = data.get("environment", "default")

        # Kafka configuration
        if "kafka" in data:
            config.kafka = self._parse_kafka_config(data["kafka"])

        # MongoDB configuration
        if "mongodb" in data:
            config.mongodb = self._parse_mongodb_config(data["mongodb"])

        # Calendar configuration
        if "calendar" in data:
            config.calendar = self._parse_calendar_config(data["calendar"])

        # Stream definitions
        if "streams" in data:
            for name, stream_data in data["streams"].items():
                config.streams[name] = self._parse_stream_definition(name, stream_data)

        # Persistence targets
        if "persistence" in data:
            for name, persist_data in data["persistence"].items():
                config.persistence[name] = self._parse_persistence_target(name, persist_data)

        # Resource configuration
        if "resources" in data:
            config.resources = self._parse_resource_config(data["resources"])

        # Validate the configuration
        errors = config.validate()
        if errors:
            raise InfraParseError(
                f"Configuration validation failed: {'; '.join(errors)}",
                file=source_file
            )

        return config

    def _parse_kafka_config(self, data: Dict[str, Any]) -> KafkaConfig:
        """Parse Kafka cluster configuration."""
        brokers = data.get("brokers")
        if not brokers:
            raise InfraParseError("Kafka configuration requires 'brokers' field")

        # Parse security protocol
        security_str = data.get("security_protocol", "PLAINTEXT").upper()
        try:
            security_protocol = SecurityProtocol(security_str)
        except ValueError:
            raise InfraParseError(f"Invalid security_protocol: {security_str}")

        # Parse SASL mechanism
        sasl_mechanism = None
        sasl_str = data.get("sasl_mechanism")
        if sasl_str:
            try:
                sasl_mechanism = SASLMechanism(sasl_str.upper())
            except ValueError:
                raise InfraParseError(f"Invalid sasl_mechanism: {sasl_str}")

        return KafkaConfig(
            brokers=brokers,
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            sasl_username=data.get("sasl_username"),
            sasl_password=data.get("sasl_password"),
            ssl_truststore_location=data.get("ssl_truststore_location"),
            ssl_truststore_password=data.get("ssl_truststore_password"),
            properties=data.get("properties", {}),
        )

    def _parse_mongodb_config(self, data: Dict[str, Any]) -> MongoDBConfig:
        """Parse MongoDB cluster configuration."""
        uri = data.get("uri")
        if not uri:
            raise InfraParseError("MongoDB configuration requires 'uri' field")

        return MongoDBConfig(
            uri=uri,
            auth_source=data.get("auth_source", "admin"),
            auth_mechanism=data.get("auth_mechanism"),
            tls_enabled=data.get("tls_enabled", False),
            tls_ca_file=data.get("tls_ca_file"),
            properties=data.get("properties", {}),
        )

    def _parse_calendar_config(self, data: Dict[str, Any]) -> CalendarConfig:
        """Parse calendar service configuration.

        Example YAML:
            calendar:
              name: trading_calendar
              service: calendar-service      # K8s service name (optional)
              endpoint: ${CALENDAR_API_URL:http://calendar-api:8080}
              cache:
                ttl: 300s
                refresh_on_phase: true
              fallback:
                strategy: last_known
                max_stale: 1h
                alert_channel: ops-critical
              timeout: 5s
              retry_attempts: 3
        """
        name = data.get("name")
        if not name:
            raise InfraParseError("Calendar configuration requires 'name' field")

        # Parse cache config
        cache_data = data.get("cache", {})
        cache_config = CalendarCacheConfig(
            ttl=cache_data.get("ttl", "300s"),
            refresh_on_phase=cache_data.get("refresh_on_phase", True),
        )

        # Parse fallback config
        fallback_data = data.get("fallback", {})
        fallback_strategy_str = fallback_data.get("strategy", "last_known").lower()
        try:
            fallback_strategy = CalendarFallbackStrategy(fallback_strategy_str)
        except ValueError:
            valid_strategies = [s.value for s in CalendarFallbackStrategy]
            raise InfraParseError(
                f"Invalid fallback strategy: {fallback_strategy_str}. "
                f"Valid values: {', '.join(valid_strategies)}"
            )

        fallback_config = CalendarFallbackConfig(
            strategy=fallback_strategy,
            max_stale=fallback_data.get("max_stale", "1h"),
            alert_channel=fallback_data.get("alert_channel"),
        )

        return CalendarConfig(
            name=name,
            service=data.get("service"),
            endpoint=data.get("endpoint", "${CALENDAR_API_URL:http://calendar-api:8080}"),
            cache=cache_config,
            fallback=fallback_config,
            timeout=data.get("timeout", "5s"),
            retry_attempts=data.get("retry_attempts", 3),
            properties=data.get("properties", {}),
        )

    def _parse_stream_definition(self, name: str, data: Dict[str, Any]) -> StreamDefinition:
        """Parse a stream definition."""
        topic = data.get("topic")
        if not topic:
            raise InfraParseError(f"Stream '{name}' requires 'topic' field")

        # Parse start offset
        offset_str = data.get("start_offset", "latest").lower()
        try:
            start_offset = StartOffset(offset_str)
        except ValueError:
            raise InfraParseError(f"Invalid start_offset for stream '{name}': {offset_str}")

        return StreamDefinition(
            name=name,
            topic=topic,
            parallelism=data.get("parallelism", 1),
            consumer_group=data.get("consumer_group"),
            start_offset=start_offset,
            timestamp_field=data.get("timestamp_field"),
            properties=data.get("properties", {}),
        )

    def _parse_persistence_target(self, name: str, data: Dict[str, Any]) -> PersistenceTarget:
        """Parse a persistence target."""
        database = data.get("database")
        if not database:
            raise InfraParseError(f"Persistence target '{name}' requires 'database' field")

        collection = data.get("collection")
        if not collection:
            raise InfraParseError(f"Persistence target '{name}' requires 'collection' field")

        # Parse write concern
        wc_str = data.get("write_concern", "majority").lower()
        try:
            write_concern = WriteConcern(wc_str)
        except ValueError:
            raise InfraParseError(f"Invalid write_concern for '{name}': {wc_str}")

        # Parse upsert_key (can be string or list)
        upsert_key = data.get("upsert_key")
        if isinstance(upsert_key, str):
            upsert_key = [upsert_key]

        return PersistenceTarget(
            name=name,
            database=database,
            collection=collection,
            batch_size=data.get("batch_size", 100),
            flush_interval=data.get("flush_interval", "5s"),
            parallelism=data.get("parallelism", 1),
            write_concern=write_concern,
            ordered=data.get("ordered", False),
            upsert_key=upsert_key,
            properties=data.get("properties", {}),
        )

    def _parse_resource_config(self, data: Dict[str, Any]) -> ResourceConfig:
        """Parse Flink job resource configuration."""
        restart_strategy = data.get("restart_strategy", {
            "type": "fixed-delay",
            "attempts": 3,
            "delay": "10s"
        })

        return ResourceConfig(
            job_parallelism=data.get("job_parallelism", 1),
            task_slots=data.get("task_slots", 1),
            heap_memory=data.get("heap_memory", "1g"),
            managed_memory=data.get("managed_memory", 0.4),
            checkpoint_interval=data.get("checkpoint_interval", "60s"),
            checkpoint_storage=data.get("checkpoint_storage"),
            checkpoint_mode=data.get("checkpoint_mode", "exactly_once"),
            state_backend=data.get("state_backend", "rocksdb"),
            restart_strategy=restart_strategy,
        )


def parse_infra_file(file_path: Union[str, Path], resolve_env_vars: bool = True) -> InfraConfig:
    """Convenience function to parse an infrastructure file.

    Args:
        file_path: Path to .infra file
        resolve_env_vars: Whether to resolve ${VAR} patterns

    Returns:
        InfraConfig AST
    """
    parser = InfraParser(resolve_env_vars=resolve_env_vars)
    return parser.parse_file(file_path)
