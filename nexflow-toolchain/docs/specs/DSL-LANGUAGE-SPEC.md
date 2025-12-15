# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Nexflow DSL Language Specifications

## Overview

Nexflow consists of four Domain-Specific Languages (DSLs), each addressing a specific layer of data pipeline development:

| Layer | DSL | Extension | Purpose |
|-------|-----|-----------|---------|
| L1 | ProcDSL | `.proc` | Process Orchestration |
| L2 | SchemaDSL | `.schema` | Schema Registry |
| L3 | TransformDSL | `.xform` | Transform Catalog |
| L4 | RulesDSL | `.rules` | Business Rules |

## Common Syntax Elements

### Comments
```
// Single line comment
/* Block comment */
```

### Imports (v0.7.0+)
All DSLs support imports for cross-file references:
```
import ./schemas/order.schema
import ../common/transforms.xform
import rules/validation.rules
```

### Duration Literals
```
30 seconds    // 30s
5 minutes     // 5m
2 hours       // 2h
7 days        // 7d
1 week        // 1w
```

### Basic Types
All DSLs share these fundamental types:
- `string` - Text data
- `integer` - Whole numbers
- `decimal` - Decimal numbers
- `boolean` - true/false
- `date` - Date without time
- `timestamp` - Date with time
- `uuid` - Universally unique identifier
- `bytes` - Binary data
- `bizdate` - Business date (validated against calendar)

---

## L1: ProcDSL (Process Orchestration)

### Purpose
ProcDSL defines streaming and batch data processing pipelines. It orchestrates data flow, specifying sources, transformations, routing, and destinations.

### Basic Structure
```
process ProcessName
    // Execution configuration
    parallelism 4
    partition by account_id
    time by event_timestamp
    mode stream

    // Input
    receive orders from kafka "orders-topic"
        schema Order

    // Processing
    transform using enrich_order
    evaluate using validation_rules
    route using decision_result
        "approved" to approved_sink
        "rejected" to rejected_sink
        otherwise to review_sink

    // Output
    emit to output_stream
        schema ProcessedOrder
        persist to mongodb_orders async
end
```

### Execution Block

#### Parallelism
```
parallelism 4                    // Fixed parallelism
parallelism hint 8               // Hint (runtime may adjust)
```

#### Partitioning
```
partition by customer_id         // Single field
partition by region, customer_id // Multiple fields
```

#### Time Semantics
```
time by event_timestamp
    watermark delay 5 seconds
    allowed lateness 30 seconds
    late data to late_events
```

#### Mode
```
mode stream                      // Real-time streaming
mode batch                       // Batch processing
mode micro_batch 30 seconds      // Micro-batch with interval
```

### Business Date Context (v0.6.0+)
```
process DailySettlement
    business_date from trading_calendar
    processing_date auto          // System time when record is processed

    markers
        eod_1: when trades.drained and prices.drained
        eod_2: when after "18:00"
        eod_3: when eod_1 and eod_2
    end

    phase before eod_1
        receive trades from kafka "trades"
        transform using accumulate_trades
    end

    phase after eod_3
        receive positions from state_store
        transform using finalize_positions
        emit to settlements
        on complete signal "day_complete" to downstream
    end
end
```

### Receive (Input)
```
receive transactions from kafka "transactions-topic"
    schema Transaction
    filter amount > 0

receive events
    from kafka "events" group "my-group" offset latest
    schema Event
    project field1, field2, field3
```

### Processing Constructs

#### Transform
```
transform using enrich_order         // Reference L3 transform
transform                             // Inline transform
    output.total = input.price * input.quantity
    output.tax = input.total * 0.08
```

#### Evaluate (L4 Rules Integration)
```
evaluate using fraud_detection_rules
    params: { threshold: 1000 }
    output risk_result
    when risk_result.score > 0.8
        add_flag "HIGH_RISK"
        emit to high_risk_queue
    end
```

#### Route
```
route using decision_field
    "approved" to approved_sink
    "rejected" to rejected_sink
    otherwise to manual_review
```

#### Window
```
window tumbling 5 minutes
    key by customer_id
    aggregate
        count() as transaction_count
        sum(amount) as total_amount
    end

window sliding 1 hour every 5 minutes
    key by region

window session gap 30 minutes
```

#### Join
```
join orders with customers
    on orders.customer_id, customers.id
    within 1 hour
    type left
```

#### Branch (Conditional Sub-Pipelines)
```
branch high_value
    transform using premium_enrichment
    emit to premium_queue
end
```

#### Parallel (Fan-Out)
```
parallel validation_checks
    timeout 30 seconds
    require_all true

    branch fraud_check
        call external fraud_service
    end

    branch compliance_check
        evaluate using compliance_rules
    end
end
```

