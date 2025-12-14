# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Nexflow Language User Guide

## Introduction

Nexflow is a multi-layer Domain-Specific Language (DSL) toolchain designed for building streaming and batch data processing pipelines. This guide walks you through building your first Nexflow application and understanding the key concepts.

## Getting Started

### Prerequisites
- Python 3.11+
- Java 17+ (for generated code)
- Apache Flink 1.17+ (runtime)

### Create Your First Project
```bash
# Initialize a new project
nexflow init --name my-first-flow

# Navigate to project
cd my-first-flow

# Verify structure
ls -la
# nexflow.toml
# src/
#   flow/
#   schema/
#   transform/
#   rules/
#   infra/
```

## Tutorial: Building an Order Processing Pipeline

### Step 1: Define Your Data Schema (L2)

Create `src/schema/order.schema`:
```
schema Order
    pattern event_log
    version 1.0.0

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
        total_amount: decimal[precision: 10, scale: 2] required,
        status: string[values: pending, confirmed, shipped, delivered] required,
        created_at: timestamp required,
    end
end

schema OrderItem
    fields
        product_id: string required,
        quantity: integer[range: 1..1000] required,
        unit_price: decimal[precision: 10, scale: 2] required,
    end
end

schema ProcessedOrder
    pattern event_log

    fields
        order_id: uuid required,
        customer_id: string required,
        customer_name: string,
        total_amount: decimal required,
        tax_amount: decimal required,
        final_amount: decimal required,
        risk_score: decimal,
        decision: string,
        processed_at: timestamp required,
    end
end
```

### Step 2: Create Transformation Logic (L3)

Create `src/transform/order_enrichment.xform`:
```
transform enrich_order
    version: 1.0.0
    description: "Enrich order with customer data and calculate totals"
    pure: true

    input: Order
    lookup: CustomerService
    output: ProcessedOrder

    validate_input
        input.total_amount > 0: "Order amount must be positive"
        input.items.length > 0: "Order must have items"
    end

    apply
        output.order_id = input.order_id
        output.customer_id = input.customer_id

        // Lookup customer information
        let customer = lookup.get_customer(input.customer_id)
        output.customer_name = customer?.name ?? "Unknown"

        // Calculate amounts
        output.total_amount = input.total_amount
        output.tax_amount = input.total_amount * 0.08
        output.final_amount = input.total_amount + output.tax_amount

        output.processed_at = now()
    end

    on_error
        log_error("Failed to enrich order")
        emit with defaults
    end
end
```

### Step 3: Define Business Rules (L4)

Create `src/rules/order_validation.rules`:
```
decision_table order_risk_assessment
    hit_policy first_match
    description "Assess order risk based on amount and customer history"

    given:
        order_amount: money
        customer_tenure_days: number
        previous_order_count: number

    decide:
        | order_amount | customer_tenure_days | previous_order_count | decision  | risk_score |
        |==============|======================|======================|===========|============|
        | > $10000     | < 30                 | < 3                  | review    | 0.8        |
        | > $5000      | < 30                 | *                    | review    | 0.6        |
        | > $10000     | *                    | > 10                 | approve   | 0.2        |
        | *            | > 90                 | > 5                  | approve   | 0.1        |
        | *            | *                    | *                    | review    | 0.5        |

    return:
        decision: text
        risk_score: number
end
```

### Step 4: Orchestrate the Pipeline (L1)

Create `src/flow/order_processing.proc`:
```
import ../schema/order.schema
import ../transform/order_enrichment.xform
import ../rules/order_validation.rules

process OrderProcessing
    parallelism 4
    partition by customer_id
    time by created_at
        watermark delay 5 seconds
    mode stream

    // Receive orders from Kafka
    receive orders from kafka "incoming-orders"
        schema Order
        filter total_amount > 0

    // Enrich with customer data
    transform using enrich_order

    // Apply business rules
    evaluate using order_risk_assessment
        params: {
            order_amount: input.final_amount,
            customer_tenure_days: 90,
            previous_order_count: 5
        }
        output risk_result

    // Route based on decision
    route using risk_result.decision
        "approve" to approved_orders
        "review" to review_queue
        otherwise to manual_review

    // Error handling
    on error
        log_error("Order processing failed")
        retry 3 times
            delay 1 second
            backoff exponential
        then
            emit to dead_letter_queue
                reason "Processing failed after retries"
    end
end
```

