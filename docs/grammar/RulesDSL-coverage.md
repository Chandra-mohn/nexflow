# RulesDSL.g4 Feature Coverage

> **Grammar Version**: 1.0.0
> **Verification Date**: 2025-11-29

---

## Coverage Summary

| Category | Features | Covered | Status |
|----------|----------|---------|--------|
| Rule Paradigms | 2 | 2 | ✅ 100% |
| Hit Policies | 3 | 3 | ✅ 100% |
| Condition Types | 7 | 7 | ✅ 100% |
| Action Types | 5 | 5 | ✅ 100% |
| Return/Execute | 3 | 3 | ✅ 100% |

**Overall Coverage**: ~95%

---

## 1. Rule Paradigms (2/2) ✅

| Paradigm | Grammar Rule | Example Syntax |
|----------|--------------|----------------|
| Decision Table | `decisionTableDef` | `decision_table fraud_screening ... end` |
| Procedural Rules | `proceduralRuleDef` | `rule creditCardApplication: ... end` |

---

## 2. Hit Policies (3/3) ✅

| Policy | Grammar Rule | Behavior |
|--------|--------------|----------|
| `first_match` | `hitPolicyType` | Stop at first matching rule (default) |
| `single_hit` | `hitPolicyType` | Exactly one rule must match |
| `multi_hit` | `hitPolicyType` | Execute all matching rules |

---

## 3. Condition Types (7/7) ✅

| Type | Grammar Rule | Example |
|------|--------------|---------|
| Exact match | `exactMatch` | `200`, `"active"`, `true` |
| Range | `rangeCondition` | `700-799`, `$1000-$5000` |
| Comparison | `comparisonCondition` | `>= 700`, `< 0.3`, `!= "closed"` |
| Set membership | `setCondition` | `IN (active, pending)`, `NOT IN (...)` |
| Pattern matching | `patternCondition` | `matches "^4.*"`, `ends_with "@company.com"` |
| Null check | `nullCondition` | `is null`, `is not null` |
| Wildcard | `WILDCARD` | `*` (matches any) |

---

## 4. Action Types (5/5) ✅

| Type | Grammar Rule | Example |
|------|--------------|---------|
| Assign | `assignAction` | `"Approve"`, `$30000` |
| Calculate | `calculateAction` | `balance * 0.01`, `principal * rate / 12` |
| Lookup | `lookupAction` | `lookup(currency_rates, currency)` |
| Call | `callAction` | `complete_payment(payment)`, `schedule_retry(payment, 5min)` |
| Emit | `emitAction` | `emit to approved_transactions` |

---

## 5. Return/Execute Specifications (3/3) ✅

| Specification | Grammar Rule | Example |
|---------------|--------------|---------|
| Return values | `returnSpec` | `return: - decision: text` |
| Execute actions | `executeSpec` | `execute: yes` |
| Hybrid (both) | `hybridSpec` | `return: ... execute: notification` |

---

## 6. Procedural Rules Features ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Single condition | `ruleStatement` | `if score >= 700 then approve` |
| AND logic | `booleanExpr` | `score >= 700 AND income > 50000` |
| OR logic | `booleanExpr` | `score >= 800 OR is_premier` |
| Parentheses | `booleanTerm` | `(score >= 650 OR income > 75000) AND years >= 2` |
| Nested attributes | `fieldPath` | `applicant.employment.status` |
| Array access | `fieldPath` | `customer.addresses[0].country` |

---

## 7. Expression Features ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Arithmetic | `arithmeticExpr` | `balance * 0.01 + $15` |
| Function calls | `functionCall` | `min(amount, limit)`, `round(value, 2)` |
| Field paths | `fieldPath` | `transaction.merchant.category` |
| Named arguments | `actionArg` | `schedule_retry(payment, delay: 5min)` |
| Complex conditions | `expressionCondition` | `(amount > 10000 AND risk_score > 70)` |

---

## 8. Literal Types ✅

| Type | Grammar Rule | Example |
|------|--------------|---------|
| String | `STRING` | `"active"`, `"APPROVED"` |
| Integer | `INTEGER` | `200`, `700`, `-5` |
| Decimal | `DECIMAL` | `3.14`, `0.035` |
| Money | `MONEY_LITERAL` | `$1,000`, `$50,000.00` |
| Percentage | `PERCENTAGE_LITERAL` | `3.5%`, `10%` |
| Boolean | `BOOLEAN` | `true`, `false`, `yes`, `no` |

---

## Example Decision Table (Validating Grammar)

```rules
decision_table approve_credit_application
  hit_policy first_match
  description "Complex credit approval with multiple conditions and actions"

  given:
    - credit_score: number
    - debt_ratio: percentage
    - account_age: number
    - annual_income: money
    - customer: customer

  decide:
    | priority | credit_score | debt_ratio | account_age | annual_income | decision | credit_limit | review_required |
    |----------|--------------|------------|-------------|---------------|------------|--------------|-----------------|
    | 1        | >= 800       | < 0.2      | > 5         | > $100,000    | Approve    | $50,000      | no              |
    | 2        | >= 750       | < 0.3      | > 3         | > $75,000     | Approve    | $30,000      | no              |
    | 3        | >= 700       | < 0.35     | > 2         | > $50,000     | Approve    | $20,000      | yes             |
    | 4        | >= 650       | < 0.4      | > 2         | > $40,000     | Review     | calculate_limit() | yes         |
    | 5        | >= 600       | < 0.35     | > 5         | *             | Review     | $10,000      | yes             |
    | 6        | *            | *          | *           | *             | Deny       | $0           | no              |

  return:
    - decision: text
    - credit_limit: money
    - review_required: boolean
end
```

---

## Example Procedural Rule (Validating Grammar)

```rules
rule riskBasedApproval:
    if applicant.creditScore >= 800
       and applicant.existingDebt < 20000
    then instantApproval

    if applicant.creditScore >= 700
       and applicant.existingDebt < 50000
       and applicant.employmentYears >= 2
    then approveApplication

    if applicant.creditScore >= 600
       and applicant.annualIncome > 75000
    then conditionalApproval

    if applicant.creditScore < 600
       or applicant.existingDebt > 100000
    then rejectApplication
end
```

---

## Example with Actions and Lookup

```rules
decision_table handle_payment_response
  given:
    - result: text
    - status: number
    - payment: payment

  decide:
    | result  | status | execute                           |
    |---------|--------|-----------------------------------|
    | success | 200    | complete_payment(payment)         |
    | failure | 400    | schedule_retry(payment, delay: 5min) |
    | failure | 500    | schedule_retry(payment, delay: 30min) |
    | pending | 102    | mark_as_pending(payment)          |
    | error   | *      | alert_operations(payment, status) |

  execute: yes
end
```

---

## Notes

1. **Semantic Validation** - The grammar parses syntax; the compiler must validate:
   - Exhaustiveness checking (wildcard row present)
   - Overlap detection (no ambiguous matches)
   - Type checking (conditions match input types)
   - Action validation (referenced actions exist)

2. **Decision Tables vs Procedural Rules**:
   - Decision tables: Many condition combinations, visual matrix
   - Procedural rules: Sequential priority logic, complex boolean expressions

3. **L1 Integration**:
   - L1 references L4 via `route using` and `transform using`
   - L1 knows outcome names (approved, declined), not logic

4. **Future Considerations**:
   - Explicit priority column optimization
   - Gap analysis for exhaustiveness
   - Overlap detection warnings

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-29 | Initial coverage verification |
