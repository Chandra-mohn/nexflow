# L1: Process Orchestration DSL Specification

> **Layer**: L1 - The Railroad
> **Status**: Draft
> **Version**: 0.1.0
> **Last Updated**: 2025-01-XX

---

## 1. Overview

### 1.1 Purpose

L1 is the **Process Orchestration DSL** — the "railroad" that defines how data flows through the system. It specifies:

- **Data Flow**: Sources, sinks, routing
- **Execution Semantics**: Parallelism, time model, windowing
- **State Management**: Shared and local state declarations
- **Resilience**: Error handling, checkpointing, back-pressure
- **Composition**: Joins, fan-out, fan-in, DAG topology

### 1.2 Design Philosophy

| Principle | Description |
|-----------|-------------|
| **Railroad-Pure** | L1 orchestrates; it does NOT define business logic |
| **Controlled Natural Language** | Restricted vocabulary, defined grammar, unambiguous parsing |
| **Verb-First** | Actions lead: `receive`, `emit`, `transform`, `route` |
| **Reference-Based** | Schemas, transforms, rules referenced by name (defined in L2-L4) |
| **Infrastructure-Agnostic** | Logical names; physical binding happens at L5 |

### 1.3 What L1 Does NOT Own

| Concept | Owner | L1 Role |
|---------|-------|---------|
| Field definitions | L2 Schema Registry | References by name |
| Transform logic | L3 Transform Catalog | Invokes by name |
| Business rules | L4 Business Rules | Delegates routing decisions |
| Physical infrastructure | L5 Infrastructure Binding | Uses logical names |

> **Note**: Business domain concepts (e.g., "credit score", "fraud threshold", "APR calculation")
> never appear directly in L1. L1 uses abstract references like `transform using fraud_check`
> rather than embedding domain logic. The domain semantics live in L2-L4.

---

## 2. Language Design

### 2.1 Tooling

- **Parser Generator**: ANTLR4
- **Target Languages**: Java (primary), TypeScript (tooling)
- **Output**: Abstract Syntax Tree (AST) for compilation to Flink/Spark

### 2.2 Lexical Conventions

#### Comments
```
// Single line comment only
// Multi-line comments use consecutive single-line comments
// like this
```

#### Identifiers
- Process names: `snake_case` (e.g., `authorization_enrichment`)
- References: `snake_case` (e.g., `auth_request_v3`, `fraud_detection_v2`)
- Keywords: lowercase (e.g., `process`, `receive`, `emit`)

#### Literals
- Numbers: `128`, `5.0`, `0.7`
- Durations: `5 seconds`, `1 hour`, `30 minutes`, `5m`, `1h`
- Strings: `"quoted strings"` (for rare cases)

#### Reserved Keywords
```
// Structure
process, end

// Input/Output
receive, from, emit, to, fanout, broadcast, round_robin, schema, project, except

// Processing
transform, enrich, route, aggregate, using, on, select

// Execution
parallelism, hint, partition, by, mode, stream, batch, micro_batch

// Time
time, watermark, delay, late, data, allowed, lateness

// Window
window, tumbling, sliding, session, gap, every

// Join
join, with, within, type, inner, left, right, outer, merge

// State
state, uses, local, keyed, counter, gauge, map, list

// Correlation (await/hold)
await, until, arrives, matching, timeout, hold, buffer, store, in, match

// Resilience
on, error, failure, dead_letter, skip, retry, checkpoint, when, slow,
strategy, block, drop, sample, alert, after
```

### 2.3 Program Structure

```
// A Nexflow file contains one or more process definitions

process <name>
    <declarations>
    <data_flow>
    <state_block>
    <resilience_block>
end

process <name>
    ...
end
```

---

## 3. Process Definition

### 3.1 Basic Structure

```
process <identifier>

    // Execution semantics (optional, has defaults)
    <execution_block>

    // Data flow (required)
    <input_block>
    <processing_block>
    <output_block>

    // State management (optional)
    <state_block>

    // Resilience (optional, has defaults)
    <resilience_block>

end
```

### 3.2 Execution Block

Defines HOW the process executes.

```
// Parallelism
parallelism <integer>                    // Explicit parallelism
parallelism hint <integer>               // Compiler can adjust
partition by <field_path>                // Partition key for parallel processing

// Time semantics
time by <field_path>                     // Event time field
    watermark delay <duration>           // Max out-of-order delay
    late data to <stream_name>           // Side output for late records
    allowed lateness <duration>          // Window lateness tolerance

// Processing mode
mode stream                              // Default: continuous streaming
mode batch                               // Batch processing (Spark)
mode micro_batch <duration>              // Micro-batch with interval
```