### Emit (Output)
```
emit to output_stream
    schema OutputRecord
    persist to mongodb async
        batch size 100
        flush interval 5 seconds
        on error emit to dlq
```

### Correlation (Await/Hold)
```
await payment_confirmation
    until confirmation arrives
        matching on order_id
    timeout 24 hours
        emit to timeout_queue

hold batch_items
    keyed by batch_id
    complete when count >= 100
    timeout 1 hour
        emit to partial_batch
```

### State Management
```
state
    uses transaction_state
    local velocity_counter keyed by account_id
        type counter
        ttl sliding 24 hours
        cleanup on_checkpoint
end
```

### Error Handling
```
on error
    log_error "Processing failed"
    retry 3 times
        delay 1 second
        backoff exponential
        max_delay 30 seconds
    then
        emit to dead_letter_queue
end

checkpoint every 5 minutes to rocksdb
```

---

## L2: SchemaDSL (Schema Registry)

### Purpose
SchemaDSL defines data structures with constraints, evolution rules, and mutation patterns.

### Basic Structure
```
schema Order
    pattern event_log
    version 1.2.0
    compatibility backward

    identity
        order_id: uuid required,
    end

    streaming
        key_fields: [order_id]
        time_field: created_at
        time_semantics: event_time
        watermark_delay: 5 seconds
    end

    fields
        customer_id: string required,
        items: list<OrderItem>,
        total: decimal[precision: 10, scale: 2] required,
        status: string[values: pending, confirmed, shipped, delivered],
        created_at: timestamp required,
    end

    computed
        item_count = length(items)
        average_price = total / item_count
    end
end
```

### Mutation Patterns (9 Patterns)
```
pattern master_data           // SCD Type 2 with full history
pattern immutable_ledger      // Append-only financial records
pattern versioned_configuration   // Immutable versions with dates
pattern operational_parameters    // Hot-reloadable parameters
pattern event_log             // Append-only event stream
pattern state_machine         // Workflow state tracking
pattern temporal_data         // Effective-dated values
pattern reference_data        // Lookup tables
pattern business_logic        // Compiled rules
```

### Version Block
```
version 2.0.0
    compatibility backward
    previous_version 1.5.0
    deprecated: "Use v2 fields instead"
    migration_guide: """
        Rename 'amount' to 'total_amount'
        Add 'currency' field with default 'USD'
    """
```

### Identity Block
```
identity
    id: uuid required,
    tenant_id: string required,
end
```

### Streaming Block
```
streaming
    key_fields: [order_id, customer_id]
    time_field: event_timestamp
    time_semantics: event_time
    watermark_delay: 30 seconds
    allowed_lateness: 5 minutes
    late_data_handling: side_output
    idle_timeout: 1 hour
end
```

### Fields Block
```
fields
    // Basic types with constraints
    name: string[length: 1..100] required,
    age: integer[range: 0..150] optional,
    email: string[pattern: "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"],

    // Decimal with precision
    amount: decimal[precision: 15, scale: 2],

    // Enumerations
    status: string[values: active, inactive, suspended],

    // Collections
    tags: list<string>,
    attributes: map<string, string>,

    // Nested objects
    address: object
        street: string required,
        city: string required,
        postal_code: string,
    end

    // PII with Voltage encryption
    ssn: string required pii.ssn,
    card_number: string pii.pan,
    email: string pii.email,
end
```

### Computed Fields
```
computed
    full_name = concat(first_name, " ", last_name)
    total_with_tax = subtotal * (1 + tax_rate)
    risk_category = when score > 0.8 then "HIGH"
                    when score > 0.5 then "MEDIUM"
                    else "LOW"
end
```

### Constraints Block
```
constraints
    end_date > start_date as "End date must be after start date"
    quantity > 0 as "Quantity must be positive"
end
```

### State Machine Block
```
states
    pending: initial
    approved
    rejected
    completed: terminal
end

transitions
    pending -> approved: approve_event
    pending -> rejected: reject_event
    approved -> completed: complete_event
    * -> rejected: cancel_event
end

on_transition
    to completed: send_notification("Order completed")
end
```

### Parameters Block (for operational_parameters pattern)
```
parameters
    rate_limit: integer
        default: 1000
        range: 1..10000
        can_schedule: true
        change_frequency: hourly
end
```

### Entries Block (for reference_data pattern)
```
entries
    USD:
        code: "USD"
        name: "US Dollar"
        symbol: "$"
    EUR:
        code: "EUR"
        name: "Euro"
        symbol: "EUR"
        deprecated: true
        deprecated_reason: "Use EUR_NEW"
end
```

---

## L3: TransformDSL (Transform Catalog)

### Purpose
TransformDSL defines reusable data transformations with type safety, validation, and composition.

