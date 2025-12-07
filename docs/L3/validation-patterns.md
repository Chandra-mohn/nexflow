# L3: Validation Patterns

> **Source**: Adapted from ccdsl/core/CORE_DSL_SPECIFICATION.md
> **Status**: Complete Specification

---

## Overview

Validation patterns ensure data quality and constraint enforcement in Nexflow transforms. They provide:

- **Input Validation**: Pre-condition checks before transformation
- **Output Validation**: Post-condition checks after transformation
- **Constraint Enforcement**: Business rule validation
- **Data Quality Rules**: Format, range, and consistency checks

---

## Validation Types

### Pre-Transform Validation

Validate inputs before transformation begins:

```xform
transform calculate_interest
  input
    principal: decimal
    rate: decimal
    days: integer
  end

  validate_input
    principal >= 0: "Principal cannot be negative"
    rate >= 0 and rate <= 100: "Rate must be between 0 and 100"
    days > 0: "Days must be positive"
  end

  output: decimal

  apply
    output = round(principal * (rate / 100) * (days / 365), 2)
  end
end
```

### Post-Transform Validation

Validate outputs after transformation:

```xform
transform normalize_amount
  input
    amount: decimal
    currency: string
  end

  output: decimal

  apply
    rate = get_exchange_rate(currency, "USD")
    output = round(amount * rate, 2)
  end

  validate_output
    output >= 0: "Normalized amount cannot be negative"
    output < 1000000000: "Amount exceeds maximum threshold"
  end
end
```

### Invariant Validation

Conditions that must hold throughout transformation:

```xform
transform_block account_update
  input
    account: account_schema
    transaction: transaction_schema
  end

  invariant
    // Balance must always be consistent
    account.balance = account.credit_limit - account.available_credit
  end

  apply
    // ... transformation logic ...
  end
end
```

---

## Constraint Types

### Required Field Validation

```xform
validate_input
  // Field must be present and non-null
  customer_id is not null: "Customer ID is required"
  amount is not null: "Amount is required"

  // Field must have value
  email is not null and length(email) > 0: "Email is required"
end
```

### Type Validation

```xform
validate_input
  // Numeric validation
  amount is number: "Amount must be a number"

  // String validation
  status is string: "Status must be a string"

  // Date validation
  transaction_date is date: "Transaction date must be a valid date"
end
```

### Range Validation

```xform
validate_input
  // Numeric ranges
  credit_score between 300 and 850: "Credit score out of valid range"
  age >= 18 and age <= 120: "Age must be between 18 and 120"

  // Date ranges
  expiry_date > today(): "Card must not be expired"
  birth_date < today(): "Birth date cannot be in the future"
end
```

### Pattern Validation

```xform
validate_input
  // Regex patterns
  email matches "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$": "Invalid email format"
  phone matches "^\\+[1-9]\\d{1,14}$": "Phone must be E.164 format"
  postal_code matches "^[0-9]{5}(-[0-9]{4})?$": "Invalid postal code"

  // Credit card patterns
  card_number matches "^[0-9]{16,19}$": "Invalid card number format"
end
```

### Enumeration Validation

```xform
validate_input
  // Value must be in set
  status in ["active", "pending", "closed"]: "Invalid status"
  currency in ["USD", "EUR", "GBP", "JPY"]: "Unsupported currency"
  card_type in ["credit", "debit", "prepaid"]: "Invalid card type"
end
```

### Length Validation

```xform
validate_input
  // String length
  length(account_number) = 16: "Account number must be 16 digits"
  length(cvv) between 3 and 4: "CVV must be 3 or 4 digits"
  length(description) <= 500: "Description too long"
end
```

---

## Validation Behaviors

### on_invalid Actions

Define what happens when validation fails:

```xform
transform process_transaction
  validate_input
    amount > 0: "Amount must be positive"
  end

  on_invalid
    reject: true              // Reject the record
    error_code: "INVALID_AMT"
    error_message: $validation_error
    emit_to: invalid_transactions  // Send to error stream
  end
end
```

### Validation Modes

```xform
transform lenient_parse
  validation_mode: warn  // warn, fail, skip

  // warn: Log warning, continue processing
  // fail: Stop processing, raise error
  // skip: Silently skip invalid records
end
```

### Partial Validation

Validate only specific fields:

```xform
transform partial_update
  validate_only: [amount, currency, status]

  // Only validates specified fields
  // Other fields pass through unchanged
end
```

---

## Cross-Field Validation

### Field Dependencies

```xform
validate_input
  // Conditional requirement
  when card_type = "credit":
    credit_limit is not null: "Credit limit required for credit cards"
  end

  // Cross-field comparison
  available_credit <= credit_limit: "Available credit cannot exceed limit"
  payment_due_date > statement_date: "Due date must be after statement date"
end
```

### Mutual Exclusivity

