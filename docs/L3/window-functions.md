# L3: Window and Aggregate Functions

> **Source**: Native Nexflow specification
> **Status**: Complete Specification
> **Context**: Streaming CEP (Complex Event Processing)

---

## Overview

Window and aggregate functions enable stateful computations over event streams. These functions are essential for:

- **Real-time Aggregations**: Running totals, moving averages, velocity counting
- **Pattern Detection**: Sequence analysis, trend identification
- **Temporal Analysis**: Time-based groupings and comparisons
- **Session Analytics**: User session metrics and behavior analysis

**Key Concepts**:
- **Window**: A bounded subset of the stream (by time, count, or session)
- **Aggregate**: A function that reduces multiple values to a single result
- **Incremental**: State is updated incrementally as events arrive

---

## Window Types

### Time Windows

```
┌─────────────────────────────────────────────────────────────────┐
│                         Time Window Types                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TUMBLING (non-overlapping)                                     │
│  ├────────┼────────┼────────┼────────┤                          │
│  │ Window │ Window │ Window │ Window │                          │
│  │   1    │   2    │   3    │   4    │                          │
│  └────────┴────────┴────────┴────────┘                          │
│                                                                  │
│  SLIDING (overlapping)                                          │
│  ├────────────┤                                                 │
│  │   ├────────────┤                                             │
│  │   │   ├────────────┤                                         │
│  │   │   │   ├────────────┤                                     │
│  Slide interval < Window size                                   │
│                                                                  │
│  SESSION (gap-based)                                            │
│  ├───────┤   ├────────────┤   ├───┤                            │
│  │ Sess1 │   │   Sess2    │   │ 3 │                            │
│  └───────┘   └────────────┘   └───┘                            │
│           ↑                 ↑                                   │
│        gap > threshold    gap > threshold                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Window Definition Syntax

```xform
// Tumbling window: 1 hour, non-overlapping
window tumbling_1h
  type: tumbling
  size: 1 hour
end

// Sliding window: 1 hour window, slides every 5 minutes
window sliding_1h_5m
  type: sliding
  size: 1 hour
  slide: 5 minutes
end

// Session window: sessions separated by 30 minute gaps
window session_30m
  type: session
  gap: 30 minutes
end

// Count-based window: last 100 events
window last_100
  type: count
  size: 100
end

// Count-based sliding: last 100, slide by 10
window sliding_100_10
  type: count
  size: 100
  slide: 10
end
```

### Window Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `size` | duration/integer | Window size | Required |
| `slide` | duration/integer | Slide interval (sliding only) | = size |
| `gap` | duration | Session gap threshold | Required for session |
| `time_field` | field_ref | Event time field | `event_time` |
| `late_data` | policy | Late data handling | `drop` |
| `allowed_lateness` | duration | Max lateness to accept | `0` |
| `trigger` | trigger_spec | When to emit results | `on_close` |

---

## Aggregate Functions

### Basic Aggregates

| Function | Signature | Description |
|----------|-----------|-------------|
| `count()` | `window → integer` | Count of events in window |
| `count_distinct(field)` | `field, window → integer` | Count of distinct values |
| `sum(field)` | `field, window → decimal` | Sum of field values |
| `avg(field)` | `field, window → decimal` | Average of field values |
| `min(field)` | `field, window → any` | Minimum value |
| `max(field)` | `field, window → any` | Maximum value |

#### Examples

```xform
// Count transactions in last hour
txn_count = count() over tumbling_1h

// Sum of amounts in 24-hour sliding window
daily_amount = sum(amount) over sliding_24h_1h

// Average transaction size
avg_amount = avg(amount) over tumbling_1h

// Distinct merchants visited
unique_merchants = count_distinct(merchant_id) over session_30m
```

### Statistical Aggregates

| Function | Signature | Description |
|----------|-----------|-------------|
| `stddev(field)` | `field, window → decimal` | Standard deviation |
| `stddev_pop(field)` | `field, window → decimal` | Population standard deviation |
| `variance(field)` | `field, window → decimal` | Sample variance |
| `variance_pop(field)` | `field, window → decimal` | Population variance |
| `median(field)` | `field, window → decimal` | Median value |
| `percentile(field, p)` | `field, decimal, window → decimal` | Percentile (0-100) |
| `mode(field)` | `field, window → any` | Most frequent value |

#### Examples

```xform
// Standard deviation of amounts
amount_stddev = stddev(amount) over tumbling_1h

