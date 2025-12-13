"""
Tests for L5 Binding Resolver

Tests the binding resolver that connects logical names to physical infrastructure.
"""

import pytest

from backend.parser.infra import InfraParser
from backend.generators.infra import BindingResolver, BindingError


class TestBindingResolverBasic:
    """Basic binding resolution tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.yaml_content = """
version: "1.0"
environment: production

kafka:
  brokers: kafka.prod:9092
  security_protocol: SASL_SSL
  sasl_mechanism: PLAIN
  sasl_username: user
  sasl_password: secret

mongodb:
  uri: mongodb://mongo.prod:27017
  auth_source: admin

streams:
  auth_events:
    topic: prod.auth.events.v3
    parallelism: 8
    consumer_group: fraud-detection
    start_offset: earliest

  processed_transactions:
    topic: prod.transactions.processed
    parallelism: 4

persistence:
  transaction_store:
    database: fraud_detection
    collection: transactions
    batch_size: 100
    flush_interval: 5s
    parallelism: 4
    write_concern: majority

resources:
  job_parallelism: 16
  checkpoint_interval: 60s
"""
        parser = InfraParser(resolve_env_vars=False)
        self.config = parser.parse_string(self.yaml_content)
        self.resolver = BindingResolver(self.config)

    def test_resolve_source(self):
        """Test resolving a source stream."""
        source = self.resolver.resolve_source("auth_events")

        assert source.topic == "prod.auth.events.v3"
        assert source.brokers == "kafka.prod:9092"
        assert source.consumer_group == "fraud-detection"
        assert source.parallelism == 8
        assert source.start_offset == "earliest"
        assert source.is_secure is True
        assert source.security_protocol == "SASL_SSL"

    def test_resolve_sink(self):
        """Test resolving a sink stream."""
        sink = self.resolver.resolve_sink("processed_transactions")

        assert sink.topic == "prod.transactions.processed"
        assert sink.brokers == "kafka.prod:9092"
        assert sink.parallelism == 4
        assert sink.is_secure is True

    def test_resolve_persistence(self):
        """Test resolving a persistence target."""
        persistence = self.resolver.resolve_persistence("transaction_store")

        assert persistence.uri == "mongodb://mongo.prod:27017"
        assert persistence.database == "fraud_detection"
        assert persistence.collection == "transactions"
        assert persistence.batch_size == 100
        assert persistence.flush_interval_ms == 5000
        assert persistence.parallelism == 4
        assert persistence.write_concern == "majority"

    def test_resolve_persistence_with_override(self):
        """Test resolving persistence with DSL overrides."""
        persistence = self.resolver.resolve_persistence(
            "transaction_store",
            batch_size_override=200,
            flush_interval_override="10s"
        )

        assert persistence.batch_size == 200
        assert persistence.flush_interval_ms == 10000

    def test_resolve_resources(self):
        """Test resolving Flink resources."""
        resources = self.resolver.resolve_resources()

        assert resources.job_parallelism == 16
        assert resources.checkpoint_interval_ms == 60000


class TestBindingResolverNoConfig:
    """Test binding resolver without configuration (development mode)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = BindingResolver(None)

    def test_has_config(self):
        """Test has_config property."""
        assert self.resolver.has_config is False

    def test_environment(self):
        """Test environment property."""
        assert self.resolver.environment == "default"

    def test_resolve_source_fallback(self):
        """Test resolving source with fallback to stub."""
        source = self.resolver.resolve_source("unknown_stream")

        # Falls back to using logical name as topic
        assert source.topic == "unknown_stream"
        assert source.brokers == "localhost:9092"
        assert source.consumer_group == "nexflow-unknown_stream"
        assert source.parallelism == 1
        assert source.is_secure is False

    def test_resolve_sink_fallback(self):
        """Test resolving sink with fallback to stub."""
        sink = self.resolver.resolve_sink("output_stream")

        assert sink.topic == "output_stream"
        assert sink.brokers == "localhost:9092"

    def test_resolve_persistence_fallback(self):
        """Test resolving persistence with fallback to stub."""
        persistence = self.resolver.resolve_persistence("my_store")

        assert persistence.uri == "mongodb://localhost:27017"
        assert persistence.database == "nexflow"
        assert persistence.collection == "my_store"
        assert persistence.batch_size == 100


class TestBindingResolverValidation:
    """Test binding validation."""

    def setup_method(self):
        """Set up test fixtures."""
        yaml_content = """
kafka:
  brokers: localhost:9092

mongodb:
  uri: mongodb://localhost:27017

streams:
  input_events:
    topic: input
  output_events:
    topic: output

persistence:
  store:
    database: test
    collection: data
"""
        parser = InfraParser(resolve_env_vars=False)
        self.config = parser.parse_string(yaml_content)
        self.resolver = BindingResolver(self.config)

    def test_validate_valid_bindings(self):
        """Test validation with all valid bindings."""
        errors = self.resolver.validate_bindings(
            stream_refs=["input_events", "output_events"],
            persistence_refs=["store"]
        )
        assert len(errors) == 0

    def test_validate_missing_stream(self):
        """Test validation with missing stream reference."""
        errors = self.resolver.validate_bindings(
            stream_refs=["input_events", "nonexistent_stream"],
            persistence_refs=[]
        )
        assert len(errors) == 1
        assert "nonexistent_stream" in errors[0]

    def test_validate_missing_persistence(self):
        """Test validation with missing persistence reference."""
        errors = self.resolver.validate_bindings(
            stream_refs=[],
            persistence_refs=["store", "missing_store"]
        )
        assert len(errors) == 1
        assert "missing_store" in errors[0]

    def test_list_streams(self):
        """Test listing available streams."""
        streams = self.resolver.list_streams()
        assert "input_events" in streams
        assert "output_events" in streams

    def test_list_persistence_targets(self):
        """Test listing available persistence targets."""
        targets = self.resolver.list_persistence_targets()
        assert "store" in targets


class TestBindingResolverConsumerGroup:
    """Test consumer group handling."""

    def test_explicit_consumer_group(self):
        """Test that explicit consumer group is used."""
        yaml_content = """
kafka:
  brokers: localhost:9092

streams:
  events:
    topic: events
    consumer_group: my-custom-group
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)
        resolver = BindingResolver(config)

        source = resolver.resolve_source("events")
        assert source.consumer_group == "my-custom-group"

    def test_default_consumer_group(self):
        """Test that default consumer group is generated."""
        yaml_content = """
kafka:
  brokers: localhost:9092

streams:
  events:
    topic: events
"""
        parser = InfraParser(resolve_env_vars=False)
        config = parser.parse_string(yaml_content)
        resolver = BindingResolver(config)

        source = resolver.resolve_source("events")
        assert source.consumer_group == "nexflow-events"
