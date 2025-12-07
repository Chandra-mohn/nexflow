# L5: Infrastructure Binding Specification

> **Layer**: L5 - Deployment Configuration
> **Status**: Specification
> **Version**: 1.0.0
> **Last Updated**: 2025-11-27

---

## 1. Overview

### 1.1 Purpose

L5 is the **Infrastructure Binding** layer — maps logical names to physical infrastructure:

- **Stream Bindings**: Kafka topics, Kinesis streams, Pulsar topics
- **Lookup Bindings**: MongoDB, Redis, PostgreSQL, Cassandra
- **State Backends**: RocksDB, HashMap, external state stores
- **Checkpoint Storage**: S3, HDFS, GCS, local filesystem
- **Resource Configuration**: Parallelism, memory, CPU allocation
- **Environment Profiles**: Development, staging, production configurations

### 1.2 Key Principle

> **L1-L4 are infrastructure-agnostic.**
>
> L1 uses logical names (`auth_events`, `customers`).
> L5 maps to physical resources (`kafka://broker:9092/prod.auth.events.v3`).
>
> Same L1 process can deploy to dev, staging, prod with different L5 bindings.

### 1.3 File Extension

| Extension | Layer | Owner |
|-----------|-------|-------|
| `.infra` | L5 Infrastructure Binding | Platform/DevOps |

### 1.4 Railroad-Towns Metaphor

In the railroad-towns architecture:
- L5 is the **track configuration** — defines where the railroad connects to physical infrastructure
- Determines track gauge (resource sizing), station connections (data sources/sinks), and signal systems (monitoring)

---

## 2. Binding Architecture

### 2.1 Logical to Physical Mapping

```
┌─────────────────────────────────────────────────────────────────────┐
│                     L5 Binding Resolution                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  L1 Process (Logical)              L5 Binding (Physical)            │
│  ─────────────────────             ──────────────────────           │
│                                                                      │
│  receive from auth_events    →     kafka://broker:9092/prod.auth.v3 │
│  enrich using customers      →     mongodb://cluster/cc.customers   │
│  emit to enriched_auths      →     kafka://broker:9092/prod.enrich  │
│  checkpoint auth_cp          →     s3://bucket/checkpoints/auth/    │
│                                                                      │
│  parallelism hint 128        →     resources.parallelism: 128       │
│                                    resources.task_memory: 4gb       │
│                                    resources.task_cpu: 2            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Binding Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Streams** | Event sources and sinks | Kafka, Kinesis, Pulsar |
| **Lookups** | Reference data stores | MongoDB, Redis, PostgreSQL |
| **State** | Stateful computation backend | RocksDB, HashMap |
| **Checkpoints** | Fault tolerance storage | S3, HDFS, GCS |
| **Dead Letters** | Error handling destinations | Kafka, S3, MongoDB |
| **Completions** | Transaction confirmation events | Kafka (Flink Sink Callback) |
| **Resources** | Compute allocation | Parallelism, memory, CPU |
| **Secrets** | Credential references | Vault, AWS Secrets Manager |

---

## 3. Syntax Specification

### 3.1 File Format

L5 uses **YAML format** for tooling compatibility with existing DevOps ecosystems (Kubernetes, Terraform, Ansible).

```yaml
# production.infra
version: "1.0"
environment: production
description: "Production infrastructure bindings for credit card processing"

# Binding sections follow...
```

### 3.2 Core Structure

```yaml
version: "1.0"
environment: <env_name>
description: "<description>"

# Optional: inherit from another binding file
extends: base.infra

# Binding sections
streams:
  <logical_name>: <stream_binding>

lookups:
  <logical_name>: <lookup_binding>

checkpoints:
  <logical_name>: <checkpoint_binding>

state_backends:
  <backend_name>: <state_config>

dead_letters:
  <logical_name>: <dlq_binding>

completions:
  <logical_name>: <completion_binding>

resources:
  <process_name>: <resource_config>

secrets:
  <secret_name>: <secret_ref>

monitoring:
  <config>: <value>
```

---

## 4. Binding Types

### 4.1 Stream Bindings

Stream bindings map logical stream names to physical message systems.

```yaml
streams:
  # Kafka binding
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}
    partitions: 128
    replication: 3
    properties:
      security.protocol: SASL_SSL
      sasl.mechanism: SCRAM-SHA-512
      sasl.jaas.config: ${KAFKA_JAAS_CONFIG}

  # Kinesis binding
  fraud_alerts:
    type: kinesis
    stream: prod-fraud-alerts
    region: us-east-1
    shard_count: 16

  # Pulsar binding
  settlement_events:
    type: pulsar
    topic: persistent://credit-card/settlement/events
    service_url: pulsar://pulsar-cluster:6650
