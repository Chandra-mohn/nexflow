# L3: Transform Syntax

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Transform syntax defines the declaration format for Nexflow transformations. This document covers:

- **Transform Declaration**: How to define transforms
- **Input/Output Signatures**: Type annotations and schema references
- **Apply Blocks**: Transformation logic
- **Composition Patterns**: Combining transforms

---

## Transform Declaration

### Basic Structure

```xform
transform transform_name
  version: "1.0.0"           // Optional version
  description: "..."         // Optional description
  pure: true                 // Purity annotation (default: true)

  input
    field1: type
    field2: type
  end

  output: type

  apply
    // transformation logic
  end
end
```

### Minimal Transform

```xform
transform double_value
  input: decimal
  output: decimal

  apply
    output = input * 2
  end
end
```

### Complete Transform

```xform
transform calculate_late_fee
  version: "2.1.0"
  description: "Calculate late payment fee based on balance and days overdue"
  pure: true

  input
    balance: decimal
    days_overdue: integer
    is_first_offense: boolean
  end

  output
    fee_amount: decimal
    fee_waived: boolean
    waiver_reason: string, nullable
  end

  validate_input
    balance >= 0: "Balance cannot be negative"
    days_overdue >= 0: "Days overdue cannot be negative"
  end

  apply
    base_fee = when balance >= 5000: 40.00
               when balance >= 1000: 35.00
               otherwise: 25.00

    fee_amount = when is_first_offense: min(base_fee, 25.00)
                 otherwise: base_fee

    fee_waived = days_overdue <= 3 and is_first_offense
    waiver_reason = when fee_waived: "First offense grace period"
                    otherwise: null
  end

  validate_output
    fee_amount >= 0: "Fee cannot be negative"
  end
end
```

---

## Input Specification

### Single Input

```xform
transform uppercase_name
  input: string
  output: string

  apply
    output = upper(input)
  end
end
```

### Multiple Inputs

```xform
transform calculate_interest
  input
    principal: decimal
    rate: decimal [range: 0..100]
    days: integer [range: 1..365]
  end

  output: decimal

  apply
    output = round(principal * (rate / 100) * (days / 365), 2)
  end
end
```

### Schema Reference Input

```xform
transform enrich_transaction
  input
    transaction: transaction_schema    // Reference L2 schema
    customer: customer_schema
  end

  output: enriched_transaction_schema

  apply
    // Access schema fields
    output.customer_name = customer.full_name
    output.risk_tier = customer.risk_tier
  end
end
```

### Named vs Positional

```xform
// Named inputs (preferred for 2+ parameters)
transform calculate_fee
  input
    amount: decimal
    rate: decimal
  end
end

// Positional (simple transforms)
transform double
  input: decimal
  output: decimal
end
```

---

## Output Specification

### Single Output

```xform
transform to_uppercase
  input: string
  output: string

  apply
    output = upper(input)
  end
end
```

### Multiple Outputs

```xform
transform split_name
  input: string

  output
    first_name: string
    last_name: string
    middle_initial: string, nullable
  end

  apply
    parts = split(input, " ")
    first_name = parts[0]
    last_name = parts[length(parts) - 1]
    middle_initial = when length(parts) > 2: substring(parts[1], 0, 1)
                     otherwise: null
  end
end
```

### Nullable Output

```xform
transform safe_parse_int
  input: string
  output: integer, nullable

  apply
    output = when matches(input, "^-?[0-9]+$"): parse_int(input)
             otherwise: null
  end
end
```

### Output with Constraints

```xform
transform calculate_percentage
  input
    part: decimal
    whole: decimal
  end

  output: decimal [range: 0..100, precision: 5, scale: 2]

  apply
    output = when whole = 0: 0
             otherwise: round((part / whole) * 100, 2)
  end
end
```

---

## Apply Block

### Basic Assignment

```xform
apply
  result = input * 2
end
```

### Sequential Operations

```xform
apply
  // Operations execute in order
  step1 = input + 10
  step2 = step1 * 2
  step3 = round(step2, 2)
  output = step3
end
```

### Conditional Logic

```xform
apply
  output = when condition1: value1
           when condition2: value2
           when condition3: value3
           otherwise: default_value
end
```

### Local Variables

```xform
apply
  // Local variables (not in output)
  temp_value = input * rate
  adjusted = temp_value - discount

  // Output assignment
  output = round(adjusted, 2)
end
```

### Function Calls

```xform
apply
  // Single function
  upper_name = upper(name)

  // Nested functions
  normalized = trim(lower(input))

  // Function with multiple args
  formatted = format_date(date_value, "YYYY-MM-DD")
end
```

---

## Transform Block (Multi-Field)

### Structure

```xform
transform_block block_name
  version: "1.0.0"

  input
    source1: schema1
    source2: schema2
  end

  output: output_schema

  mappings
    // Field mappings
  end
end
```

### Direct Mappings

```xform
transform_block customer_flatten
  input
    customer: customer_schema
  end

  output: flat_customer_schema

  mappings
    // Direct copy
    customer_id = customer.customer_id
    email = customer.email

    // Nested access
    city = customer.address.city
    state = customer.address.state

    // Rename
    full_name = customer.name
  end
end
```

### Calculated Mappings

```xform
transform_block transaction_enrichment
  input
    txn: transaction_schema
    customer: customer_schema
    exchange: exchange_rates
  end

  output: enriched_transaction_schema

  mappings
    // Direct
    transaction_id = txn.transaction_id
    card_id = txn.card_id

    // Calculated
    amount_usd = round(txn.amount * exchange.rate, 2)
    utilization = round((txn.amount / customer.credit_limit) * 100, 2)

    // Conditional
    risk_flag = when txn.amount > 1000 and customer.risk_tier = "high": "REVIEW"
                otherwise: "PASS"

    // Function
    formatted_date = format_date(txn.event_timestamp, "YYYY-MM-DD HH:mm:ss")
  end
end
```

