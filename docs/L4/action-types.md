# L4: Action Types

> **Source**: Adapted from ccdsl/DSL_DECISION_TABLES.md
> **Status**: Complete Specification

---

## Overview

Action types define what happens when a decision table rule matches. Nexflow supports five primary action types that can be combined in decision table action columns.

---

## 1. Assign (`assign`)

Set a value to a field or variable.

**Syntax**:
```
| condition | route_to        |
|-----------|-----------------|
| > 1000    | "manual_review" |
| <= 1000   | "auto_approve"  |
```

**Semantics**: `route_to = "manual_review"`

**Use Cases**:
- Setting routing destinations
- Assigning status values
- Setting flags

---

## 2. Calculate (`calculate`)

Compute a value using expressions.

**Syntax**:
```
| balance   | days_late | fee                      |
|-----------|-----------|--------------------------|
| > $10,000 | 1-7       | balance * 0.01           |
| > $10,000 | 8-30      | $15 + (days_late - 7) * $2 |
| *         | *         | $35                      |
```

**Semantics**: `fee = balance * 0.01`

**Supported Operators**:
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Functions: `min()`, `max()`, `round()`, `abs()`
- Type conversions: `to_money()`, `to_percent()`

**Examples**:
```
// Percentage calculation
| amount | fee              |
|--------|------------------|
| *      | amount * 0.03    |

// Compound calculation
| principal | rate | term | monthly_payment                      |
|-----------|------|------|--------------------------------------|
| *         | *    | *    | (principal * rate/12) / (1 - (1 + rate/12)^-term) |

// With functions
| values | result                  |
|--------|-------------------------|
| *      | max(values) - min(values) |
```

---

## 3. Lookup (`lookup`)

Fetch a value from an external source.

**Syntax**:
```
| currency | rate                             |
|----------|----------------------------------|
| *        | lookup(currency_rates, currency) |
```

**Semantics**: `rate = currency_rates.get(currency)`

**Lookup Patterns**:

```
// Simple key lookup
lookup(table_name, key)

// Composite key lookup
lookup(interest_rates, credit_tier, term)

// With default
lookup(discounts, customer_id, default: 0)

// Temporal lookup (effective date)
lookup(rates, as_of: transaction_date)
```

**Examples**:
```
| merchant_id | risk_score                        |
|-------------|-----------------------------------|
| *           | lookup(merchant_risk, merchant_id) |

| country | product | tax_rate                        |
|---------|---------|----------------------------------|
| *       | *       | lookup(tax_table, country, product) |
```

---

## 4. Call (`call`)

Invoke a function or action handler.

**Syntax**:
```
| status | execute                           |
|--------|-----------------------------------|
| 200    | complete_payment(payment)         |
| 400    | schedule_retry(payment, 5min)     |
| 500    | alert_operations(payment, status) |
```

**Semantics**: Direct function invocation

**Call Patterns**:

```
// Simple call
send_notification(customer)

// With parameters
schedule_retry(payment, delay: 5min)

// Chained calls (multiple action columns)
| condition | action_1          | action_2              |
|-----------|-------------------|-----------------------|
| high_risk | hold(transaction) | alert_fraud(customer) |
```

**Examples**:
```
// Application processing
| decision | execute                        |
|----------|--------------------------------|
| approved | create_account(application)    |
| declined | send_rejection(application)    |
| review   | assign_to_underwriter(application) |

// With context
| amount | execute                                    |
|--------|-------------------------------------------|
| > 10000 | require_approval(transaction, level: "VP") |
```

---

## 5. Emit (`emit`)

Output an event to a destination stream.

**Syntax**:
```
| fraud_score | emit_to                |
|-------------|------------------------|
| > 0.9       | blocked_transactions   |
| > 0.7       | review_queue           |
| *           | approved_transactions  |
```

**Semantics**: `emit event to stream_name`

**Emit Patterns**:

```
// Simple emit
emit to approved_auths

// With transformation
emit to alerts with {
  severity: "high",
  timestamp: now()
}

// Conditional emit (in L1, not L4)
// L4 determines which stream, L1 executes the emit
```

---

## Multiple Actions

### Sequential Execution

Multiple action columns execute left-to-right:

```
| credit_score | action_1                | action_2                    | action_3                |
|--------------|-------------------------|-----------------------------|--------------------------
| >= 750       | approve(application)    | send_email(customer)        | setup_account(customer) |
| >= 650       | review(application)     | assign_reviewer(application)| -                       |
| < 650        | deny(application)       | send_denial(customer)       | -                       |
```

**Notes**:
- `-` means "no action" for that column
- All non-empty actions in the matched row execute

### Mixed Return + Actions

Some columns return values, others execute actions:

```
decision_table approve_and_notify
  decide:
    | credit_score | decision | credit_limit | execute_notification           |
    |--------------|------------|--------------|--------------------------------|
    | >= 750       | Approve    | $30,000      | send_approval(application)     |
    | >= 650       | Review     | $15,000      | assign_reviewer(application)   |
    | < 650        | Deny       | $0           | send_denial(application)       |

  return:
    - decision: text
    - credit_limit: money

  execute: notification  // Only 'execute_notification' column is callable
end
```

---

## Action Parameters

### Literal Parameters

```
schedule_retry(payment, 5min)
set_priority(task, "high")
```

### Expression Parameters

```
calculate_fee(amount * 0.03)
notify(customer, message: "Transaction of " + amount + " approved")
```

### Context Parameters

Actions receive full context and can access any field:

```
// Action implementation receives RuleContext
action.execute(context)

// Inside action:
String customerId = context.getValue("customer.id");
Money amount = context.getValue("transaction.amount");
```

---

## Action Result Types

| Action Type | Returns | Side Effect |
|-------------|---------|-------------|
| `assign` | Value | No |
| `calculate` | Computed value | No |
| `lookup` | Looked-up value | No (reads only) |
| `call` | Optional return | Yes (function execution) |
| `emit` | None | Yes (event emission) |

---

## Code Generation

### Return Values

**DSL**:
```
| credit_score | interest_rate   |
|--------------|-----------------|
| >= 800       | 3.5%            |
| >= 700       | 5.5%            |
| *            | 8.0%            |
```

**Generated Java**:
```java
public BigDecimal getInterestRate(int creditScore) {
    if (creditScore >= 800) return new BigDecimal("0.035");
    if (creditScore >= 700) return new BigDecimal("0.055");
    return new BigDecimal("0.080");
}
```

### Executable Actions

**DSL**:
```
| status | execute                       |
|--------|-------------------------------|
| 200    | complete_payment(payment)     |
| 400    | schedule_retry(payment, 5min) |
```

**Generated Java**:
```java
public void handleResponse(int status, Payment payment, ActionContext ctx) {
    if (status == 200) {
        ctx.execute("complete_payment", payment);
    } else if (status == 400) {
        ctx.execute("schedule_retry", payment, Duration.ofMinutes(5));
    }
}
```

---

## Action Type Summary

| Type | Syntax | Returns | Side Effect |
|------|--------|---------|-------------|
| `assign` | `"value"`, `123` | Value | No |
| `calculate` | `a * b + c` | Computed value | No |
| `lookup` | `lookup(table, key)` | External value | No |
| `call` | `function(args)` | Optional | Yes |
| `emit` | `emit to stream` | None | Yes |

---

## Related Documents

- [decision-tables.md](./decision-tables.md) - Decision table syntax
- [condition-types.md](./condition-types.md) - Condition matching
- [action-catalog.md](./action-catalog.md) - Available actions