```

#### Stream Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | `kafka`, `kinesis`, `pulsar` |
| `topic/stream` | string | Yes | Physical topic/stream name |
| `brokers/service_url` | string | Yes | Connection endpoint |
| `partitions` | integer | No | Number of partitions (Kafka) |
| `replication` | integer | No | Replication factor |
| `shard_count` | integer | No | Number of shards (Kinesis) |
| `properties` | map | No | Provider-specific properties |

### 4.2 Lookup Bindings

Lookup bindings map enrichment sources to physical data stores.

```yaml
lookups:
  # MongoDB binding
  customers:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers
    read_preference: secondaryPreferred
    max_pool_size: 100
    cache:
      enabled: true
      ttl: 5m
      max_size: 100000

  # Redis binding
  currency_rates:
    type: redis
    uri: ${REDIS_URI}
    database: 0
    key_pattern: "fx:rate:{currency}"
    cluster_mode: true

  # PostgreSQL binding
  merchant_categories:
    type: postgresql
    jdbc_url: ${POSTGRES_URL}
    schema: reference
    table: merchant_categories
    pool_size: 20
```

#### Lookup Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | `mongodb`, `redis`, `postgresql`, `cassandra` |
| `uri/jdbc_url` | string | Yes | Connection string |
| `database` | string | Yes* | Database/keyspace name |
| `collection/table` | string | Yes* | Collection/table name |
| `read_preference` | string | No | Read routing strategy |
| `cache` | object | No | Caching configuration |
| `pool_size` | integer | No | Connection pool size |

### 4.3 Checkpoint Bindings

Checkpoint bindings configure fault tolerance storage.

```yaml
checkpoints:
  # S3 binding
  auth_checkpoints:
    type: s3
    bucket: company-checkpoints
    prefix: auth/enrichment/
    region: us-east-1
    interval: 60s
    min_pause: 30s

  # HDFS binding
  batch_checkpoints:
    type: hdfs
    path: hdfs://namenode:9000/checkpoints/batch/
    replication: 3

  # GCS binding
  fraud_checkpoints:
    type: gcs
    bucket: fraud-processing-checkpoints
    prefix: detection/
```

#### Checkpoint Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | `s3`, `hdfs`, `gcs`, `filesystem` |
| `bucket/path` | string | Yes | Storage location |
| `prefix` | string | No | Key/path prefix |
| `interval` | duration | No | Checkpoint interval |
| `min_pause` | duration | No | Minimum pause between checkpoints |
| `replication` | integer | No | Storage replication factor |

### 4.4 State Backend Bindings

State backends configure how stateful operations store their state.

```yaml
state_backends:
  # RocksDB (recommended for production)
  default:
    type: rocksdb
    incremental: true
    local_directories:
      - /mnt/ssd1/state
      - /mnt/ssd2/state
    options:
      block_cache_size: 256mb
      write_buffer_size: 64mb

  # HashMapStateBackend (for development)
  dev_state:
    type: hashmap
    async_snapshots: true
```

### 4.5 Dead Letter Queue Bindings

DLQ bindings configure where failed records are sent.

```yaml
dead_letters:
  # Kafka DLQ
  auth_dlq:
    type: kafka
    topic: prod.auth.dlq
    brokers: ${KAFKA_BROKERS}
    include_metadata: true

  # S3 DLQ (for batch analysis)
  batch_dlq:
    type: s3
    bucket: failed-records
    prefix: auth/
    format: json
    partition_by: date
```

### 4.6 Completion Event Bindings

Completion event bindings configure the transaction confirmation infrastructure for the **Flink Sink Callback** pattern.

```yaml
completions:
  # Success completion topic
  transaction_completions:
    type: kafka
    topic: prod.transaction.completions.v1
    brokers: ${KAFKA_BROKERS}
    partitions: 64
    replication: 3

    # Partition by correlation_id for efficient consumer lookup
    producer:
      key_field: correlation_id
      acks: all
      idempotence: true
      compression: lz4

    # Short retention - API gateways consume quickly
    retention_ms: 86400000  # 24 hours

    # Serialization
    serialization:
      value_format: avro
      schema_registry_url: ${SCHEMA_REGISTRY_URL}

  # Failure completion topic (optional separate topic)
  transaction_failures:
    type: kafka
    topic: prod.transaction.failures.v1
    brokers: ${KAFKA_BROKERS}
    partitions: 16

    producer:
      key_field: correlation_id
      acks: all

    # Longer retention for failure analysis
    retention_ms: 604800000  # 7 days