```xform
validate_input
  // One or the other, not both
  (email is not null and phone is null) or
  (email is null and phone is not null) or
  (email is not null and phone is not null): "At least one contact method required"

  // Exactly one
  exactly_one_of(preferred_contact, [email, phone, mail]): "Choose one contact method"
end
```

### Aggregate Validation

```xform
validate_input
  // Sum validation
  sum(line_items.amount) = total_amount: "Line items must sum to total"

  // Count validation
  count(addresses) >= 1: "At least one address required"
  count(phones where type = "mobile") <= 3: "Maximum 3 mobile phones"
end
```

---

## Data Quality Rules

### Consistency Checks

```xform
validate_consistency
  // Balance consistency
  current_balance + available_credit = credit_limit: "Balance equation violated"

  // Date consistency
  opened_date <= first_transaction_date: "First transaction before account opened"
  closed_date is null or closed_date >= opened_date: "Close date before open date"
end
```

### Referential Integrity

```xform
validate_references
  // Foreign key validation
  customer_id exists_in customers: "Unknown customer"
  product_code exists_in products where status = "active": "Invalid or inactive product"
  merchant_id exists_in merchants: "Unknown merchant"
end
```

### Business Rules

```xform
validate_business_rules
  // Credit decision rules
  when application_type = "instant":
    credit_score >= 700: "Instant approval requires score >= 700"
  end

  // Fraud prevention rules
  when is_international = true:
    customer.international_enabled = true: "International transactions not enabled"
  end

  // Regulatory rules
  when country = "US":
    ssn is not null: "SSN required for US customers"
  end
end
```

---

## Validation Error Handling

### Error Structure

```xform
// Validation errors contain:
// - field: The field that failed validation
// - rule: The validation rule that failed
// - message: Human-readable error message
// - value: The actual value that failed
// - code: Error code for programmatic handling
```

### Error Aggregation

```xform
transform validate_application
  validation_mode: aggregate  // Collect all errors

  validate_input
    applicant.name is not null: "Name required"
    applicant.email is not null: "Email required"
    applicant.income > 0: "Income must be positive"
    applicant.credit_score between 300 and 850: "Invalid credit score"
  end

  on_invalid
    // Returns all validation errors, not just first
    emit_all_errors: true
    emit_to: validation_errors
  end
end
```

### Custom Error Codes

```xform
validate_input
  amount > 0:
    message: "Amount must be positive"
    code: "ERR_INVALID_AMOUNT"
    severity: error

  credit_score >= 600:
    message: "Credit score below minimum"
    code: "WARN_LOW_SCORE"
    severity: warning
end
```

---

## Recalculation Patterns

### Auto-Recalculation on Change

When a field changes, automatically recalculate dependent fields:

```xform
transform_block account_balance_update
  on_change [balance, credit_limit]
    recalculate
      available_credit = credit_limit - balance
      utilization_pct = round((balance / credit_limit) * 100, 2)
      is_overlimit = balance > credit_limit
    end
  end
end
```

### Cascade Recalculation

```xform
transform_block statement_update
  on_change [transactions]
    recalculate
      // First tier
      statement_balance = sum(transactions.amount)

      // Second tier (depends on first)
      minimum_payment = max(25.00, statement_balance * 0.02)

      // Third tier (depends on second)
      payment_due_date = add_days(statement_date, 21)
    end
  end
end
```

---

## Best Practices

### 1. Validate Early

```xform
// Good: Validate at input
transform process_payment
  validate_input
    amount > 0: "Invalid amount"
  end
  // ... processing ...
end

// Avoid: Late validation
transform process_payment
  apply
    // ... lots of processing ...
    when amount <= 0:
      raise_error("Invalid amount")  // Too late!
  end
end
```

### 2. Use Specific Error Messages

```xform
// Good: Specific, actionable
validate_input
  credit_score between 300 and 850:
    "Credit score ${credit_score} is outside valid range (300-850)"
end

// Avoid: Vague
validate_input
  credit_score between 300 and 850: "Invalid score"
end
```

### 3. Group Related Validations

```xform
// Good: Logical grouping
validate_input
  // Customer validations
  customer_id is not null: "Customer ID required"
  customer.status = "active": "Customer must be active"

  // Amount validations
  amount > 0: "Amount must be positive"
  amount <= customer.credit_limit: "Amount exceeds limit"
end
```

### 4. Separate Business Rules from Data Validation

```xform
// Data validation (L3)
validate_input
  amount is number: "Amount must be numeric"
  amount >= 0: "Amount cannot be negative"
end

// Business rules (L4)
// Move complex business logic to L4 decision tables
```

---

## Related Documents

- [expression-patterns.md](./expression-patterns.md) - Expression syntax
- [transform-syntax.md](./transform-syntax.md) - Transform declaration
- [builtin-functions.md](./builtin-functions.md) - Validation functions
- [../L4-Business-Rules.md](../L4-Business-Rules.md) - Business rule validation
