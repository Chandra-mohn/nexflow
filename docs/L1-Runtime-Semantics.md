# L1: Runtime Semantics Specification

> **Companion to**: L1 Process Orchestration DSL
> **Status**: Draft
> **Version**: 0.1.0
> **Last Updated**: 2025-01-XX

---

## 1. Overview

### 1.1 Purpose

This document defines the **runtime semantics** of L1 Nexflow — how stages behave at execution time:

- **Lifecycle Management**: Initialization, operation, shutdown, failure
- **Processing Semantics**: Delivery guarantees, ordering, idempotency
- **State Management**: Keyed state, TTL, cleanup, schema evolution
- **Correlation Internals**: How await/hold patterns execute
- **Error Handling**: Classification, retry, dead letter, circuit breaker
- **Checkpointing**: Barriers, snapshots, recovery
- **Backpressure**: Detection, propagation, mitigation
- **Observability**: Metrics, logging, tracing

### 1.2 Relationship to Other Layers

| Layer | Role | L7 Relationship |
|-------|------|-----------------|
| L1 | Declares behavior | L7 implements what L1 declares |
| L5 | Binds infrastructure | L7 uses L5-bound resources |
| L6 | Compiles to code | L7 is the runtime of compiled code |

```
L1 (declares) → L6 (compiles) → L7 (executes)
                                    ↑
                               L5 (resources)
```

### 1.3 Stage Definition

A **stage** is a single Nexflow process deployed as an independent execution unit:

```
┌─────────────────────────────────────────────────────────────┐
│                     STAGE: auth_enrichment                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐ │
│  │ Sources │ →  │ Operators │ →  │  State  │ →  │  Sinks  │ │
│  └─────────┘    └──────────┘    └─────────┘    └─────────┘ │
│       ↑              ↑              ↑              ↑        │
│       └──────────────┴──────────────┴──────────────┘        │
│                    Checkpoint Barrier                        │
├─────────────────────────────────────────────────────────────┤
│  Metrics │ Logging │ Tracing │ Health Check                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Stage Lifecycle

### 2.1 Lifecycle State Machine

```
                    ┌──────────────────┐
                    │                  │
                    ▼                  │
┌──────────┐    ┌──────────┐    ┌──────────┐
│  CREATED │ →  │  INIT    │ →  │ RUNNING  │ ←──┐
└──────────┘    └──────────┘    └────┬─────┘    │
                    │                │          │
                    │ init failure   │          │
                    ▼                ▼          │
               ┌──────────┐    ┌──────────┐    │
               │  FAILED  │    │CHECKPOINT│ ───┘
               └──────────┘    └──────────┘
                    ▲                │
                    │                │ checkpoint
                    │                │ complete
                    │                ▼
               ┌──────────┐    ┌──────────┐
               │ STOPPED  │ ←  │ DRAINING │
               └──────────┘    └──────────┘
```

### 2.2 State Definitions

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `CREATED` | Stage instantiated, not yet initialized | → INITIALIZING |
| `INITIALIZING` | Loading config, connecting resources, recovering state | → RUNNING, → FAILED |
| `RUNNING` | Processing records normally | → CHECKPOINTING, → DRAINING, → FAILED |
| `CHECKPOINTING` | Taking state snapshot | → RUNNING, → FAILED |
| `DRAINING` | Finishing in-flight records, no new input | → STOPPED, → FAILED |
| `STOPPED` | Graceful shutdown complete | (terminal) |
| `FAILED` | Unrecoverable error | (terminal, triggers restart) |

### 2.3 Initialization Sequence

```
CREATED → INITIALIZING
    │
    ├─ 1. Load configuration
    │      • Parse L5 bindings
    │      • Resolve connection strings
    │      • Apply environment overrides
    │
    ├─ 2. Initialize metrics
    │      • Register standard metrics
    │      • Register custom metrics
    │      • Start metric reporters
    │
    ├─ 3. Connect to sources
    │      • Kafka consumer setup
    │      • Assign partitions
    │      • Seek to checkpoint offsets (if recovering)
    │
    ├─ 4. Connect to sinks
    │      • Kafka producer setup
    │      • Transaction initialization (for exactly-once)
    │
    ├─ 5. Initialize state backend
    │      • Open RocksDB / HashMap state
    │      • Restore from checkpoint (if recovering)
    │      • Verify state integrity
    │
    ├─ 6. Connect to external services
    │      • MongoDB connection pool
    │      • REST API clients
    │      • Initialize circuit breakers
    │
    ├─ 7. Warm-up (optional)
    │      • Pre-populate caches
    │      • Load reference data
    │      • Compile UDFs
    │
    └─ 8. Signal ready
           • Health check returns healthy
           • Begin accepting records
           → RUNNING