```

#### Completion Binding Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Currently only `kafka` supported |
| `topic` | string | Yes | Physical Kafka topic name |
| `brokers` | string | Yes | Kafka bootstrap servers |
| `partitions` | integer | No | Recommended: match input topic partitions |
| `producer.key_field` | string | Yes | Field for partition key (typically `correlation_id`) |
| `producer.acks` | string | No | Default: `all` for durability |
| `producer.idempotence` | boolean | No | Default: `true` for exactly-once |
| `retention_ms` | integer | No | Topic retention (default: 24 hours) |

#### Sink Callback Configuration

Configure how the Flink sink emits completion events:

```yaml
completions:
  transaction_completions:
    type: kafka
    topic: prod.transaction.completions.v1

    # Sink callback configuration
    callback:
      # When to emit completion (default: after_commit)
      trigger: after_commit    # after_commit | after_flush | after_ack

      # Timeout for sink confirmation before failure
      timeout: 30s

      # Retry configuration for completion emission
      retry:
        attempts: 3
        backoff: exponential
        initial_delay: 100ms
        max_delay: 5s

      # Include sink response data in completion
      include_sink_response: true
```

#### MongoDB Sink with Completion Example

```yaml
# Output sink (where data is written)
streams:
  accounts_collection:
    type: mongodb_sink
    uri: ${MONGO_URI}
    database: credit_card
    collection: accounts

    # Enable completion callback
    completion:
      enabled: true
      target: transaction_completions

      # Extract MongoDB _id as target_id
      id_field: _id

      # Capture write concern acknowledgment
      write_concern: majority

# Completion topic binding
completions:
  transaction_completions:
    type: kafka
    topic: prod.transaction.completions.v1
    brokers: ${KAFKA_BROKERS}
```

### 4.7 Resource Bindings

Resource bindings configure compute allocation per process.

```yaml
resources:
  # Per-process resource configuration
  authorization_enrichment:
    parallelism: 128
    max_parallelism: 256
    task_memory: 4gb
    task_cpu: 2
    managed_memory: 1gb
    network_memory: 128mb

  hourly_transaction_summary:
    parallelism: 64
    task_memory: 8gb
    task_cpu: 4
    managed_memory: 4gb

  # Global defaults
  _defaults:
    parallelism: 16
    task_memory: 2gb
    task_cpu: 1
```

#### Resource Properties Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `parallelism` | integer | 1 | Number of parallel instances |
| `max_parallelism` | integer | parallelism | Maximum for rescaling |
| `task_memory` | size | 1gb | Memory per task slot |
| `task_cpu` | number | 1 | CPU cores per task slot |
| `managed_memory` | size | 0 | Flink managed memory |
| `network_memory` | size | 64mb | Network buffer memory |

---

## 5. Environment Management

### 5.1 Environment Profiles

L5 supports environment-specific configurations through separate files or inheritance.

```
infra/
├── base.infra           # Shared configuration
├── development.infra    # Dev overrides
├── staging.infra        # Staging overrides
└── production.infra     # Production configuration
```

### 5.2 Inheritance Pattern

```yaml
# base.infra - Shared configuration
version: "1.0"
environment: base

streams:
  auth_events:
    type: kafka
    partitions: 128
    properties:
      security.protocol: SASL_SSL

state_backends:
  default:
    type: rocksdb
    incremental: true
```

```yaml
# development.infra
version: "1.0"
environment: development
extends: base.infra

streams:
  auth_events:
    # Override topic and brokers, inherit other properties
    topic: dev.auth.events.v3
    brokers: localhost:9092
    partitions: 4  # Override partition count

resources:
  _defaults:
    parallelism: 2
    task_memory: 1gb
```

```yaml
# production.infra
version: "1.0"
environment: production
extends: base.infra

streams:
  auth_events:
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}
    replication: 3

resources:
  authorization_enrichment:
    parallelism: 128
    task_memory: 4gb
```

### 5.3 Environment Variables

L5 supports environment variable substitution using `${VAR_NAME}` syntax.

```yaml
streams:
  auth_events:
    brokers: ${KAFKA_BROKERS}
    properties:
      sasl.jaas.config: ${KAFKA_JAAS_CONFIG}

lookups:
  customers:
    uri: ${MONGO_URI}
