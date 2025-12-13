"""
Tests for L5 Infrastructure Parser

Tests the YAML parser for .infra files.
"""

import pytest
import os

from backend.parser.infra import InfraParser, InfraParseError
from backend.ast.infra import (
    InfraConfig,
    SecurityProtocol,
    StartOffset,
    WriteConcern,
)


class TestInfraParserBasic:
    """Basic parsing tests."""

    def test_parse_minimal_config(self):
        """Test parsing a minimal infrastructure config."""
        yaml_content = """
version: "1.0"
environment: development

kafka:
  brokers: localhost:9092

streams:
  auth_events:
    topic: dev.auth.events
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        assert config.version == "1.0"
        assert config.environment == "development"
        assert config.kafka is not None
        assert config.kafka.brokers == "localhost:9092"
        assert "auth_events" in config.streams
        assert config.streams["auth_events"].topic == "dev.auth.events"

    def test_parse_full_kafka_config(self):
        """Test parsing full Kafka configuration."""
        yaml_content = """
kafka:
  brokers: kafka1:9092,kafka2:9092
  security_protocol: SASL_SSL
  sasl_mechanism: PLAIN
  sasl_username: user
  sasl_password: secret
  properties:
    ssl.endpoint.identification.algorithm: https

streams:
  transactions:
    topic: prod.transactions
    parallelism: 8
    consumer_group: fraud-detection
    start_offset: earliest
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        assert config.kafka.security_protocol == SecurityProtocol.SASL_SSL
        assert config.kafka.sasl_mechanism.value == "PLAIN"
        assert config.kafka.is_secure() is True

        stream = config.streams["transactions"]
        assert stream.topic == "prod.transactions"
        assert stream.parallelism == 8
        assert stream.consumer_group == "fraud-detection"
        assert stream.start_offset == StartOffset.EARLIEST

    def test_parse_mongodb_config(self):
        """Test parsing MongoDB configuration."""
        yaml_content = """
mongodb:
  uri: mongodb://localhost:27017
  auth_source: admin
  tls_enabled: false

persistence:
  transaction_store:
    database: fraud_detection
    collection: transactions
    batch_size: 100
    flush_interval: 5s
    parallelism: 4
    write_concern: majority
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        assert config.mongodb is not None
        assert config.mongodb.uri == "mongodb://localhost:27017"
        assert config.mongodb.auth_source == "admin"

        target = config.persistence["transaction_store"]
        assert target.database == "fraud_detection"
        assert target.collection == "transactions"
        assert target.batch_size == 100
        assert target.flush_interval == "5s"
        assert target.flush_interval_ms() == 5000
        assert target.write_concern == WriteConcern.MAJORITY

    def test_parse_resources_config(self):
        """Test parsing Flink resources configuration."""
        yaml_content = """
kafka:
  brokers: localhost:9092

resources:
  job_parallelism: 16
  task_slots: 4
  heap_memory: 4g
  checkpoint_interval: 60s
  checkpoint_storage: s3://checkpoints/
  checkpoint_mode: exactly_once
  state_backend: rocksdb
  restart_strategy:
    type: fixed-delay
    attempts: 5
    delay: 30s
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        assert config.resources.job_parallelism == 16
        assert config.resources.task_slots == 4
        assert config.resources.heap_memory == "4g"
        assert config.resources.heap_memory_mb() == 4096
        assert config.resources.checkpoint_interval_ms() == 60000
        assert config.resources.checkpoint_storage == "s3://checkpoints/"
        assert config.resources.state_backend == "rocksdb"
        assert config.resources.restart_strategy["attempts"] == 5