#### Defaults
| Property | Default Value |
|----------|---------------|
| `parallelism` | Inferred from source partitions |
| `partition by` | None (round-robin) |
| `time by` | Processing time |
| `watermark delay` | 0 (no delay) |
| `allowed lateness` | 0 (no late data) |
| `mode` | `stream` |

### 3.3 Input Block

Defines WHERE data comes from.

```
// Single source
receive from <source_name>
    schema <schema_ref>

// Multiple sources (for joins)
receive <alias> from <source_name>
    schema <schema_ref>

receive <alias> from <source_name>
    schema <schema_ref>
```

#### Source Name Resolution
- `auth_events` → Resolved to physical topic/table by L5
- Supports logical naming only; no physical addresses in L1

### 3.4 Processing Block

Defines WHAT operations happen.

#### Enrichment
```
enrich using <lookup_ref>
    on <field_path>                      // Join key
    select <field_list>                  // Optional: specific fields
```

#### Transformation
```
transform using <transform_block_ref>    // Reference to L3 catalog
```

#### Routing
```
route using <rule_set_ref>               // L4 decides routing outcome
```

#### Aggregation (windowed)
```
aggregate using <aggregation_ref>        // L4 defines aggregation logic
```

### 3.5 Window Block

For windowed operations (aggregations, joins).

```
window tumbling <duration>
    allowed lateness <duration>
    late data to <stream_name>

window sliding <size> every <slide>
    allowed lateness <duration>

window session gap <duration>
    allowed lateness <duration>
```

### 3.6 Join Block

For multi-stream processes with time-bounded correlation.

```
join <alias1> with <alias2>
    on <field_path>                      // Join key
    within <duration>                    // Time bound for streaming joins
    type inner                           // inner | left | right | outer
```

### 3.7 Correlation Block (Await/Hold)

For **indefinite waiting** — when records must wait for correlated events without a fixed time bound. This differs from joins (time-bounded) and windows (time-based aggregation).

#### Use Cases
| Scenario | Why Not Join/Window |
|----------|---------------------|
| Auth waits for settlement (could be days) | Join `within` would timeout |
| Order waits for all line items | Unknown how many, no time bound |
| Event waits for "complete" signal | Indefinite until signal arrives |

#### Syntax Option A: `await` (Event-Driven)
```
await <event_type>
    until <trigger_event> arrives
        matching on <field_path>
    timeout <duration>
        <timeout_action>
```

**Example:**
```
process settlement_matching

    receive auths from auth_events
    receive settlements from settlement_events

    await auths
        until settlement arrives
            matching on transaction_id
        timeout 7 days
            emit to unmatched_auths

    // When matched, both records available as 'auth' and 'settlement'
    transform using settlement_reconciliation
    emit to reconciled_transactions

end
```

#### Syntax Option B: `hold` (Buffer-Based)
```
hold <alias> in <buffer_name>
    keyed by <field_path>
    timeout <duration>
        <timeout_action>

match from <buffer_name>
    on <field_path>
```

**Example:**
```
process settlement_matching

    hold pending_auths
        keyed by transaction_id
        timeout 7 days
            emit to unmatched_auths

    receive auth from auth_events
        store in pending_auths

    receive settlement from settlement_events
        match from pending_auths on transaction_id

    // When matched
    transform using settlement_reconciliation
    emit to reconciled_transactions

end
```

#### Semantic Differences

| Aspect | `await` | `hold` |
|--------|---------|--------|
| Mental model | "Wait for something" | "Store, then retrieve" |
| Control flow | Declarative correlation | Explicit buffer operations |
| Multiple matches | Implicit (first match) | Explicit (can match multiple) |
| State visibility | Hidden | Named buffer (queryable?) |

#### Correlation vs Join vs Window

| Feature | `join within` | `window` | `await`/`hold` |
|---------|---------------|----------|----------------|
| Time bound | Required | Required | Optional (timeout) |
| Cardinality | 1:1 or 1:N in window | N records aggregated | 1:1 correlation |
| Waiting | Up to `within` duration | Until window closes | Until match or timeout |
| Use case | Enrich with recent data | Aggregate over time | Match across time |

### 3.8 Output Block

Defines WHERE data goes.

```
// Single output
emit to <sink_name>
    schema <schema_ref>

// Routed output (routing decision made by L4)
route using <rule_set_ref>
    // Routes defined in L4 rule set, L1 just executes

// Fan-out
emit to <sink_name>
    fanout broadcast                     // All downstream get all records
    fanout round_robin                   // Load balanced distribution
```