// 95th percentile transaction amount
p95_amount = percentile(amount, 95) over tumbling_24h

// Median transaction
median_amount = median(amount) over sliding_1h_15m
```

### Order-Based Aggregates

| Function | Signature | Description |
|----------|-----------|-------------|
| `first_value(field)` | `field, window → any` | First value in window |
| `last_value(field)` | `field, window → any` | Last value in window |
| `first_value_by(field, order_by)` | `field, field, window → any` | First by ordering |
| `last_value_by(field, order_by)` | `field, field, window → any` | Last by ordering |
| `nth_value(field, n)` | `field, integer, window → any` | Nth value |

#### Examples

```xform
// First transaction in session
first_txn_amount = first_value(amount) over session_30m

// Most recent transaction amount
latest_amount = last_value(amount) over tumbling_1h

// First transaction ordered by amount (smallest)
smallest_first = first_value_by(transaction_id, amount) over tumbling_1h
```

### Conditional Aggregates

| Function | Signature | Description |
|----------|-----------|-------------|
| `count_if(condition)` | `condition, window → integer` | Conditional count |
| `sum_if(field, condition)` | `field, condition, window → decimal` | Conditional sum |
| `avg_if(field, condition)` | `field, condition, window → decimal` | Conditional average |
| `min_if(field, condition)` | `field, condition, window → any` | Conditional minimum |
| `max_if(field, condition)` | `field, condition, window → any` | Conditional maximum |

#### Examples

```xform
// Count high-value transactions
high_value_count = count_if(amount > 1000) over tumbling_1h

// Sum of declined amounts
declined_total = sum_if(amount, status = "declined") over tumbling_24h

// Average of approved transactions
avg_approved = avg_if(amount, status = "approved") over sliding_1h_15m
```

### Collection Aggregates

| Function | Signature | Description |
|----------|-----------|-------------|
| `collect_list(field)` | `field, window → list<any>` | Collect all values |
| `collect_set(field)` | `field, window → set<any>` | Collect distinct values |
| `collect_list_limit(field, n)` | `field, integer, window → list<any>` | Collect up to N values |
| `string_agg(field, delim)` | `field, string, window → string` | Concatenate strings |
| `array_agg(field)` | `field, window → array<any>` | Aggregate to array |

#### Examples

```xform
// Collect all merchant IDs in session
merchants = collect_set(merchant_id) over session_30m

// Last 5 transaction IDs
recent_txns = collect_list_limit(transaction_id, 5) over sliding_1h_5m

// Concatenate countries visited
countries = string_agg(merchant_country, ", ") over tumbling_24h
```

---

## Window Navigation Functions

### Relative Position Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `lag(field, offset)` | `field, integer → any` | Value N events ago |
| `lag(field, offset, default)` | `field, integer, any → any` | With default |
| `lead(field, offset)` | `field, integer → any` | Value N events ahead |
| `lead(field, offset, default)` | `field, integer, any → any` | With default |
| `row_number()` | `→ integer` | Sequential row number |
| `rank()` | `→ integer` | Rank with gaps |
| `dense_rank()` | `→ integer` | Rank without gaps |

#### Examples

```xform
// Previous transaction amount
prev_amount = lag(amount, 1) over partition_by_card

// Amount change from previous
amount_change = amount - lag(amount, 1, amount) over partition_by_card

// Previous merchant (default to "N/A" for first)
prev_merchant = lag(merchant_id, 1, "N/A") over session_30m