### Basic Structure
```
transform enrich_order
    version: 1.0.0
    description: "Enrich order with customer data"
    pure: true

    input: Order
    lookup: CustomerService
    output: EnrichedOrder

    validate_input
        input.amount > 0: "Amount must be positive"
    end

    apply
        output.order_id = input.order_id
        output.customer_name = lookup.get_customer(input.customer_id).name
        output.total = input.quantity * input.unit_price
        output.enriched_at = now()
    end

    validate_output
        output.total >= 0: "Total cannot be negative"
    end

    on_error
        log_error("Enrichment failed")
        emit with defaults
    end
end
```

### Transform Definition

#### Metadata
```
transform calculate_risk
    version: 2.1.0
    description: "Calculate risk score based on transaction patterns"
    previous_version: 2.0.0
    compatibility: backward
    pure: true
    idempotent: true
    cache: 5 minutes
```

#### Input/Output Specification
```
// Single input/output
input: Transaction
output: RiskAssessment

// Multiple inputs
input
    transaction: Transaction
    customer: Customer, nullable
end

// Multiple outputs
output
    score: decimal, required
    flags: list<string>
    decision: string
end
```

#### Parameters (Parameterized Transforms)
```
params:
    threshold: decimal required default: 0.7
    include_historical: boolean optional default: true
end
```

#### Lookups
```
lookup: CustomerService

lookups:
    customer: CustomerService
    rates: ExchangeRateService
end
```

#### State (Stateful Transforms)
```
state: VelocityState
```

### Apply Block
```
apply
    // Direct assignment
    output.id = input.id

    // Calculations
    output.total = input.price * input.quantity

    // Conditional logic
    output.category = when input.amount > 1000 then "HIGH"
                      when input.amount > 100 then "MEDIUM"
                      otherwise "LOW"

    // Function calls
    output.normalized_name = uppercase(trim(input.name))

    // Local variables
    let tax_rate = lookup.get_tax_rate(input.region)
    output.tax = input.subtotal * tax_rate

    // Null coalescing
    output.description = input.description ?? "No description"

    // Optional chaining
    output.city = input.address?.city ?? "Unknown"

    // Collection operations
    output.total = sum(input.items, item -> item.price)
    output.high_value = filter(input.items, amount > 1000)
    output.has_premium = any(input.items, tier == "premium")
end
```

### Validation Blocks
```
validate_input
    input.amount > 0: "Amount must be positive"
    input.currency is not null: "Currency required"
    require input.items.length > 0 else "At least one item required"
end

validate_output
    output.total >= 0: message: "Invalid total", code: "ERR001", severity: error
end
```

### Block Transforms (50+ Field Mappings)
```
transform_block order_to_invoice
    use common_transforms

    input: Order
    output: Invoice

    invariant
        input.status == "confirmed": "Order must be confirmed"
    end

    mappings
        output.invoice_id = generate_uuid()
        output.order_id = input.id
        output.customer = input.customer
        output.line_items = input.items
        output.subtotal = sum(input.items, price * quantity)
        output.tax = output.subtotal * 0.08
        output.total = output.subtotal + output.tax
    end

    on_change [customer.address]
        recalculate
            output.shipping_address = input.customer.address
        end
    end
end
```

### Transform Composition
```
compose order_pipeline
    sequential
        validate_order
        when input.is_international: international_enrichment
        otherwise: domestic_enrichment
        calculate_totals
    end

    then
        parallel
            audit_log
            notification
        end
    end
end
```

### Collection Functions (RFC)
```
// Predicate functions
any(items, amount > 100)          // true if any match
all(items, status == "active")    // true if all match
none(items, expired == true)      // true if none match

// Aggregate functions
sum(items, price)                 // sum of field
count(items)                      // count of items
avg(items, score)                 // average of field
max(items, timestamp)             // maximum value
min(items, priority)              // minimum value

// Transform functions
filter(items, active == true)     // filter collection
find(items, id == target_id)      // find first match
distinct(items)                   // unique values

// Lambda expressions
filter(items, x -> x.amount > 1000 and x.status == "pending")
```

---

## L4: RulesDSL (Business Rules)

### Purpose
RulesDSL defines decision logic using decision tables and procedural rules.

### Decision Table Structure
```
decision_table credit_approval
    hit_policy first_match
    description "Credit approval based on score and income"
    version: 1.0.0

    given:
        credit_score: number
        annual_income: money
        debt_ratio: percentage

    decide:
        | credit_score | annual_income | debt_ratio | decision | limit      |
        |==============|===============|============|==========|============|
        | >= 750       | >= $100000    | < 30%      | approved | $50000     |
        | >= 700       | >= $75000     | < 40%      | approved | $25000     |
        | >= 650       | *             | < 50%      | review   | $10000     |
        | *            | *             | *          | rejected | $0         |

    return:
        decision: text
        limit: money
end
```

