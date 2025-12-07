# L4: Business Rules Layer

> **Layer**: L4 Business Rules
> **File Extension**: `.rules`
> **Owner**: Business/Risk Team
> **Status**: Specification
> **Version**: 1.0.0

---

## Overview

L4 Business Rules defines the decision logic that L1 processes reference via `route using` and `transform using` statements. This layer supports two complementary paradigms:

1. **Decision Tables**: Matrix-based logic for multi-condition scenarios
2. **Procedural Rules**: If-then-else chains for sequential logic

Both paradigms compile to optimized UDFs for Flink/Spark execution.

---

## Two Paradigms

### Decision Tables

Best for scenarios with many condition combinations forming a matrix:

```
decision_table fraud_screening
  hit_policy first_match

  conditions
    amount_vs_average: range
    location_distance: range
    merchant_risk: equals
  end

  rules
    | amount     | location | merchant | action          |
    |------------|----------|----------|-----------------|
    | > 10x      | > 500mi  | *        | block           |
    | > 5x       | > 100mi  | high     | manual_review   |
    | *          | *        | *        | approve         |
  end
end
```

### Procedural Rules

Best for sequential conditional logic:

```
rule creditCardApplication:
    if applicant.creditScore >= 750
       and applicant.annualIncome > 60000
    then instantApproval

    if applicant.creditScore >= 650
       and applicant.employmentYears >= 2
    then standardApproval

    if applicant.age < 18
       or applicant.creditScore < 500
    then rejectApplication
end
```

---

## When to Use Each

| Scenario | Paradigm | Rationale |
|----------|----------|-----------|
| Many condition combinations | Decision Table | Visual matrix shows all cases |
| Sequential business logic | Procedural | Natural reading order |
| Lookup/mapping rules | Decision Table | Clear input-to-output mapping |
| Complex boolean expressions | Procedural | AND/OR with parentheses |
| Exhaustiveness checking needed | Decision Table | Gap/overlap detection |
| Multiple sequential steps | Procedural | If-then-elseif chains |

---

## How L1 References L4

### Route Using (Branching)

```proc
process fraud_screening
  receive events from transactions
  route using fraud_detection_rules    // ← References L4
  emit approved to approved_txns
  emit flagged to review_queue
  emit blocked to blocked_txns
end
```

### Transform Using (Calculation)

```proc
process risk_scoring
  receive events from applications
  transform using calculate_risk_score  // ← References L4
  emit to scored_applications
end
```

---

## Critical Boundary

> **L1 does NOT contain business logic.**
>
> L1 says: "route using fraud_detection_v2"
> L4 defines: "when risk_score < 0.7 then approved"
>
> L1 only knows outcome names (approved, declined), not the logic that produces them.

---

## Hit Policies (Decision Tables)

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `first_match` | Stop at first matching rule | Most common, ordered priority |
| `single_hit` | Exactly one rule must match | Validation, error if multiple |
| `multi_hit` | Execute all matching rules | Aggregation, multiple actions |

---

## Action Types

L4 rules terminate with actions. Actions are registered implementations:

| Category | Actions | Count |
|----------|---------|-------|
| **Application Processing** | approve, reject, instantApproval, conditionalApproval, manualReview | 6 |
| **Transaction Authorization** | approveTransaction, blockTransaction, decline, temporaryBlock | 4 |
| **Risk Management** | flagForReview, requireVerification, requireStepUpAuth | 5 |
| **Communication** | sendAlert, sendSMSVerification, sendRealTimeAlert | 3 |
| **Account Management** | increaseCreditLimit, decreaseCreditLimit | 2 |

See: [action-catalog.md](./L4/action-catalog.md) for complete catalog (20 actions).

---

## File Structure

```
project/
├── rules/
│   ├── fraud-detection.rules      # Decision table approach
│   ├── credit-approval.rules      # Procedural approach
│   └── velocity-checks.rules      # Hybrid approach
```

---

## Detailed Specifications

| Topic | Document |
|-------|----------|
| Decision table syntax | [L4/decision-tables.md](./L4/decision-tables.md) |
| Condition types | [L4/condition-types.md](./L4/condition-types.md) |
| Action types | [L4/action-types.md](./L4/action-types.md) |
| Procedural rules grammar | [L4/procedural-rules.md](./L4/procedural-rules.md) |
| Action catalog | [L4/action-catalog.md](./L4/action-catalog.md) |
| Examples | [L4/examples/](./L4/examples/) |

---

## Code Generation

L4 rules compile to:
- **Flink**: Java UDFs implementing `MapFunction` or `ProcessFunction`
- **Spark**: Scala/Python UDFs for DataFrame operations

Decision tables optimize to:
- Hash tables for exact match
- Interval trees for ranges
- Decision trees for complex conditions

See: [L6-Compilation-Pipeline.md](./L6-Compilation-Pipeline.md) for compilation details.

---

## Validation

### Compile-Time Checks

1. **Exhaustiveness**: All input combinations covered
2. **Overlap Detection**: No ambiguous rule matches
3. **Type Checking**: Conditions match input types
4. **Action Validation**: Referenced actions exist

### Runtime Guarantees

- First-match semantics enforced
- Default case fallback (wildcard)
- Type-safe comparisons
- Null handling

---

## Integration Example

Complete flow from L1 → L4:

```proc
// L1: authorization_enrichment.proc
process authorization_enrichment
  receive events from auth_requests
    schema auth_request_schema        // L2 reference

  enrich using customers on card_id
    select customer_name, risk_tier

  transform using normalize_amount    // L3 reference

  route using fraud_detection_rules   // L4 reference ←

  emit approved to approved_auths
  emit flagged to manual_review
  emit blocked to blocked_transactions
end
```

```rules
// L4: fraud_detection.rules
decision_table fraud_detection_rules
  hit_policy first_match

  conditions
    amount: range
    risk_tier: equals
    merchant_category: in_set
  end

  rules
    | amount   | risk_tier | merchant_category           | action    |
    |----------|-----------|-----------------------------|-----------|
    | > 10000  | high      | *                           | block     |
    | > 5000   | *         | IN (5912, 5993, 7995)       | flag      |
    | > 1000   | high      | *                           | flag      |
    | *        | *         | *                           | approve   |
  end
end
```

---

## Source Attribution

This specification integrates patterns from:
- **ccdsl**: Decision tables, condition types, action types (~70% reusable)
- **rules_engine**: Procedural rules grammar, action catalog (~85% reusable)

See: [ccdsl-nexflow-feature-matrix.md](./ccdsl-nexflow-feature-matrix.md) and [rules-engine-nexflow-feature-matrix.md](./rules-engine-nexflow-feature-matrix.md)

---

## Related Documents

- [L1-Process-Orchestration-DSL.md](./L1-Process-Orchestration-DSL.md) - How L1 references L4
- [L2-Schema-Registry.md](./L2-Schema-Registry.md) - Data types for conditions
- [L3-Transform-Catalog.md](./L3-Transform-Catalog.md) - Calculation transforms
- [L6-Compilation-Pipeline.md](./L6-Compilation-Pipeline.md) - Code generation

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-01-XX | - | Complete specification from ccdsl + rules_engine |
| 0.1.0 | 2025-01-XX | - | Placeholder created |
