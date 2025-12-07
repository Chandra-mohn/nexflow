# L2: Streaming Annotations

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Streaming annotations provide metadata that stream processing engines (Flink, Spark) need to properly handle data:

- **Key fields**: How to partition data
- **Time semantics**: Event time vs processing time
- **Watermarks**: Progress tracking for out-of-order data
- **Late data handling**: What to do with late arrivals

---

## Key Fields (Partitioning)

### Single Key

```schema
schema transaction
  streaming
    key_fields: [account_id]
  end
end
```

**Semantics**: All events with the same `account_id` processed by same operator instance.

### Composite Key

```schema
schema transaction
  streaming
    key_fields: [card_id, merchant_id]
  end
end
```

**Semantics**: Events partitioned by combination of `card_id` AND `merchant_id`.

### No Key (Broadcast)

```schema
schema configuration
  streaming
    key_fields: []  // Broadcast to all operators
  end
end
```

---

## Time Semantics

### Event Time

Use timestamp embedded in the event:

```schema
schema auth_event
  streaming
    time_field: event_timestamp      // Field containing event time
    time_semantics: event_time       // Process by event time
  end

  fields
    event_timestamp: timestamp, required
  end
end
```

**Use when**:
- Events can arrive out of order
- Need reproducible results (reprocessing)
- Source provides reliable timestamps

### Processing Time

Use time when event is processed:

```schema
schema metrics
  streaming
    time_semantics: processing_time  // Use processing time
  end
end
```

**Use when**:
- Order doesn't matter
- Real-time dashboards
- No reliable event timestamps

### Ingestion Time

Use time when event enters the system:

```schema
schema log_event
  streaming
    time_semantics: ingestion_time   // Timestamp at source
  end
end
```

**Use when**:
- Source doesn't provide timestamps
- Want compromise between event/processing time

---

## Watermarks

Watermarks track progress through event time, enabling the system to know when all events up to a certain time have arrived.

### Fixed Delay Watermark

```schema
schema transaction
  streaming
    time_field: event_timestamp
    watermark_delay: 30 seconds
  end
end
```

**Semantics**: Watermark = max(event_time) - 30 seconds

Events arriving more than 30 seconds late are considered late.

### Bounded Out-of-Orderness

```schema
schema auth_event
  streaming
    time_field: event_timestamp
    watermark_strategy: bounded_out_of_orderness
    max_out_of_orderness: 5 minutes
  end
end
```

### Periodic Watermarks

```schema
schema transaction
  streaming
    time_field: event_timestamp
    watermark_strategy: periodic
    watermark_interval: 100 milliseconds
  end
end
```

### Punctuated Watermarks

```schema
schema control_event
  streaming
    watermark_strategy: punctuated
    watermark_field: watermark_timestamp  // Explicit watermark in data
  end
end
```

---

## Late Data Handling

### Side Output (Recommended)

Late data sent to separate stream for analysis/reprocessing:

```schema
schema transaction
  streaming
    time_field: event_timestamp
    watermark_delay: 30 seconds
    late_data_handling: side_output
    late_data_stream: late_transactions
  end
end
```

**Generated L1**:
```proc
receive events from transactions
  late data to late_transactions
```

### Drop Late Data

Discard late events (fastest, but loses data):

```schema
schema transaction
  streaming
    time_field: event_timestamp
    watermark_delay: 30 seconds
    late_data_handling: drop
  end
end
```

### Update Results

Allow late data to update already-emitted results:

```schema
schema transaction
  streaming
    time_field: event_timestamp
    watermark_delay: 30 seconds
    late_data_handling: update
    allowed_lateness: 5 minutes
  end
end
```

**Semantics**:
- Results may be emitted multiple times
- Downstream must handle updates
- State retained for `allowed_lateness` duration

### Allowed Lateness Window

How long to keep state for late updates:

