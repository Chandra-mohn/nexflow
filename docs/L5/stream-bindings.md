# L5: Stream Bindings

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Stream bindings map logical stream names (used in L1 `receive` and `emit` statements) to physical message systems. Nexflow supports multiple streaming platforms with consistent configuration patterns.

---

## Supported Platforms

| Platform | Use Case | Key Features |
|----------|----------|--------------|
| **Apache Kafka** | Primary streaming | High throughput, exactly-once, ordering |
| **Amazon Kinesis** | AWS-native | Managed service, auto-scaling |
| **Apache Pulsar** | Multi-tenant | Geo-replication, tiered storage |

---

## Kafka Bindings

### Basic Configuration

```yaml
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: broker1:9092,broker2:9092,broker3:9092
```

### Complete Configuration

```yaml
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}

    # Topic configuration
    partitions: 128
    replication: 3
    retention_ms: 604800000  # 7 days

    # Consumer configuration (for receive)
    consumer:
      group_id: auth-enrichment-consumer
      auto_offset_reset: earliest
      max_poll_records: 500
      isolation_level: read_committed

    # Producer configuration (for emit)
    producer:
      acks: all
      retries: 3
      batch_size: 16384
      linger_ms: 5
      compression: lz4
      idempotence: true

    # Security
    properties:
      security.protocol: SASL_SSL
      sasl.mechanism: SCRAM-SHA-512
      sasl.jaas.config: ${KAFKA_JAAS_CONFIG}
      ssl.truststore.location: /etc/kafka/truststore.jks
      ssl.truststore.password: ${TRUSTSTORE_PASSWORD}

    # Schema registry (if using Avro/Protobuf)
    schema_registry:
      url: ${SCHEMA_REGISTRY_URL}
      basic_auth: ${SCHEMA_REGISTRY_AUTH}
```

### Kafka Property Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `topic` | string | required | Kafka topic name |
| `brokers` | string | required | Bootstrap servers (comma-separated) |
| `partitions` | integer | - | Number of partitions (topic creation) |
| `replication` | integer | - | Replication factor (topic creation) |
| `consumer.group_id` | string | auto | Consumer group identifier |
| `consumer.auto_offset_reset` | string | earliest | `earliest`, `latest`, `none` |
| `consumer.max_poll_records` | integer | 500 | Max records per poll |
| `consumer.isolation_level` | string | read_uncommitted | `read_committed` for exactly-once |
| `producer.acks` | string | all | `0`, `1`, `all` |
| `producer.retries` | integer | 3 | Number of retries |
| `producer.idempotence` | boolean | true | Enable idempotent producer |
| `producer.compression` | string | none | `none`, `gzip`, `snappy`, `lz4`, `zstd` |

---

## Kinesis Bindings

### Basic Configuration

```yaml
streams:
  fraud_alerts:
    type: kinesis
    stream: prod-fraud-alerts
    region: us-east-1
```

### Complete Configuration

```yaml
streams:
  fraud_alerts:
    type: kinesis
    stream: prod-fraud-alerts
    region: us-east-1

    # Stream configuration
    shard_count: 16
    retention_hours: 168  # 7 days
    encryption: true
    kms_key_id: ${KMS_KEY_ID}

    # Consumer configuration
    consumer:
      type: enhanced_fan_out  # or standard
      consumer_name: fraud-processor
      starting_position: LATEST

    # Producer configuration
    producer:
      aggregation: true
      max_connections: 24
      record_max_buffered_time: 100ms
      collection_max_count: 500

    # AWS credentials
    credentials:
      type: assume_role  # or default, profile, static
      role_arn: arn:aws:iam::123456789:role/kinesis-consumer
      session_name: fraud-processor
```

### Kinesis Property Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `stream` | string | required | Kinesis stream name |
| `region` | string | required | AWS region |
| `shard_count` | integer | - | Number of shards |
| `retention_hours` | integer | 24 | Data retention (24-8760) |
| `consumer.type` | string | standard | `standard`, `enhanced_fan_out` |
| `consumer.starting_position` | string | LATEST | `TRIM_HORIZON`, `LATEST`, `AT_TIMESTAMP` |
| `producer.aggregation` | boolean | true | Enable KPL aggregation |

---

## Pulsar Bindings

### Basic Configuration

```yaml
streams:
  settlement_events:
    type: pulsar
    topic: persistent://credit-card/settlement/events
    service_url: pulsar://pulsar-cluster:6650
```

