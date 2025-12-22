# L4: RulesDSL Language Reference

## Business Rules Domain-Specific Language

**Version**: 1.1.0
**Purpose**: Define business rules using decision tables and procedural logic with rich condition and action expressions.

---

## Table of Contents

1. [Overview](#overview)
2. [Rule Types](#rule-types)
3. [Decision Tables](#decision-tables)
4. [Procedural Rules](#procedural-rules)
5. [Services Block](#services-block)
6. [Actions Block](#actions-block)
7. [Condition Types](#condition-types)
8. [Action Types](#action-types)
9. [Expression Language](#expression-language)
10. [Collection Operations](#collection-operations)
11. [Hit Policies](#hit-policies)
12. [Complete Examples](#complete-examples)

---

## Overview

RulesDSL (L4) provides a declarative way to express business logic through:

- **Decision Tables**: Matrix-based logic for multi-condition scenarios
- **Procedural Rules**: Full if-then-elseif-else chains with nesting
- **External Services**: Integration with external APIs and services
- **Actions Catalog**: Reusable action definitions

```
┌─────────────────────────────────────────────────────────────┐
│                    L4: RulesDSL                             │
│              Business Rules & Decision Logic                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────┐    ┌───────────────────────────────┐│
│  │  Decision Tables  │    │     Procedural Rules          ││
│  │  ┌─────┬─────┐    │    │  if condition then            ││
│  │  │ C1  │ A1  │    │    │      action                   ││
│  │  ├─────┼─────┤    │    │  elseif condition then        ││
│  │  │ C2  │ A2  │    │    │      action                   ││
│  │  └─────┴─────┘    │    │  else                         ││
│  └───────────────────┘    │      action                   ││
│                           └───────────────────────────────┘│
│              │                          │                  │
│              ▼                          ▼                  │
│        ┌──────────────────────────────────────┐           │
│        │        Output Records (L2)           │           │
│        └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Rule Types

### Decision Tables vs Procedural Rules

| Feature | Decision Tables | Procedural Rules |
|---------|-----------------|------------------|
| **Best For** | Multi-condition matrices | Complex branching logic |
| **Readability** | High for stakeholders | Better for developers |
| **Maintenance** | Easy to add rows | Easy to modify logic |
| **Hit Policies** | first_match, collect_all | N/A (sequential) |
| **Complexity** | Low-medium | Medium-high |

---

## Decision Tables

### Basic Structure

```
decision_table table_name
    hit_policy first_match           // Optional: defaults to first_match
    description "Description"        // Optional
    version: 1.0.0                   // Optional

    given:                           // Input parameters
        param_name: type

    decide:                          // Decision matrix
        | Column1      | Column2      | Result       |
        |==============|==============|==============|
        | condition1   | condition2   | action1      |
        | condition3   | *            | action2      |

    return:                          // Output parameters
        result_name: type

    post_calculate:                  // Optional: derived calculations
        derived = expression

    aggregate:                       // Optional: for collect_all
        aggregated = expression
end
```

### Table Header

```
decide:
    | priority | credit_score | income      | decision   | rate        |
    |==========|==============|=============|============|=============|
```

### Priority Column (Optional)

```
decide:
    | priority | credit_score | income      | decision   |
    |==========|==============|=============|============|
    | 1        | >= 750       | >= $100,000 | "approve"  |
    | 2        | >= 700       | >= $75,000  | "approve"  |
    | 3        | >= 650       | *           | "review"   |
    | 4        | *            | *           | "reject"   |
```

---

## Procedural Rules

### Basic Structure

```
rule rule_name:
    description "Rule description"

    // Variables
    set variable = expression
    let local_var = expression

    // Control flow
    if condition then
        action_sequence
    elseif condition then
        action_sequence
    else
        action_sequence
    endif

    return
end
```

### Nested Rules

```
rule complex_fraud_detection:
    if transaction.amount > 10000 then
        if customer.risk_score > 80 then
            if transaction.is_international then
                block_transaction("High-value international from high-risk customer")
            else
                flag_for_review("High-value from high-risk customer")
            endif
        else
            log_info("High-value transaction from normal customer")
        endif
    endif
end
```

---

## Services Block

Define external service integrations.

```
services {
    // Synchronous service
    credit_check: sync CreditService.checkCredit(
        ssn: text,
        amount: money
    ) -> number
        timeout: 5s
        fallback: 0
        retry: 3

    // Asynchronous service
    fraud_analysis: async FraudService.analyze(
        transaction: transaction
    ) -> fraud_result
        timeout: 10s

    // Cached service
    exchange_rates: cached(1h) ExchangeService.getRate(
        from_currency: text,
        to_currency: text
    ) -> decimal
}
```

### Service Types

| Type | Description | Use Case |
|------|-------------|----------|
| `sync` | Blocking call | Real-time lookups |
| `async` | Non-blocking | Background processing |
| `cached(duration)` | Cached results | Reference data |

### Service Options

| Option | Description |
|--------|-------------|
| `timeout: duration` | Maximum wait time |
| `fallback: value` | Default if service fails |
| `retry: count` | Retry attempts |

---

## Actions Block

Define reusable action methods.

```
actions {
    // Emit to output stream
    approve_loan(reason: text) -> emit to approved_loans

    // Update state
    add_fraud_flag(flag: text) -> state flags.add(flag)

    // Emit to audit trail
    log_decision(decision: text, reason: text) -> audit

    // Call external service
    notify_customer(message: text) -> call NotificationService.send
}
```

### Action Targets

| Target | Description | Example |
|--------|-------------|---------|
| `emit to stream` | Send to output | `-> emit to approved` |
| `state name.op` | State operation | `-> state flags.add(flag)` |
| `audit` | Audit trail | `-> audit` |
| `call Service.method` | Service call | `-> call Notify.send` |

---

## Condition Types

### Wildcard

```
| *                | action |         // Match anything
```

### Exact Match

```
| "approved"       | action |         // String exact match
| 750              | action |         // Number exact match
| true             | action |         // Boolean exact match
```

### Range Conditions

```
| 700 to 799       | action |         // Inclusive range
| $100 to $500     | action |         // Money range
```

### Comparison Conditions

```
| >= 750           | action |         // Greater or equal
| > 1000           | action |         // Greater than
| <= 0.3           | action |         // Less or equal
| < 100            | action |         // Less than
| != "closed"      | action |         // Not equal
```

### Set Conditions

```
| in ("A", "B", "C")     | action |   // In set
| not in ("X", "Y")      | action |   // Not in set
```

### Pattern Conditions

```
| matches "^[A-Z]{2}\\d{4}$"  | action |   // Regex match
| starts_with "PREM"          | action |   // Starts with
| ends_with "_VIP"            | action |   // Ends with
| contains "GOLD"             | action |   // Contains
```

### Null Conditions

```
| is null          | action |         // Is null
| is not null      | action |         // Is not null
| is_null          | action |         // Alternative syntax
| is_not_null      | action |         // Alternative syntax
```

### Expression Conditions

```
| (amount > 1000 and risk < 0.5)  | action |   // Complex expression
| (score >= 700 or income > $100000) | action |
```

### Marker State Conditions (v0.6.0+)

```
| marker eod_1 fired              | action |   // Marker fired
| marker eod_1 pending            | action |   // Marker pending
| between eod_1 and eod_2         | action |   // Between markers
```

---

## Action Types

### Literal Value

```
| condition | "approved"    |              // String value
| condition | 750           |              // Number value
| condition | $1,000.00     |              // Money literal
| condition | 5.5%          |              // Percentage literal
| condition | true          |              // Boolean value
```

### Calculated Expression

```
| condition | amount * 0.1             |   // Arithmetic
| condition | base_rate + risk_premium |   // Addition
| condition | min(requested, max_limit)|   // Function call
```

### Lookup Action

```
| condition | lookup(rate_table, credit_tier)                    |
| condition | lookup(rates, currency, default: 1.0)              |
| condition | lookup(effective_rates, as_of: business_date)      |
```

### Function Call

```
| condition | calculate_premium(age, coverage)   |
| condition | format_currency(amount, currency)  |
```

### Emit Action

```
| condition | emit to high_risk_queue           |
```

---

## Expression Language

### Literals

| Type | Examples |
|------|----------|
| String | `"text"`, `'text'` |
| Integer | `123`, `-45` |
| Decimal | `12.34`, `-0.5` |
| Money | `$1,000.00`, `$50` |
| Percentage | `5.5%`, `10%` |
| Boolean | `true`, `false`, `yes`, `no` |
| Null | `null` |

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `%` or `mod` | Modulo | `a % b` |

### Comparison Operators

| Operator | Description |
|----------|-------------|
| `==` or `=` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less or equal |
| `>=` | Greater or equal |

### Logical Operators

| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

### Field Paths

```
customer.name                        // Nested access
customer.address.city                // Deep nesting
items[0].price                       // Array indexing
"special-field"                      // Quoted field names
```

### When Expression

```
let tier = when score >= 800 then "platinum"
           when score >= 700 then "gold"
           when score >= 600 then "silver"
           otherwise "bronze"
```

### Object Literals

```
{
    decision: "approved",
    rate: calculated_rate,
    effective_date: today()
}
```

### List Literals

```
[item1, item2, item3]
["A", "B", "C"]
```

### Lambda Expressions

```
x -> x.amount > 1000
(a, b) -> a + b
```

---

## Collection Operations

### Predicate Functions

```
// any - true if any element matches
any(transactions, amount > 1000)
any(items, t -> t.status == "pending")

// all - true if all elements match
all(items, valid == true)
all(payments, p -> p.amount > 0)

// none - true if no element matches
none(transactions, status == "failed")
```

### Aggregate Functions

```
// sum - sum of field values
sum(items, price)
sum(line_items, quantity * unit_price)

// count - count of items
count(items)
count(items, status == "active")

// avg - average of field values
avg(scores, value)

// max - maximum value
max(bids, amount)

// min - minimum value
min(prices, value)
```

### Transform Functions

```
// filter - filter items by predicate
filter(items, active == true)
filter(transactions, t -> t.amount > 100)

// find - find first matching item
find(customers, id == target_id)

// distinct - unique values
distinct(categories)
```

### Collection Predicate Syntax

```
// Simple field comparison
any(items, amount > 100)

// Set membership
any(items, type in ("A", "B"))

// Null check
any(items, description is not null)

// Compound conditions
any(items, amount > 100 and status == "active")

// Lambda style
any(items, item -> item.price * item.quantity > 1000)
```

---

## Hit Policies

### first_match (Default)

Returns the first matching row. Use when rules have priority ordering.

```
decision_table credit_decision
    hit_policy first_match           // Stop at first match

    decide:
        | credit_score | income       | decision   |
        |==============|==============|============|
        | >= 750       | >= $100,000  | "approve"  |
        | >= 700       | >= $75,000   | "approve"  |
        | >= 650       | *            | "review"   |
        | *            | *            | "reject"   |

    return:
        decision: text
end
```

### collect_all

Returns all matching rows. Use for accumulating results.

```
decision_table applicable_discounts
    hit_policy collect_all           // Collect all matches

    decide:
        | customer_tier | order_total  | discount   |
        |===============|==============|============|
        | "platinum"    | *            | 10%        |
        | "gold"        | *            | 5%         |
        | *             | >= $1,000    | 3%         |
        | *             | >= $500      | 1%         |

    return:
        discount: percentage

    aggregate:
        total_discount = sum(discount)
end
```

### single_hit

Expects exactly one match. Throws error if multiple matches.

```
decision_table tax_rate_lookup
    hit_policy single_hit

    decide:
        | jurisdiction | category     | rate       |
        |==============|==============|============|
        | "CA"         | "goods"      | 7.25%      |
        | "CA"         | "services"   | 0%         |
        | "TX"         | "goods"      | 6.25%      |
        | "TX"         | "services"   | 0%         |

    return:
        rate: percentage
end
```

### multi_hit

Returns multiple results as separate outputs.

```
decision_table risk_flags
    hit_policy multi_hit

    decide:
        | amount       | velocity     | flag           |
        |==============|==============|================|
        | >= $10,000   | *            | "high_value"   |
        | *            | > 10         | "high_velocity"|
        | >= $5,000    | > 5          | "suspicious"   |

    return:
        flag: text

    execute: multi
end
```

---

## Post-Calculate Block

Derive additional values after the decision.

```
decision_table loan_pricing
    given:
        credit_score: number
        loan_amount: money
        term_months: number

    decide:
        | credit_score | base_rate    |
        |==============|==============|
        | >= 750       | 5.0%         |
        | >= 700       | 6.5%         |
        | >= 650       | 8.0%         |
        | *            | 10.0%        |

    return:
        base_rate: percentage

    post_calculate:
        let term_adjustment = when term_months > 60 then 0.5%
                              when term_months > 36 then 0.25%
                              otherwise 0%

        final_rate = base_rate + term_adjustment
        monthly_payment = calculate_pmt(loan_amount, final_rate, term_months)
        total_interest = (monthly_payment * term_months) - loan_amount
end
```

---

## Complete Examples

### Fraud Detection Decision Table

```
import ./schemas/transaction.schema
import ./schemas/fraud_result.schema

services {
    velocity_check: sync VelocityService.check(
        customer_id: text,
        window_hours: number
    ) -> number
        timeout: 500ms
        fallback: 0

    ml_score: async MLService.scoreFraud(
        transaction: transaction
    ) -> decimal
        timeout: 2s
}

actions {
    block_transaction(reason: text) -> emit to blocked_transactions
    flag_review(reason: text) -> emit to manual_review
    add_flag(flag: text) -> state transaction_flags.add(flag)
    log_fraud_check(result: text) -> audit
}

decision_table fraud_detection_rules
    hit_policy first_match
    description "Primary fraud detection decision table"
    version: 1.2.0

    given:
        transaction_id: text
        amount: money
        customer_risk_score: number
        velocity_hour: number
        ml_fraud_score: number
        is_international: boolean
        is_new_merchant: boolean

    decide:
        | priority | amount      | ml_fraud_score | velocity_hour | decision   | reason                    |
        |==========|=============|================|===============|============|===========================|
        | 1        | >= $10,000  | >= 0.9         | *             | "block"    | "High-value + ML flagged" |
        | 2        | *           | >= 0.95        | *             | "block"    | "Extreme ML fraud score"  |
        | 3        | >= $5,000   | >= 0.7         | > 5           | "block"    | "High risk combination"   |
        | 4        | >= $1,000   | >= 0.8         | *             | "review"   | "ML flagged for review"   |
        | 5        | *           | >= 0.7         | > 10          | "review"   | "Velocity + ML concern"   |
        | 6        | >= $5,000   | *              | > 10          | "review"   | "High-value + velocity"   |
        | 7        | *           | < 0.3          | < 5           | "approve"  | "Low risk transaction"    |
        | 8        | *           | *              | *             | "approve"  | "Default approval"        |

    return:
        decision: text
        reason: text

    post_calculate:
        let risk_tier = when ml_fraud_score >= 0.8 then "critical"
                        when ml_fraud_score >= 0.5 then "elevated"
                        otherwise "normal"

        final_score = (ml_fraud_score * 0.6) + (customer_risk_score / 1000 * 0.3) + (velocity_hour / 20 * 0.1)
        requires_callback = decision == "review" and amount >= $2,000
end
```

### Credit Decision Procedural Rule

```
rule credit_application_decision:
    description "Complex credit application decision logic"

    // Initialize tracking variables
    set approval_reasons = []
    set rejection_reasons = []
    set final_decision = "pending"

    // Check credit score
    if credit_score >= 750 then
        set approval_reasons = approval_reasons + ["Excellent credit score"]
    elseif credit_score >= 700 then
        set approval_reasons = approval_reasons + ["Good credit score"]
    elseif credit_score >= 650 then
        // Marginal - need additional factors
        if income >= $75000 and employment_years >= 2 then
            set approval_reasons = approval_reasons + ["Adequate credit with strong income"]
        else
            set rejection_reasons = rejection_reasons + ["Credit score below threshold"]
        endif
    else
        set rejection_reasons = rejection_reasons + ["Poor credit score"]
        set final_decision = "rejected"
        return
    endif

    // Check debt-to-income ratio
    let dti = monthly_debt / monthly_income
    if dti > 0.45 then
        set rejection_reasons = rejection_reasons + ["DTI ratio too high"]
    elseif dti > 0.35 then
        if credit_score < 720 then
            set rejection_reasons = rejection_reasons + ["DTI elevated with marginal credit"]
        endif
    else
        set approval_reasons = approval_reasons + ["Healthy DTI ratio"]
    endif

    // Check for existing relationship
    if customer.is_existing and customer.years_with_bank >= 3 then
        set approval_reasons = approval_reasons + ["Valued existing customer"]
    endif

    // Check collateral for secured loans
    if loan_type == "secured" then
        if collateral_value >= loan_amount * 1.2 then
            set approval_reasons = approval_reasons + ["Adequate collateral"]
        else
            set rejection_reasons = rejection_reasons + ["Insufficient collateral"]
        endif
    endif

    // Final decision
    if count(rejection_reasons) == 0 and count(approval_reasons) >= 2 then
        set final_decision = "approved"
        approve_application(join(approval_reasons, "; "))
    elseif count(rejection_reasons) <= 1 and count(approval_reasons) >= 1 then
        set final_decision = "review"
        flag_for_review(join(rejection_reasons, "; "))
    else
        set final_decision = "rejected"
        reject_application(join(rejection_reasons, "; "))
    endif

    log_decision(final_decision, "Application processed")
end
```

### Collection-Based Risk Assessment

```
decision_table portfolio_risk_assessment
    hit_policy first_match
    description "Assess portfolio risk based on transaction patterns"

    given:
        customer_id: text
        transactions: transaction[]         // List of transactions
        account_age_days: number

    decide:
        | any(transactions, amount > $50000) | sum(transactions, amount) | risk_level |
        |====================================|==========================|============|
        | true                               | >= $500,000              | "critical" |
        | true                               | >= $100,000              | "high"     |
        | false                              | >= $200,000              | "elevated" |
        | *                                  | >= $50,000               | "moderate" |
        | *                                  | *                        | "low"      |

    return:
        risk_level: text

    post_calculate:
        transaction_count = count(transactions)
        average_transaction = avg(transactions, amount)
        max_transaction = max(transactions, amount)
        high_value_count = count(filter(transactions, amount > $10000))

        let velocity_factor = when transaction_count > 100 then 1.5
                              when transaction_count > 50 then 1.2
                              otherwise 1.0

        adjusted_risk_score = when risk_level == "critical" then 100 * velocity_factor
                              when risk_level == "high" then 80 * velocity_factor
                              when risk_level == "elevated" then 60 * velocity_factor
                              when risk_level == "moderate" then 40 * velocity_factor
                              otherwise 20
end
```

---

## Quick Reference

### Keywords by Category

**Structure**: `decision_table`, `rule`, `end`, `import`

**Sections**: `services`, `actions`, `given`, `decide`, `return`, `execute`, `post_calculate`, `aggregate`

**Hit Policies**: `hit_policy`, `first_match`, `single_hit`, `multi_hit`, `collect_all`

**Control Flow**: `if`, `then`, `elseif`, `else`, `endif`, `when`, `otherwise`

**Variables**: `set`, `let`

**Conditions**: `in`, `not in`, `is`, `null`, `is_null`, `is_not_null`, `matches`, `contains`, `starts_with`, `ends_with`, `to` (range)

**Actions**: `emit`, `to`, `lookup`, `default`, `as_of`

**Services**: `sync`, `async`, `cached`, `timeout`, `fallback`, `retry`

**Logic**: `and`, `or`, `not`

**Types**: `text`, `number`, `boolean`, `date`, `timestamp`, `money`, `percentage`, `bizdate`

**Collection Functions**: `any`, `all`, `none`, `sum`, `count`, `avg`, `max`, `min`, `filter`, `find`, `distinct`

**Markers**: `marker`, `fired`, `pending`, `between`

**Other**: `description`, `version`, `priority`, `return`, `state`, `audit`, `call`

---

*Generated from RulesDSL Grammar v1.1.0*
