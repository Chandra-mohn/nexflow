# L2: Schema Registry Layer

> **Layer**: L2 Schema Registry
> **File Extension**: `.schema`
> **Owner**: Data Governance Team
> **Status**: Specification
> **Version**: 1.0.0

---

## Overview

L2 Schema Registry defines the structure of data flowing through Nexflow pipelines. It provides:

- **Data Mutation Patterns**: 9 patterns for different data lifecycle requirements
- **Type System**: Base types, constrained types, and domain types
- **Streaming Annotations**: Key fields, time semantics, watermarks
- **Schema Evolution**: Versioning and compatibility rules

---

## How L1 References L2

```proc
process authorization_enrichment
  receive events from auth_events
    schema auth_event_schema         // ← L2 reference

  partition by account_id            // L2 validates field exists

  time by event_timestamp            // L2 validates timestamp type
    watermark delay 30 seconds

  enrich using customers on card_id  // L2 validates join key type
    select customer_name, risk_tier

  emit to enriched_auths
    schema enriched_auth_schema      // ← L2 reference
end
```

---

## Data Mutation Patterns

L2 schemas declare their mutation pattern, which determines:
- What operations are allowed (CRUD)
- How history is tracked
- What infrastructure is generated

### The 9 Patterns

| Pattern | Use Case | Mutability | History |
|---------|----------|------------|---------|
| `master_data` | Customer profiles, entities | Mutable | Full SCD Type 2 |
| `immutable_ledger` | Transactions, fees | Append-only | Immutable |
| `versioned_configuration` | Product configs | Immutable versions | Version chain |
| `operational_parameters` | Grace periods, limits | Hot-reloadable | Timeline |
| `event_log` | Audit events, calculations | Append-only | Time-based retention |
| `state_machine` | Workflow states | State transitions | Transition log |
| `temporal_data` | Interest rates, limits | Effective-dated | Point-in-time |
| `reference_data` | Fee types, categories | Rarely changes | Deprecation only |
| `business_logic` | Rules, calculations | Code deployment | Code versioning |

See: [L2/mutation-patterns.md](./L2/mutation-patterns.md) for complete specification.

---

## Type System

### Base Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text values | `"John Doe"` |
| `integer` | Whole numbers | `42`, `-100` |
| `decimal` | Precise decimals | `3.14159`, `1000.50` |
| `boolean` | True/false | `true`, `false` |
| `date` | Calendar date | `2024-01-15` |
| `timestamp` | Date + time + zone | `2024-01-15T10:30:00Z` |
| `uuid` | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |

### Constrained Types

```schema
credit_score: integer [range: 300..850]
account_number: string [length: 16]
email: string [pattern: "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"]
percentage: decimal [range: 0..100]
```

### Domain Types

```schema
currency_code: string [values: USD, EUR, GBP, JPY]
country_code: string [pattern: "^[A-Z]{2}$"]
mcc_code: string [length: 4, pattern: "^[0-9]+$"]
card_number: string [length: 16..19]
```

See: [L2/type-system.md](./L2/type-system.md) for complete specification.

---

## Basic Schema Syntax

```schema
schema auth_event_schema
  pattern event_log
  version 3.2.1

  // Identity fields
  identity
    transaction_id: uuid, required, unique
  end

  // Streaming annotations
  streaming
    key_fields: [card_id]
    time_field: event_timestamp
    watermark_delay: 30 seconds
  end

  // Field definitions
  fields
    card_id: string, required
    event_timestamp: timestamp, required
    amount: decimal, required
    currency: currency_code, required
    merchant_id: string, required
  end

  // Nested structures
  merchant: object
    name: string
    category: mcc_code
    location: object
      city: string
      country: country_code
    end
  end
end
```

---

## Streaming Annotations

For stream processing, schemas need additional metadata:

### Key Fields (Partitioning)

```schema
streaming
  key_fields: [account_id]           // Single key
  key_fields: [card_id, merchant_id] // Composite key
end
```

### Time Semantics

```schema
streaming
  time_field: event_timestamp        // Event time field
  watermark_delay: 30 seconds        // Watermark configuration
  allowed_lateness: 5 minutes        // Late arrival window
end
```

### Late Data Handling

```schema
streaming
  late_data_handling: side_output    // Send to separate stream
  late_data_handling: drop           // Discard late records
  late_data_handling: update         // Update existing results
end
```

See: [L2/streaming-annotations.md](./L2/streaming-annotations.md) for complete specification.

---

## Schema Evolution

### Versioning

```schema
schema customer_schema
  version 2.0.0                      // Semantic versioning
  compatibility backward             // Backward compatible changes only
  previous_version 1.5.0
end
```

### Compatibility Modes

| Mode | Adding Fields | Removing Fields | Changing Types |
|------|--------------|-----------------|----------------|
| `backward` | OK (optional) | Not allowed | Not allowed |
| `forward` | Not allowed | OK (optional) | Not allowed |
| `full` | OK (optional) | OK (optional) | Not allowed |
| `none` | Any change | Any change | Any change |

See: [L2/schema-evolution.md](./L2/schema-evolution.md) for complete specification.

---

## File Structure