```schema
schema transaction
  streaming
    watermark_delay: 30 seconds
    allowed_lateness: 5 minutes
    late_data_handling: update
  end
end
```

**Timeline**:
```
Watermark: T
Window closes: T (based on watermark)
Late data accepted: T to T+5min (allowed_lateness)
State discarded: T+5min (no more updates possible)
```

---

## Idle Sources

Handle sources that stop producing events:

```schema
schema transaction
  streaming
    time_field: event_timestamp
    idle_timeout: 1 minute
    idle_behavior: mark_idle
  end
end
```

**Behaviors**:
- `mark_idle`: Mark partition as idle, don't hold watermark
- `advance_to_infinity`: Advance watermark to max
- `keep_waiting`: Wait indefinitely (blocks watermark)

---

## Sparsity Hints

For wide schemas (~5000 fields), indicate which fields are typically populated:

```schema
schema enriched_auth
  streaming
    sparsity
      // Core fields (always present)
      dense: [transaction_id, card_id, amount, timestamp]

      // Customer enrichment (80% populated)
      moderate: [customer_name, credit_score, risk_tier]

      // Extended fields (10% populated)
      sparse: [fraud_score_details, manual_review_notes]
    end
  end
end
```

**Optimization**:
- Dense fields: Column-oriented storage
- Sparse fields: Map/JSON storage
- Reduces storage for wide, sparse schemas

---

## Retention Configuration

For event_log pattern schemas:

```schema
schema audit_event
  pattern event_log

  streaming
    retention
      time: 90 days
      size: 100 GB
      policy: delete_oldest
    end
  end
end
```

**Policies**:
- `delete_oldest`: Remove oldest events first
- `archive`: Move to cold storage
- `compact`: Keep latest per key

---

## Complete Example

```schema
schema auth_event
  pattern event_log
  version 3.2.1

  streaming
    // Partitioning
    key_fields: [card_id]

    // Time semantics
    time_field: event_timestamp
    time_semantics: event_time

    // Watermark configuration
    watermark_strategy: bounded_out_of_orderness
    watermark_delay: 30 seconds

    // Late data handling
    late_data_handling: side_output
    late_data_stream: late_auth_events
    allowed_lateness: 5 minutes

    // Idle handling
    idle_timeout: 1 minute
    idle_behavior: mark_idle

    // Retention
    retention
      time: 7 days
    end
  end

  identity
    transaction_id: uuid, required, unique
  end

  fields
    card_id: string, required
    event_timestamp: timestamp, required
    amount: decimal, required
    currency: currency_code, required
    merchant_id: string, required
  end
end
```

---

## Integration with L1

Streaming annotations inform L1 process behavior:

```proc
// L1 references L2 streaming configuration
process fraud_detection
  receive events from auth_events
    // L2 provides: key_fields, time_field, watermark config

  partition by card_id               // From L2 key_fields

  time by event_timestamp            // From L2 time_field
    watermark delay 30 seconds       // From L2 watermark_delay

  late data to late_auth_events      // From L2 late_data_stream

  // ... processing ...
end
```

---

## Flink/Spark Mapping

| Nexflow | Flink | Spark Structured Streaming |
|----------|-------|---------------------------|
| `key_fields` | `keyBy()` | `groupBy()` |
| `time_field` | `.assignTimestampsAndWatermarks()` | `withWatermark()` |
| `watermark_delay` | `BoundedOutOfOrdernessWatermarks` | `watermark threshold` |
| `late_data_handling: side_output` | `OutputTag` | N/A (drop or allow) |
| `allowed_lateness` | `.allowedLateness()` | `withWatermark()` |

---

## Related Documents

- [mutation-patterns.md](./mutation-patterns.md) - Data patterns
- [type-system.md](./type-system.md) - Type definitions
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - L2 overview
- [../L1-Process-Orchestration-DSL.md](../L1-Process-Orchestration-DSL.md) - L1 time semantics
