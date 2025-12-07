# JOLT vs Nexflow Transform: Comparison Analysis

**Date**: December 7, 2025
**Decision**: Continue with Nexflow Transform Generator

---

## Overview

| Aspect | JOLT | Nexflow Transform |
|--------|------|-------------------|
| **Purpose** | JSON → JSON restructuring | Domain data → Domain data transformation |
| **Specification** | JSON-based declarative spec | Custom DSL with business semantics |
| **Runtime** | Java library (interpret at runtime) | Code generator (compile-time Java) |
| **Target** | Structural transformation | Business logic + structural mapping |

---

## Fundamental Difference: Paradigm

### JOLT: Declarative JSON Restructuring
```json
[{
  "operation": "shift",
  "spec": {
    "client": {
      "employeeDetails": {
        "*": {
          "name": "employees[].fullName"
        }
      }
    }
  }
}]
```
- **Interprets** spec at runtime
- **Moves/copies** data between paths
- **No computation** - pure structural mapping

### Nexflow: Business Transform DSL
```
transform calculate_risk_score
    input
        amount: decimal, required
        velocity_24h: integer, required
    end
    output
        risk_score: decimal
    end
    apply
        base_score = when amount > 10000: 0.4
            when amount > 5000: 0.2
            otherwise: 0.05
        risk_score = min(base_score + velocity_factor, 1.0)
    end
end
```
- **Generates** compiled Java code
- **Computes** values with expressions
- **Business logic** - validation, caching, error handling

---

## Feature Comparison

| Feature | JOLT | Nexflow Transform |
|---------|------|-------------------|
| **Field Mapping** | ✅ Shift operation | ✅ Mappings block |
| **Default Values** | ✅ Default operation | ✅ `??` null coalesce |
| **Remove Fields** | ✅ Remove operation | ❌ Not explicit (planned) |
| **Array Handling** | ✅ Cardinality operation | ⚠️ Limited |
| **Arithmetic** | ❌ Not supported | ✅ Full expressions |
| **Conditionals** | ❌ Not supported | ✅ `when/otherwise` |
| **Function Calls** | ❌ Not supported | ✅ User-defined + built-in |
| **Validation** | ❌ Not supported | ✅ Input/output validation |
| **Caching** | ❌ Not supported | ✅ With TTL |
| **Error Handling** | ❌ Not supported | ✅ `on_error` block |
| **Type Safety** | ❌ Untyped JSON | ✅ Typed schemas |
| **Streaming** | ⚠️ Batch only | ✅ Flink integration |

---

## Where Each Excels

### JOLT Strengths
1. **Declarative simplicity** - No code, just JSON spec
2. **Path-based navigation** - Powerful wildcards (`*`, `$`, `@`)
3. **Runtime flexibility** - Change transforms without recompile
4. **Ecosystem** - Apache NiFi integration, online tester
5. **Learning curve** - Lower barrier for simple mappings

### Nexflow Transform Strengths
1. **Business logic** - Computation, conditions, functions
2. **Type safety** - Schema-linked input/output
3. **Validation** - Built-in input/output/invariant checks
4. **Performance** - Compiled Java, not interpreted
5. **Streaming** - Native Flink state management
6. **Composability** - `use` block for transform chaining
7. **Error handling** - Structured error flows

---

## Equivalent Operations

### Simple Field Mapping

**JOLT:**
```json
{
  "operation": "shift",
  "spec": {
    "transaction": {
      "id": "enriched.transaction_id",
      "amount": "enriched.amount"
    }
  }
}
```

**Nexflow:**
```
mappings
    enriched.transaction_id = transaction.transaction_id
    enriched.amount = transaction.amount
end
```

### Default Values

**JOLT:**
```json
{
  "operation": "default",
  "spec": {
    "currency": "USD"
  }
}
```

**Nexflow (both syntaxes supported):**
```
// Preferred - more readable
enriched.currency = transaction.currency default "USD"

// Also supported - developer shorthand
enriched.currency = transaction.currency ?? "USD"
```

### What JOLT Can't Do (Nexflow Can)

**Computed values:**
```
normalized_amount = amount * get_exchange_rate(currency, "USD")
```

**Conditional logic:**
```
risk_score = when amount > 10000: 0.4
    when amount > 5000: 0.2
    otherwise: 0.05
```

**Validation:**
```
validate_input
    amount > 0: "Amount must be positive"
end
```

---

## Decision Rationale

**For Nexflow's use case (Flink streaming pipelines with business logic)**, JOLT is insufficient:

1. **Computation requirement** - `amount * rate` not possible in JOLT
2. **Conditionals** - `when/otherwise` essential for business rules
3. **Validation** - `validate_input/output` critical for data quality
4. **Streaming** - Flink state management for caching
5. **Error handling** - Structured error flows for production

**Verdict**: JOLT is complementary for simple ETL, not a replacement for Nexflow Transform.

---

## References
- [JOLT GitHub](https://github.com/bazaarvoice/jolt)
- [Mastering JOLT Spec Operations](https://dev.to/sunil_yaduvanshi/mastering-jolt-spec-operations-a-guide-with-examples-197o)
- [Apache NiFi JoltTransformJSON](https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-standard-nar/1.9.2/org.apache.nifi.processors.standard.JoltTransformJSON/index.html)