```

**Resolution Order**:
1. Shell environment variables
2. `.env` file in project root
3. Default values (if specified): `${VAR_NAME:-default_value}`

---

## 6. Secret Management

### 6.1 Secret References

L5 does NOT store secrets directly. It references external secret stores.

```yaml
secrets:
  # HashiCorp Vault
  kafka_credentials:
    provider: vault
    path: secret/data/kafka/production
    keys:
      - username
      - password

  # AWS Secrets Manager
  mongo_connection:
    provider: aws_secrets_manager
    secret_id: prod/mongodb/connection
    region: us-east-1

  # Kubernetes Secret
  redis_password:
    provider: kubernetes
    namespace: credit-card
    secret_name: redis-credentials
    key: password
```

### 6.2 Secret Usage

Reference secrets in bindings using `secret://` prefix:

```yaml
lookups:
  customers:
    type: mongodb
    uri: secret://mongo_connection/uri

streams:
  auth_events:
    properties:
      sasl.username: secret://kafka_credentials/username
      sasl.password: secret://kafka_credentials/password
```

---

## 7. Monitoring Configuration

### 7.1 Metrics Binding

```yaml
monitoring:
  metrics:
    type: prometheus
    port: 9249
    path: /metrics
    labels:
      environment: production
      team: credit-card

  tracing:
    type: jaeger
    endpoint: http://jaeger-collector:14268/api/traces
    sampling_rate: 0.1

  logging:
    level: INFO
    format: json
    outputs:
      - type: stdout
      - type: elasticsearch
        endpoint: ${ES_ENDPOINT}
        index_pattern: nexflow-logs-%{+YYYY.MM.dd}
```

### 7.2 Alerting Configuration

```yaml
monitoring:
  alerts:
    - name: high_latency
      condition: "processing_latency_p99 > 1000ms"
      severity: warning
      channels:
        - slack://credit-card-alerts
        - pagerduty://high-priority

    - name: checkpoint_failure
      condition: "checkpoint_failures > 3"
      severity: critical
      channels:
        - pagerduty://critical
```

---

## 8. Deployment Integration

### 8.1 Kubernetes Deployment

L5 can generate Kubernetes manifests for deployment.

```yaml
deployment:
  type: kubernetes
  namespace: credit-card-processing

  service_account: nexflow-runner

  pod_template:
    annotations:
      prometheus.io/scrape: "true"
      prometheus.io/port: "9249"
    node_selector:
      workload-type: streaming
    tolerations:
      - key: dedicated
        operator: Equal
        value: streaming
        effect: NoSchedule

  scaling:
    type: horizontal
    min_replicas: 1
    max_replicas: 10
    metrics:
      - type: cpu
        target_utilization: 70
```

### 8.2 YARN Deployment

```yaml
deployment:
  type: yarn
  queue: streaming

  application_master:
    memory: 2gb
    vcores: 2

  container:
    memory: 4gb
    vcores: 2
```

---

## 9. Validation Rules

### 9.1 Compile-Time Validation

L6 compiler validates L5 bindings:

| Validation | Description |
|------------|-------------|
| **Reference Check** | All logical names in L1 must have L5 bindings |
| **Type Compatibility** | Stream type must match usage (source vs sink) |
| **Required Properties** | All required binding properties must be set |
| **Secret References** | All `secret://` references must exist in secrets section |
| **Environment Variables** | All `${VAR}` must be resolvable or have defaults |

### 9.2 Runtime Validation

| Validation | Description |
|------------|-------------|
| **Connectivity** | Verify connections to all bound resources |
| **Permissions** | Verify read/write access as needed |
| **Schema Compatibility** | Verify schema registry compatibility |
| **Capacity** | Verify resource availability |

---

## 10. Module Documentation

For detailed specifications, see:

| Module | Description |
|--------|-------------|
| [stream-bindings.md](./L5/stream-bindings.md) | Kafka, Kinesis, Pulsar configurations |
| [lookup-bindings.md](./L5/lookup-bindings.md) | MongoDB, Redis, PostgreSQL configurations |
| [state-checkpoints.md](./L5/state-checkpoints.md) | State backends and checkpoint storage |
| [resource-allocation.md](./L5/resource-allocation.md) | Parallelism, memory, CPU configuration |
| [secret-management.md](./L5/secret-management.md) | Secret providers and references |
| [deployment-targets.md](./L5/deployment-targets.md) | Kubernetes, YARN deployment |

---

## 11. Example Schemas

| Example | Description | Patterns Used |
|---------|-------------|---------------|
| [development.infra](./L5/examples/development.infra) | Local development setup | Minimal config, localhost |
| [production.infra](./L5/examples/production.infra) | Full production binding | All binding types |
| [multi-region.infra](./L5/examples/multi-region.infra) | Multi-region deployment | Replication, failover |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Placeholder created |
| 1.0.0 | 2025-11-27 | - | Complete specification |
