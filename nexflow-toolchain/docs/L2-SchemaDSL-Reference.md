# L2: SchemaDSL Language Reference

## Schema Registry Domain-Specific Language

**Version**: 1.0.0
**Purpose**: Define data schemas with mutation patterns, type systems, streaming annotations, and schema evolution.

---

## Table of Contents

1. [Overview](#overview)
2. [Schema Structure](#schema-structure)
3. [Mutation Patterns](#mutation-patterns)
4. [Type System](#type-system)
5. [Field Qualifiers](#field-qualifiers)
6. [Identity Block](#identity-block)
7. [Streaming Configuration](#streaming-configuration)
8. [Computed Fields](#computed-fields)
9. [State Machine](#state-machine)
10. [Parameters & Entries](#parameters--entries)
11. [Constraints](#constraints)
12. [Schema Evolution](#schema-evolution)
13. [PII & Encryption](#pii--encryption)
14. [Type Aliases](#type-aliases)
15. [Complete Examples](#complete-examples)

---

## Overview

SchemaDSL (L2) defines the data contracts for your streaming applications. It provides:

- **Type Safety**: Strong typing with constraints
- **Mutation Patterns**: Predefined patterns for common data scenarios
- **Streaming Semantics**: Key fields, time semantics, watermarks
- **Schema Evolution**: Version management and compatibility
- **PII Protection**: Built-in encryption annotations

```
┌─────────────────────────────────────────────────────────────┐
│                    L2: SchemaDSL                            │
│              Schema Registry & Type System                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Mutation   │  │   Type      │  │     Streaming       │ │
│  │  Patterns   │  │   System    │  │     Semantics       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────────┐          │
│   │   L1     │   │   L3     │   │     L4       │          │
│   │ Process  │   │Transform │   │   Rules      │          │
│   └──────────┘   └──────────┘   └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## Schema Structure

### Basic Schema Definition

```
schema schema_name
    pattern pattern_type             // Optional: mutation pattern
    version 1.0.0                    // Optional: semantic version

    identity                         // Optional: identity fields
        field: type, required
    end

    streaming                        // Optional: streaming configuration
        key_fields: [field1, field2]
        time_field: timestamp_field
    end

    fields                           // Required: field definitions
        field_name: type qualifier*
    end

    // Optional blocks: computed, states, transitions, parameters, entries, constraints, migration
end
```

### Import Statements

```
import ./common/base_types.schema
import ../shared/customer.schema
```

---

## Mutation Patterns

Patterns provide semantic meaning and enforce specific behaviors for different data types.

### Available Patterns

| Pattern | Description | Requirements |
|---------|-------------|--------------|
| `master_data` | SCD Type 2 with full history | Identity block, version tracking |
| `immutable_ledger` | Append-only financial records | Identity block, immutable |
| `versioned_configuration` | Immutable versions with effective dates | Version, effective dates |
| `operational_parameters` | Hot-reloadable parameters | Parameters block |
| `event_log` | Append-only event stream | Streaming block required |
| `state_machine` | Workflow state tracking | States, transitions blocks |
| `temporal_data` | Effective-dated values | Effective date fields |
| `reference_data` | Lookup tables | Entries block |
| `business_logic` | Compiled rules | Rule block |
| `command` | Command/request pattern | - |
| `response` | Response pattern | - |
| `aggregate` | Aggregate/summary pattern | - |
| `document` | Document/output pattern | - |
| `audit_event` | Audit trail events | Immutable |

### Pattern Declaration

```
schema customer_profile
    pattern master_data              // Single pattern

schema order_event
    pattern event_log, audit_event   // Multiple patterns
```

---

## Type System

### Base Types

| Type | Description | Java Mapping |
|------|-------------|--------------|
| `string` | Text data | `String` |
| `integer` | Whole numbers | `Long` |
| `decimal` | Decimal numbers | `BigDecimal` |
| `boolean` | True/false | `Boolean` |
| `date` | Date without time | `LocalDate` |
| `timestamp` | Date with time | `Instant` |
| `uuid` | Universally unique identifier | `UUID` |
| `bytes` | Binary data | `byte[]` |
| `bizdate` | Business date (calendar-aware) | `LocalDate` |

### Collection Types

```
// List: ordered collection
items: list<order_item>

// Set: unique collection
tags: set<string>

// Map: key-value pairs
metadata: map<string, string>
properties: map<string, integer>
```

### Type Constraints

```
// Range constraint
score: integer [range: 0..100]
rate: decimal [range: 0.0..1.0]

// Length constraint
name: string [length: 1..100]
code: string [length: 3]              // Exact length
description: string [length: ..500]   // Max only

// Pattern constraint (regex)
email: string [pattern: "^[a-z]+@[a-z]+\\.[a-z]+$"]
phone: string [pattern: "^\\d{3}-\\d{3}-\\d{4}$"]

// Values constraint (enum)
status: string [values: pending, active, closed]
priority: string [values: "low", "medium", "high"]

// Precision and scale
amount: decimal [precision: 18, scale: 2]
rate: decimal [scale: 6]

// Combined constraints
percentage: decimal [range: 0..100, precision: 5, scale: 2]
```

### Inline Object Type

```
fields
    address: object {
        street: string required
        city: string required
        state: string [length: 2]
        zip: string [pattern: "^\\d{5}$"]
    }
end
```

### Schema References

```
fields
    customer: customer_profile       // Reference another schema
    orders: list<order_schema>       // List of schema references
end
```

---

## Field Qualifiers

### Basic Qualifiers

| Qualifier | Description |
|-----------|-------------|
| `required` | Field must be present |
| `optional` | Field may be absent (default) |
| `unique` | Value must be unique |
| `cannot_change` | Field is immutable after creation |
| `encrypted` | Field is encrypted at rest |

### Examples

```
fields
    id: uuid required unique
    name: string required
    email: string optional unique
    created_at: timestamp required cannot_change
    ssn: string encrypted
end
```

### Default Values

```
fields
    status: string default: "pending"
    priority: integer default: 1
    created_at: timestamp default: now()
    is_active: boolean default: true
end
```

### Deprecation

```
fields
    old_field: string deprecated: "Use new_field instead"
        removal: 2.0.0
    new_field: string required
end
```

---

## Identity Block

The identity block defines the natural key of the schema.

```
schema customer
    pattern master_data

    identity
        customer_id: uuid required
    end

    fields
        name: string required
        email: string required unique
    end
end
```

### Composite Identity

```
schema order_line
    identity
        order_id: uuid required
        line_number: integer required
    end

    fields
        product_id: uuid required
        quantity: integer required
        price: decimal required
    end
end
```

---

## Streaming Configuration

### Key Fields

```
streaming
    key_fields: [customer_id]                    // Partition key
    key_fields: [customer_id, region]            // Composite key
    key_fields: []                               // Broadcast (no key)
end
```

### Time Semantics

```
streaming
    time_field: event_timestamp
    time_semantics: event_time       // event_time | processing_time | ingestion_time
end
```

### Watermark Configuration

```
streaming
    time_field: event_timestamp
    time_semantics: event_time
    watermark_delay: 10 seconds
    watermark_strategy: bounded_out_of_orderness   // bounded_out_of_orderness | periodic | punctuated
    max_out_of_orderness: 30 seconds
    watermark_interval: 200 milliseconds
    watermark_field: custom_watermark              // Custom watermark field
end
```

### Late Data Handling

```
streaming
    late_data_handling: side_output    // side_output | drop | update
    late_data_stream: late_events
    allowed_lateness: 5 minutes
end
```

### Idle Source Configuration

```
streaming
    idle_timeout: 1 minute
    idle_behavior: mark_idle           // mark_idle | advance_to_infinity | keep_waiting
end
```

### Sparsity Declaration

```
streaming
    sparsity
        dense: [id, timestamp, amount]           // Always present
        moderate: [customer_id, status]          // Usually present
        sparse: [notes, metadata, custom_fields] // Rarely present
    end
end
```

### Retention Configuration

```
streaming
    retention
        time: 7 days
        size: 100 GB
        policy: delete_oldest          // delete_oldest | archive | compact
    end
end
```

---

## Computed Fields

Derived fields calculated from other fields.

```
schema order
    fields
        quantity: integer required
        unit_price: decimal required
        discount_percent: decimal default: 0
    end

    computed
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / 100)
        total = subtotal - discount_amount

        // Conditional computation
        priority = when total > 1000 then "high"
                   when total > 100 then "medium"
                   else "low"

        // Function call
        order_year = year(created_at)
    end
end
```

### Computed Expression Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Logical | `and`, `or`, `not` |
| Conditional | `when...then...else` |

---

## State Machine

For `state_machine` pattern schemas.

### States Definition

```
schema order_workflow
    pattern state_machine

    // Compact syntax
    states: [created, pending, confirmed, shipped, delivered, cancelled]

    // Intuitive syntax with qualifiers
    states
        created: initial
        pending
        confirmed
        shipped
        delivered: terminal
        cancelled: terminal
    end
end
```

### Transitions Definition

```
schema order_workflow
    // Original syntax
    transitions
        from created: [pending, cancelled]
        from pending: [confirmed, cancelled]
        from confirmed: [shipped, cancelled]
        from shipped: [delivered]
    end

    // Arrow syntax
    transitions
        created -> pending: submit_order
        created -> cancelled: cancel_order
        pending -> confirmed: confirm_payment
        pending -> cancelled: timeout_cancel
        confirmed -> shipped: ship_order
        shipped -> delivered: delivery_confirmed
        * -> cancelled: admin_cancel           // From any state
    end
end
```

### On Transition Actions

```
on_transition
    to confirmed: notify_customer("Order confirmed")
    to shipped: send_tracking_email("tracking_number", "carrier")
    to delivered: update_inventory("order_id")
end
```

### Entity Binding

```
for_entity: order_id

states
    draft: initial
    submitted
    completed: terminal
end
```

---

## Parameters & Entries

### Parameters Block (for `operational_parameters` pattern)

```
schema fraud_thresholds
    pattern operational_parameters

    parameters
        max_transaction_amount: decimal
            default: 10000.00
            range: 0..1000000
            can_schedule: true
            change_frequency: daily

        velocity_window_minutes: integer
            default: 60
            range: 1..1440
            can_schedule: false
    end
end
```

### Entries Block (for `reference_data` pattern)

```
schema country_codes
    pattern reference_data

    fields
        code: string [length: 2] required
        name: string required
        currency: string [length: 3]
    end

    entries
        US:
            code: "US"
            name: "United States"
            currency: "USD"

        GB:
            code: "GB"
            name: "United Kingdom"
            currency: "GBP"

        DE:
            code: "DE"
            name: "Germany"
            currency: "EUR"
            deprecated: true
            deprecated_reason: "Use EU region instead"
    end
end
```

---

## Constraints

Business rule constraints at the schema level.

```
schema transaction
    fields
        amount: decimal required
        currency: string required
        debit_account: string required
        credit_account: string required
        transaction_type: string [values: transfer, payment, withdrawal]
    end

    constraints
        amount > 0 as "Amount must be positive"
        debit_account != credit_account as "Cannot transfer to same account"
        (transaction_type == "withdrawal" and amount <= 10000) or transaction_type != "withdrawal"
            as "Withdrawal limit exceeded"
    end
end
```

---

## Schema Evolution

### Version Block

```
schema customer
    version 2.0.0
        compatibility backward       // backward | forward | full | none
        previous_version 1.5.0
        deprecated: "Version 1.x is deprecated"
            deprecated_since: "2024-01-01"
            removal_version: 3.0.0
        migration_guide: "See docs/migration/v2.md for upgrade instructions"
end
```

### Compatibility Modes

| Mode | Description | Allowed Changes |
|------|-------------|-----------------|
| `backward` | New can read old | Add optional fields, widen types |
| `forward` | Old can read new | Remove optional fields, narrow types |
| `full` | Both directions | Add/remove optional fields only |
| `none` | Breaking changes allowed | Any change |

### Migration Block

```
schema customer
    version 2.0.0
        previous_version 1.0.0

    migration
        full_name = concat(first_name, " ", last_name)
        address.country_code = lookup_country_code(address.country)
        (latitude, longitude) = geocode(address)
    end
end
```

### Retention Declaration

```
schema audit_log
    retention 7 years
end
```

### Immutable Declaration

```
schema financial_transaction
    pattern immutable_ledger
    immutable true
end
```

---

## PII & Encryption

### PII Modifier

Nexflow supports Voltage encryption profiles for PII data.

```
fields
    // Full encryption (default)
    secret_data: string pii

    // Format-preserving encryption profiles
    ssn: string required pii.ssn              // Last 4 digits clear
    card_number: string pii.pan               // First 4 + last 4 clear
    email: string pii.email                   // Format preserving
    phone: string pii.phone                   // Format preserving

    // Custom encryption profile
    custom_field: string pii.my_custom_profile
end
```

### Available PII Profiles

| Profile | Description | Clear Portion |
|---------|-------------|---------------|
| `pii` | Full encryption | None |
| `pii.ssn` | SSN format | Last 4 digits |
| `pii.pan` | Credit card | First 4 + last 4 |
| `pii.email` | Email format | Domain preserved |
| `pii.phone` | Phone format | Area code |

---

## Type Aliases

Define reusable type definitions.

```
types
    // Simple alias with constraints
    Currency: string [length: 3, values: USD, EUR, GBP, JPY]
    Percentage: decimal [range: 0..100, scale: 2]
    Email: string [pattern: "^[a-z]+@[a-z]+\\.[a-z]+$"]

    // Object alias
    Address: object
        street: string required
        city: string required
        state: string [length: 2]
        zip: string [pattern: "^\\d{5}$"]
        country: string default: "US"
    end

    // Money type
    MoneyAmount: decimal [precision: 18, scale: 2, range: 0..]
end

schema order
    fields
        currency: Currency required
        amount: MoneyAmount required
        shipping_address: Address required
        discount: Percentage optional
    end
end
```

---

## Complete Examples

### Event Log Schema

```
schema transaction_event
    pattern event_log

    version 1.0.0

    identity
        event_id: uuid required
    end

    streaming
        key_fields: [customer_id]
        time_field: event_time
        time_semantics: event_time
        watermark_delay: 10 seconds
        late_data_handling: side_output
        late_data_stream: late_transactions
        allowed_lateness: 5 minutes
    end

    fields
        event_id: uuid required
        event_time: timestamp required
        event_type: string [values: created, updated, deleted] required
        customer_id: uuid required
        account_id: uuid required
        amount: decimal [precision: 18, scale: 2] required
        currency: string [length: 3] required
        description: string [length: ..500] optional
        metadata: map<string, string> optional
    end
end
```

### Master Data Schema

```
schema customer_profile
    pattern master_data

    version 2.1.0
        compatibility backward
        previous_version 2.0.0

    identity
        customer_id: uuid required
    end

    streaming
        key_fields: [customer_id]
    end

    fields
        customer_id: uuid required cannot_change
        email: string required unique
        first_name: string required
        last_name: string required
        phone: string pii.phone optional
        ssn: string pii.ssn optional
        date_of_birth: date optional
        risk_score: integer [range: 0..1000] default: 500
        status: string [values: active, suspended, closed] default: "active"
        created_at: timestamp required cannot_change
        updated_at: timestamp required
        version: integer required default: 1
    end

    computed
        full_name = concat(first_name, " ", last_name)
        is_high_risk = risk_score > 800
        age = years_between(date_of_birth, current_date())
    end

    constraints
        risk_score >= 0 and risk_score <= 1000 as "Risk score must be between 0 and 1000"
        email matches ".*@.*\\..*" as "Invalid email format"
    end
end
```

### State Machine Schema

```
schema loan_application
    pattern state_machine

    version 1.0.0

    for_entity: application_id

    identity
        application_id: uuid required
    end

    states
        draft: initial
        submitted
        under_review
        approved
        rejected: terminal
        funded: terminal
        withdrawn: terminal
    end

    transitions
        draft -> submitted: submit_application
        submitted -> under_review: start_review
        under_review -> approved: approve
        under_review -> rejected: reject
        approved -> funded: fund_loan
        draft -> withdrawn: withdraw
        submitted -> withdrawn: withdraw
        under_review -> withdrawn: withdraw
    end

    on_transition
        to submitted: validate_application("application_id")
        to approved: send_approval_email("customer_email")
        to rejected: send_rejection_email("customer_email", "rejection_reason")
        to funded: initiate_funding("application_id", "amount")
    end

    fields
        application_id: uuid required cannot_change
        customer_id: uuid required
        amount: decimal [precision: 18, scale: 2] required
        term_months: integer [range: 12..360] required
        interest_rate: decimal [scale: 4] optional
        status: string required
        submitted_at: timestamp optional
        decision_at: timestamp optional
        funded_at: timestamp optional
        rejection_reason: string optional
    end
end
```

---

## Quick Reference

### Keywords by Category

**Structure**: `schema`, `end`, `import`, `types`

**Patterns**: `pattern`, `master_data`, `immutable_ledger`, `versioned_configuration`, `operational_parameters`, `event_log`, `state_machine`, `temporal_data`, `reference_data`, `business_logic`, `command`, `response`, `aggregate`, `document`, `audit_event`

**Version**: `version`, `compatibility`, `backward`, `forward`, `full`, `none`, `previous_version`, `deprecated`, `migration_guide`

**Blocks**: `identity`, `streaming`, `fields`, `computed`, `constraints`, `states`, `transitions`, `on_transition`, `parameters`, `entries`, `migration`

**Types**: `string`, `integer`, `decimal`, `boolean`, `date`, `timestamp`, `uuid`, `bytes`, `bizdate`, `list`, `set`, `map`, `object`

**Constraints**: `range`, `length`, `pattern`, `values`, `precision`, `scale`

**Qualifiers**: `required`, `optional`, `unique`, `cannot_change`, `encrypted`, `default`, `pii`

**Streaming**: `key_fields`, `time_field`, `time_semantics`, `event_time`, `processing_time`, `ingestion_time`, `watermark_delay`, `watermark_strategy`, `late_data_handling`, `allowed_lateness`, `idle_timeout`, `sparsity`, `retention`

**State Machine**: `states`, `initial`, `terminal`, `transitions`, `from`, `for_entity`, `on_transition`

**Expressions**: `when`, `then`, `else`, `otherwise`, `and`, `or`, `not`, `null`

---

*Generated from SchemaDSL Grammar v1.0.0*