// Transaction rank by amount (descending)
amount_rank = rank() over tumbling_1h order_by amount desc
```

### Running Calculations

| Function | Signature | Description |
|----------|-----------|-------------|
| `running_sum(field)` | `field, window → decimal` | Cumulative sum |
| `running_count()` | `window → integer` | Cumulative count |
| `running_avg(field)` | `field, window → decimal` | Running average |
| `running_min(field)` | `field, window → any` | Running minimum |
| `running_max(field)` | `field, window → any` | Running maximum |

#### Examples

```xform
// Running total in session
session_total = running_sum(amount) over session_30m

// Running average amount
running_avg_amount = running_avg(amount) over tumbling_1h

// Running max (track peak)
peak_amount = running_max(amount) over tumbling_24h
```

---

## Window Partitioning

### Partition By Clause

Partitioning creates independent windows per partition key:

```xform
// Window definition with partitioning
window hourly_by_card
  type: tumbling
  size: 1 hour
  partition_by: card_id
end

// Usage
card_hourly_count = count() over hourly_by_card
card_hourly_total = sum(amount) over hourly_by_card
```

### Multi-Key Partitioning

```xform
// Partition by multiple fields
window by_card_and_merchant
  type: tumbling
  size: 1 hour
  partition_by: [card_id, merchant_id]
end

// Transactions per card-merchant pair per hour
card_merchant_count = count() over by_card_and_merchant
```

### Dynamic Partitioning

```xform
// Partition by expression
window by_risk_tier
  type: tumbling
  size: 1 hour
  partition_by: customer.risk_tier
end

// Count per risk tier
tier_count = count() over by_risk_tier
```

---

## Window Ordering

### Order By Clause

Ordering affects functions like `first_value`, `last_value`, `rank`:

```xform
// Window with explicit ordering
window hourly_ordered
  type: tumbling
  size: 1 hour
  order_by: event_timestamp asc
end

// Order by multiple fields
window hourly_multi_order
  type: tumbling
  size: 1 hour
  order_by: [amount desc, event_timestamp asc]
end
```

### Usage with Ordering

```xform
// Highest amount in window
max_txn = first_value(transaction_id) over hourly_ordered order_by amount desc

// Rank by amount
amount_rank = rank() over hourly_ordered order_by amount desc
```

---

## Late Data Handling

### Late Data Policies

```xform
// Drop late data (default)
window strict_hourly
  type: tumbling
  size: 1 hour
  late_data: drop
end

// Accept late data within threshold
window lenient_hourly
  type: tumbling
  size: 1 hour
  late_data: accept
  allowed_lateness: 5 minutes
end

// Route late data to side output
window routed_hourly
  type: tumbling
  size: 1 hour
  late_data: route
  late_data_output: late_events
end

// Update results with late data
window updating_hourly
  type: tumbling
  size: 1 hour
  late_data: update
  allowed_lateness: 10 minutes
end
```

### Late Data Policies Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                    Late Data Handling Policies                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  drop    │ Discard late events silently                         │
│  accept  │ Include in next window (if within lateness)          │
│  route   │ Send to separate output for reprocessing             │
│  update  │ Re-emit updated window results                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Window Triggers

### Trigger Types

```xform
// Emit only when window closes (default)
window trigger_close
  type: tumbling
  size: 1 hour
  trigger: on_close
end

// Emit on every event (continuous)
window trigger_every
  type: tumbling
  size: 1 hour
  trigger: on_event
end

// Emit at intervals within window
window trigger_periodic
  type: tumbling
  size: 1 hour
  trigger: periodic
  trigger_interval: 5 minutes
end

// Emit when count threshold reached
window trigger_count
  type: tumbling
  size: 1 hour
  trigger: on_count
  trigger_count: 100
end

// Emit on watermark progress
window trigger_watermark
  type: tumbling
  size: 1 hour
  trigger: on_watermark
end
```

### Combined Triggers

```xform
// Emit periodically OR on close (whichever comes first)
window trigger_combined
  type: tumbling
  size: 1 hour
  trigger
    periodic: 5 minutes
    on_close: true
  end