### Step 5: Configure Infrastructure (L5)

Create `src/infra/local.infra`:
```
environment local

streams
    incoming-orders:
        type kafka
        topic "orders.incoming"
        bootstrap_servers "localhost:9092"
        consumer_group "order-processor"

    approved_orders:
        type kafka
        topic "orders.approved"
        bootstrap_servers "localhost:9092"

    review_queue:
        type kafka
        topic "orders.review"
        bootstrap_servers "localhost:9092"

    dead_letter_queue:
        type kafka
        topic "orders.dlq"
        bootstrap_servers "localhost:9092"
end

persistence
    order_db:
        type mongodb
        uri "mongodb://localhost:27017"
        database "orders"
        collection "processed_orders"
end
```

### Step 6: Build and Run

```bash
# Validate all files
nexflow validate

# Build the project
nexflow build --target flink

# Build with verification
nexflow build --verify

# View generated files
ls generated/flink/src/main/java/
```

## Key Concepts

### The Zero-Code Covenant
Nexflow follows a zero-code philosophy: users never write Java code. All business logic is expressed in DSLs, and the toolchain generates production-ready code.

### Layer Separation

| Layer | Purpose | Contains |
|-------|---------|----------|
| L1 | Orchestration | Data flow, routing, timing |
| L2 | Contracts | Data structures, constraints |
| L3 | Logic | Transformations, calculations |
| L4 | Decisions | Business rules, policies |
| L5 | Bindings | Infrastructure connections |

### Data Flow Principle
L1 is the "railroad" - it orchestrates data flow but contains NO business logic. Business logic belongs in L3 (transforms) and L4 (rules).

## Common Patterns

### Event Sourcing Pattern
```
process AuditTrail
    receive events
        schema Event

    emit_audit_event "event_received"
        actor system "audit-service"
        payload: { event_type: input.type, timestamp: now() }

    transform using audit_transform

    emit to audit_stream
        persist to audit_db async
end
```

### Aggregation Pattern
```
process DailyMetrics
    mode batch
    business_date from trading_calendar

    receive transactions
        schema Transaction

    window tumbling 1 day
        key by account_id
        aggregate
            count() as transaction_count
            sum(amount) as total_amount
            avg(amount) as avg_amount
        end

    emit to daily_metrics
end
```

### Correlation Pattern
```
process OrderConfirmation
    receive orders
        schema Order
        store in pending_orders

    await payment
        until confirmation arrives
            matching on order_id
        timeout 24 hours
            emit to expired_orders

    transform using confirm_order

    emit to confirmed_orders
end
```

### Fan-Out Pattern
```
process MultiValidation
    receive applications

    parallel validation_checks
        timeout 30 seconds
        require_all true

        branch credit_check
            call external credit_service
        end

        branch fraud_check
            evaluate using fraud_rules
        end

        branch compliance_check
            evaluate using compliance_rules
        end
    end

    aggregate validation_results
        from credit_check, fraud_check, compliance_check
        timeout 35 seconds
        on_partial_timeout
            log_warning "Partial timeout on validation"
            add_flag "PARTIAL_VALIDATION"

    route using aggregated_result
        "all_pass" to approved
        otherwise to manual_review
end
```

### State Machine Pattern
```
schema OrderStatus
    pattern state_machine

    states
        pending: initial
        confirmed
        processing
        shipped
        delivered: terminal
        cancelled: terminal
    end

    transitions
        pending -> confirmed: confirm_order
        pending -> cancelled: cancel_order
        confirmed -> processing: start_processing
        processing -> shipped: ship_order
        shipped -> delivered: confirm_delivery
    end
end

process OrderStateMachine
    state_machine order_state
        schema OrderStatus
        persistence order_state_store
        checkpoint every 100 events

    receive order_events

    transition to input.new_status

    on error
        log_error "Invalid state transition"
        emit to invalid_transitions
    end
end
```

### Phase-Based Processing (EOD Pattern)
```
process EndOfDaySettlement
    business_date from trading_calendar
    processing_date auto

    markers
        trading_closed: when after "16:00"
        all_trades_received: when trades.drained
        prices_finalized: when prices.count >= 1000
        eod_ready: when trading_closed and all_trades_received and prices_finalized
    end

    phase before eod_ready
        receive trades from kafka "trades"
            schema Trade
        transform using accumulate_trade
        emit to trade_buffer
    end

    phase after eod_ready
        receive buffered_trades from state_store "trade_buffer"
        transform using calculate_settlements
        emit to settlements
            persist to settlement_db sync
        on complete signal "settlement_complete" to downstream
    end
end
```

