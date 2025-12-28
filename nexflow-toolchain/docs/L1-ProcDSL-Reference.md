# L1: ProcDSL Language Reference

## Process Orchestration Domain-Specific Language

**Version**: 0.5.0
**Purpose**: Define streaming and batch data processing pipelines with controlled natural language syntax.

---

## Table of Contents

1. [Overview](#overview)
2. [Process Structure](#process-structure)
3. [Execution Configuration](#execution-configuration)
4. [Input Sources](#input-sources)
5. [Processing Operations](#processing-operations)
6. [Output Operations](#output-operations)
7. [Windowing & Aggregation](#windowing--aggregation)
8. [Joins & Merges](#joins--merges)
9. [Correlation & Await](#correlation--await)
10. [State Management](#state-management)
11. [Error Handling & Resilience](#error-handling--resilience)
12. [Business Date & Phases](#business-date--phases)
13. [Metrics & Observability](#metrics--observability)
14. [Expression Language](#expression-language)
15. [Complete Example](#complete-example)

---

## Overview

ProcDSL (L1) is the top layer of the Nexflow DSL stack. It orchestrates data flow between sources, transformations, rules, and sinks. Think of it as the "glue" that connects all other layers together.

```
┌─────────────────────────────────────────────────────────────┐
│                    L1: ProcDSL                              │
│         Process Orchestration & Data Flow                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐  │
│  │ Sources │ -> │Transforms│ -> │  Rules   │ -> │ Sinks  │  │
│  │ (Kafka) │    │   (L3)   │    │   (L4)   │    │(Kafka) │  │
│  └─────────┘    └──────────┘    └──────────┘    └────────┘  │
│                        V                                    │
│              ┌──────────────────┐                           │
│              │ Schemas (L2)     │                           │
│              └──────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Process Structure

### Basic Process Definition

```
process process_name
    // execution configuration (optional)
    // business date configuration (optional)
    // markers block (optional)
    // state machine declaration (optional)

    // body: receive, transform, emit statements

    // state block (optional)
    // metrics block (optional)
    // error handling block (optional)
end
```

### Import Statements

```
import ./schemas/customer.schema
import ../common/transforms.transform
import ./rules/fraud_detection.rules
```

---

## Execution Configuration

### Parallelism

```
process high_volume_processor
    parallelism 8                    // Fixed parallelism
    parallelism hint 16              // Hint for auto-scaling
```

### Partitioning

```
process partitioned_processor
    partition by customer_id         // Single field
    partition by customer_id, region // Multiple fields
```

### Time Configuration

```
process event_time_processor
    time by event_timestamp          // Event time field
        watermark delay 10 seconds   // Watermark configuration
        late data to late_events     // Late data side output
        allowed lateness 5 minutes   // Grace period
```

### Processing Mode

```
process stream_processor
    mode stream                      // Real-time streaming

process batch_processor
    mode batch                       // Batch processing

process micro_batch_processor
    mode micro_batch 30 seconds      // Micro-batch with interval
```

---

## Input Sources

### Receive Declaration

```
receive transactions
    schema raw_transaction           // L2 schema reference
    from kafka "transactions-topic"  // Kafka topic (quoted)
        group "fraud-detection-group"
        offset latest                // latest | earliest
        isolation read_committed     // Transaction isolation
        key customer_id              // Partition key field
```

### Connector Types

| Connector | Syntax | Options |
|-----------|--------|---------|
| **Kafka** | `from kafka "topic"` | group, offset, isolation, key, headers |
| **MongoDB** | `from mongodb "collection"` | filter, index |
| **Redis** | `from redis "pattern"` | - |
| **State Store** | `from state_store "name"` | filter |
| **Scheduler** | `from scheduler "cron"` | - |

### Kafka Options

```
receive events
    from kafka "events-topic"
        group "consumer-group"
        offset earliest              // Start from beginning
        isolation read_committed     // Only committed messages
        key event_id                 // Partition key
        headers: {
            source: "upstream",
            priority: input.priority
        }
```

### Projection

```
receive transactions
    from kafka "full-transactions"
    project customer_id, amount, timestamp    // Include only these fields

receive transactions
    from kafka "full-transactions"
    project except internal_id, debug_info    // Exclude these fields
```

### Filtering at Source

```
receive transactions
    from kafka "transactions"
    filter amount > 0 and status != "cancelled"
```

---

## Processing Operations

### Transform Using Reference

```
// Reference an L3 transform by name
transform using enrich_with_customer

// With parameters
transform using calculate_risk
    params: { threshold: 0.7, mode: "strict" }

// With lookup data
transform using enrich_transaction
    lookup customer_profile
        from mongodb "customers"
        key customer_id
        cache ttl 5 minutes
```

### Inline Transform

```
transform
    enriched_amount = amount * exchange_rate
    is_high_value = amount > 10000
    processed_at = now()
```

### Evaluate (L4 Rules Integration)

```
// Simple rules evaluation
evaluate using fraud_detection_rules
    output fraud_result

// With conditional actions
evaluate using credit_scoring
    when result.score < 500 then
        add_flag "high_risk"
        emit to rejected_applications
    end
```

### Route (Conditional Routing)

```
// Route using a field value
route using decision
    "approved" to approved_sink
    "rejected" to rejected_sink
    otherwise continue

// Route using conditions
route when amount > 10000
    to high_value_processing
```

### Lookup

```
lookup customer_profile
    key customer_id
    from state_store "customers"
    cache ttl 10 minutes

lookup account_details
    from mongodb "accounts"
    filter account_status = "active"
```

### Set Statement

```
set transaction.enriched = true
set processing_timestamp = now()
set risk_level = when score > 80 then "high"
                when score > 50 then "medium"
                otherwise "low"
```

### Let Statement (Local Variables)

```
let base_rate = lookup("rates", currency).rate
let adjusted_amount = amount * base_rate
set final_amount = adjusted_amount + fee
```

### If Statement

```
if amount > 10000 then
    transform using high_value_enrichment
    emit to high_value_stream
elseif amount > 1000 then
    transform using standard_enrichment
else
    emit to low_value_stream
endif
```

### Collection Operations

Instead of explicit iteration, ProcDSL uses declarative collection operations:

```
// Check if any item meets a condition
if any(order.items, item => item.quantity > 100) then
    set order.bulk_order = true
endif

// Check if all items meet a condition
if all(order.items, item => item.valid) then
    emit to valid_orders
endif

// Filter items
let high_value_items = filter(order.items, item => item.price > 1000)

// Sum values
let total = sum(order.items, item => item.quantity * item.price)

// Count items
let item_count = count(order.items, item => item.active)
```

Available collection operations: `any`, `all`, `filter`, `sum`, `count`, `first`, `last`, `min`, `max`

### Call External

```
call external fraud_api
    endpoint "https://api.fraud-service.com/check"
    timeout 5 seconds
    features: {
        amount: transaction.amount,
        customer_id: transaction.customer_id
    }
    retry 3 times
    circuit_breaker
        failure_threshold 5
        reset_timeout 30 seconds

call ml_service risk_model
    features: transaction
    timeout 2 seconds
```

### Deduplicate

```
deduplicate by transaction_id
    window 1 hour
    on_duplicate
        add_flag "duplicate_detected"
        emit to duplicates_stream
    end
```

### Validate Input

```
validate_input
    require transaction_id is not null else "Transaction ID required"
    require amount > 0 else "Amount must be positive"
    require customer_id is not null else "Customer ID required"
```

### Emit Audit Event

```
emit_audit_event "transaction_processed"
    actor system "fraud-detector"
    payload: {
        transaction_id: transaction.id,
        decision: result.decision,
        timestamp: now()
    }
```

### Branch

```
branch process_domestic
    transform using domestic_rules
    emit to domestic_output
end
```

### Parallel

```
parallel risk_checks
    timeout 10 seconds
    require_all false
    min_required 2

    branch credit_check
        call external credit_service
        emit to credit_results
    end

    branch fraud_check
        evaluate using fraud_rules
        emit to fraud_results
    end

    branch aml_check
        call external aml_service
        emit to aml_results
    end
end
```

---

## Output Operations

### Emit Declaration

```
emit to output_stream
    schema enriched_transaction
    to kafka "enriched-transactions"
        key customer_id
        headers: {
            source: "enrichment-service",
            version: "1.0"
        }
```

### Fanout Modes

```
emit to all_consumers
    broadcast                        // Send to all partitions

emit to balanced_consumers
    round_robin                      // Round-robin distribution
```

### Persist to MongoDB

```
emit to audit_log
    persist to audit_collection
        async                        // Non-blocking write
        batch size 100
        flush interval 10 seconds
        on error emit to failed_writes
```

### Error Reasons

```
emit to rejected_transactions
    reason "Validation failed: amount exceeds limit"
    preserve_state true
    include_error_context true
```

---

## Windowing & Aggregation

### Window Types

```
// Tumbling window (fixed, non-overlapping)
window tumbling 5 minutes
    key by customer_id
    aggregate
        count() as transaction_count
        sum(amount) as total_amount
        avg(amount) as average_amount
    end

// Sliding window (overlapping)
window sliding 1 hour every 5 minutes
    key by merchant_id
    aggregate
        max(amount) as max_transaction
        collect(transaction_id) as transaction_ids
    end

// Session window (gap-based)
window session gap 30 minutes
    key by session_id
    aggregate
        first(entry_page) as landing_page
        last(exit_page) as exit_page
        count() as page_views
    end
```

### Aggregate Functions

| Function | Description | Example |
|----------|-------------|---------|
| `count()` | Count of records | `count() as total` |
| `sum(field)` | Sum of field values | `sum(amount) as total_amount` |
| `avg(field)` | Average of field values | `avg(score) as avg_score` |
| `min(field)` | Minimum value | `min(timestamp) as first_seen` |
| `max(field)` | Maximum value | `max(amount) as largest` |
| `first(field)` | First value in window | `first(event_type) as first_event` |
| `last(field)` | Last value in window | `last(status) as final_status` |
| `collect(field)` | Collect all values | `collect(id) as all_ids` |

### Late Data Handling

```
window tumbling 5 minutes
    key by customer_id
    aggregate
        count() as event_count
    end
    allowed lateness 2 minutes
    late data to late_events
```

---

## Joins & Merges

### Windowed Join

```
join orders with payments
    on order_id
    within 1 hour
    type inner                       // inner | left | right | outer
```

### Merge Multiple Streams

```
merge domestic_transactions, international_transactions, wire_transfers
    into all_transactions
```

### Enrich

```
enrich using customer_profile
    on customer_id
    select name, email, risk_score
```

---

## Correlation & Await

### Await Pattern

```
await order_confirmation
    until payment_received arrives
        matching on order_id
    timeout 24 hours
        emit to unconfirmed_orders
```

### Hold Pattern

```
hold batch_items
    in batch_buffer
    keyed by batch_id
    complete when count >= 100
    timeout 5 minutes
        emit to partial_batches
```

### Completion Conditions

```
// Count-based completion
complete when count >= 100

// Marker-based completion
complete when marker received

// Custom function
complete when using batch_completeness_checker
```

---

## State Management

### State Block

```
state
    uses customer_velocity_state     // Reference external state

    local hourly_counts keyed by customer_id
        type counter
        ttl sliding 1 hour
        cleanup on_checkpoint

    local transaction_history keyed by customer_id
        type list
        ttl absolute 24 hours
        cleanup background

    buffer pending_approvals keyed by approval_id
        type priority by priority_score
        ttl 30 minutes
end
```

### State Types

| Type | Description | Use Case |
|------|-------------|----------|
| `counter` | Increment/decrement counter | Velocity tracking |
| `gauge` | Current value | Real-time metrics |
| `map` | Key-value store | Lookup cache |
| `list` | Ordered collection | Transaction history |

### Buffer Types

| Type | Description | Use Case |
|------|-------------|----------|
| `fifo` | First-in-first-out | Order processing |
| `lifo` | Last-in-first-out | Stack operations |
| `priority by field` | Priority queue | Prioritized processing |

### TTL Types

```
ttl sliding 1 hour      // Resets on access
ttl absolute 24 hours   // Fixed expiration
```

### Cleanup Strategies

```
cleanup on_checkpoint   // Clean during checkpoint
cleanup on_access       // Clean on each access
cleanup background      // Background cleanup process
```

---

## Error Handling & Resilience

### Error Block

```
on error
    transform_error skip
    lookup_error retry 3
    rule_error dead_letter rule_failures
    correlation_error dead_letter correlation_failures
end
```

### Simple Error Handler

```
on error
    log_error "Processing failed"
    emit_audit_event "processing_failure"
    retry 3 times
        delay 1 second
        backoff exponential
        max_delay 30 seconds
    then
        emit to dead_letter_queue
end
```

### Checkpoint Configuration

```
checkpoint every 5 minutes using rocksdb_backend
checkpoint every 1000 events or 1 minute to s3_checkpoint
```

### Backpressure

```
backpressure strategy block         // Block upstream
backpressure strategy drop          // Drop messages
backpressure strategy sample 0.1    // Sample 10%
    alert after 5 minutes
```

### Circuit Breaker

```
call external service
    circuit_breaker
        failure_threshold 10
        reset_timeout 1 minute
```

---

## Business Date & Phases

### Business Date Configuration

```
process eod_processor
    business_date from trading_calendar
    processing_date auto             // System clock
```

### Markers Block

```
markers
    eod_1: when market_close_signal
    eod_2: when eod_1 and trades_stream.drained
    eod_3: when eod_2 and settlements_complete
    final_eod: when eod_3 and after "18:00"
end
```

### Phase Blocks

```
// Before EOD processing
phase before eod_1
    receive live_trades
    transform using trade_enrichment
    emit to enriched_trades

    on complete signal trades_processed to downstream
end

// Between EOD markers
phase between eod_1 and eod_2
    receive pending_settlements
    evaluate using settlement_rules
    emit to settled_trades
end

// After all EOD markers
phase after eod_3
    aggregate using daily_summary
    emit to daily_reports
end

// Runs anytime
phase anytime
    receive control_messages
    transform using control_handler
end
```

### Signal Statement

```
signal batch_complete to downstream_processor
```

---

## Metrics & Observability

### Metrics Block

```
metrics
    counter transactions_processed
    counter transactions_failed
    histogram processing_latency
    gauge active_sessions
    rate transactions_per_second window 1 minute
end
```

---

## Expression Language

### Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Logical | `and`, `or`, `not` |
| Null | `is null`, `is not null` |
| Set | `in (a, b, c)`, `not in [x, y]` |

### Field Paths

```
customer.address.city              // Nested field access
items[0].name                      // Array index access
input.metadata.source              // Input prefix
```

### Literals

```
"string value"                     // String
123                                // Integer
45.67                              // Decimal
true / false                       // Boolean
null                               // Null
{ key: "value", count: 10 }        // Object
[1, 2, 3]                          // Array
```

### Function Calls

```
now()                              // Current timestamp
lookup(table, key)                 // Table lookup
contains(field, "substring")       // String contains
format("Template {0}", value)      // String formatting
```

### Ternary Expression

```
field ? expression_if_true : expression_if_false
```

### Duration Literals

```
5 seconds
10 minutes
1 hour
7 days
2 weeks
```

---

## Complete Example

```
// Import dependencies
import ./schemas/transaction.schema
import ./transforms/fraud_transforms.transform
import ./rules/fraud_rules.rules

process fraud_detection_pipeline
    parallelism 8
    partition by customer_id
    time by transaction_time
        watermark delay 10 seconds
        late data to late_transactions
    mode stream

    // Define EOD markers
    markers
        market_close: when market_close_signal
        eod_complete: when market_close and all_queues_drained
    end

    // Input from Kafka
    receive transactions
        schema raw_transaction
        from kafka "raw-transactions"
            group "fraud-detection"
            offset latest

    // Validate input
    validate_input
        require transaction_id is not null else "Missing transaction ID"
        require amount > 0 else "Invalid amount"

    // Enrich with customer data
    transform using enrich_with_customer
        lookup customer_profile
            from mongodb "customers"
            key customer_id
            cache ttl 5 minutes

    // Calculate velocity metrics
    window tumbling 1 hour
        key by customer_id
        aggregate
            count() as transactions_last_hour
            sum(amount) as amount_last_hour
        end
        state velocity_metrics

    // Apply fraud scoring
    transform using apply_fraud_scoring

    // Evaluate fraud rules
    evaluate using fraud_detection_rules
        output fraud_decision
        when fraud_decision.decision == "blocked" then
            emit to blocked_transactions
            emit_audit_event "transaction_blocked"
        end

    // Route based on decision
    route using fraud_decision.decision
        "approved" to approved_transactions
        "review" to manual_review_queue
        otherwise to approved_transactions

    // State management
    state
        uses customer_velocity_state
        local fraud_scores keyed by customer_id
            type map
            ttl sliding 24 hours
    end

    // Metrics
    metrics
        counter transactions_processed
        counter fraud_blocked
        histogram processing_latency
    end

    // Error handling
    on error
        log_error "Processing failed"
        retry 3 times
            delay 1 second
            backoff exponential
        then
            dead_letter failed_transactions
    end
end
```

---

## Quick Reference

### Keywords by Category

**Structure**: `process`, `end`, `import`

**Execution**: `parallelism`, `partition by`, `time by`, `mode`, `watermark`, `late data`

**Input**: `receive`, `from`, `schema`, `filter`, `project`

**Connectors**: `kafka`, `mongodb`, `redis`, `state_store`, `scheduler`

**Processing**: `transform`, `using`, `evaluate`, `route`, `lookup`, `set`, `let`, `if`, `call`, `deduplicate`, `validate_input`

**Collection Operations**: `any`, `all`, `filter`, `sum`, `count`, `first`, `last`, `min`, `max`

**Output**: `emit`, `to`, `broadcast`, `round_robin`, `persist`

**Windows**: `window`, `tumbling`, `sliding`, `session`, `aggregate`, `key by`

**Joins**: `join`, `with`, `on`, `within`, `merge`, `enrich`

**Correlation**: `await`, `until`, `arrives`, `matching`, `hold`, `complete when`

**State**: `state`, `uses`, `local`, `buffer`, `ttl`, `cleanup`

**Resilience**: `on error`, `retry`, `dead_letter`, `skip`, `checkpoint`, `backpressure`

**Phases**: `business_date`, `markers`, `phase`, `before`, `after`, `between`, `signal`

**Metrics**: `metrics`, `counter`, `histogram`, `gauge`, `rate`

---

*Generated from ProcDSL Grammar v0.5.0*