end
```

---

## Complex Window Patterns

### Multi-Window Aggregations

```xform
// Compare short-term vs long-term velocity
transform velocity_comparison
  input
    card_id: string
    amount: decimal
    event_timestamp: timestamp
  end

  output
    short_term_count: integer
    long_term_count: integer
    velocity_ratio: decimal
  end

  windows
    short_window
      type: tumbling
      size: 1 hour
      partition_by: card_id
    end

    long_window
      type: tumbling
      size: 24 hours
      partition_by: card_id
    end
  end

  apply
    short_term_count = count() over short_window
    long_term_count = count() over long_window

    // Ratio of hourly to daily (normalized)
    expected_hourly = long_term_count / 24.0
    velocity_ratio = when expected_hourly > 0:
                       short_term_count / expected_hourly
                     otherwise: 1.0
  end
end
```

### Sessionization with Gap Detection

```xform
// Session analytics with gap tracking
transform session_analysis
  windows
    user_session
      type: session
      gap: 30 minutes
      partition_by: customer_id
    end
  end

  apply
    // Session metrics
    session_duration = datediff(
      last_value(event_timestamp) over user_session,
      first_value(event_timestamp) over user_session,
      "seconds"
    )

    session_txn_count = count() over user_session
    session_total_amount = sum(amount) over user_session

    // Average time between transactions in session
    avg_gap = when session_txn_count > 1:
                session_duration / (session_txn_count - 1)
              otherwise: 0
  end
end
```

### Rolling Comparison Windows

```xform
// Compare current hour to same hour yesterday
transform hour_over_hour
  windows
    current_hour
      type: tumbling
      size: 1 hour
      partition_by: card_id
    end

    same_hour_yesterday
      type: tumbling
      size: 1 hour
      offset: -24 hours
      partition_by: card_id
    end
  end

  apply
    current_count = count() over current_hour
    yesterday_count = count() over same_hour_yesterday

    // Change ratio
    change_ratio = when yesterday_count > 0:
                     (current_count - yesterday_count) / yesterday_count
                   otherwise: 0
  end
end
```

---

## State Management

### Window State Size

Window functions maintain state. Consider:

| Window Type | State Size | Memory Impact |
|-------------|------------|---------------|
| Tumbling Count | O(1) per aggregate | Low |
| Tumbling with collect_list | O(n) per window | High |
| Sliding | O(n × overlap) | Very High |
| Session | O(active sessions) | Variable |

### State TTL Configuration

```xform
// Configure state cleanup
window with_ttl
  type: session
  gap: 30 minutes
  state
    ttl: 2 hours  // Clean up abandoned sessions
    cleanup: periodic
    cleanup_interval: 15 minutes
  end
end
```

### State Backend Hints

```xform
// Hint for state backend selection
window large_state_window
  type: tumbling
  size: 1 hour
  state
    backend: rocksdb  // Use disk-based state for large windows
    incremental_checkpoints: true
  end
end
```

---

## Performance Considerations

### Efficient Patterns

```xform
// GOOD: Pre-aggregate before window
transform efficient_velocity
  // Filter early to reduce state
  filter: amount > 0

  apply
    count = count() over hourly_window
  end
end

// GOOD: Use approximate aggregates for high cardinality
transform approx_distinct
  apply
    // HyperLogLog-based approximate distinct count
    unique_merchants = approx_count_distinct(merchant_id) over daily_window
  end
end
```

### Patterns to Avoid

```xform
// AVOID: collect_list on high-volume streams
// BAD:
all_amounts = collect_list(amount) over daily_window  // Could be millions!

// BETTER: Use statistical aggregates
p99_amount = percentile(amount, 99) over daily_window

// AVOID: Very long windows with no partitioning
// BAD:
global_count = count() over yearly_window  // Single partition, huge state

// BETTER: Partition and roll up
daily_count = count() over daily_by_region
```

---

## Related Documents

- [transform-syntax.md](./transform-syntax.md) - Transform declaration syntax
- [builtin-functions.md](./builtin-functions.md) - Core functions
- [../L1/windowing.md](../L1/windowing.md) - L1 window specification
- [../L2/streaming-annotations.md](../L2/streaming-annotations.md) - Event time configuration