```

**Initialization Timeout**: Configurable (default: 5 minutes)
**Initialization Failure**: → FAILED, trigger restart with backoff

### 2.4 Normal Operation (RUNNING)

```
while (state == RUNNING):
    1. Poll for records (with timeout)
    2. For each record batch:
       a. Deserialize
       b. Process through operator chain
       c. Update state
       d. Emit outputs
       e. Update offsets (but don't commit)
    3. If checkpoint triggered:
       → CHECKPOINTING
    4. If shutdown requested:
       → DRAINING
    5. If unrecoverable error:
       → FAILED
```

**Processing Loop Guarantees**:
- Records processed in partition order
- State updates atomic per-record
- Outputs buffered until checkpoint

### 2.5 Checkpointing (CHECKPOINTING)

```
RUNNING → CHECKPOINTING
    │
    ├─ 1. Receive checkpoint barrier
    │
    ├─ 2. Align barriers (wait for all input channels)
    │      • Buffer records arriving after barrier
    │      • Continue processing records before barrier
    │
    ├─ 3. Snapshot state
    │      • Trigger async state snapshot
    │      • Include: operator state, keyed state, offsets
    │
    ├─ 4. Forward barrier to downstream
    │
    ├─ 5. Wait for snapshot completion
    │
    ├─ 6. Acknowledge checkpoint
    │      • Commit Kafka transactions (exactly-once)
    │      • Notify checkpoint coordinator
    │
    └─ 7. Resume processing buffered records
           → RUNNING
```

### 2.6 Graceful Shutdown (DRAINING)

```
RUNNING → DRAINING
    │
    ├─ 1. Stop accepting new records
    │      • Close consumer (no more polls)
    │      • Reject incoming requests
    │
    ├─ 2. Process remaining in-flight records
    │      • Complete current batch
    │      • Flush operator buffers
    │      • Emit pending outputs
    │
    ├─ 3. Trigger final checkpoint
    │      • Snapshot final state
    │      • Commit final offsets
    │
    ├─ 4. Close connections
    │      • Close producers
    │      • Close state backend
    │      • Close external service clients
    │
    ├─ 5. Report final metrics
    │
    └─ 6. Signal shutdown complete
           → STOPPED
```

**Drain Timeout**: Configurable (default: 10 minutes)
**Drain Failure**: → FAILED (state may be inconsistent)

### 2.7 Failure Handling

```
Any State → FAILED
    │
    ├─ 1. Log failure details
    │      • Exception stack trace
    │      • Current record (if applicable)
    │      • State snapshot (if possible)
    │
    ├─ 2. Emit failure metrics
    │      • Increment failure counter
    │      • Record failure reason
    │
    ├─ 3. Attempt graceful resource cleanup
    │      • Best-effort connection close
    │      • Release locks
    │
    ├─ 4. Signal failure to orchestrator
    │
    └─ 5. Orchestrator decision:
           • Restart with backoff
           • Restore from last checkpoint
           • Alert and wait for manual intervention
```

---

## 3. Processing Semantics

### 3.1 Delivery Guarantees

| Mode | Guarantee | When to Use |
|------|-----------|-------------|
| `exactly-once` | Each record processed exactly once | Financial transactions, ledger entries |
| `at-least-once` | Record may be reprocessed on failure | Idempotent operations, metrics |
| `at-most-once` | Record may be lost on failure | Best-effort notifications |

**Default**: `exactly-once` (configurable per stage)

### 3.2 Exactly-Once Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                  Exactly-Once Protocol                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Source (Kafka)          Stage              Sink (Kafka)    │
│       │                    │                      │          │
│       │  read records      │                      │          │
│       │ ─────────────────► │                      │          │
│       │                    │                      │          │
│       │                    │  process & produce   │          │
│       │                    │ ────────────────────►│          │
│       │                    │  (transactional)     │          │
│       │                    │                      │          │
│       │         ┌──────────┴──────────┐          │          │
│       │         │ CHECKPOINT BARRIER  │          │          │
│       │         └──────────┬──────────┘          │          │
│       │                    │                      │          │
│       │                    │  commit transaction  │          │
│       │                    │ ────────────────────►│          │
│       │                    │                      │          │
│       │  commit offsets    │                      │          │
│       │ ◄───────────────── │                      │          │
│       │  (atomic with tx)  │                      │          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Properties**:
- Offsets committed atomically with output transaction
- State snapshot taken at barrier
- Recovery replays from last committed offset
- Outputs deduplicated by transaction ID

### 3.3 Ordering Guarantees

| Scope | Guarantee |
|-------|-----------|
| Per-partition | Records from same Kafka partition processed in order |
| Per-key | Records with same partition key processed in order |
| Cross-partition | No ordering guarantee |
| Cross-stage | No ordering guarantee (use correlation for sequencing) |

```
Partition 0: [A1, A2, A3] → processed as A1 → A2 → A3
Partition 1: [B1, B2, B3] → processed as B1 → B2 → B3

A1 vs B1: No ordering guarantee (may interleave)
```

### 3.4 Idempotency Requirements

For `at-least-once` mode, operators must be idempotent:

| Operation | Idempotent? | Strategy |
|-----------|-------------|----------|
| Increment counter | No | Use `set` with computed value |
| Insert record | No | Use upsert with unique key |
| Send notification | No | Deduplicate by message ID |
| Update balance | No | Use version/sequence number |

**Idempotency Key Sources**:
- Record event ID
- Composite key (source + timestamp + sequence)
- Hash of record content

### 3.5 Transaction Boundaries

```
┌─────────────────────────────────────────┐
│         Transaction Boundary            │
│                                         │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐ │
│  │ R1  │ → │ Op  │ → │State│ → │ Out │ │
│  │ R2  │ → │ Op  │ → │State│ → │ Out │ │
│  │ ... │   │     │   │     │   │     │ │
│  │ Rn  │ → │ Op  │ → │State│ → │ Out │ │
│  └─────┘   └─────┘   └─────┘   └─────┘ │
│                                         │
│  All committed atomically at checkpoint │
└─────────────────────────────────────────┘
```

**Transaction Scope**: Checkpoint interval
**Transaction Size**: Configurable (default: 10,000 records or 1 minute)

---

## 4. State Management

### 4.1 State Types

| Type | Scope | Use Case | Example |
|------|-------|----------|---------|
| **Keyed State** | Per partition key | Per-entity aggregations | Account balance, daily counts |
| **Operator State** | Per operator instance | Operator-level aggregations | Window buffers |
| **Broadcast State** | Shared across all instances | Reference data | Exchange rates, fee tables |

### 4.2 Keyed State API

```java
// Conceptual API for state access (implemented by generated code)

interface KeyedStateStore<K> {
    // Value state - single value per key
    <V> ValueState<V> getValueState(String name, Class<V> type);

    // List state - append-only list per key
    <V> ListState<V> getListState(String name, Class<V> type);

    // Map state - key-value map per key
    <K2, V> MapState<K2, V> getMapState(String name, Class<K2> keyType, Class<V> valueType);

    // Reducing state - aggregating state per key
    <V> ReducingState<V> getReducingState(String name, ReduceFunction<V> reducer);
}

// Example usage in transform UDF
public class DailyCountTransform {
    private ValueState<Long> dailyCount;

    public void open() {
        dailyCount = stateStore.getValueState("daily_count", Long.class);
    }

    public Record process(Record input) {
        Long count = dailyCount.value();
        if (count == null) count = 0L;
        dailyCount.update(count + 1);
        return input.withField("daily_count", count + 1);
    }
}
```

### 4.3 State Backends

| Backend | Characteristics | Best For |
|---------|-----------------|----------|
| **HashMap** | In-memory, fast, limited by heap | Small state, low latency |
| **RocksDB** | Disk-backed, large capacity, slower | Large state, millions of keys |
| **Remote** | External store (Redis, MongoDB) | Shared state across stages |

**Selection Criteria**:
```
State Size < 1GB           → HashMap
State Size 1GB - 100GB     → RocksDB
State Size > 100GB         → RocksDB + tiered storage
Shared across stages       → Remote (with caching)
```

### 4.4 State TTL and Cleanup

```
// L1 Declaration (from state block)
local daily_counts keyed by account_id
    type counter
    ttl 24 hours
    cleanup on_checkpoint
```

**TTL Semantics**:

| Strategy | Behavior |
|----------|----------|
| `ttl <duration>` | State expires after duration since last access |
| `ttl sliding <duration>` | TTL resets on each access |
| `ttl absolute <duration>` | State expires after duration since creation |

**Cleanup Strategies**:

| Strategy | When Cleanup Runs |
|----------|-------------------|
| `on_checkpoint` | During checkpoint (default) |
| `on_access` | When state is accessed |
| `background` | Continuous background process |

### 4.5 State Size Management

```
┌─────────────────────────────────────────────────────────────┐
│                  State Size Governance                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Metric: stage.state.size.bytes                             │
│                                                              │
│  Thresholds:                                                │
│    Warning:  80% of allocated state budget                  │
│    Critical: 95% of allocated state budget                  │
│    Limit:    100% - reject new state entries                │
│                                                              │
│  Actions on Warning:                                         │
│    • Emit metric alert                                       │
│    • Increase cleanup frequency                              │
│    • Log largest keys                                        │
│                                                              │
│  Actions on Critical:                                        │
│    • Emit PagerDuty alert                                   │
│    • Force cleanup of expired entries                       │
│    • Consider state spillover to disk                       │
│                                                              │
│  Actions on Limit:                                           │
│    • Reject new state entries                               │
│    • Route affected records to overflow queue               │
│    • Require manual intervention                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.6 State Schema Evolution

**Supported Changes**:
| Change | Support | Migration |
|--------|---------|-----------|
| Add optional field | ✓ | Automatic (default value) |
| Remove unused field | ✓ | Automatic (ignore on read) |
| Rename field | ✗ | Requires migration job |
| Change field type | ✗ | Requires migration job |
| Add required field | ✗ | Requires migration job |

**Migration Protocol**:
```
1. Deploy new stage version with dual-read capability
2. New writes use new schema
3. Old reads upgraded on access
4. Run migration job to upgrade remaining state
5. Remove dual-read capability
```

---

## 5. Correlation Internals

### 5.1 Await Pattern Implementation

The `await` pattern correlates two streams with indefinite wait and timeout:

```
// L1 Declaration
await auths
    until capture arrives
        matching on authorization_code
    timeout 7 days
        emit to orphan_authorizations
```

**Implementation Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                 AWAIT Correlation Engine                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Auth Stream                         Capture Stream          │
│       │                                    │                 │
│       ▼                                    ▼                 │
│  ┌─────────┐                         ┌─────────┐            │
│  │ Extract │                         │ Extract │            │
│  │   Key   │                         │   Key   │            │
│  └────┬────┘                         └────┬────┘            │
│       │                                    │                 │
│       ▼                                    ▼                 │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Correlation State Store             │        │
│  │                                                  │        │
│  │  Key: authorization_code                        │        │
│  │  Value: {                                       │        │
│  │    auth_record: <serialized auth>,             │        │
│  │    created_at: <timestamp>,                    │        │
│  │    timeout_at: <created_at + 7 days>           │        │
│  │  }                                              │        │
│  │                                                  │        │
│  └──────────────────────┬──────────────────────────┘        │
│                         │                                    │
│       ┌─────────────────┼─────────────────┐                 │
│       │                 │                 │                 │
│       ▼                 ▼                 ▼                 │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│  │ Matched │      │ Timeout │      │ Pending │             │
│  │  Pairs  │      │ Handler │      │  State  │             │
│  └────┬────┘      └────┬────┘      └─────────┘             │
│       │                │                                    │
│       ▼                ▼                                    │
│  downstream       orphan_auths                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Correlation Algorithm**:

```python
# Pseudocode for await correlation

def process_auth(auth_record):
    key = auth_record.authorization_code
    timeout_at = current_time() + Duration("7 days")

    # Store in correlation state
    correlation_state.put(key, {
        "auth": auth_record,
        "created_at": current_time(),
        "timeout_at": timeout_at
    })

    # Register timer for timeout
    timer_service.register(key, timeout_at)

def process_capture(capture_record):
    key = capture_record.authorization_code

    # Lookup pending auth
    pending = correlation_state.get(key)

    if pending:
        # Match found - emit correlated record
        correlation_state.delete(key)
        timer_service.cancel(key)
        emit_downstream({
            "auth": pending.auth,
            "capture": capture_record,
            "correlation_latency": current_time() - pending.created_at
        })
    else:
        # No pending auth - capture arrived first (unusual)
        emit_to_unmatched_captures(capture_record)

def on_timer(key, timeout_at):
    pending = correlation_state.get(key)

    if pending and pending.timeout_at <= current_time():
        # Timeout - emit to orphan queue
        correlation_state.delete(key)
        emit_to_orphan_auths({
            "auth": pending.auth,
            "reason": "timeout",
            "waited_duration": current_time() - pending.created_at
        })
```

### 5.2 Hold Pattern Implementation

The `hold` pattern buffers records keyed by a field, waiting for related records:

```
// L1 Declaration
hold pending_orders
    keyed by order_id
    timeout 24 hours
        emit to incomplete_orders
```

**Implementation Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                  HOLD Buffer Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Order Headers              Line Items                       │
│       │                          │                           │
│       ▼                          ▼                           │
│  ┌─────────┐               ┌─────────┐                      │
│  │  store  │               │  match  │                      │
│  │   in    │               │  from   │                      │
│  └────┬────┘               └────┬────┘                      │
│       │                          │                           │
│       ▼                          ▼                           │
│  ┌─────────────────────────────────────────────────┐        │
│  │                Hold Buffer State                 │        │
│  │                                                  │        │
│  │  Key: order_id                                  │        │
│  │  Value: {                                       │        │
│  │    header: <order header or null>,             │        │
│  │    line_items: [<list of line items>],         │        │
│  │    created_at: <timestamp>,                    │        │
│  │    timeout_at: <created_at + 24 hours>,        │        │
│  │    complete: <boolean>                          │        │
│  │  }                                              │        │
│  │                                                  │        │
│  └──────────────────────┬──────────────────────────┘        │
│                         │                                    │
│       ┌─────────────────┼─────────────────┐                 │
│       │                 │                 │                 │
│       ▼                 ▼                 ▼                 │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│  │Complete │      │ Timeout │      │ Partial │             │
│  │ Orders  │      │ Handler │      │  State  │             │
│  └────┬────┘      └────┬────┘      └─────────┘             │
│       │                │                                    │
│       ▼                ▼                                    │
│  downstream       incomplete_orders                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Completion Trigger**:
The hold buffer needs a completion condition. Options:

| Strategy | Configuration | Use Case |
|----------|---------------|----------|
| `count` | `complete when count >= N` | Fixed number of items expected |
| `marker` | `complete when marker received` | Explicit completion signal |
| `timeout` | `complete on timeout` | Time-bounded collection |
| `custom` | `complete using <rule>` | L4 rule determines completeness |

### 5.3 Timeout Detection

**Efficient Timeout Detection**:

```
┌─────────────────────────────────────────────────────────────┐
│              Timer Service Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Approach 1: Priority Queue (small scale)                   │
│  ─────────────────────────────────────────                  │
│  • Min-heap ordered by timeout_at                           │
│  • O(log n) insert, O(1) peek, O(log n) delete             │
│  • Check head on each record, fire if expired              │
│  • Good for < 1M pending correlations                       │
│                                                              │
│  Approach 2: Timer Wheel (large scale)                      │
│  ─────────────────────────────────────────                  │
│  • Buckets for time ranges (e.g., 1-hour buckets)          │
│  • O(1) insert into bucket, O(bucket size) on tick         │
│  • Coarse granularity acceptable for long timeouts         │
│  • Good for > 1M pending correlations                       │
│                                                              │
│  Approach 3: Watermark-Driven (event time)                  │
│  ─────────────────────────────────────────                  │
│  • Timeout triggers when watermark passes timeout_at       │
│  • Integrated with existing watermark infrastructure       │
│  • Handles out-of-order events correctly                   │
│  • Recommended for event-time processing                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Credit Card Domain Considerations**:
- 7-day auth-capture timeout = millions of pending correlations
- Timer wheel with 1-hour buckets recommended
- Watermark-driven for event-time correctness

### 5.4 Memory Management for Correlations

```
Correlation Memory Budget:

  Records: 1,000,000 pending authorizations
  × Size:  1 KB per serialized auth record
  ─────────────────────────────────────
  = 1 GB correlation state

  Plus overhead:
    Timer entries:    ~100 bytes × 1M = 100 MB
    Index structures: ~200 bytes × 1M = 200 MB
  ─────────────────────────────────────
  Total: ~1.3 GB per stage instance
```

**Memory Pressure Mitigation**:

| Strategy | Description |
|----------|-------------|
| **Spillover to disk** | RocksDB state backend for large correlations |
| **Compression** | Compress serialized records in state |
| **Projection** | Store only fields needed for correlation |
| **Sharding** | Distribute correlations across more instances |
| **Early eviction** | Evict low-priority correlations under pressure |

### 5.5 Correlation State Recovery

On failure recovery:
1. Restore correlation state from checkpoint
2. Rebuild timer service from state entries
3. Reprocess records since checkpoint
4. Deduplicate outputs using transaction IDs

```
Recovery Timeline:

Checkpoint @ T1          Failure @ T2         Recovery @ T3
     │                        │                    │
     ▼                        ▼                    ▼
─────┼────────────────────────┼────────────────────┼─────
     │                        │                    │
     │  Records processed     │                    │
     │  (will be reprocessed) │                    │
     │◄───────────────────────►                    │
     │                                             │
     │  State restored from checkpoint             │
     │◄────────────────────────────────────────────►
```

---

## 6. Error Handling

### 6.1 Error Taxonomy

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Classification                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 TRANSIENT ERRORS                     │   │
│  │  • Recoverable with retry                           │   │
│  │  • Network timeout, temporary unavailability        │   │
│  │  • Retry with exponential backoff                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 PERMANENT ERRORS                     │   │
│  │  • Not recoverable with retry                       │   │
│  │  • Validation failure, business rule violation     │   │
│  │  • Route to dead letter queue                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  SYSTEM ERRORS                       │   │
│  │  • Infrastructure failure                           │   │
│  │  • Out of memory, disk full, network partition     │   │
│  │  • Stage failure, require restart                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Error Types (from L1)

| L1 Error Type | Category | Default Action |
|---------------|----------|----------------|
| `transform failure` | Permanent | dead_letter |
| `lookup failure` | Transient | retry 3 |
| `rule failure` | Permanent | dead_letter |
| `correlation failure` | Permanent | dead_letter |

### 6.3 Retry Semantics

```
┌─────────────────────────────────────────────────────────────┐
│                  Retry Configuration                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  // L1 Declaration                                          │
│  on error                                                   │
│      lookup failure retry 3                                 │
│                                                              │
│  Retry Parameters:                                          │
│  ─────────────────                                          │
│  max_attempts:      3 (from L1)                             │
│  initial_delay:     100ms (default)                         │
│  max_delay:         30s (default)                           │
│  multiplier:        2.0 (exponential backoff)               │
│  jitter:            0.1 (10% randomization)                 │
│                                                              │
│  Retry Timeline:                                            │
│  ───────────────                                            │
│  Attempt 1: immediate                                       │
│  Attempt 2: after 100ms (± 10ms jitter)                    │
│  Attempt 3: after 200ms (± 20ms jitter)                    │
│  Exhausted: route to dead_letter                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.4 Dead Letter Queue Protocol

```
┌─────────────────────────────────────────────────────────────┐
│               Dead Letter Record Schema                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  {                                                          │
│    // Original record                                       │
│    "original_record": { ... },                             │
│    "original_topic": "auth_events",                        │
│    "original_partition": 42,                               │
│    "original_offset": 123456,                              │
│                                                              │
│    // Error context                                         │
│    "error_type": "transform_failure",                      │
│    "error_message": "NullPointerException at ...",         │
│    "error_stack_trace": "...",                             │
│    "retry_count": 3,                                       │
│                                                              │
│    // Processing context                                    │
│    "stage_name": "auth_enrichment",                        │
│    "stage_instance": "auth_enrichment-42",                 │
│    "operator_name": "customer_lookup",                     │
│    "processing_time": "2025-01-15T10:30:00Z",             │
│                                                              │
│    // Correlation context                                   │
│    "trace_id": "abc123",                                   │
│    "span_id": "def456"                                     │
│  }                                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.5 Poison Pill Detection

A **poison pill** is a record that consistently causes failures:

```
Detection Algorithm:

1. Track failure count per record key in sliding window
2. If same key fails > threshold in window:
   → Mark as poison pill
   → Route directly to DLQ without retry
   → Log alert

Configuration:
  poison_threshold: 5 failures
  poison_window: 1 minute
  poison_action: dead_letter_immediate
```

### 6.6 Circuit Breaker Patterns

For external service calls (MongoDB lookup, REST APIs):

```
┌─────────────────────────────────────────────────────────────┐
│                 Circuit Breaker States                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│         ┌─────────┐                                         │
│    ┌────│ CLOSED  │◄───────────────────┐                   │
│    │    └────┬────┘                    │                   │
│    │         │                          │                   │
│    │         │ failure_threshold        │ success_threshold │
│    │         │ exceeded                 │ reached           │
│    │         ▼                          │                   │
│    │    ┌─────────┐    timeout     ┌────┴────┐             │
│    │    │  OPEN   │ ──────────────►│HALF-OPEN│             │
│    │    └─────────┘                └────┬────┘             │
│    │         │                          │                   │
│    │         │ reject all              │ test request      │
│    │         │ requests                │ fails             │
│    │         │                          │                   │
│    │         └──────────────────────────┘                   │
│    │                                                        │
│    │  Fallback action when OPEN:                           │
│    │    • Return cached value (if available)               │
│    │    • Return default value                             │
│    │    • Route to fallback queue                          │
│    │    • Fail fast with circuit_open error                │
│    │                                                        │
└────┴────────────────────────────────────────────────────────┘

Configuration:
  failure_threshold: 5 failures in 10 seconds
  success_threshold: 3 consecutive successes
  timeout: 30 seconds
  fallback: return_cached | return_default | fail_fast
```

---

## 7. Checkpointing

### 7.1 Checkpoint Triggers

| Trigger | Configuration | Description |
|---------|---------------|-------------|
| **Periodic** | `checkpoint every 5 minutes` | Time-based interval |
| **Record count** | `checkpoint every 100000 records` | Volume-based |
| **Manual** | API call | Operator-initiated |
| **Shutdown** | Automatic | Before graceful shutdown |

### 7.2 Checkpoint Barrier Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Checkpoint Barrier Alignment                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Source 1     Source 2        Operator        Sink          │
│     │            │               │              │            │
│     │  records   │   records     │              │            │
│     │───────────►│──────────────►│              │            │
│     │            │               │              │            │
│     │ ═══════════╪═══════════════╪══════════════╪════       │
│     │  barrier   │   barrier     │   barrier    │            │
│     │ ═══════════╪═══════════════╪══════════════╪════       │
│     │            │               │              │            │
│     │            │  Buffer       │              │            │
│     │            │  records      │              │            │
│     │            │  after        │              │            │
│     │            │  barrier 1    │◄─────────────│            │
│     │            │               │              │            │
│     │ ═══════════╪═══════════════╪══════════════╪════       │
│     │            │   barrier     │              │            │
│     │ ═══════════╪═══════════════╪══════════════╪════       │
│     │            │               │              │            │
│     │            │  Both barriers│              │            │
│     │            │  received     │              │            │
│     │            │               │              │            │
│     │            │  SNAPSHOT     │              │            │
│     │            │  STATE        │              │            │
│     │            │               │              │            │
│     │            │  Forward      │              │            │
│     │            │  barrier      │─────────────►│            │
│     │            │               │              │            │
│     │            │  Release      │              │            │
│     │            │  buffered     │─────────────►│            │
│     │            │  records      │              │            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Incremental vs Full Snapshots

| Mode | Description | Best For |
|------|-------------|----------|
| **Full** | Snapshot entire state | Small state, simpler recovery |
| **Incremental** | Snapshot only changes since last checkpoint | Large state, faster checkpoints |

**Incremental Snapshot Protocol**:
```
Checkpoint N:   Full state snapshot (baseline)
Checkpoint N+1: Delta from N (changes only)
Checkpoint N+2: Delta from N (cumulative)
...
Checkpoint N+K: New full snapshot (consolidation)
```

### 7.4 Recovery Procedure

```
┌─────────────────────────────────────────────────────────────┐
│                  Recovery Sequence                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Locate latest successful checkpoint                     │
│     • Query checkpoint storage                              │
│     • Verify checkpoint integrity (checksum)                │
│                                                              │
│  2. Restore operator state                                  │
│     • Load state snapshots                                  │
│     • Rebuild in-memory structures                          │
│     • Verify state consistency                              │
│                                                              │
│  3. Restore source offsets                                  │
│     • Read committed offsets from checkpoint                │
│     • Seek consumers to checkpoint positions                │
│                                                              │
│  4. Resume processing                                       │
│     • Process records from checkpoint offset                │
│     • Outputs may duplicate (handled by sink idempotency)   │
│     • State updates idempotent (same input → same state)    │
│                                                              │
│  Recovery Time:                                             │
│    State restore: O(state size / disk bandwidth)            │
│    Reprocessing:  O(records since checkpoint)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 Checkpoint Failure Handling

| Failure Mode | Action |
|--------------|--------|
| Storage unavailable | Retry with backoff, alert after threshold |
| Timeout exceeded | Abort checkpoint, retry on next interval |
| Barrier alignment timeout | Abort checkpoint, continue processing |
| State snapshot failure | Stage failure, require restart |

---

## 8. Backpressure

### 8.1 Detection Mechanisms

```
┌─────────────────────────────────────────────────────────────┐
│              Backpressure Detection Signals                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Input Buffer Utilization                                │
│     ───────────────────────                                 │
│     threshold: > 80% full                                   │
│     metric: stage.input_buffer.utilization                  │
│                                                              │
│  2. Output Buffer Utilization                               │
│     ────────────────────────                                │
│     threshold: > 80% full                                   │
│     metric: stage.output_buffer.utilization                 │
│                                                              │
│  3. Processing Latency                                      │
│     ───────────────────                                     │
│     threshold: > 2x normal p99                              │
│     metric: stage.processing.latency_p99                    │
│                                                              │
│  4. Consumer Lag                                            │
│     ─────────────                                           │
│     threshold: > 1M messages behind                         │
│     metric: stage.consumer.lag                              │
│                                                              │
│  5. GC Pressure                                             │
│     ───────────                                             │
│     threshold: > 30% time in GC                             │
│     metric: stage.jvm.gc_time_percent                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Backpressure Propagation

```
Upstream Propagation:

Sink (slow)
    │
    │ output buffer full
    ▼
Operator
    │
    │ stop pulling from input
    ▼
Source
    │
    │ pause consumer
    │ (Kafka: pause partition assignment)
    │
    │ Credit-based flow control:
    │ - Downstream grants credits
    │ - Upstream sends only with credit
    │ - No credit = no send
    │
    ▼
Producer (previous stage)
```

### 8.3 Mitigation Strategies

From L1 `when slow` block:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `block` | Pause upstream, wait for capacity | Default, preserves all data |
| `drop` | Drop newest records | Metrics, best-effort |
| `sample <rate>` | Keep 1 in N records | High-volume, statistical |

**Configuration**:
```
// L1 Declaration
when slow
    strategy sample 0.1    // Keep 10% under backpressure
    alert after 5 minutes  // Alert if sustained
```

### 8.4 Recovery Behavior

```
Backpressure Recovery:

1. Backpressure detected
   → Activate mitigation strategy
   → Emit backpressure metric
   → Start alert timer

2. Sustained backpressure (> alert threshold)
   → Emit alert
   → Consider auto-scaling (if enabled)

3. Backpressure relieved
   → Deactivate mitigation
   → Resume normal processing
   → Reset alert timer
   → Emit recovery metric
```

---

## 9. Fan-out Processing

### 9.1 1:N Explosion Semantics

```
// L1 Pattern (implicit in ledger explosion)
transform using ledger_explosion_rules

// Input: 1 transaction
{
  "transaction_id": "tx123",
  "amount": 100.00,
  "merchant": "Store ABC"
}

// Output: N ledger entries (fan-out)
[
  { "entry_id": "e1", "account": "cash", "debit": 100.00 },
  { "entry_id": "e2", "account": "receivable", "credit": 100.00 },
  { "entry_id": "e3", "account": "fee_revenue", "credit": 2.50 },
  { "entry_id": "e4", "account": "interchange", "debit": 2.50 }
]
```

**Fan-out Guarantees**:
- All N outputs emitted atomically (same transaction)
- Partial fan-out not visible to downstream
- On failure, entire fan-out retried

### 9.2 Partial Failure Handling

```
┌─────────────────────────────────────────────────────────────┐
│              Fan-out Failure Modes                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Scenario: Transform 1 record → 10 outputs                  │
│                                                              │
│  Case 1: Transform failure (before fan-out)                 │
│  ──────────────────────────────────────────                 │
│  Action: Route original record to DLQ                       │
│  Outputs: None emitted                                      │
│                                                              │
│  Case 2: Partial emit failure (during fan-out)              │
│  ──────────────────────────────────────────                 │
│  Action: Rollback transaction, retry entire fan-out         │
│  Outputs: None visible until all succeed                    │
│                                                              │
│  Case 3: Checkpoint during fan-out                          │
│  ──────────────────────────────────                         │
│  Action: Complete fan-out before checkpoint                 │
│  Outputs: All emitted in same checkpoint epoch              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Idempotency for Fan-out

```
Idempotency Key Generation:

// Option 1: Derived from input
output.idempotency_key = hash(input.record_id + output.index)

// Option 2: Deterministic UUID
output.idempotency_key = uuid5(namespace, input.record_id + output.type)

// Option 3: Sequence-based
output.idempotency_key = input.record_id + "." + sequence_number

Sink Idempotency:
- Kafka: Transactional producer handles duplicates
- MongoDB: Upsert with idempotency key as _id
- REST API: Include idempotency key in header
```

### 9.4 Output Ordering

| Guarantee | Description |
|-----------|-------------|
| **Per-input ordering** | Outputs from same input in defined order |
| **Cross-input ordering** | No guarantee (parallel processing) |
| **Sink ordering** | Depends on sink (Kafka partition = ordered) |

---

## 10. External Service Integration

### 10.1 Lookup Timeout Handling

```
// Lookup with timeout
enrichment = lookup(customer_id, timeout=500ms)

Timeout Handling:
  if timeout:
    if cache_available:
      return cached_value (stale ok)
    else if default_available:
      return default_value
    else:
      throw LookupTimeoutException
      → handled by error block
```

### 10.2 Connection Pool Management

```
┌─────────────────────────────────────────────────────────────┐
│              Connection Pool Configuration                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MongoDB Connection Pool:                                   │
│    min_connections: 10                                      │
│    max_connections: 100                                     │
│    connection_timeout: 5s                                   │
│    socket_timeout: 30s                                      │
│    max_wait_time: 10s                                       │
│    idle_timeout: 5m                                         │
│                                                              │
│  HTTP Client Pool:                                          │
│    max_connections_per_host: 50                             │
│    connection_timeout: 5s                                   │
│    read_timeout: 30s                                        │
│    idle_timeout: 1m                                         │
│    retry_on_connection_failure: true                        │
│                                                              │
│  Pool Monitoring:                                           │
│    metric: pool.connections.active                          │
│    metric: pool.connections.idle                            │
│    metric: pool.wait_time_ms                                │
│    alert: pool.wait_time_ms > 5000                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 Circuit Breaker Configuration

```yaml
# Circuit breaker per external service
circuit_breakers:
  customer_lookup_mongodb:
    failure_threshold: 5
    failure_window: 10s
    success_threshold: 3
    open_timeout: 30s
    fallback: return_cached

  risk_scoring_api:
    failure_threshold: 10
    failure_window: 30s
    success_threshold: 5
    open_timeout: 60s
    fallback: return_default_score
```

### 10.4 Fallback Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `return_cached` | Return last known value | Customer data (ok if stale) |
| `return_default` | Return configured default | Risk score (conservative default) |
| `fail_fast` | Throw immediately | Critical lookups |
| `queue_for_retry` | Buffer and retry later | Non-time-sensitive |
| `degrade_gracefully` | Skip enrichment, continue | Best-effort enrichment |

---

## 11. Metrics Contract

### 11.1 Standard Metrics

Every stage emits these metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `stage.records.in` | Counter | Records received |
| `stage.records.out` | Counter | Records emitted |
| `stage.records.error` | Counter | Records failed |
| `stage.processing.latency` | Histogram | Processing time per record |
| `stage.throughput.records_per_sec` | Gauge | Current throughput |
| `stage.consumer.lag` | Gauge | Records behind head |
| `stage.state.size_bytes` | Gauge | Total state size |
| `stage.checkpoint.duration_ms` | Histogram | Checkpoint duration |
| `stage.checkpoint.size_bytes` | Gauge | Checkpoint size |
| `stage.backpressure.active` | Gauge | 1 if backpressured |

### 11.2 Naming Conventions

```
<namespace>.<stage_name>.<metric_name>

Examples:
  nexflow.auth_enrichment.records.in
  nexflow.auth_enrichment.processing.latency
  nexflow.auth_enrichment.state.size_bytes
```

### 11.3 Custom Metrics Declaration

```
// Future: L1 extension for custom metrics
metrics
    counter approved_count
    counter declined_count
    histogram amount_distribution
        buckets 10, 100, 1000, 10000
```

### 11.4 Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| `consumer.lag` | > 100K | > 1M |
| `error_rate` | > 1% | > 5% |
| `processing.latency_p99` | > 1s | > 5s |
| `state.size_bytes` | > 80% budget | > 95% budget |
| `checkpoint.duration_ms` | > 30s | > 60s |

---

## 12. Resource Management

### 12.1 Memory Allocation

```
┌─────────────────────────────────────────────────────────────┐
│              JVM Memory Layout (Flink)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Total Process Memory: 8 GB (from L5)                       │
│                                                              │
│  ├─ JVM Heap: 4 GB (50%)                                    │
│  │   ├─ Framework Heap: 512 MB                              │
│  │   └─ Task Heap: 3.5 GB                                   │
│  │       ├─ User code: 2 GB                                 │
│  │       ├─ State (HashMap): 1 GB                           │
│  │       └─ Buffers: 512 MB                                 │
│  │                                                           │
│  ├─ Off-Heap: 3 GB                                          │
│  │   ├─ Managed Memory: 2 GB (RocksDB, batch)               │
│  │   ├─ Network Buffers: 512 MB                             │
│  │   └─ JVM Overhead: 512 MB                                │
│  │                                                           │
│  └─ JVM Metaspace: 1 GB                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 Thread Pools

| Pool | Size | Purpose |
|------|------|---------|
| `source-reader` | parallelism | Reading from sources |
| `operator` | parallelism | Record processing |
| `sink-writer` | parallelism | Writing to sinks |
| `async-io` | parallelism × 2 | Async lookups |
| `checkpoint` | 2 | Checkpoint coordination |
| `timer` | 1 | Timer service |

### 12.3 Buffer Management

```
Input Buffer:
  size: 32 KB per partition
  count: partitions × 2 (double buffering)
  backpressure_threshold: 80%

Output Buffer:
  size: 32 KB per partition
  flush_interval: 100ms
  flush_threshold: 80% full

Network Buffer:
  size: 32 KB
  pool_size: (parallelism × 4) per task
```

### 12.4 Connection Pools

| Resource | Min | Max | Idle Timeout |
|----------|-----|-----|--------------|
| Kafka Consumer | 1 | 1 per partition | N/A |
| Kafka Producer | 1 | parallelism | 5 min |
| MongoDB | 10 | 100 | 5 min |
| HTTP Client | 10 | 50 per host | 1 min |

---

## 13. Open Questions

| Question | Options | Notes |
|----------|---------|-------|
| State migration tooling | Built-in / External | Needed for schema evolution |
| Custom metrics in L1 | Yes / No | Keep L1 simple vs observable |
| Correlation completion semantics | Count / Marker / Custom | Flexibility vs complexity |
| Multi-stage transactions | Support / Not support | Cross-stage exactly-once |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Initial draft |