### 3.9 State Block

Declares state dependencies.

```
state
    uses <shared_state_ref>              // External shared state
    uses <shared_state_ref>

    local <name> keyed by <field_path>   // Stage-local state
        type counter                     // counter | gauge | map | list
```

### 3.10 Completion Event Block

Declares completion event emission for transaction confirmation. This enables the **Flink Sink Callback** pattern where completion events are emitted after successful writes to downstream systems.

```
on commit
    emit completion to <completion_topic>
        correlation <field_path>                 // Required: links request to response
        include <field_list>                     // Optional: additional fields in completion event

on commit failure
    emit completion to <failure_topic>
        correlation <field_path>
        include <field_list>
```

#### Completion Event Fields

| Field | Type | Description |
|-------|------|-------------|
| `correlation` | Required | Field used to correlate completion with original request |
| `include` | Optional | Additional fields from the processed record to include |
| `schema` | Optional | Override completion event schema (defaults to `completion_event_v1`) |

#### Completion Semantics

| Trigger | Description |
|---------|-------------|
| `on commit` | Emitted after Flink sink confirms successful write |
| `on commit failure` | Emitted when sink write fails after all retries |

#### Generated Completion Event

When `on commit` triggers, the system generates a completion event with:
- `correlation_id`: Value from the specified correlation field
- `transaction_id`: System-generated unique identifier
- `status`: `COMMITTED` or `FAILED`
- `target_system`: Sink type (e.g., `mongodb`, `postgresql`)
- `target_id`: ID in target system (e.g., MongoDB `_id`)
- `timestamp`: Completion timestamp
- `included_fields`: Any fields specified in `include` clause
- `error_details`: Populated on failure

### 3.11 Resilience Block

Defines error handling and recovery.

```
on error
    transform failure dead_letter <dlq_name>
    lookup failure    skip                        // skip | retry <n> | dead_letter
    rule failure      dead_letter <dlq_name>

checkpoint every <duration>
    to <checkpoint_location>

when slow
    strategy block                       // block | drop | sample <rate>
    alert after <duration>
```

---

## 4. Complete Examples

### 4.1 Simple Streaming Process

```
process authorization_enrichment

    // Execution
    parallelism 128
    partition by account_id

    time by event_timestamp
        watermark delay 5 seconds
        late data to late_auth_events
        allowed lateness 1 hour

    // Input
    receive from auth_events
        schema auth_request_v3

    // Processing
    enrich using customer_lookup
        on account_id

    transform using auth_enrichment_block

    route using fraud_detection_v2

    // State
    state
        uses account_balances
        local daily_counts keyed by account_id
            type counter

    // Resilience
    on error
        transform failure dead_letter transform_errors
        lookup failure    skip
        rule failure      dead_letter rule_errors

    checkpoint every 5 minutes
        to auth_checkpoints

    when slow
        strategy block
        alert after 30 seconds

end
```

### 4.2 Windowed Aggregation Process

```
process hourly_transaction_summary

    parallelism 64
    partition by account_id

    time by transaction_timestamp
        watermark delay 10 seconds

    receive from transaction_events
        schema transaction_v2

    window tumbling 1 hour
        allowed lateness 15 minutes
        late data to late_transactions

    aggregate using hourly_summary_rules

    emit to hourly_summaries
        schema hourly_summary_v1

    checkpoint every 5 minutes
        to hourly_checkpoints

end
```

### 4.3 Stream Join Process

```
process transaction_with_merchant

    parallelism 64

    time by event_time
        watermark delay 5 seconds

    receive transactions from transaction_events
        schema transaction_v2

    receive merchants from merchant_updates
        schema merchant_v1

    join transactions with merchants
        on merchant_id
        within 1 hour
        type left

    transform using merchant_enrichment_block

    emit to enriched_transactions
        schema enriched_transaction_v1

    checkpoint every 5 minutes
        to merchant_join_checkpoints

end
```

### 4.4 Batch Process

```
process daily_reconciliation

    mode batch

    receive from daily_transactions
        schema transaction_v2

    transform using reconciliation_block

    aggregate using daily_summary_rules

    emit to daily_summaries
        schema daily_summary_v1

end
```

### 4.5 Fan-Out Process

```
process event_distribution

    parallelism 32

    receive from incoming_events
        schema event_v1

    route using event_router_rules

    // Routing decisions made by L4 rule set
    // L4 defines: event_type=A to stream_a, event_type=B to stream_b, etc.

end
```

### 4.6 Correlation Process (Await)

