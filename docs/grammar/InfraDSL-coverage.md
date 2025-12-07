# L5 Infrastructure Binding Coverage

> **Schema Version**: 1.0.0
> **Verification Date**: 2025-11-30

---

## Coverage Summary

| Category | Features | Covered | Status |
|----------|----------|---------|--------|
| Stream Bindings | 3 platforms | 3 | ✅ 100% |
| Lookup Bindings | 5 stores | 5 | ✅ 100% |
| Checkpoint Storage | 4 backends | 4 | ✅ 100% |
| State Backends | 2 types | 2 | ✅ 100% |
| Secret Providers | 4 providers | 4 | ✅ 100% |
| Resource Config | 6 properties | 6 | ✅ 100% |
| Monitoring | 4 subsystems | 4 | ✅ 100% |
| Deployment | 3 targets | 3 | ✅ 100% |

**Overall Coverage**: ~95%

---

## 1. Stream Bindings (3/3) ✅

### Supported Platforms

| Platform | Schema Definition | Example File |
|----------|------------------|--------------|
| Apache Kafka | `KafkaBinding` | production.infra:16-65 |
| Amazon Kinesis | `KinesisBinding` | (supported in schema) |
| Apache Pulsar | `PulsarBinding` | (supported in schema) |

### Kafka Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Topic configuration | `topic`, `partitions`, `replication` | `partitions: 128` |
| Consumer config | `KafkaConsumerConfig` | `auto_offset_reset: earliest` |
| Producer config | `KafkaProducerConfig` | `acks: all`, `idempotence: true` |
| Security | `properties` | `security.protocol: SASL_SSL` |
| Schema Registry | `schema_registry` | `url: ${SCHEMA_REGISTRY_URL}` |
| Serialization | `serialization` | `value_format: avro` |
| Error handling | `error_handling` | `action: dlq` |

### Kinesis Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Stream name | `stream` | `prod-fraud-alerts` |
| Region | `region` | `us-east-1` |
| Shards | `shard_count` | `16` |
| Consumer type | `consumer.type` | `enhanced_fan_out` |
| AWS credentials | `credentials` | `type: assume_role` |

### Pulsar Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Topic path | `topic` | `persistent://ns/topic` |
| Service URL | `service_url` | `pulsar://cluster:6650` |
| Subscription | `consumer.subscription_type` | `Key_Shared` |
| Authentication | `auth` | `type: token` |
| TLS | `tls` | `enabled: true` |

---

## 2. Lookup Bindings (5/5) ✅

| Store | Schema Definition | Key Features |
|-------|-------------------|--------------|
| MongoDB | `MongoDbBinding` | URI, read preference, caching |
| Redis | `RedisBinding` | Cluster mode, key pattern |
| PostgreSQL | `PostgreSqlBinding` | JDBC, connection pool |
| Cassandra | `CassandraBinding` | Contact points, consistency |
| Elasticsearch | `ElasticsearchBinding` | Index, hosts |

### Common Features

| Feature | Schema Property | Supported |
|---------|-----------------|-----------|
| Connection pooling | `max_pool_size`, `pool_size` | ✅ |
| Read caching | `cache` | ✅ |
| Cache TTL | `cache.ttl` | ✅ |
| Cache size | `cache.max_size` | ✅ |
| TLS/SSL | `tls`, `ssl` | ✅ |

---

## 3. Checkpoint Storage (4/4) ✅

| Backend | Schema Definition | Key Properties |
|---------|-------------------|----------------|
| Amazon S3 | `S3CheckpointConfig` | bucket, prefix, region |
| HDFS | `HdfsCheckpointConfig` | path, replication |
| Google Cloud Storage | `GcsCheckpointConfig` | bucket, prefix |
| Local Filesystem | `FilesystemCheckpointConfig` | path |

### Common Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Checkpoint interval | `interval` | `60s` |
| Minimum pause | `min_pause` | `30s` |
| Retention | (via deployment config) | `max_checkpoints: 5` |

---

## 4. State Backends (2/2) ✅

| Backend | Schema Definition | Use Case |
|---------|-------------------|----------|
| RocksDB | `RocksDbConfig` | Production (persistent) |
| HashMap | `HashMapConfig` | Development (in-memory) |

### RocksDB Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Incremental checkpoints | `incremental` | `true` |
| Local directories | `local_directories` | `/mnt/ssd1/state` |
| Block cache | `options.block_cache_size` | `256mb` |
| Write buffer | `options.write_buffer_size` | `64mb` |

---

## 5. Secret Management (4/4) ✅

| Provider | Schema Definition | Use Case |
|----------|-------------------|----------|
| HashiCorp Vault | `VaultSecretConfig` | Production |
| AWS Secrets Manager | `AwsSecretConfig` | AWS environments |
| Kubernetes Secrets | `K8sSecretConfig` | Kubernetes deployments |
| Environment Variables | `provider: env` | Development |

### Secret Reference Syntax

