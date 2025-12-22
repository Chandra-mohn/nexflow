# L3: TransformDSL Language Reference

## Transform Catalog Domain-Specific Language

**Version**: 1.0.0
**Purpose**: Define data transformations including field-level operations, expressions, block-level mappings, and transform composition.

---

## Table of Contents

1. [Overview](#overview)
2. [Transform Structure](#transform-structure)
3. [Transform Types](#transform-types)
4. [Input & Output Specifications](#input--output-specifications)
5. [Apply Block](#apply-block)
6. [Expression Language](#expression-language)
7. [Validation Blocks](#validation-blocks)
8. [Error Handling](#error-handling)
9. [Transform Composition](#transform-composition)
10. [Caching & Performance](#caching--performance)
11. [Functions Reference](#functions-reference)
12. [Complete Examples](#complete-examples)

---

## Overview

TransformDSL (L3) defines reusable data transformation logic. Transforms are pure functions that map input records to output records, with support for:

- **Type Safety**: Typed inputs and outputs with schema references
- **Expression Language**: Rich expressions with null handling
- **Validation**: Input and output validation with custom error messages
- **Composition**: Combine transforms sequentially, in parallel, or conditionally
- **Caching**: Built-in caching support for expensive operations

```
┌─────────────────────────────────────────────────────────────┐
│                    L3: TransformDSL                         │
│              Transform Catalog & Mappings                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Input     │ -> │    Apply     │ -> │   Output     │  │
│  │  Validation  │    │    Logic     │    │  Validation  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Schema References (L2)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Transform Structure

### Basic Transform Definition

```
transform transform_name
    version: 1.0.0
    description: "Description of what this transform does"
    pure: true                       // No side effects

    input: input_schema              // L2 schema reference
    output: output_schema            // L2 schema reference

    validate_input
        // Input validation rules
    end

    apply
        // Transformation logic
    end

    validate_output
        // Output validation rules
    end

    on_error
        // Error handling
    end
end
```

### Import Statements

```
import ./schemas/customer.schema
import ./transforms/common_utils.transform
```

---

## Transform Types

### Field-Level Transform

Simple transforms that operate on individual fields or expressions.

```
transform calculate_total
    version: 1.0.0
    pure: true

    input: order_input
    output: decimal

    apply
        result = input.quantity * input.unit_price * (1 - input.discount)
    end
end
```

### Transform Block (Multi-Field Mappings)

Block-level transforms for complex mappings (50+ fields).

```
transform_block map_customer_to_output
    version: 1.0.0

    input: raw_customer
    output: customer_profile

    mappings
        id = input.customer_id
        full_name = concat(input.first_name, " ", input.last_name)
        email = lower(input.email)
        created_at = input.registration_date
        status = when input.is_active then "active" otherwise "inactive"
    end
end
```

---

## Input & Output Specifications

### Single Input/Output

```
transform simple_transform
    input: raw_transaction           // Schema reference
    output: enriched_transaction     // Schema reference
```

### Multiple Inputs

```
transform merge_data
    input
        transaction: raw_transaction, required
        customer: customer_profile, nullable
        account: account_info, nullable
    end

    output: enriched_transaction
```

### Multiple Outputs

```
transform split_transaction
    input: raw_transaction

    output
        domestic: domestic_transaction
        international: international_transaction
        invalid: error_record
    end
```

### Inline Field Definitions

```
transform calculate_metrics
    input
        amount: decimal, required
        quantity: integer, required
        discount: decimal, nullable, default: 0
    end

    output
        subtotal: decimal
        total: decimal
        average_price: decimal
    end

    apply
        subtotal = amount * quantity
        total = subtotal * (1 - discount)
        average_price = total / quantity
    end
end
```

### Type Qualifiers

| Qualifier | Description |
|-----------|-------------|
| `required` | Field must be present |
| `nullable` | Field may be null |
| `default: value` | Default value if missing |

---

## Apply Block

### Field Assignment

```
apply
    // Simple assignment
    output_field = input.source_field

    // Expression assignment
    total = quantity * price

    // Nested field access
    customer_name = input.customer.profile.name

    // Array indexing
    first_item = input.items[0].name
end
```

### Let Statements (Local Variables)

```
apply
    let base_rate = lookup("rates", currency).rate
    let tax_amount = amount * tax_rate
    let shipping = when weight > 10 then 15.00 otherwise 5.00

    subtotal = amount
    tax = tax_amount
    total = amount + tax_amount + shipping
end
```

### Conditional Expressions

```
apply
    // When-Otherwise (colon style)
    risk_level = when score > 80: "high"
                 when score > 50: "medium"
                 otherwise: "low"

    // When-Then-Otherwise style
    priority = when amount > 10000 then "urgent"
               when amount > 1000 then "normal"
               otherwise "low"
end
```

---

## Expression Language

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `%` | Modulo | `a % b` |

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` or `=` | Equal | `a == b` |
| `!=` | Not equal | `a != b` |
| `<` | Less than | `a < b` |
| `>` | Greater than | `a > b` |
| `<=` | Less or equal | `a <= b` |
| `>=` | Greater or equal | `a >= b` |
| `=?` | Null-safe equal | `a =? b` |

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | Logical AND | `a and b` |
| `or` | Logical OR | `a or b` |
| `not` | Logical NOT | `not a` |

### Null Handling

```
// Null coalescing
name = input.name default "Unknown"
name = input.name ?? "Unknown"

// Null checks
is_valid = input.value is not null
is_empty = input.value is null

// Optional chaining
city = input.address?.city?.name    // Returns null if any part is null
```

### Set Operations

```
// In set
is_valid = status in ["active", "pending", "approved"]
is_invalid = status not in ("active", "pending")

// Between
in_range = amount between 100 and 1000
out_of_range = score not between 0 and 100
```

### Pattern Matching

```
is_email = value matches "^[a-z]+@[a-z]+\\.[a-z]+$"
```

### Object Literals

```
apply
    metadata = {
        source: "transform",
        timestamp: now(),
        version: "1.0"
    }

    empty_object = {}
end
```

### List Literals

```
apply
    tags = ["important", "urgent", "review"]
    empty_list = []
end
```

### Lambda Expressions

```
apply
    // Single parameter
    doubled = items.map(x -> x * 2)

    // Multiple parameters
    combined = pairs.map((a, b) -> a + b)
end
```

### Array Indexing

```
apply
    first_item = items[0]
    second_name = items[1].name
    nested_value = data[0].children[2].value
end
```

---

## Validation Blocks

### Input Validation

```
validate_input
    // Simple validation
    input.amount > 0: "Amount must be positive"

    // With error details
    input.email is not null: message: "Email required"
                             code: "VAL001"
                             severity: error

    // Require-else syntax
    require input.customer_id is not null else "Customer ID is required"
    require input.amount > 0 else "Amount must be positive"

    // Conditional validation
    when input.type == "international" then
        require input.swift_code is not null else "SWIFT code required for international"
        require input.iban is not null else "IBAN required for international"
    end
end
```

### Output Validation

```
validate_output
    output.total >= 0: "Total cannot be negative"
    output.id is not null: "ID must be generated"

    when output.status == "approved" then
        require output.approval_date is not null else "Approval date required"
    end
end
```

### Severity Levels

| Level | Description |
|-------|-------------|
| `error` | Validation failure, reject record |
| `warning` | Log warning, continue processing |
| `info` | Informational, always continue |

---

## Error Handling

### On Error Block

```
on_error
    // Log error
    log_error("Transform failed")

    // Emit with defaults
    emit with defaults

    // Emit partial data
    emit with partial

    // Reject with code
    reject with code "TRANSFORM_ERROR"
    reject with "Processing failed"

    // Action-based handling
    action: reject
    default: null
    log_level: error
    emit_to: error_stream
    error_code: "ERR001"
end
```

### Error Action Types

| Action | Description |
|--------|-------------|
| `reject` | Reject the record |
| `skip` | Skip processing, continue |
| `use_default` | Use default values |
| `raise` | Raise exception |

---

## Transform Composition

### Compose Block

```
transform_block complex_pipeline
    input: raw_data
    output: final_output

    compose sequential
        validate_input
        enrich_with_customer
        calculate_metrics
        apply_business_rules
    end
end
```

### Composition Types

| Type | Description |
|------|-------------|
| `sequential` | Execute transforms in order |
| `parallel` | Execute transforms concurrently |
| `conditional` | Execute based on conditions |

### Conditional Composition

```
transform_block route_processor
    input: transaction
    output: processed_transaction

    compose conditional
        when input.type == "domestic": process_domestic
        when input.type == "international": process_international
        otherwise: process_default
    end
end
```

### Chained Composition

```
compose sequential
    step_one
    step_two
end
then sequential
    final_step
end
```

### Use Block (Dependencies)

```
transform_block main_transform
    use
        helper_transform_a
        helper_transform_b
        utility_functions
    end

    input: raw_data
    output: processed_data

    mappings
        // Can reference transforms from use block
    end
end
```

---

## Caching & Performance

### Cache Declaration

```
transform expensive_lookup
    version: 1.0.0
    pure: true

    // Short form
    cache: 5 minutes

    // Full form
    cache
        ttl: 10 minutes
        key: [input.customer_id, input.region]
    end

    input: request
    output: enriched_request
end
```

### Purity Declaration

```
transform pure_calculation
    pure: true                       // No side effects, deterministic
```

### Idempotent Declaration

```
transform retry_safe_operation
    idempotent: true                 // Safe to retry
```

### State Declaration

```
transform stateful_aggregation
    state: customer_aggregates       // Reference to state store
```

### Lookups Block

```
transform enrich_transaction
    lookups:
        customer: customer_profile_lookup
        account: account_lookup
        rates: exchange_rate_lookup
    end

    apply
        customer_name = lookups.customer.name
        account_status = lookups.account.status
        exchange_rate = lookups.rates.rate
    end
end
```

### Parameters Block

```
transform configurable_transform
    params:
        threshold: decimal required
        mode: string optional, default: "standard"
        multiplier: decimal required, default: 1.0
    end

    apply
        adjusted = input.value * params.multiplier
        is_over = adjusted > params.threshold
    end
end
```

---

## Functions Reference

### String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `concat(a, b, ...)` | Concatenate strings | `concat(first, " ", last)` |
| `upper(s)` | Uppercase | `upper(name)` |
| `lower(s)` | Lowercase | `lower(email)` |
| `trim(s)` | Remove whitespace | `trim(input)` |
| `substring(s, start, len)` | Extract substring | `substring(id, 0, 3)` |
| `length(s)` | String length | `length(description)` |
| `replace(s, old, new)` | Replace text | `replace(phone, "-", "")` |
| `split(s, delim)` | Split string | `split(tags, ",")` |

### Date/Time Functions

| Function | Description | Example |
|----------|-------------|---------|
| `now()` | Current timestamp | `now()` |
| `today()` | Current date | `today()` |
| `date(s)` | Parse date | `date("2024-01-15")` |
| `year(d)` | Extract year | `year(created_at)` |
| `month(d)` | Extract month | `month(created_at)` |
| `day(d)` | Extract day | `day(created_at)` |
| `add_days(d, n)` | Add days | `add_days(due_date, 30)` |
| `days_between(d1, d2)` | Days difference | `days_between(start, end)` |

### Business Date Functions

| Function | Description |
|----------|-------------|
| `current_business_date()` | Current business date |
| `previous_business_date()` | Previous business date |
| `next_business_date()` | Next business date |
| `add_business_days(date, n)` | Add N business days |
| `is_business_day(date)` | Check if business day |
| `is_holiday(date)` | Check if holiday |
| `business_days_between(d1, d2)` | Business days between |

### Math Functions

| Function | Description | Example |
|----------|-------------|---------|
| `abs(n)` | Absolute value | `abs(difference)` |
| `round(n, places)` | Round number | `round(price, 2)` |
| `floor(n)` | Floor | `floor(value)` |
| `ceil(n)` | Ceiling | `ceil(value)` |
| `min(a, b)` | Minimum | `min(a, b)` |
| `max(a, b)` | Maximum | `max(a, b)` |

### Collection Functions

| Function | Description | Example |
|----------|-------------|---------|
| `any(coll, pred)` | Any match predicate | `any(items, amount > 100)` |
| `all(coll, pred)` | All match predicate | `all(items, valid == true)` |
| `none(coll, pred)` | None match predicate | `none(items, status == "error")` |
| `sum(coll, field)` | Sum of field | `sum(items, price)` |
| `count(coll)` | Count items | `count(items)` |
| `avg(coll, field)` | Average of field | `avg(scores, value)` |
| `max(coll, field)` | Maximum value | `max(items, amount)` |
| `min(coll, field)` | Minimum value | `min(items, amount)` |
| `filter(coll, pred)` | Filter items | `filter(items, active == true)` |
| `find(coll, pred)` | Find first match | `find(items, id == target_id)` |
| `distinct(coll)` | Remove duplicates | `distinct(categories)` |

### Utility Functions

| Function | Description | Example |
|----------|-------------|---------|
| `uuid()` | Generate UUID | `uuid()` |
| `lookup(table, key)` | Table lookup | `lookup("rates", currency)` |
| `coalesce(a, b, ...)` | First non-null | `coalesce(nick, first, "Unknown")` |
| `format(template, args)` | Format string | `format("{0} - {1}", id, name)` |

---

## Complete Examples

### Customer Enrichment Transform

```
transform enrich_with_customer
    version: 1.0.0
    description: "Enrich transaction with customer profile data"
    pure: false                      // Uses external lookup

    input: raw_transaction
    lookup: customer_profile
    output: enriched_transaction

    validate_input
        require transaction_id is not null else "Transaction ID required"
        require card_holder_id is not null else "Card holder ID required"
        require amount > 0 else "Amount must be positive"
    end

    apply
        // Pass through original fields
        transaction_id = input.transaction_id
        card_number = input.card_number
        card_holder_id = input.card_holder_id
        amount = input.amount
        currency = input.currency
        merchant_id = input.merchant_id
        transaction_time = input.transaction_time

        // Lookup customer profile
        let profile = lookup(customer_profile, input.card_holder_id)

        // Enrich with customer data (with defaults)
        customer_risk_score = when profile is not null
                              then profile.risk_score
                              otherwise 75

        customer_account_age = when profile is not null
                               then profile.account_age_days
                               otherwise 0

        is_premium_customer = when profile is not null
                              then profile.is_premium
                              otherwise false
    end

    on_error
        log_error("Customer enrichment failed")
        emit with defaults
    end
end
```

### Fraud Scoring Transform

```
transform apply_fraud_scoring
    version: 1.0.0
    description: "Apply ML model and rule-based fraud scoring"
    pure: true

    input: enriched_transaction
    output: fraud_scored_transaction

    validate_input
        require transaction_id is not null else "Transaction ID required"
        require amount > 0 else "Amount must be positive"
    end

    apply
        // Pass through core fields
        transaction_id = input.transaction_id
        card_number = input.card_number
        amount = input.amount
        customer_risk_score = input.customer_risk_score

        // ML model scoring (simulated)
        ml_fraud_score = call_model("fraud_detector_v2", {
            amount: input.amount,
            channel: input.channel,
            customer_risk: input.customer_risk_score,
            velocity_hour: input.transactions_last_hour
        })

        // Rule-based velocity scoring
        velocity_risk_score = when input.transactions_last_hour > 10 then 90
                              when input.transactions_last_hour > 5 then 70
                              when input.transactions_last_hour > 3 then 50
                              otherwise 20

        // Rule-based amount scoring
        amount_risk_score = when input.amount > 5000 then 80
                            when input.amount > 2000 then 60
                            when input.amount > 1000 then 40
                            otherwise 20

        // Combine scores with weights
        let ml_weight = 0.5
        let velocity_weight = 0.3
        let amount_weight = 0.2

        combined_fraud_score = (ml_fraud_score * ml_weight) +
                               (velocity_risk_score / 100 * velocity_weight) +
                               (amount_risk_score / 100 * amount_weight)
    end

    on_error
        log_error("Fraud scoring failed")
        reject with "Scoring error"
    end
end
```

### Transform Block Example

```
transform_block map_order_to_invoice
    version: 1.0.0
    description: "Map order data to invoice format"

    use
        calculate_totals
        format_address
    end

    input: order
    output: invoice

    validate_input
        require input.order_id is not null else "Order ID required"
        require input.items is not null else "Order must have items"
        require count(input.items) > 0 else "Order must have at least one item"
    end

    invariant
        output.total >= 0: "Invoice total cannot be negative"
        output.tax >= 0: "Tax cannot be negative"
    end

    mappings
        invoice_id = uuid()
        order_id = input.order_id
        customer_id = input.customer.id
        customer_name = concat(input.customer.first_name, " ", input.customer.last_name)
        customer_email = lower(input.customer.email)

        billing_address = format_address(input.billing)
        shipping_address = format_address(input.shipping)

        items = input.items
        subtotal = sum(input.items, price * quantity)
        tax = subtotal * input.tax_rate
        shipping = when input.shipping_method == "express" then 15.00
                   when input.shipping_method == "standard" then 5.00
                   otherwise 0.00
        total = subtotal + tax + shipping

        created_at = now()
        due_date = add_days(now(), 30)
        status = "pending"
    end

    validate_output
        require output.total > 0 else "Invoice total must be positive"
        require output.items is not null else "Invoice must have items"
    end

    on_change [input.items]
        recalculate
            subtotal = sum(input.items, price * quantity)
            tax = subtotal * input.tax_rate
            total = subtotal + tax + shipping
        end
    end
end
```

### Composed Transform

```
transform_block order_processing_pipeline
    version: 1.0.0

    input: raw_order
    output: processed_order

    compose sequential
        validate_order
        enrich_with_customer
        calculate_pricing
    end
    then conditional
        when output.total > 10000: apply_bulk_discount
        when output.customer.is_premium: apply_loyalty_discount
        otherwise: apply_standard_pricing
    end
    then sequential
        generate_invoice
        send_confirmation
    end
end
```

---

## Quick Reference

### Keywords by Category

**Structure**: `transform`, `transform_block`, `end`, `import`

**Metadata**: `version`, `description`, `pure`, `idempotent`, `previous_version`, `compatibility`

**I/O**: `input`, `output`, `lookup`, `lookups`, `state`, `params`

**Processing**: `apply`, `mappings`, `let`

**Validation**: `validate_input`, `validate_output`, `invariant`, `require`, `else`, `when`, `message`, `code`, `severity`

**Error Handling**: `on_error`, `action`, `default`, `log_level`, `emit_to`, `error_code`, `log_error`, `emit`, `reject`

**Composition**: `compose`, `sequential`, `parallel`, `conditional`, `use`, `then`, `otherwise`

**Caching**: `cache`, `ttl`, `key`

**Types**: `string`, `integer`, `decimal`, `boolean`, `date`, `timestamp`, `uuid`, `bytes`, `list`, `set`, `map`

**Operators**: `and`, `or`, `not`, `in`, `between`, `is`, `null`, `matches`, `default`, `??`

**Qualifiers**: `required`, `nullable`

---

*Generated from TransformDSL Grammar v1.0.0*
