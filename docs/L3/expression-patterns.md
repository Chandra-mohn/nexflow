# L3: Expression Patterns

> **Source**: Adapted from rules_engine/function_registry.py
> **Status**: Complete Specification

---

## Overview

Expression patterns define how Nexflow evaluates calculations, comparisons, and data transformations. The expression engine provides:

- **Math Expression Parser**: Shunting Yard algorithm for operator precedence
- **Type-Safe Comparisons**: Null-safe equality and ordering
- **Nested Attribute Resolution**: Deep field access with optional chaining
- **Function Invocation**: Standard library and custom function calls

---

## Math Expression Parser

### Shunting Yard Algorithm

The parser converts infix expressions to postfix notation for evaluation:

```
Input:  a + b * c
Tokens: [a, +, b, *, c]
Output: [a, b, c, *, +]  (postfix)
Result: a + (b * c)      (correct precedence)
```

### Operator Precedence

| Precedence | Operators | Associativity |
|------------|-----------|---------------|
| 1 (lowest) | `or` | Left |
| 2 | `and` | Left |
| 3 | `not` | Right (unary) |
| 4 | `=`, `!=`, `<`, `>`, `<=`, `>=` | Left |
| 5 | `+`, `-` | Left |
| 6 | `*`, `/`, `%` | Left |
| 7 (highest) | Unary `-`, function calls | Right |

### Tokenization

```
Expression: applicant.income * 0.30 - applicant.debt

Tokens:
  - IDENTIFIER: applicant.income
  - OPERATOR: *
  - NUMBER: 0.30
  - OPERATOR: -
  - IDENTIFIER: applicant.debt
```

### Parentheses Support

```
// Without parentheses: a + b * c = a + (b * c)
available = limit - balance * rate

// With parentheses: (a + b) * c
monthly_payment = (principal + interest) * months
```

---

## Type-Safe Value Comparison

### Equality Comparison

```
// String equality
status = "active"
status != "closed"

// Numeric equality
amount = 100.00
count = 5

// Boolean equality
is_verified = true
is_premier = yes  // 'yes' is alias for true
```

### Null-Safe Comparison

```
// Standard null check
email is null
phone is not null

// Null-safe equality (null = null → true)
preferred_name =? backup_name

// Null propagation (null in expression → null result)
total = amount + fee  // If either is null, result is null
```

### Ordering Comparison

```
// Numeric ordering
amount > 1000
credit_score >= 700
balance <= limit

// Date ordering
transaction_date > "2024-01-01"
expiry_date < today()

// String ordering (lexicographic)
last_name >= "M"
```

### Range Comparison

```
// BETWEEN syntax (inclusive)
credit_score between 700 and 850

// Equivalent to:
credit_score >= 700 and credit_score <= 850

// NOT BETWEEN
amount not between 0 and 100
```

---

## Nested Attribute Resolution

### Dot Notation

Access nested fields using dot notation:

```
// Simple nesting
customer.name
customer.address.city
customer.address.coordinates.latitude

// Array indexing
customer.addresses[0].city
customer.phones[1].number
```

### Optional Chaining

Safely access potentially null nested values:

```
// Optional chain operator: ?.
customer?.address?.city

// Returns null if any part is null, instead of error

// Equivalent to:
when customer is null: null
when customer.address is null: null
otherwise: customer.address.city
```

### Default Values

Provide fallback for null values:

```
// Null coalescing: ??
display_name = customer.preferred_name ?? customer.full_name ?? "Unknown"

// With optional chaining
city = customer?.address?.city ?? "Not Provided"
```

---

## Expression Types

### Arithmetic Expressions

```
// Basic arithmetic
total = subtotal + tax
net = gross - deductions
interest = principal * rate
monthly = annual / 12
remainder = total % batch_size

// Complex expressions
debt_to_income = (monthly_debt / monthly_income) * 100
compound_interest = principal * power(1 + rate, periods) - principal
```

### Boolean Expressions

```
// Logical operators
is_eligible = is_active and has_verified_email
show_offer = is_premier or balance > 10000
is_valid = not is_expired

// Compound conditions
qualified = (credit_score >= 700 and income > 50000) or is_premier
```