## Best Practices

### Schema Design
1. **Use appropriate patterns** - Choose mutation pattern based on data behavior
2. **Define identity** - Always specify identity fields for keyed streams
3. **Add streaming metadata** - Include time_field and watermark for event-time processing
4. **Use constraints** - Add validation at the schema level

### Transform Design
1. **Keep transforms pure** - Avoid side effects for testability
2. **Validate inputs** - Check preconditions before processing
3. **Handle nulls** - Use null coalescing (??) and optional chaining (?.)
4. **Use meaningful names** - Transform names should describe the operation

### Rule Design
1. **Cover all cases** - Use wildcard rows for catch-all behavior
2. **Order by specificity** - Most specific conditions first
3. **Document decisions** - Use description for complex rules
4. **Use appropriate hit policy** - first_match for most cases, collect_all for aggregation

### Process Design
1. **Separate concerns** - Keep orchestration separate from logic
2. **Plan for failure** - Include error handling blocks
3. **Set timeouts** - Always specify timeouts for awaits and external calls
4. **Use checkpoints** - Enable state recovery with checkpoint configuration

## Debugging

### Validation Errors
```bash
# Validate specific file
nexflow validate src/flow/order_processing.proc

# Validate with verbose output
nexflow -v validate
```

### Parse AST
```bash
# View parsed structure
nexflow parse src/rules/validation.rules --format tree

# Export as JSON for analysis
nexflow parse src/schema/order.schema --format json > order_ast.json
```

### Dry Run
```bash
# See what would be generated without writing files
nexflow build --dry-run
```

## Reference

### Runtime Functions

Date/Time functions available in expressions:
- `now()` - Current timestamp
- `processing_date()` - Processing system time (v0.7.0+)
- `business_date()` - Business date from calendar context
- `business_date_offset(n)` - Business date offset by n days

String functions:
- `concat(a, b, ...)` - Concatenate strings
- `trim(s)` - Remove whitespace
- `uppercase(s)` / `lowercase(s)` - Case conversion
- `substring(s, start, length)` - Extract substring
- `length(s)` - String length

Math functions:
- `abs(n)` - Absolute value
- `round(n, decimals)` - Round to decimals
- `ceil(n)` / `floor(n)` - Ceiling/floor
- `max(a, b)` / `min(a, b)` - Maximum/minimum

Collection functions:
- `sum(collection, field)` - Sum of field values
- `count(collection)` - Count of items
- `avg(collection, field)` - Average of field values
- `any(collection, predicate)` - True if any match
- `all(collection, predicate)` - True if all match
- `filter(collection, predicate)` - Filter items
- `find(collection, predicate)` - Find first match

### Type Reference

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text | `"hello"` |
| `integer` | Whole number | `42` |
| `decimal` | Decimal number | `3.14` |
| `boolean` | True/false | `true` |
| `date` | Date only | `2024-01-15` |
| `timestamp` | Date and time | `2024-01-15T10:30:00Z` |
| `uuid` | UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `bizdate` | Business date | Validated against calendar |
| `list<T>` | List of T | `[1, 2, 3]` |
| `map<K,V>` | Key-value map | `{"a": 1}` |
| `money` | Monetary amount | `$100.00` |
| `percentage` | Percentage | `15%` |

### Constraint Reference

```
string[length: 10]           // Exact length
string[length: 1..100]       // Length range
string[pattern: "^[A-Z]+$"]  // Regex pattern
integer[range: 0..100]       // Value range
decimal[precision: 10, scale: 2]  // Decimal precision
string[values: a, b, c]      // Enumeration
```

## Further Reading

- [Architecture Document](ARCHITECTURE.md) - System architecture overview
- [DSL Language Specifications](DSL-LANGUAGE-SPEC.md) - Complete grammar reference
- [Backend Usage Guide](BACKEND-USAGE.md) - CLI and API documentation
- [VS Code Extension Guide](VSCODE-EXTENSION-GUIDE.md) - IDE setup and features