```yaml
# Secret reference pattern
uri: secret://mongo_connection/uri

# Schema validation
pattern: ^secret://[a-z_][a-z0-9_]*/[a-z_][a-z0-9_]*$
```

---

## 6. Resource Configuration (6/6) ✅

| Property | Schema Definition | Example |
|----------|-------------------|---------|
| Parallelism | `parallelism` | `128` |
| Max parallelism | `max_parallelism` | `256` |
| Task memory | `task_memory` | `4gb` |
| Task CPU | `task_cpu` | `2` |
| Managed memory | `managed_memory` | `1gb` |
| Network memory | `network_memory` | `128mb` |

### Per-Process Override

```yaml
resources:
  _defaults:
    parallelism: 16

  authorization_enrichment:
    parallelism: 128  # Override for specific process
```

---

## 7. Monitoring Configuration (4/4) ✅

### Metrics

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Metrics type | `metrics.type` | `prometheus` |
| Port | `metrics.port` | `9249` |
| Path | `metrics.path` | `/metrics` |
| Labels | `metrics.labels` | `environment: production` |

### Tracing

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Tracing type | `tracing.type` | `jaeger`, `zipkin`, `otel` |
| Endpoint | `tracing.endpoint` | `http://jaeger:14268/api/traces` |
| Sampling rate | `tracing.sampling_rate` | `0.01` |

### Logging

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Log level | `logging.level` | `INFO` |
| Format | `logging.format` | `json` |
| Outputs | `logging.outputs` | `stdout`, `elasticsearch` |

### Alerting

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Alert name | `alerts[].name` | `high_latency` |
| Condition | `alerts[].condition` | `p99 > 1000ms` |
| Severity | `alerts[].severity` | `critical` |
| Channels | `alerts[].channels` | `pagerduty://...` |

---

## 8. Deployment Targets (3/3) ✅

| Target | Schema Definition | Key Features |
|--------|-------------------|--------------|
| Kubernetes | `KubernetesDeployment` | Namespace, pod template, scaling |
| YARN | `YarnDeployment` | Queue, container config |
| Standalone | `type: standalone` | Local execution |

### Kubernetes Features

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Namespace | `namespace` | `credit-card-production` |
| Service account | `service_account` | `nexflow-runner` |
| Pod annotations | `pod_template.annotations` | `prometheus.io/scrape: "true"` |
| Node selector | `pod_template.node_selector` | `workload-type: streaming` |
| Tolerations | `pod_template.tolerations` | `key: dedicated` |
| Scaling | `scaling` | `type: horizontal` |

---

## 9. Environment Features ✅

| Feature | Schema Property | Example |
|---------|-----------------|---------|
| Version | `version` | `"1.0"` |
| Environment name | `environment` | `production` |
| Description | `description` | `"Production bindings"` |
| Inheritance | `extends` | `base.infra` |
| Environment variables | `${VAR_NAME}` | `${KAFKA_BROKERS}` |
| Default values | `${VAR:-default}` | `${PORT:-9092}` |

---

## Schema Validation Features

### Type Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Duration | `^[0-9]+(ms\|s\|m\|h\|d)$` | `30s`, `5m`, `7d` |
| Byte size | `^[0-9]+(b\|kb\|mb\|gb)$` | `64mb`, `4gb` |
| Secret ref | `^secret://...` | `secret://creds/password` |
| Env variable | `^\$\{...\}$` | `${KAFKA_BROKERS}` |

### Conditional Validation

```json
{
  "if": { "properties": { "type": { "const": "kafka" } } },
  "then": { "$ref": "#/definitions/KafkaBinding" }
}
```

---

## Example Files

| File | Description | Features Demonstrated |
|------|-------------|----------------------|
| `base.infra` | Shared configuration | Inheritance, defaults |
| `development.infra` | Local dev setup | Minimal config, filesystem checkpoints |
| `production.infra` | Full production | All binding types, Vault secrets, K8s |
| `multi-region.infra` | Multi-AZ deployment | Replication, failover |

---

## Validation Rules

### Compile-Time Validation

| Rule | Description |
|------|-------------|
| Reference check | All L1 logical names must have L5 bindings |
| Type compatibility | Stream type must match usage (source/sink) |
| Required properties | All required binding properties must be set |
| Secret references | All `secret://` refs must exist in secrets section |
| Environment variables | All `${VAR}` must be resolvable |

### Runtime Validation

| Rule | Description |
|------|-------------|
| Connectivity | Verify connections to all bound resources |
| Permissions | Verify read/write access as needed |
| Schema compatibility | Verify schema registry compatibility |
| Capacity | Verify resource availability |

---

## Notes

1. **YAML Format**: L5 uses YAML (not a custom DSL) for DevOps tooling compatibility
2. **JSON Schema**: `InfraSchema.json` provides IDE autocompletion and validation
3. **Inheritance**: Use `extends: base.infra` to reduce duplication across environments
4. **Secrets**: Never store secrets directly - always use secret provider references

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-30 | Initial coverage verification |