```
project/
├── schemas/
│   ├── customer.schema              # Master data
│   ├── transaction.schema           # Immutable ledger
│   ├── card_account.schema          # State machine
│   ├── auth_event.schema            # Event log
│   └── completion_event.schema      # System schema for transaction confirmations
```

---

## System Schemas

### Completion Event Schema

The `completion_event_v1` schema is a **system-provided schema** used for transaction confirmation in async processing pipelines. It's automatically available without explicit definition.

```schema
schema completion_event_v1
  pattern event_log
  version 1.0.0

  // Core completion fields (always populated)
  identity
    transaction_id: uuid, required, unique
  end

  streaming
    key_fields: [correlation_id]
    time_field: timestamp
  end

  fields
    // Correlation
    correlation_id: string, required       // Links to original request

    // Transaction outcome
    transaction_id: uuid, required         // System-generated ID
    status: enum [COMMITTED, FAILED], required

    // Target system info
    target_system: string, required        // e.g., "mongodb", "postgresql"
    target_id: string                      // ID in target system (e.g., MongoDB _id)

    // Timing
    timestamp: timestamp, required         // When completion occurred
    processing_duration_ms: integer        // Time from receive to commit

    // Included fields (from L1 `include` clause)
    included_fields: map<string, any>      // Dynamic fields from source record

    // Error details (populated on failure)
    error_code: string                     // Error classification
    error_message: string                  // Human-readable error
    retry_count: integer                   // Number of retries attempted

    // Metadata
    process_name: string                   // L1 process that emitted this
    source_topic: string                   // Original input topic
  end
end
```

#### Usage in L1

```proc
// Automatic: uses completion_event_v1
on commit
    emit completion to transaction_completions
        correlation correlation_id
        include account_id, customer_id

// Explicit schema override (optional)
on commit
    emit completion to transaction_completions
        schema custom_completion_v1        // Custom schema must extend completion_event_v1
        correlation correlation_id
```

#### Completion Event Example

```json
{
  "correlation_id": "uuid-123-from-api",
  "transaction_id": "txn-456-generated",
  "status": "COMMITTED",
  "target_system": "mongodb",
  "target_id": "507f1f77bcf86cd799439011",
  "timestamp": "2025-12-01T10:30:00.000Z",
  "processing_duration_ms": 245,
  "included_fields": {
    "account_id": "ACC001",
    "customer_id": "C456",
    "status": "ACTIVE"
  },
  "process_name": "account_creation",
  "source_topic": "account_requests"
}
```

---

## Example Schemas

Complete working examples demonstrating pattern composition:

| Example | Patterns Used | Description |
|---------|---------------|-------------|
| [customer.schema](./L2/examples/customer.schema) | `master_data` | Customer profiles with SCD Type 2 history, nested objects, validations |
| [transaction.schema](./L2/examples/transaction.schema) | `immutable_ledger` + `event_log` | Financial transactions with streaming annotations, fraud indicators |
| [card_account.schema](./L2/examples/card_account.schema) | `state_machine` + `temporal_data` | Account lifecycle states, time-varying credit limits and APRs |

Each example includes:
- Complete field definitions with constraints
- Nested object structures
- Generated operations documentation
- Infrastructure generation comments

---

## Detailed Specifications

| Topic | Document |
|-------|----------|
| Mutation patterns | [L2/mutation-patterns.md](./L2/mutation-patterns.md) |
| Type system | [L2/type-system.md](./L2/type-system.md) |
| Streaming annotations | [L2/streaming-annotations.md](./L2/streaming-annotations.md) |
| Schema evolution | [L2/schema-evolution.md](./L2/schema-evolution.md) |
| Examples | [L2/examples/](./L2/examples/) |

---

## Integration with Other Layers

### L1 → L2 (Schema Resolution)

```proc
receive events from auth_events
  schema auth_event_schema           // L2 resolves full schema
```

### L2 → L3 (Transform Validation)

L3 transforms declare input/output schemas:
```xform
transform normalize_amount
  input: auth_event_schema
  output: normalized_event_schema
end
```

### L2 → L4 (Rule Field Validation)

L4 rules reference schema fields:
```rules
decision_table fraud_screening
  given:
    - amount: decimal                // Validated against schema
    - risk_tier: string
```

### L2 → L5 (Physical Mapping)

L5 maps logical schemas to physical storage:
```yaml
schemas:
  auth_event_schema:
    kafka:
      topic: prod.auth.events.v3
      format: avro
      schema_registry: confluent
```

---

## Source Attribution

This specification integrates patterns from:
- **ccdsl**: 9 data mutation patterns, type system (~70% reusable)
- **Native Nexflow**: Streaming annotations, schema evolution

See: [ccdsl-nexflow-feature-matrix.md](./ccdsl-nexflow-feature-matrix.md)

---

## Related Documents

- [L1-Process-Orchestration-DSL.md](./L1-Process-Orchestration-DSL.md) - How L1 references L2
- [L3-Transform-Catalog.md](./L3-Transform-Catalog.md) - Transform input/output schemas
- [L4-Business-Rules.md](./L4-Business-Rules.md) - Rule field validation
- [L5-Infrastructure-Binding.md](./L5-Infrastructure-Binding.md) - Physical schema mapping

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-01-XX | - | Complete specification from ccdsl |
| 0.1.0 | 2025-01-XX | - | Placeholder created |