class TestInfraParserEnvVars:
    """Environment variable substitution tests."""

    def test_env_var_substitution(self):
        """Test ${VAR} substitution."""
        os.environ["TEST_KAFKA_BROKERS"] = "kafka.prod:9092"
        try:
            yaml_content = """
kafka:
  brokers: ${TEST_KAFKA_BROKERS}

streams:
  events:
    topic: events
"""
            parser = InfraParser(resolve_env_vars=True)
            config = parser.parse_string(yaml_content)

            assert config.kafka.brokers == "kafka.prod:9092"
        finally:
            del os.environ["TEST_KAFKA_BROKERS"]

    def test_env_var_with_default(self):
        """Test ${VAR:-default} substitution."""
        # Ensure the var is NOT set
        if "UNSET_TEST_VAR" in os.environ:
            del os.environ["UNSET_TEST_VAR"]

        yaml_content = """
kafka:
  brokers: ${UNSET_TEST_VAR:-localhost:9092}

streams:
  events:
    topic: events
"""
        parser = InfraParser(resolve_env_vars=True)
        config = parser.parse_string(yaml_content)

        assert config.kafka.brokers == "localhost:9092"

    def test_env_var_unresolved(self):
        """Test unresolved env var is kept as-is."""
        yaml_content = """
kafka:
  brokers: ${UNDEFINED_VAR}

streams:
  events:
    topic: events
"""
        parser = InfraParser(resolve_env_vars=True)
        config = parser.parse_string(yaml_content)

        # Unresolved vars are kept as-is for later resolution
        assert config.kafka.brokers == "${UNDEFINED_VAR}"


class TestInfraParserValidation:
    """Validation tests."""

    def test_missing_kafka_with_streams(self):
        """Test error when streams defined without Kafka config."""
        yaml_content = """
streams:
  events:
    topic: events
"""
        parser = InfraParser(resolve_env_vars=False)
        with pytest.raises(InfraParseError) as exc_info:
            parser.parse_string(yaml_content)

        assert "Kafka configuration" in str(exc_info.value)

    def test_missing_mongodb_with_persistence(self):
        """Test error when persistence defined without MongoDB config."""
        yaml_content = """
persistence:
  store:
    database: test
    collection: data
"""
        parser = InfraParser(resolve_env_vars=False)
        with pytest.raises(InfraParseError) as exc_info:
            parser.parse_string(yaml_content)

        assert "MongoDB configuration" in str(exc_info.value)

    def test_stream_missing_topic(self):
        """Test error when stream is missing topic."""
        yaml_content = """
kafka:
  brokers: localhost:9092

streams:
  events:
    parallelism: 4
"""
        parser = InfraParser(resolve_env_vars=False)
        with pytest.raises(InfraParseError) as exc_info:
            parser.parse_string(yaml_content)

        assert "topic" in str(exc_info.value)

    def test_persistence_missing_database(self):
        """Test error when persistence is missing database."""
        yaml_content = """
mongodb:
  uri: mongodb://localhost:27017

persistence:
  store:
    collection: data
"""
        parser = InfraParser(resolve_env_vars=False)
        with pytest.raises(InfraParseError) as exc_info:
            parser.parse_string(yaml_content)

        assert "database" in str(exc_info.value)


class TestInfraConfigMethods:
    """Test InfraConfig helper methods."""

    def test_get_stream(self):
        """Test get_stream method."""
        yaml_content = """
kafka:
  brokers: localhost:9092

streams:
  auth_events:
    topic: auth.events
  transactions:
    topic: transactions
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        stream = config.get_stream("auth_events")
        assert stream.topic == "auth.events"

        with pytest.raises(Exception):
            config.get_stream("nonexistent")

    def test_get_persistence(self):
        """Test get_persistence method."""
        yaml_content = """
mongodb:
  uri: mongodb://localhost:27017

persistence:
  store:
    database: test
    collection: data
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        target = config.get_persistence("store")
        assert target.database == "test"

        with pytest.raises(Exception):
            config.get_persistence("nonexistent")

    def test_source_and_sink_streams(self):
        """Test source_streams and sink_streams methods."""
        yaml_content = """
kafka:
  brokers: localhost:9092

streams:
  input_events:
    topic: input
    consumer_group: my-consumer
  output_events:
    topic: output
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)

        sources = config.source_streams()
        sinks = config.sink_streams()

        assert "input_events" in sources
        assert "output_events" in sinks
        assert sources["input_events"].is_source() is True
        assert sinks["output_events"].is_source() is False
