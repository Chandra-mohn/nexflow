# L4: Condition Types

> **Source**: Adapted from ccdsl/DSL_DECISION_TABLES.md
> **Status**: Complete Specification

---

## Overview

Condition types define how values in decision table condition cells are matched against input data. Nexflow supports six primary condition types.

---

## 1. Exact Match (`equals`)

**Syntax**: Literal value

```
| status | action    |
|--------|-----------|
| 200    | Success   |
| 404    | NotFound  |
| 500    | Error     |
```

**Semantics**: `status == 200`

**Supported Types**:
- Numbers: `200`, `3.14`, `-5`
- Strings: `"active"`, `"PENDING"`
- Booleans: `true`, `false`
- Enums: `APPROVED`, `DECLINED`

---

## 2. Range Conditions (`range`)

### Numeric Ranges

```
| credit_score | rating      |
|--------------|-------------|
| 800-850      | Excellent   |
| 750-799      | Very Good   |
| 700-749      | Good        |
| 650-699      | Fair        |
| 300-649      | Poor        |
```

**Semantics**: `credit_score >= 800 AND credit_score <= 850`

### Money Ranges

```
| balance           | fee_tier   |
|-------------------|------------|
| $0-$1,000         | Tier1      |
| $1,001-$10,000    | Tier2      |
| > $10,000         | Tier3      |
```

### Date Ranges

```
| payment_date      | status     |
|-------------------|------------|
| <= due_date       | OnTime     |
| due_date + 1-7    | Grace      |
| > due_date + 7    | Late       |
```

---

## 3. Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `>` | Greater than | `> 700` |
| `>=` | Greater or equal | `>= 750` |
| `<` | Less than | `< 0.3` |
| `<=` | Less or equal | `<= $10,000` |
| `=` | Equal (explicit) | `= "active"` |
| `!=` | Not equal | `!= "suspended"` |

**Example**:
```
| credit_score | debt_ratio | decision   |
|--------------|------------|------------|
| >= 700       | < 0.3      | Approve    |
| >= 650       | < 0.4      | Review     |
| < 650        | *          | Deny       |
```

---

## 4. Set Membership (`in_set`)

### IN Operator

```
| account_status              | action     |
|-----------------------------|------------|
| IN (active, pending)        | Process    |
| IN (suspended, frozen)      | Block      |
```

**Semantics**: `account_status IN ['active', 'pending']`

### NOT IN Operator

```
| merchant_category                    | risk_level   |
|--------------------------------------|--------------|
| IN (gambling, adult, crypto)         | High         |
| NOT IN (grocery, gas, pharmacy)      | Review       |
```

**Semantics**: `merchant_category NOT IN ['grocery', 'gas', 'pharmacy']`

---

## 5. Pattern Matching (`pattern`)

### Regex Patterns

```
| card_number              | card_type   |
|--------------------------|-------------|
| matches "^4.*"           | Visa        |
| matches "^5[1-5].*"      | Mastercard  |
| matches "^3[47].*"       | Amex        |
| matches "^6.*"           | Discover    |
```

**Semantics**: `card_number.matches("^4.*")`

### Wildcard Patterns

```
| email                    | domain      |
|--------------------------|-------------|
| ends_with "@company.com" | Internal    |
| contains "@gmail"        | Consumer    |
| *                        | Other       |
```

---

## 6. Null Check (`null_check`)

```
| customer_id      | action         |
|------------------|----------------|
| is null          | CreateCustomer |
| is not null      | UpdateCustomer |
```

**Semantics**: `customer_id == null` or `customer_id != null`

---

## 7. Wildcard (`any`)

**Syntax**: `*`

```
| credit_score | decision   |
|--------------|------------|
| >= 700       | Approve    |
| >= 600       | Review     |
| *            | Deny       |
```

**Semantics**: Matches any value. Used for default/catch-all cases.

**Best Practice**: Always include a wildcard row as the last row.

---

## Complex Expressions

### AND Logic (Implicit)

All conditions in a row must match:

```
| credit_score | debt_ratio | account_age | decision   |
|--------------|------------|-------------|------------|
| >= 700       | < 0.3      | > 2         | Approve    |
```

**Semantics**: `(credit_score >= 700) AND (debt_ratio < 0.3) AND (account_age > 2)`

### OR Logic (Explicit)

Use parentheses for OR:

```
| condition                                      | decision   |
|------------------------------------------------|------------|
| (credit_score >= 800) OR (debt_ratio < 0.2)   | Approve    |
| (account_age > 10) OR (annual_income > 200k)  | Review     |
```

### NOT Logic

```
| account_status      | action     |
|---------------------|------------|
| NOT "suspended"     | Process    |
| NOT IN (closed, inactive) | Review |
```

### Nested Expressions

```
| condition                                                           | decision   |
|---------------------------------------------------------------------|------------|
| (credit_score >= 700 AND debt_ratio < 0.3) OR account_age > 10    | Approve    |
| (credit_score < 600) AND NOT (account_age > 5)                     | Deny       |
```

---

## Function Calls in Conditions

### Built-in Functions

```
| condition                           | action     |
|-------------------------------------|------------|
| is_vip_customer(customer_id)        | FastTrack  |
| has_outstanding_balance(account_id) | Collect    |
| days_since(last_payment) > 30       | Late       |
```

### Custom Validation Functions

```
| condition                                  | decision   |
|--------------------------------------------|------------|
| validate_credit_history(customer) = true   | Approve    |
| check_fraud_score(transaction) < 50        | Process    |
| verify_identity(customer, document) = true | Proceed    |
```

### Combined Functions and Operators

```
| condition                                              | action     |
|--------------------------------------------------------|------------|
| calculate_dti(income, debts) < 0.4 AND credit_score >= 700 | Approve |
| get_account_age(account) > 2 OR is_referral(customer)      | Review  |
```

---

## Type Compatibility

| Condition Type | Compatible Input Types |
|----------------|------------------------|
| `equals` | string, number, boolean, enum |
| `range` | number, money, date, timestamp |
| `in_set` | string, number, enum |
| `pattern` | string |
| `null_check` | any nullable type |
| `any` | all types |

---

## Condition Type Summary

| Type | Syntax Example | Use Case |
|------|----------------|----------|
| `equals` | `200`, `"active"` | Exact value match |
| `range` | `700-799`, `> $1000` | Numeric/date ranges |
| `in_set` | `IN (a, b, c)` | Set membership |
| `pattern` | `matches "^4.*"` | Regex matching |
| `null_check` | `is null` | Null handling |
| `any` | `*` | Default/catch-all |

---

## Related Documents

- [decision-tables.md](./decision-tables.md) - Decision table syntax
- [action-types.md](./action-types.md) - Action column types
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - Type definitions