### Complete Configuration

```yaml
streams:
  settlement_events:
    type: pulsar
    topic: persistent://credit-card/settlement/events
    service_url: pulsar://pulsar-cluster:6650
    admin_url: http://pulsar-admin:8080

    # Topic configuration
    partitions: 32
    retention_time: 7d
    retention_size: 100GB
    compaction: true

    # Consumer configuration
    consumer:
      subscription_name: settlement-processor
      subscription_type: Failover  # Exclusive, Shared, Key_Shared, Failover
      receiver_queue_size: 1000
      acknowledgment_timeout: 30s
      negative_ack_redelivery_delay: 1m
      dead_letter_policy:
        max_redeliver_count: 3
        dead_letter_topic: persistent://credit-card/settlement/dlq

    # Producer configuration
    producer:
      batching_enabled: true
      batching_max_messages: 1000
      batching_max_publish_delay: 10ms
      compression: LZ4
      send_timeout: 30s

    # Authentication
    auth:
      type: token  # or tls, oauth2
      token: ${PULSAR_TOKEN}

    # TLS
    tls:
      enabled: true
      trust_cert_path: /etc/pulsar/ca.pem
      allow_insecure: false
```

### Pulsar Property Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `topic` | string | required | Full topic path |
| `service_url` | string | required | Pulsar broker URL |
| `partitions` | integer | - | Topic partitions |
| `consumer.subscription_type` | string | Shared | `Exclusive`, `Shared`, `Key_Shared`, `Failover` |
| `producer.compression` | string | NONE | `NONE`, `LZ4`, `ZLIB`, `ZSTD`, `SNAPPY` |

---

## Stream Direction

L6 compiler infers stream direction from L1 usage:

| L1 Statement | Direction | Stream Role |
|--------------|-----------|-------------|
| `receive events from X` | Source | Consumer/Reader |
| `emit to X` | Sink | Producer/Writer |
| Used in both | Bidirectional | Both configured |

```yaml
# Explicit direction (optional override)
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    direction: source  # source, sink, bidirectional
```

---

## Serialization

### Format Configuration

```yaml
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3

    serialization:
      key_format: string
      value_format: avro  # json, avro, protobuf

      # Avro-specific
      avro:
        schema_registry_url: ${SCHEMA_REGISTRY_URL}
        subject_name_strategy: TopicNameStrategy
        auto_register: false

      # Protobuf-specific
      protobuf:
        message_class: com.example.AuthEvent
        include_schema: true
```

### Supported Formats

| Format | Use Case | Schema Evolution |
|--------|----------|------------------|
| `json` | Development, flexibility | Manual |
| `avro` | Production, large messages | Schema Registry |
| `protobuf` | High performance, cross-language | Schema Registry |
| `string` | Simple keys | N/A |
| `bytes` | Raw data | N/A |

---

## Error Handling

### Deserialization Errors

```yaml
streams:
  auth_events:
    type: kafka

    error_handling:
      deserialization:
        action: skip  # skip, fail, dlq
        dlq_topic: prod.auth.deserialize-errors
        log_level: warn
        max_errors_per_minute: 100
```

### Connectivity Errors

```yaml
streams:
  auth_events:
    type: kafka

    error_handling:
      connectivity:
        retry_attempts: 5
        retry_backoff: exponential
        initial_backoff: 1s
        max_backoff: 60s
        fail_after: 10m
```

---

## Performance Tuning

### High-Throughput Configuration

```yaml
streams:
  high_volume_events:
    type: kafka
    topic: prod.transactions.v3

    # Consumer tuning
    consumer:
      max_poll_records: 1000
      fetch_min_bytes: 1048576  # 1MB
      fetch_max_wait: 500ms

    # Producer tuning
    producer:
      batch_size: 65536  # 64KB
      linger_ms: 20
      buffer_memory: 67108864  # 64MB
      compression: lz4
```

### Low-Latency Configuration

```yaml
streams:
  real_time_alerts:
    type: kafka
    topic: prod.alerts.v3

    consumer:
      max_poll_records: 100
      fetch_min_bytes: 1
      fetch_max_wait: 100ms

    producer:
      batch_size: 1024
      linger_ms: 0
      acks: 1  # Trade durability for latency
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [lookup-bindings.md](./lookup-bindings.md) - Lookup data stores
- [state-checkpoints.md](./state-checkpoints.md) - State and checkpoints
