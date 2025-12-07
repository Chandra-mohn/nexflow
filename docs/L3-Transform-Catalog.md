# L3: Transform Catalog Layer

> **Layer**: L3 Transform Catalog
> **File Extension**: `.xform`
> **Owner**: Data Engineering Team
> **Status**: Specification
> **Version**: 1.0.0

---

## Overview

L3 Transform Catalog defines reusable data transformations for Nexflow pipelines. It provides:

- **Expression Patterns**: Math parsing, type-safe comparisons, nested attribute resolution
- **Validation Patterns**: Input validation, constraint enforcement, data quality rules
- **Transform Syntax**: Declaration format, input/output types, composition
- **Builtin Functions**: Standard library of math, string, date, and conversion functions

---

## How L1 References L3

```proc
process authorization_enrichment
  receive events from auth_events
    schema auth_event_schema

  // Field-level transform
  transform amount using normalize_currency
    from_currency: currency
    to_currency: "USD"

  // Block-level transform (multiple fields)
  transform using auth_enrichment_block

  // Inline expression
  derive available_credit = credit_limit - current_balance

  // Lookup transform
  enrich using customer_lookup on card_id
    select customer_name, risk_tier, credit_score

  emit to enriched_auths
end
```

---

## Transform Levels

L3 supports three levels of transformation complexity:

### 1. Field-Level Transforms

Single field operations with type preservation or conversion:

```xform
transform normalize_phone
  input: string
  output: string

  apply
    // Remove non-digits
    digits_only = regex_replace(input, "[^0-9]", "")
    // Format as E.164
    output = concat("+1", digits_only)
  end
end
```

### 2. Expression-Level Transforms

Derived field calculations with multiple inputs:

```xform
transform calculate_utilization
  input
    current_balance: decimal
    credit_limit: decimal
  end

  output: decimal [range: 0..100]

  apply
    output = round((current_balance / credit_limit) * 100, 2)
  end
end
```

### 3. Block-Level Transforms

Grouped operations for complex mappings (50+ fields):

```xform
transform_block auth_enrichment_block
  version 2.1.0

  input
    auth: auth_event_schema
    customer: customer_schema
    product: product_config_schema
  end

  output: enriched_auth_schema

  mappings
    // Direct mappings
    transaction_id = auth.transaction_id
    card_id = auth.card_id
    amount = auth.amount

    // Derived fields
    customer_name = customer.full_name
    risk_tier = customer.risk_tier
    credit_limit = product.credit_limit

    // Calculated fields
    utilization_pct = round((auth.amount / product.credit_limit) * 100, 2)
    days_since_last_txn = date_diff(auth.event_timestamp, customer.last_activity_date, "days")

    // Conditional mappings
    risk_flag = when customer.risk_tier = "high" and auth.amount > 1000: "REVIEW"
                otherwise: "PASS"
  end
end
```

---

## Expression Language

L3 uses a type-safe expression language shared with L4:

### Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `=`, `!=`, `<`, `>`, `<=`, `>=` |
| Logical | `and`, `or`, `not` |
| Null-safe | `??` (coalesce), `?.` (optional chain) |

### Expressions

```xform
// Arithmetic
available_credit = credit_limit - current_balance

// Conditional
fee_amount = when is_premier: 0
             when balance > 5000: 25.00
             otherwise: 35.00

// Null coalescing
display_name = preferred_name ?? full_name ?? "Unknown"

// Function calls
formatted_date = format_date(transaction_date, "YYYY-MM-DD")
risk_score = round(raw_score * 100, 2)
```

---

## Transform Composition

Transforms can be composed for reusability:

### Sequential Composition

```xform
transform full_amount_normalization
  compose
    normalize_currency       // Step 1: Convert to USD
    round_to_cents          // Step 2: Round to 2 decimals
    apply_minimum           // Step 3: Ensure minimum value
  end
end
```

### Parallel Composition

```xform
transform_block parallel_enrichment
  parallel
    enrich_customer         // Independent enrichment 1
    enrich_merchant         // Independent enrichment 2
    enrich_product          // Independent enrichment 3
  end

  then
    calculate_risk_score    // Depends on all enrichments
  end
end
```

---

## Type Safety

### Input/Output Type Annotations

