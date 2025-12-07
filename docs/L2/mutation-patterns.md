# L2: Data Mutation Patterns

> **Source**: Adapted from ccdsl/core/CORE_DSL_SPECIFICATION.md
> **Status**: Complete Specification

---

## Overview

Data mutation patterns define **how data can change** over its lifecycle. Each pattern encapsulates:
- Allowed operations (create, update, delete)
- History tracking requirements
- Infrastructure generation rules
- Audit and compliance behaviors

Declare the pattern once; the compiler generates all operations and infrastructure.

---

## The 9 Patterns

### 1. master_data (Slowly Changing Dimension)

**Use Case**: Customer profiles, account details, entity master data

**Characteristics**:
- Mutable with full history tracking (SCD Type 2)
- Soft delete only (never hard delete)
- Audit trail for all changes

**Operations Generated**:
- `add()`, `update()`, `soft_delete()`, `retrieve()`, `get_history()`

**Example**:
```schema
schema customer
  pattern master_data

  identity
    customer_id: string, unique, required
  end

  fields
    name: string, required
    email: string
    credit_score: integer [range: 300..850]
    segment: string [values: premier, preferred, standard]
  end

  // Auto-generated: customer_history table with SCD Type 2
end
```

**Generated Infrastructure**:
```sql
CREATE TABLE customer (
  customer_id VARCHAR(100) PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255),
  credit_score INTEGER,
  segment VARCHAR(50),
  valid_from TIMESTAMP NOT NULL,
  valid_to TIMESTAMP,
  is_current BOOLEAN DEFAULT TRUE,
  deleted_at TIMESTAMP
);

CREATE TABLE customer_history (
  history_id SERIAL PRIMARY KEY,
  customer_id VARCHAR(100),
  -- all fields...
  change_type VARCHAR(20),
  changed_by VARCHAR(100),
  changed_at TIMESTAMP
);
```

---

### 2. immutable_ledger (Append-Only Financial Records)

**Use Case**: Transactions, fees, payments - immutable financial data

**Characteristics**:
- Append-only (no updates or deletes)
- Immutability enforced at database level
- Corrections via compensating transactions (reversals)

**Operations Generated**:
- `add()`, `retrieve()` ONLY (no update/delete)
- `create_reversal()` for corrections

**Example**:
```schema
schema transaction
  pattern immutable_ledger

  identity
    transaction_id: uuid, unique, required
  end

  fields
    card_id: string, required
    amount: decimal, required
    currency: currency_code, required
    transaction_date: timestamp, required
    merchant_id: string, required
    reversal_of: uuid, optional  // Links to reversed transaction
  end
end
```

**Enforcement**:
- Database triggers prevent UPDATE/DELETE
- API layer rejects modification requests
- Audit logs capture all append operations

---

### 3. versioned_configuration (Product Configurations)

**Use Case**: Product definitions, fee schedules, pricing structures

**Characteristics**:
- Immutable versions (never modify, create new version)
- Effective dating support
- Version history chain

**Operations Generated**:
- `create_version()`, `get_version()`, `get_active()`, `get_history()`

**Example**:
```schema
schema product_config
  pattern versioned_configuration

  identity
    product_code: string, required
    version: integer, required  // Composite key
  end

  fields
    product_name: string, required
    annual_fee: decimal
    interest_rate: decimal
    effective_from: date, required
    effective_until: date, optional
  end
end
```

**Version Chain**:
```
product_config (version 1) → effective 2024-01-01
product_config (version 2) → effective 2024-06-01
product_config (version 3) → effective 2024-09-01 (current)
```

---

### 4. operational_parameters (Hot-Reloadable PCF)

**Use Case**: Grace periods, thresholds, limits - operational tuning

**Characteristics**:
- Hot-reloadable (no code deployment required)
- Effective dating support
- Monthly change frequency typical
- Timeline history

**Operations Generated**:
- `set_parameter()`, `get_current()`, `set_effective()`, `get_timeline()`
- Hot reload API endpoint

**Example**:
```schema
schema fee_parameters
  pattern operational_parameters

  parameters
    grace_period_days: integer
      default: 15
      range: 10..30
      can_schedule: true
      change_frequency: monthly

    late_fee_amount: decimal
      default: 25.00
      range: 0..100
      can_schedule: true

    auto_waiver_limit: decimal
      default: 25.00
      can_schedule: false
  end
end
```

**Hot Reload**:
```bash
# Change parameter without deployment
PUT /api/parameters/fee_parameters/grace_period_days
{
  "value": 20,
  "effective_from": "2024-03-01"
}
```

---

### 5. event_log (Append-Only Event Stream)

**Use Case**: Audit events, calculation events, system events

**Characteristics**:
- Append-only (immutable events)
- Time-based retention policies
- High-performance logging
- Optimized for streaming consumption

**Operations Generated**:
- `append()`, `retrieve()`, `stream()`, `count()`
- Retention policy enforcement

**Example**:
```schema
schema calculation_event
  pattern event_log
  retention 90 days

  streaming
    key_fields: [account_id]
    time_field: event_timestamp
  end

  fields
    event_id: uuid, required
    event_timestamp: timestamp, required
    event_type: string, required
    account_id: string, required
    calculation_result: decimal
    audit_context: string
  end
end
```