### Hit Policies
```
hit_policy first_match   // Return first matching row
hit_policy single_hit    // Expect exactly one match (error otherwise)
hit_policy multi_hit     // Return all matching rows
hit_policy collect_all   // Collect results from all matching rows
```

### Condition Types
```
// Exact match
| "premium"      |           // Equals "premium"

// Comparisons
| >= 700         |           // Greater than or equal
| < 1000         |           // Less than
| != "closed"    |           // Not equal

// Ranges
| 700 to 799     |           // Inclusive range
| $100 to $500   |           // Money range

// Sets
| in ("A", "B")  |           // In set
| not in (1, 2)  |           // Not in set

// Patterns
| matches "^[A-Z]" |         // Regex match
| starts_with "PRE" |        // Starts with
| ends_with ".com"  |        // Ends with
| contains "error"  |        // Contains

// Null checks
| is null        |           // Is null
| is not null    |           // Is not null

// Wildcards
| *              |           // Any value (wildcard)

// Marker conditions (v0.6.0+)
| marker eod_1 fired |       // Phase marker state
```

### Action Types
```
// Literal assignment
| "approved"     |

// Calculations
| amount * 0.05  |

// Lookups
| lookup(rates, currency, default: 1.0) |

// Function calls
| calculate_fee(amount, tier) |

// Emit
| emit to alert_queue |
```

### Post-Calculate Block
```
decision_table with_calculations
    given:
        base_amount: money
        tier: text

    decide:
        | tier      | rate    |
        |===========|=========|
        | "gold"    | 0.05    |
        | "silver"  | 0.10    |
        | *         | 0.15    |

    return:
        rate: number

    post_calculate:
        fee = base_amount * rate
        total = base_amount + fee
end
```

### Aggregate Block (for collect_all)
```
decision_table risk_factors
    hit_policy collect_all

    given:
        transaction: Transaction

    decide:
        | amount    | country          | risk_score |
        |===========|==================|============|
        | > 10000   | *                | 30         |
        | *         | in ("XX", "YY")  | 40         |
        | *         | is null          | 20         |

    return:
        risk_score: number

    aggregate:
        total_risk = sum(risk_score)
        risk_count = count(risk_score)
        max_risk = max(risk_score)
end
```

### Procedural Rules
```
rule fraud_detection:
    description "Complex fraud detection with multiple checks"

    let velocity_score = 0
    let pattern_score = 0

    if transaction.amount > 10000 then
        set velocity_score = check_velocity(transaction.account_id)
        if velocity_score > 80 then
            flag_suspicious("high_velocity")
            emit to fraud_review
            return
        endif
    endif

    if transaction.country in high_risk_countries then
        set pattern_score = analyze_pattern(transaction)
        if pattern_score > 70 and velocity_score > 50 then
            block_transaction("combined_risk")
            emit to blocked_transactions
        elseif pattern_score > 70 then
            flag_for_review("pattern_match")
        endif
    endif
end
```

### Services Block (External Service Declarations)
```
services {
    velocity_check: async VelocityService.check(account_id: text) -> number
        timeout: 500ms
        fallback: 0
        retry: 2

    risk_model: cached(1h) RiskService.predict(features: object) -> number
}
```

### Actions Block
```
actions {
    flag_suspicious(reason: text) -> state flags.add(reason)
    block_transaction(code: text) -> emit to blocked_queue
    send_alert(message: text) -> call AlertService.send
    log_audit(event: text) -> audit
}
```

### Collection Operations in Rules
```
rule validate_line_items:
    // Check if any item exceeds limit
    if any(order.items, amount > params.max_item_amount) then
        flag_high_value()
    endif

    // Check all items are valid
    if not all(order.items, status == "valid") then
        reject_order("invalid_items")
    endif

    // Calculate totals
    let total = sum(order.items, price * quantity)
    let item_count = count(order.items)

    // Filter high-value items
    let premium_items = filter(order.items, tier == "premium")
end
```

---

## Cross-DSL Integration

### Import System
```
// In .proc file
import ./schemas/order.schema
import ./transforms/enrichment.xform
import ./rules/validation.rules

process OrderProcessing
    receive orders
        schema Order           // From imported schema

    transform using enrich_order    // From imported transform
    evaluate using validation_rules // From imported rules
end
```

### Type Resolution
- L1 references L2 schemas for input/output types
- L1 references L3 transforms for processing
- L1 references L4 rules for decision logic
- L3 references L2 schemas for input/output validation
- L4 references L2 schemas for parameter types

### File Organization
```
project/
├── schemas/           # L2 SchemaDSL
│   ├── order.schema
│   └── customer.schema
├── transforms/        # L3 TransformDSL
│   └── enrichment.xform
├── rules/            # L4 RulesDSL
│   └── validation.rules
├── flows/            # L1 ProcDSL
│   └── order_processing.proc
└── infra/            # L5 Infrastructure
    └── production.infra
```