```
process settlement_matching

    parallelism 64
    partition by transaction_id

    time by event_timestamp
        watermark delay 1 minute

    receive auths from auth_events
        schema auth_v3

    receive settlements from settlement_events
        schema settlement_v2

    await auths
        until settlement arrives
            matching on transaction_id
        timeout 7 days
            emit to unmatched_auths

    transform using settlement_reconciliation_block

    emit to reconciled_transactions
        schema reconciled_v1

    state
        uses pending_correlations

    checkpoint every 5 minutes
        to settlement_checkpoints

end
```

### 4.7 Correlation Process (Hold/Buffer)

```
process order_assembly

    parallelism 32
    partition by order_id

    hold pending_orders
        keyed by order_id
        timeout 24 hours
            emit to incomplete_orders

    receive order_header from order_headers
        schema order_header_v1
        store in pending_orders

    receive line_item from order_lines
        schema order_line_v1
        match from pending_orders on order_id

    // When order_header and line_items matched
    aggregate using order_assembly_rules

    emit to complete_orders
        schema complete_order_v1

end
```

### 4.8 Transaction with Completion Confirmation

This example demonstrates the **Flink Sink Callback** pattern for async transaction confirmation. The API sends a create account request with a `correlation_id`, and the completion event confirms when MongoDB write succeeds.

```
process account_creation

    parallelism 64
    partition by correlation_id

    time by request_timestamp
        watermark delay 5 seconds

    // Input from API gateway via Kafka
    receive from account_requests
        schema account_request_v1

    // Enrich with customer data
    enrich using customer_lookup
        on customer_id
        select credit_tier, risk_score

    // Apply business rules for account setup
    transform using account_setup_block

    // Persist to MongoDB (Flink MongoDB Sink)
    emit to accounts_collection
        schema account_v1

    // ⭐ Completion event: confirms successful MongoDB write
    on commit
        emit completion to transaction_completions
            correlation correlation_id
            include account_id, customer_id, status

    // ⭐ Failure event: notifies when write fails
    on commit failure
        emit completion to transaction_failures
            correlation correlation_id
            include error_code, retry_count

    // State for deduplication
    state
        local processed_requests keyed by correlation_id
            type map
            ttl absolute 24 hours

    // Resilience
    on error
        transform failure dead_letter account_dlq
        lookup failure    retry 3

    checkpoint every 5 minutes
        to account_checkpoints

end
```

**Flow Sequence:**
```
1. API Gateway → Kafka (account_requests topic)
   Payload: { correlation_id: "uuid-123", customer_id: "C456", ... }

2. Flink Process → Enrichment → Transform → MongoDB Sink

3. MongoDB Sink Callback (on success) → Kafka (transaction_completions topic)
   Payload: {
     correlation_id: "uuid-123",
     transaction_id: "txn-789",
     status: "COMMITTED",
     target_system: "mongodb",
     target_id: "ObjectId(...)",
     account_id: "A001",
     customer_id: "C456",
     timestamp: "2025-12-01T10:30:00Z"
   }

4. API Gateway ← Kafka Consumer (transaction_completions topic)
   Matches correlation_id → Returns response to waiting client
```

---

## 5. Semantic Rules

### 5.1 Process Validation

| Rule | Description |
|------|-------------|
| Unique names | Process names must be unique within a file |
| Required input | Every process must have at least one `receive` |
| Required output | Every process must have `emit`, `route using`, or `aggregate` |
| Schema consistency | Input/output schemas must be compatible with transforms |
| State scope | `uses` references must exist in shared state registry |
| Join requirements | Joins require exactly two aliased inputs |

### 5.2 Execution Constraints

| Rule | Description |
|------|-------------|
| Window requires aggregation | `window` block must be followed by `aggregate` |
| Join requires within | Stream-stream joins require `within` time bound |
| Batch mode restrictions | Batch processes cannot use `watermark`, `window`, or `await` |
| Partition key presence | `partition by` field must exist in input schema |
| Correlation requires timeout | `await` and `hold` must specify `timeout` |
| Buffer keying required | `hold` must specify `keyed by` |
| Await requires two sources | `await` requires exactly two `receive` blocks |
| Completion requires correlation | `on commit` must specify `correlation` field |
| Completion requires emit | `on commit` requires at least one `emit to` in the process |
| Correlation field existence | `correlation` field must exist in output schema |

### 5.3 Reference Resolution