**Streaming Integration**:
- Automatically published to Kafka topic
- Available for real-time consumption
- Retained for specified period

---

### 6. state_machine (Workflow State Tracking)

**Use Case**: Application status, process workflow, account lifecycle

**Characteristics**:
- Valid state transitions enforced
- State change history tracked
- Transition actions triggered
- Invalid transitions rejected

**Operations Generated**:
- `transition_to()`, `get_current_state()`, `get_state_history()`
- Transition validation

**Example**:
```schema
schema account_status
  pattern state_machine

  for_entity: account

  states: [pending, active, suspended, closed]

  initial_state: pending

  transitions
    from pending: [active, closed]
    from active: [suspended, closed]
    from suspended: [active, closed]
    from closed: []  // Terminal state
  end

  on_transition
    to active: notify_customer("account_activated")
    to suspended: notify_customer("account_suspended")
    to closed: archive_account()
  end
end
```

**Transition Enforcement**:
```java
// Attempt invalid transition
account.transitionTo("closed");  // From pending → OK
account.transitionTo("active");  // From closed → ERROR: Invalid transition
```

---

### 7. temporal_data (Effective-Dated Values)

**Use Case**: Interest rates, credit limits - values that change over time

**Characteristics**:
- Point-in-time queries supported
- Future effective dates allowed
- Timeline tracking with gaps detection

**Operations Generated**:
- `set_effective()`, `get_at_date()`, `get_current()`, `get_timeline()`

**Example**:
```schema
schema interest_rate
  pattern temporal_data

  for_entity: account

  fields
    rate_percentage: decimal, required
    effective_from: date, required
    effective_until: date, optional
  end
end
```

**Point-in-Time Queries**:
```
// What was the rate on a specific date?
rate = interest_rate.get_at_date(account_id, "2024-06-15")

// What is the current rate?
rate = interest_rate.get_current(account_id)

// Set future rate
interest_rate.set_effective(account_id, 12.5, "2024-09-01")
```

---

### 8. reference_data (Lookup Tables)

**Use Case**: Fee types, customer segments, category codes

**Characteristics**:
- Shared across system
- Referential integrity enforced
- Deprecation (not deletion) for obsolete values
- Rarely changes

**Operations Generated**:
- `register()`, `update()`, `deprecate()`, `retrieve()`
- Usage tracking

**Example**:
```schema
schema fee_type
  pattern reference_data

  entries
    late_fee:
      name: "Late Payment Fee"
      description: "Fee for payment received after due date"

    annual_fee:
      name: "Annual Membership Fee"
      description: "Yearly card membership charge"

    overlimit_fee:
      name: "Over Limit Fee"
      description: "Fee for exceeding credit limit"
      deprecated: true
      deprecated_reason: "Regulatory change - no longer charged"
  end
end
```

**Deprecation vs Deletion**:
- Never delete reference data (breaks historical records)
- Mark as deprecated with reason
- New records cannot reference deprecated values
- Existing records retain references

---

### 9. business_logic (Compiled Rules)

**Use Case**: Fee calculations, eligibility rules, validation logic

**Characteristics**:
- Compiled to native code (not interpreted)
- Zero-cost abstractions at runtime
- Compile-time type safety
- Code deployment required for changes

**Example**:
```schema
schema fee_calculation_rules
  pattern business_logic

  rule calculate_late_fee
    given
      account_balance: decimal
      days_late: integer
      is_repeat: boolean
    end

    calculate
      base_fee = when account_balance >= 5000: 40.00
                 when account_balance >= 1000: 35.00
                 otherwise: 25.00

      final_fee = when is_repeat: base_fee
                  otherwise: min(base_fee, 30.00)
    end

    return
      fee_amount: decimal
    end
  end
end
```

**Generated Code** (compiled, not interpreted):
```rust
pub fn calculate_late_fee(
    account_balance: Decimal,
    days_late: i32,
    is_repeat: bool
) -> Decimal {
    let base_fee = if account_balance >= dec!(5000) {
        dec!(40.00)
    } else if account_balance >= dec!(1000) {
        dec!(35.00)
    } else {
        dec!(25.00)
    };

    if is_repeat { base_fee } else { base_fee.min(dec!(30.00)) }
}
```

---

## Pattern Selection Guide

| Your Data... | Use Pattern |
|--------------|-------------|
| Changes often, need full history | `master_data` |
| Must never change (financial records) | `immutable_ledger` |
| Has versions with effective dates | `versioned_configuration` |
| Needs runtime changes without deploy | `operational_parameters` |
| Is an event stream with retention | `event_log` |
| Has valid state transitions | `state_machine` |
| Changes over time with point-in-time queries | `temporal_data` |
| Is shared lookup/reference data | `reference_data` |
| Is calculation/decision logic | `business_logic` |

---

## Pattern Composition

Some entities need multiple patterns:

```schema
schema product_config
  pattern versioned_configuration
  pattern temporal_data

  // Versioned AND effective-dated
end
```

---

## Related Documents

- [type-system.md](./type-system.md) - Type definitions
- [streaming-annotations.md](./streaming-annotations.md) - Streaming metadata
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - L2 overview