---

## Composition Patterns

### Sequential Composition

Apply transforms in sequence:

```xform
transform normalize_and_validate
  compose sequential
    trim_whitespace     // Step 1
    normalize_case      // Step 2
    validate_format     // Step 3
  end
end
```

### Parallel Composition

Apply independent transforms concurrently:

```xform
transform_block parallel_enrichment
  compose parallel
    enrich_customer      // Independent
    enrich_merchant      // Independent
    enrich_product       // Independent
  end

  then sequential
    merge_enrichments    // Depends on all above
    calculate_risk       // Depends on merge
  end
end
```

### Conditional Composition

Choose transform based on condition:

```xform
transform process_transaction
  compose conditional
    when transaction_type = "domestic": process_domestic
    when transaction_type = "international": process_international
    otherwise: process_unknown
  end
end
```

### Reusable Composition

Reference shared transform blocks:

```xform
transform_block standard_enrichment
  use
    common_field_mapping    // Reusable block
    standard_validations    // Reusable block
  end

  mappings
    // Additional custom mappings
    custom_field = calculate_custom(input)
  end
end
```

---

## Purity Annotations

### Pure (Default)

Deterministic, no side effects:

```xform
transform calculate_tax
  pure: true  // Default

  input
    amount: decimal
    rate: decimal
  end

  output: decimal

  apply
    output = round(amount * (rate / 100), 2)
  end
end
```

### Impure

May have side effects or non-determinism:

```xform
transform get_current_rate
  pure: false

  input
    currency: string
  end

  output: decimal

  apply
    // External service call
    output = external_call("rate_service", currency)
  end
end
```

### Caching for Impure Transforms

```xform
transform get_exchange_rate
  pure: false
  cache
    ttl: 5 minutes
    key: [from_currency, to_currency]
  end

  input
    from_currency: string
    to_currency: string
  end

  output: decimal

  apply
    output = external_call("exchange_api", from_currency, to_currency)
  end
end
```

---

## Versioning

### Version Declaration

```xform
transform calculate_fee
  version: "2.1.0"
  previous_version: "2.0.0"
  compatibility: backward

  // ... rest of transform
end
```

### Version Chain

```
calculate_fee v1.0.0 (initial)
    ↓
calculate_fee v1.1.0 (added discount parameter)
    ↓
calculate_fee v2.0.0 (BREAKING: changed fee calculation)
```

---

## Error Handling

### Validation Errors

```xform
transform safe_process
  validate_input
    amount > 0: "Amount must be positive"
  end

  on_validation_error
    action: reject
    error_code: "INVALID_INPUT"
  end

  apply
    output = process(input)
  end
end
```

### Runtime Errors

```xform
transform division_with_fallback
  input
    numerator: decimal
    denominator: decimal
  end

  output: decimal

  apply
    output = when denominator = 0: 0
             otherwise: numerator / denominator
  end

  on_error
    action: use_default
    default: 0
    log_level: warning
  end
end
```

---

## Grammar (EBNF)

```ebnf
transform_def     = "transform" identifier [version] [purity]
                    input_spec output_spec [validate_input]
                    apply_block [validate_output] "end" ;

transform_block   = "transform_block" identifier [version]
                    input_spec output_spec [validate_input]
                    mappings_block [validate_output] "end" ;

identifier        = letter { letter | digit | "_" } ;
version           = "version:" string_literal ;
purity            = "pure:" ("true" | "false") ;

input_spec        = "input" (single_type | field_list) ;
output_spec       = "output" (single_type | field_list) ;

single_type       = ":" type_ref ["," qualifiers] ;
field_list        = field_def { field_def } "end" ;
field_def         = identifier ":" type_ref ["," qualifiers] ;

type_ref          = base_type | schema_ref | constrained_type ;
base_type         = "string" | "integer" | "decimal" | "boolean"
                  | "date" | "timestamp" | "uuid" ;
schema_ref        = identifier "_schema" ;
constrained_type  = base_type "[" constraints "]" ;
constraints       = constraint { "," constraint } ;
constraint        = "range:" range | "length:" length | "pattern:" string ;

qualifiers        = qualifier { "," qualifier } ;
qualifier         = "nullable" | "required" | "default:" expression ;

validate_input    = "validate_input" { validation_rule } "end" ;
validate_output   = "validate_output" { validation_rule } "end" ;
validation_rule   = expression ":" string_literal ;

apply_block       = "apply" { statement } "end" ;
mappings_block    = "mappings" { mapping } "end" ;

statement         = assignment | conditional ;
mapping           = identifier "=" expression ;
assignment        = identifier "=" expression ;

conditional       = "when" expression ":" expression
                    { "when" expression ":" expression }
                    "otherwise:" expression ;

expression        = term { binary_op term } ;
term              = factor | unary_op factor ;
factor            = literal | identifier | function_call
                  | "(" expression ")" ;
function_call     = identifier "(" [expression { "," expression }] ")" ;
```

---

## Related Documents

- [expression-patterns.md](./expression-patterns.md) - Expression syntax
- [validation-patterns.md](./validation-patterns.md) - Validation patterns
- [builtin-functions.md](./builtin-functions.md) - Standard functions
- [../L3-Transform-Catalog.md](../L3-Transform-Catalog.md) - Overview
