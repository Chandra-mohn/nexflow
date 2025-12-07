# L5: State Backends and Checkpoints

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

State and checkpoint bindings configure how Nexflow processes manage stateful computations and ensure fault tolerance. These are critical for exactly-once processing guarantees.

---

## State Backends

State backends determine how stateful operations store their intermediate state during processing.

### Supported State Backends

| Backend | Use Case | Trade-offs |
|---------|----------|------------|
| **RocksDB** | Production, large state | Disk-based, incremental checkpoints |
| **HashMap** | Development, small state | Memory-only, fast, no persistence |
| **External** | Shared state | Network latency, consistency |

---

## RocksDB State Backend

### Basic Configuration

```yaml
state_backends:
  default:
    type: rocksdb
    incremental: true
```

### Complete Configuration

```yaml
state_backends:
  default:
    type: rocksdb
    incremental: true

    # Storage configuration
    storage:
      local_directories:
        - /mnt/ssd1/flink-state
        - /mnt/ssd2/flink-state
      # Directory selection strategy
      directory_selection: round_robin  # round_robin, least_used

    # Memory configuration
    memory:
      managed: true
      write_buffer_count: 4
      # Per-column-family settings
      per_slot: 256mb

    # RocksDB options
    options:
      # Block cache (shared across column families)
      block_cache_size: 512mb

      # Write buffer
      write_buffer_size: 64mb
      max_write_buffer_number: 4
      min_write_buffer_number_to_merge: 2

      # Compaction
      level_compaction_dynamic_level_bytes: true
      max_background_compactions: 4
      max_background_flushes: 4

      # Bloom filters
      bloom_filter_bits_per_key: 10
      bloom_filter_block_based: true

      # Compression
      compression: LZ4  # NONE, SNAPPY, LZ4, ZSTD

    # Timer service
    timer_service:
      type: rocksdb  # rocksdb, heap
      async: true

    # TTL compaction (for state cleanup)
    ttl:
      enabled: true
      compaction_filter: true
```

### RocksDB Tuning Profiles

```yaml
state_backends:
  # High-throughput profile
  high_throughput:
    type: rocksdb
    options:
      write_buffer_size: 128mb
      max_write_buffer_number: 6
      block_cache_size: 1gb
      compression: LZ4

  # Low-latency profile
  low_latency:
    type: rocksdb
    options:
      write_buffer_size: 32mb
      max_write_buffer_number: 2
      block_cache_size: 256mb
      compression: NONE  # No compression for speed

  # Memory-constrained profile
  memory_constrained:
    type: rocksdb
    options:
      write_buffer_size: 16mb
      max_write_buffer_number: 2
      block_cache_size: 64mb
      compression: ZSTD  # High compression ratio
```

---

## HashMap State Backend

For development and testing with small state:

```yaml
state_backends:
  dev_state:
    type: hashmap
    async_snapshots: true  # Non-blocking checkpoints

    # Memory limits
    memory:
      max_heap_size: 1gb
      gc_threshold: 0.8  # Trigger GC at 80%
```

---

## External State Backend

For shared or persistent state requirements:

```yaml
state_backends:
  shared_state:
    type: external

    # Redis-backed state
    redis:
      uri: ${REDIS_STATE_URI}
      cluster_mode: true
      key_prefix: "flink:state:"
      ttl: 24h

    # Or distributed cache
    ignite:
      config_path: /etc/ignite/ignite-config.xml
      cache_name: flink-state
```

---

## Checkpoint Storage

Checkpoints provide fault tolerance by periodically saving the state of the entire job.

### Supported Storage Types

| Storage | Use Case | Features |
|---------|----------|----------|
| **S3** | Cloud-native | Scalable, durable |
| **HDFS** | On-premise Hadoop | Integrated, distributed |
| **GCS** | Google Cloud | Managed, global |
| **Azure Blob** | Azure | Managed, integrated |
| **Filesystem** | Development | Local, fast |

---

## S3 Checkpoint Storage

### Basic Configuration

```yaml
checkpoints:
  auth_checkpoints:
    type: s3
    bucket: my-checkpoints
    prefix: auth/
```

### Complete Configuration

```yaml
checkpoints:
  auth_checkpoints:
    type: s3
    bucket: company-flink-checkpoints
    prefix: production/auth-enrichment/
    region: us-east-1

    # Checkpoint behavior
    checkpoint:
      interval: 60s  # Checkpoint frequency
      min_pause: 30s  # Min time between checkpoints
      timeout: 10m  # Max checkpoint duration
      max_concurrent: 1  # Concurrent checkpoints
      mode: exactly_once  # exactly_once, at_least_once

    # Savepoint configuration
    savepoint:
      directory: s3://company-flink-savepoints/auth-enrichment/

    # Retention policy
    retention:
      max_checkpoints: 3  # Keep last N checkpoints
      cleanup_on_cancel: delete  # delete, retain
      externalized: retain_on_cancellation  # retain, delete

    # S3-specific options
    s3:
      endpoint: ${S3_ENDPOINT}  # For S3-compatible stores
      path_style_access: false
      multipart_upload_threshold: 100mb
      multipart_upload_part_size: 64mb

    # Authentication
    auth:
      type: instance_profile  # instance_profile, static, assume_role
      # Static credentials (not recommended for production)
      # access_key: ${AWS_ACCESS_KEY}
      # secret_key: ${AWS_SECRET_KEY}
      # Assume role
      role_arn: arn:aws:iam::123456789:role/flink-checkpoint-role

    # Encryption
    encryption:
      type: sse_s3  # sse_s3, sse_kms, none
      kms_key_id: ${KMS_KEY_ID}
```