### Conditional Expressions

```
// When-otherwise (preferred)
fee = when is_premier: 0
      when balance > 5000: 25.00
      when balance > 1000: 35.00
      otherwise: 40.00

// Nested conditions
tier = when score >= 800: "excellent"
       when score >= 700: "good"
       when score >= 600: "fair"
       otherwise: "poor"
```

### String Expressions

```
// Concatenation
full_name = concat(first_name, " ", last_name)
address_line = concat(street, ", ", city, ", ", state, " ", zip)

// Template strings (future)
greeting = "Hello, ${customer.name}!"
```

---

## Function Calls in Expressions

### Syntax

```
function_name(arg1, arg2, ...)
```

### Nested Function Calls

```
// Functions can be nested
formatted = upper(trim(input))
rounded = round(abs(value), 2)
```

### Functions as Expression Components

```
// Functions in arithmetic
adjusted = amount * get_exchange_rate(currency, "USD")

// Functions in conditions
when length(phone) >= 10: "valid"
otherwise: "invalid"

// Functions in assignments
normalized_amount = round(amount * exchange_rate, 2)
```

---

## Code Generation

### Java Target

Expression: `applicant.income * 0.30 - applicant.debt`

Generated Java:
```java
(((Number)_getFieldValue(applicant, "income")).doubleValue() * 0.30
 - ((Number)_getFieldValue(applicant, "debt")).doubleValue())
```

### SQL Target

Expression: `amount * rate / 100`

Generated SQL:
```sql
(amount * rate / 100)
```

### Flink Target

Expression: `customer.address.city`

Generated Flink:
```java
customer.getAddress().getCity()
```

---

## Type Inference

### Automatic Type Detection

```
// Numeric literals
amount = 100       // integer
rate = 0.05        // decimal
big = 1000000000L  // long

// String literals
status = "active"  // string

// Boolean literals
is_active = true   // boolean
is_premier = yes   // boolean (alias)
```

### Expression Type Rules

| Expression | Result Type |
|------------|-------------|
| `int + int` | `integer` |
| `int + decimal` | `decimal` |
| `decimal + decimal` | `decimal` |
| `string + string` | `string` (concat) |
| `int / int` | `decimal` (always) |
| `bool and bool` | `boolean` |
| `when ... otherwise` | Type of branches |

---

## Error Handling

### Compile-Time Errors

```
// Type mismatch
amount = "hello" + 5  // ERROR: Cannot add string and integer

// Unknown identifier
total = unknwon_field  // ERROR: Unknown field 'unknwon_field'

// Invalid operator
result = true + false  // ERROR: Cannot apply '+' to boolean
```

### Runtime Errors

```
// Division by zero
rate = amount / 0  // Runtime error or null (configurable)

// Null reference
city = customer.address.city  // Runtime error if address is null
city = customer?.address?.city  // Returns null instead
```

---

## Best Practices

### 1. Use Parentheses for Clarity

```
// Good: Explicit grouping
result = (a + b) * (c - d)

// Avoid: Relying on precedence
result = a + b * c - d  // What does this mean?
```

### 2. Use Null-Safe Operators

```
// Good: Handle nulls explicitly
city = customer?.address?.city ?? "Unknown"

// Risky: May throw null reference
city = customer.address.city
```

### 3. Extract Complex Expressions

```
// Good: Named intermediate values
debt_ratio = monthly_debt / monthly_income
is_low_risk = credit_score >= 700 and debt_ratio < 0.4
approved = is_low_risk and income > 50000

// Avoid: One giant expression
approved = credit_score >= 700 and (monthly_debt / monthly_income) < 0.4 and income > 50000
```

### 4. Use Functions for Reusability

```
// Good: Reusable function
utilization = calculate_utilization(balance, limit)

// Avoid: Inline calculation everywhere
utilization = round((balance / limit) * 100, 2)
```

---

## Related Documents

- [builtin-functions.md](./builtin-functions.md) - Available functions
- [transform-syntax.md](./transform-syntax.md) - Transform declaration
- [validation-patterns.md](./validation-patterns.md) - Input validation
- [../L4/condition-types.md](../L4/condition-types.md) - Shared with L4 rules