```xform
transform safe_divide
  input
    numerator: decimal
    denominator: decimal
  end

  output: decimal, nullable

  apply
    output = when denominator = 0: null
             otherwise: numerator / denominator
  end
end
```

### Type Coercion Rules

| From | To | Behavior |
|------|----|----|
| `integer` | `decimal` | Automatic |
| `decimal` | `integer` | Requires `truncate()` or `round()` |
| `string` | `integer` | Requires `parse_int()` |
| `string` | `decimal` | Requires `parse_decimal()` |
| `timestamp` | `date` | Automatic (truncates time) |
| `date` | `timestamp` | Automatic (midnight) |

---

## Purity and Side Effects

Transforms are classified by their side effects:

### Pure Transforms (Default)

No side effects, deterministic output:

```xform
transform calculate_interest
  pure: true  // Default

  input
    balance: decimal
    rate: decimal
  end

  output: decimal

  apply
    output = round(balance * (rate / 100 / 365), 2)
  end
end
```

### Impure Transforms

May have side effects (logging, external calls):

```xform
transform lookup_exchange_rate
  pure: false
  cache: 5 minutes

  input
    from_currency: currency_code
    to_currency: currency_code
  end

  output: decimal

  apply
    output = external_call("exchange_service", from_currency, to_currency)
  end
end
```

---

## File Structure

```
project/
├── transforms/
│   ├── field/
│   │   ├── normalize_phone.xform
│   │   └── format_currency.xform
│   ├── expression/
│   │   ├── calculate_utilization.xform
│   │   └── calculate_risk_score.xform
│   └── block/
│       ├── auth_enrichment_block.xform
│       └── statement_generation_block.xform
```

---

## Example Schemas

Complete working examples demonstrating transform patterns:

| Example | Pattern | Description |
|---------|---------|-------------|
| [normalize-amount.xform](./L3/examples/normalize-amount.xform) | Field + Expression | Currency conversion with exchange rate lookup |
| [calculate-risk-score.xform](./L3/examples/calculate-risk-score.xform) | Block | Multi-factor risk scoring with weighted components |

---

## Detailed Specifications

| Topic | Document |
|-------|----------|
| Expression patterns | [L3/expression-patterns.md](./L3/expression-patterns.md) |
| Validation patterns | [L3/validation-patterns.md](./L3/validation-patterns.md) |
| Transform syntax | [L3/transform-syntax.md](./L3/transform-syntax.md) |
| Builtin functions | [L3/builtin-functions.md](./L3/builtin-functions.md) |
| Examples | [L3/examples/](./L3/examples/) |

---

## Integration with Other Layers

### L1 → L3 (Transform Resolution)

```proc
transform using auth_enrichment_block   // L3 resolves full transform
```

### L2 → L3 (Schema Validation)

L3 transforms validate input/output against L2 schemas:

```xform
transform_block auth_enrichment
  input: auth_event_schema              // Validated against L2
  output: enriched_auth_schema          // Validated against L2
end
```

### L3 → L4 (Expression Sharing)

L3 and L4 share the expression language:

```
// Same syntax in L3 transforms and L4 rules
when amount > 1000 and risk_tier = "high": "REVIEW"
otherwise: "PASS"
```

### L3 → L6 (Code Generation)

L6 compiles L3 transforms to target platforms:

```yaml
transforms:
  auth_enrichment_block:
    flink: "AuthEnrichmentOperator.java"
    spark: "auth_enrichment.py"
    sql: "auth_enrichment_view.sql"
```

---

## Source Attribution

This specification integrates patterns from:
- **rules_engine**: Math expression parser, function registry
- **ccdsl**: Validation patterns, constraint definitions
- **Native Nexflow**: Transform syntax, composition patterns

See: [ccdsl-nexflow-feature-matrix.md](./ccdsl-nexflow-feature-matrix.md)

---

## Related Documents

- [L1-Process-Orchestration-DSL.md](./L1-Process-Orchestration-DSL.md) - How L1 references L3
- [L2-Schema-Registry.md](./L2-Schema-Registry.md) - Schema input/output validation
- [L4-Business-Rules.md](./L4-Business-Rules.md) - Shared expression language
- [L5-Infrastructure-Binding.md](./L5-Infrastructure-Binding.md) - Physical transform mapping

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-01-XX | - | Complete specification |
| 0.1.0 | 2025-01-XX | - | Placeholder created |