| Reference Type | Resolved At | Resolver |
|----------------|-------------|----------|
| Schema refs | Compile time | L2 Schema Registry |
| Transform refs | Compile time | L3 Transform Catalog |
| Rule refs | Compile time | L4 Business Rules |
| Stream/sink refs | Deploy time | L5 Infrastructure Binding |
| State refs | Compile time | State Registry |
| Completion topic refs | Deploy time | L5 Infrastructure Binding |
| Completion schema | Compile time | L2 Schema Registry (defaults to `completion_event_v1`) |

---

## 6. ANTLR4 Grammar

The formal grammar is maintained in a separate file for tooling integration:

**File**: [`ProcDSL.g4`](./grammar/ProcDSL.g4)

The grammar file is the authoritative source for parsing. This specification describes the language semantics; the grammar defines the syntax.

## 6.5 Compilation

L1 processes compile to executable runtime code through the **L6 Compilation Pipeline**:

```
L1 DSL → Lexer/Parser → AST → Semantic Analysis → IR → Code Generation
                                    │                        │
                                    ▼                        ▼
                              L2/L3/L4 refs            Flink SQL + UDFs
                              resolved                 Spark jobs
```

**See**: [`L6-Compilation-Pipeline.md`](./L6-Compilation-Pipeline.md) for:
- Complete compilation phases
- AST structure and validation
- Code generation for Flink SQL and Spark
- UDF generation from L4 business rules
- Deployment artifact structure

**See**: [`L1-Runtime-Semantics.md`](./L1-Runtime-Semantics.md) for:
- Stage lifecycle state machine
- Processing semantics (exactly-once, ordering)
- State management internals
- Correlation (await/hold) implementation
- Error handling and checkpointing

### 6.1 Grammar Organization

| Section | Purpose |
|---------|---------|
| Parser Rules | Structure, blocks, declarations |
| Lexer Rules | Tokens, literals, comments |
| Fragments | Reusable character patterns |

### 6.2 Key Grammar Features

- **Whitespace-insensitive** (indentation is style, not syntax)
- **Single-line comments** (`//` only)
- **Keyword-based actions** — no special operators needed for routing or error handling
- **Duration literals** support both long (`5 seconds`) and short (`5s`) forms

---

## 7. Open Questions

### 7.1 Resolved

| Question | Decision |
|----------|----------|
| YAML vs custom language | Custom language with ANTLR4 |
| Business rules in L1 | No - L1 delegates via `route using` |
| Routing conditions | L4 owns conditions; L1 routes by outcome |

### 7.2 Pending

| Question | Options | Notes |
|----------|---------|-------|
| Resource hints | In L1 vs L5 only | Memory, CPU declarations |
| Metrics declaration | Explicit in L1 vs auto-generated | Custom metric names |
| Process dependencies | Implicit via streams vs explicit DAG | `depends on` keyword? |
| Process versioning | In-language vs external | `version 2.0` keyword? |

---

## 8. Appendix

### 8.1 Keyword Quick Reference

| Category | Keywords |
|----------|----------|
| Structure | `process`, `end` |
| Input | `receive`, `from`, `schema` |
| Output | `emit`, `to`, `fanout`, `broadcast`, `round_robin` |
| Processing | `transform`, `enrich`, `route`, `aggregate`, `using`, `on`, `select` |
| Execution | `parallelism`, `hint`, `partition`, `by`, `mode`, `stream`, `batch`, `micro_batch` |
| Time | `time`, `watermark`, `delay`, `late`, `data`, `allowed`, `lateness` |
| Window | `window`, `tumbling`, `sliding`, `session`, `gap`, `every` |
| Join | `join`, `with`, `within`, `type`, `inner`, `left`, `right`, `outer`, `merge` |
| Correlation | `await`, `until`, `arrives`, `matching`, `timeout`, `hold`, `buffer`, `store`, `in`, `match` |
| Completion | `on`, `commit`, `failure`, `completion`, `correlation`, `include` |
| State | `state`, `uses`, `local`, `keyed`, `counter`, `gauge`, `map`, `list` |
| Resilience | `on`, `error`, `failure`, `dead_letter`, `skip`, `retry`, `checkpoint`, `when`, `slow`, `strategy`, `block`, `drop`, `sample`, `alert`, `after` |

### 8.2 Duration Formats

| Format | Example | Meaning |
|--------|---------|---------|
| Long | `5 seconds` | 5 seconds |
| Long plural | `30 minutes` | 30 minutes |
| Short | `5s`, `30m`, `1h`, `7d` | Abbreviated |

### 8.3 Error Handling Strategies

| Strategy | Behavior |
|----------|----------|
| `dead_letter <name>` | Send failed record to dead letter queue |
| `skip` | Drop the record, continue processing |
| `retry <n>` | Retry operation n times before failing |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Initial draft from brainstorming |