---

## HDFS Checkpoint Storage

### Complete Configuration

```yaml
checkpoints:
  batch_checkpoints:
    type: hdfs
    path: hdfs://namenode:9000/flink/checkpoints/

    # HDFS configuration
    hdfs:
      replication: 3
      block_size: 128mb
      config_path: /etc/hadoop/conf

    # Checkpoint behavior
    checkpoint:
      interval: 5m
      mode: at_least_once  # Batch jobs often use at_least_once

    # Kerberos authentication
    kerberos:
      enabled: true
      principal: flink/_HOST@REALM
      keytab: /etc/security/keytabs/flink.keytab
```

---

## GCS Checkpoint Storage

```yaml
checkpoints:
  gcs_checkpoints:
    type: gcs
    bucket: flink-checkpoints-prod
    prefix: auth-processing/

    # GCS-specific
    gcs:
      project_id: ${GCP_PROJECT}

    # Authentication
    auth:
      type: service_account
      key_file: /etc/gcp/service-account.json
      # Or workload identity
      # type: workload_identity
```

---

## Azure Blob Checkpoint Storage

```yaml
checkpoints:
  azure_checkpoints:
    type: azure_blob
    container: flink-checkpoints
    prefix: production/

    # Azure configuration
    azure:
      account_name: ${AZURE_STORAGE_ACCOUNT}
      account_key: ${AZURE_STORAGE_KEY}
      # Or managed identity
      # auth_type: managed_identity
```

---

## Local Filesystem (Development)

```yaml
checkpoints:
  local_checkpoints:
    type: filesystem
    path: file:///tmp/flink-checkpoints

    checkpoint:
      interval: 30s
      min_pause: 10s
```

---

## Checkpoint Behavior Configuration

### Checkpoint Modes

| Mode | Guarantee | Performance |
|------|-----------|-------------|
| `exactly_once` | No duplicates | Slower, barriers |
| `at_least_once` | Possible duplicates | Faster |

```yaml
checkpoints:
  default:
    checkpoint:
      mode: exactly_once

      # Aligned checkpoints (exactly-once)
      alignment:
        type: aligned  # aligned, unaligned
        timeout: 10m

      # Unaligned checkpoints (lower latency)
      # alignment:
      #   type: unaligned
      #   buffer_debloat: true
```

### Incremental Checkpoints

```yaml
checkpoints:
  default:
    checkpoint:
      incremental: true  # Only store state changes
```

### Checkpoint Recovery

```yaml
checkpoints:
  default:
    recovery:
      # Restart strategy
      restart:
        strategy: exponential_delay  # fixed_delay, failure_rate, exponential_delay
        initial_delay: 1s
        max_delay: 60s
        backoff_multiplier: 2.0
        max_attempts: 10

      # State recovery
      state:
        skip_corrupted: false
        allow_non_restored: false

      # Savepoint recovery
      from_savepoint:
        path: s3://savepoints/auth-enrichment/savepoint-123
        allow_non_restored: false
```

---

## Changelog State Backend

For very fast checkpoints with large state:

```yaml
state_backends:
  changelog_state:
    type: changelog
    base_backend: rocksdb

    changelog:
      storage: s3://changelog-bucket/auth/
      retention: 1h
      periodic_materialize:
        enabled: true
        interval: 5m
```

---

## State TTL Configuration

Configure automatic state cleanup:

```yaml
state_backends:
  default:
    type: rocksdb

    # State TTL (Time-To-Live)
    ttl:
      enabled: true
      default_ttl: 24h
      cleanup:
        strategy: incremental  # full, incremental, rocksdb_compaction
        run_interval: 1h
        delete_batch_size: 1000

    # Per-state TTL (referenced in L1)
    state_ttls:
      session_state: 30m
      aggregation_state: 1h
      user_preferences: 7d
```

---

## Metrics and Monitoring

```yaml
checkpoints:
  default:
    monitoring:
      metrics:
        enabled: true
        histogram_sample_count: 1000

      # Checkpoint history
      history:
        num_checkpoints: 10
        include_task_checkpoints: true

      # Alerting thresholds
      alerts:
        checkpoint_duration_warning: 5m
        checkpoint_duration_critical: 10m
        checkpoint_size_warning: 10gb
```

---

## Best Practices

### Production Configuration

```yaml
state_backends:
  production:
    type: rocksdb
    incremental: true
    options:
      write_buffer_size: 64mb
      block_cache_size: 256mb
      compression: LZ4

checkpoints:
  production:
    type: s3
    bucket: prod-checkpoints
    checkpoint:
      interval: 60s
      min_pause: 30s
      mode: exactly_once
      incremental: true
    retention:
      max_checkpoints: 3
      externalized: retain_on_cancellation
```

### Development Configuration

```yaml
state_backends:
  development:
    type: hashmap
    async_snapshots: true

checkpoints:
  development:
    type: filesystem
    path: file:///tmp/checkpoints
    checkpoint:
      interval: 30s
      mode: at_least_once
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [stream-bindings.md](./stream-bindings.md) - Stream configurations
- [resource-allocation.md](./resource-allocation.md) - Compute resources
