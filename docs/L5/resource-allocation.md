# L5: Resource Allocation

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Resource allocation bindings configure compute resources (parallelism, memory, CPU) for Nexflow processes. These settings are critical for performance, cost optimization, and meeting SLA requirements.

---

## Resource Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                     Resource Allocation Hierarchy                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Job Level                                                       │
│  └── Task Manager Level                                          │
│      └── Task Slot Level                                         │
│          └── Operator Level                                      │
│                                                                  │
│  _defaults → process → operator (most specific wins)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Basic Configuration

```yaml
resources:
  # Global defaults
  _defaults:
    parallelism: 16
    task_memory: 2gb
    task_cpu: 1

  # Per-process overrides
  authorization_enrichment:
    parallelism: 128
    task_memory: 4gb
    task_cpu: 2
```

---

## Parallelism Configuration

### Process-Level Parallelism

```yaml
resources:
  authorization_enrichment:
    # Execution parallelism
    parallelism: 128
    max_parallelism: 256  # For rescaling without state migration

    # Slot sharing group
    slot_sharing_group: enrichment-group
```

### Operator-Level Parallelism

Override parallelism for specific operators within a process:

```yaml
resources:
  authorization_enrichment:
    parallelism: 128

    # Per-operator overrides
    operators:
      source_auth_events:
        parallelism: 64  # Match Kafka partitions
      enrich_customers:
        parallelism: 128
      sink_enriched:
        parallelism: 64
```

### Dynamic Parallelism

Configure auto-scaling based on load:

```yaml
resources:
  authorization_enrichment:
    parallelism:
      initial: 64
      min: 32
      max: 256

    auto_scale:
      enabled: true
      metrics:
        - type: kafka_lag
          target: 10000  # Target lag per partition
        - type: cpu_utilization
          target: 70
      cooldown_period: 5m
      scale_up_factor: 2.0
      scale_down_factor: 0.5
```

---

## Memory Configuration

### Task Memory Model

```yaml
resources:
  authorization_enrichment:
    # Total memory per task slot
    task_memory: 4gb

    # Memory breakdown
    memory:
      # JVM heap for user code
      heap: 2gb  # Or fraction: 0.5

      # Off-heap managed memory (RocksDB, etc.)
      managed: 1gb  # Or fraction: 0.25

      # Framework overhead (Flink internals)
      framework_heap: 128mb
      framework_off_heap: 128mb

      # Network buffers
      network: 256mb  # Or min/max range
      network_min: 128mb
      network_max: 512mb

      # Task off-heap (JNI, native libs)
      task_off_heap: 0
```

### Memory Profiles

```yaml
resources:
  # CPU-intensive processing
  cpu_intensive_process:
    memory:
      heap: 70%
      managed: 20%
      network: 10%

  # State-heavy processing
  stateful_process:
    memory:
      heap: 40%
      managed: 50%  # More for RocksDB
      network: 10%

  # Network-intensive processing
  network_intensive_process:
    memory:
      heap: 50%
      managed: 20%
      network: 30%
```

### JVM Options

```yaml
resources:
  authorization_enrichment:
    jvm:
      options:
        - "-XX:+UseG1GC"
        - "-XX:MaxGCPauseMillis=100"
        - "-XX:ParallelGCThreads=4"
        - "-XX:+HeapDumpOnOutOfMemoryError"
        - "-XX:HeapDumpPath=/var/log/flink/heapdump"

      # Metaspace
      metaspace: 256mb
      metaspace_max: 512mb
```

---

## CPU Configuration

### Task CPU Allocation

```yaml
resources:
  authorization_enrichment:
    # CPU cores per task slot
    task_cpu: 2.0  # Can be fractional

    # CPU shares (relative priority)
    cpu_shares: 1024  # Default is 1024
```

### CPU Limits (Kubernetes)

```yaml
resources:
  authorization_enrichment:
    kubernetes:
      cpu:
        request: 2.0
        limit: 4.0  # Allow burst
```

---

## Network Configuration

### Buffer Configuration

```yaml
resources:
  authorization_enrichment:
    network:
      # Buffer pool
      buffers_per_channel: 2
      floating_buffers_per_gate: 8
      exclusive_buffers_per_channel: 2

      # Buffer size
      buffer_size: 32kb  # Default 32kb

      # Buffer timeout
      buffer_timeout: 100ms

      # Memory segment size
      memory_segment_size: 32kb
```

### Back-pressure Configuration

```yaml
resources:
  authorization_enrichment:
    backpressure:
      # Credit-based flow control
      credit_based: true

      # Buffer debloating
      buffer_debloat:
        enabled: true
        target: 1s  # Target in-flight time
        min_buffers: 1
        max_buffers: 16
```

---

## Resource Groups

Group processes with similar resource requirements:

```yaml
resources:
  _groups:
    # High-throughput streaming
    high_throughput:
      parallelism: 128
      task_memory: 4gb
      task_cpu: 2
      memory:
        managed: 40%

    # Low-latency processing
    low_latency:
      parallelism: 64
      task_memory: 2gb
      task_cpu: 1
      network:
        buffer_timeout: 10ms

    # Batch processing
    batch:
      parallelism: 32
      task_memory: 8gb
      task_cpu: 4
      memory:
        managed: 60%

  # Reference groups
  authorization_enrichment:
    _group: high_throughput

  real_time_alerts:
    _group: low_latency

  daily_aggregation:
    _group: batch
```

---

## Scheduling Configuration

### Slot Sharing

```yaml
resources:
  authorization_enrichment:
    # Slot sharing groups
    slot_sharing:
      enabled: true
      groups:
        - name: source-group
          operators: [source_*]
        - name: processing-group
          operators: [enrich_*, transform_*]
        - name: sink-group
          operators: [sink_*]
```

### Co-location

```yaml
resources:
  authorization_enrichment:
    # Co-locate operators
    co_location:
      - [source_auth_events, enrich_customers]  # Same slot
```

### Resource Constraints

```yaml
resources:
  authorization_enrichment:
    constraints:
      # Require specific node labels
      node_labels:
        workload-type: streaming
        disk-type: ssd

      # Avoid specific nodes
      anti_affinity:
        - batch-workers

      # Spread across availability zones
      topology:
        spread_constraint: zone
```

---

## Task Manager Configuration

### Task Manager Sizing

```yaml
resources:
  _task_managers:
    # Number of task managers
    count: 16

    # Per task manager
    memory: 16gb
    cpu: 8
    slots_per_manager: 4

    # Or auto-calculate
    auto_size:
      total_parallelism: 128
      slots_per_manager: 4
      # Results in 32 task managers
```

### Task Manager Resources

```yaml
resources:
  _task_managers:
    memory:
      total: 16gb

      # Process memory breakdown
      flink:
        heap: 8gb
        managed: 4gb
        network: 2gb
        framework: 512mb
        task_off_heap: 0

      # JVM overhead
      jvm_metaspace: 256mb
      jvm_overhead: 1gb
```

---

## Job Manager Configuration

```yaml
resources:
  _job_manager:
    memory: 2gb
    cpu: 2

    # High availability
    ha:
      type: zookeeper  # zookeeper, kubernetes
      zookeeper_quorum: ${ZK_QUORUM}
      storage_dir: hdfs://namenode:9000/flink/ha/

    # Web UI
    web:
      port: 8081
      submit_enable: false  # Disable in production
```

---

## Capacity Planning

### Throughput-Based Sizing

```yaml
resources:
  authorization_enrichment:
    # Target throughput
    capacity:
      target_throughput: 100000  # events/second
      target_latency_p99: 100ms

    # Auto-calculate resources
    auto_size:
      based_on: throughput
      events_per_second: 100000
      bytes_per_event: 1kb
      processing_time_ms: 5
      # Recommended: parallelism=64, task_memory=4gb
```

### SLA-Based Configuration

```yaml
resources:
  authorization_enrichment:
    sla:
      throughput:
        min: 80000  # events/sec
        target: 100000
      latency:
        p50: 10ms
        p99: 100ms
        max: 500ms
      availability: 99.9%

    # Resources sized for SLA
    parallelism: 128
    task_memory: 4gb
```

---

## Environment-Specific Resources

```yaml
# development.infra
resources:
  _defaults:
    parallelism: 2
    task_memory: 1gb
    task_cpu: 0.5

# staging.infra
resources:
  _defaults:
    parallelism: 16
    task_memory: 2gb
    task_cpu: 1

# production.infra
resources:
  _defaults:
    parallelism: 64
    task_memory: 4gb
    task_cpu: 2

  authorization_enrichment:
    parallelism: 128
    task_memory: 4gb
    task_cpu: 2
```

---

## Resource Limits

### Hard Limits

```yaml
resources:
  authorization_enrichment:
    limits:
      max_parallelism: 256
      max_task_memory: 8gb
      max_task_cpu: 4

    # Cost limits
    cost:
      max_monthly_cost: 10000  # USD
      instance_type_allowlist:
        - m5.xlarge
        - m5.2xlarge
```

### Quotas

```yaml
resources:
  _quotas:
    # Team-level quotas
    credit_card_team:
      max_total_parallelism: 512
      max_total_memory: 1tb
      max_processes: 20
```

---

## Metrics and Monitoring

```yaml
resources:
  authorization_enrichment:
    monitoring:
      resource_metrics:
        enabled: true
        interval: 15s

      alerts:
        - name: high_memory_usage
          condition: "memory_usage > 0.9"
          action: scale_up

        - name: low_cpu_utilization
          condition: "cpu_usage < 0.3 for 30m"
          action: scale_down

        - name: high_gc_time
          condition: "gc_time_percent > 10"
          action: alert
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [state-checkpoints.md](./state-checkpoints.md) - State and checkpoints
- [deployment-targets.md](./deployment-targets.md) - Deployment configuration
