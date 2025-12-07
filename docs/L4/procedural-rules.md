# L4: Procedural Rules Grammar

> **Source**: Adapted from rules_engine/COMPLEX_RULES_SAMPLES.md
> **Status**: Complete Specification

---

## Overview

Procedural rules provide an if-then-else approach to business logic, complementing decision tables. They are best for sequential conditional logic where conditions form a natural priority order.

---

## Basic Syntax

### Single Condition Rule

```
rule simpleCheck:
    if applicant.creditScore >= 700 then approveApplication
end
```

### Multi-Step Rule

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

**Semantics**: Rules evaluate top-to-bottom, first match wins.

---

## Boolean Logic

### AND Logic

All conditions must be true:

```
rule multipleConditions:
    if applicant.creditScore >= 750
       and applicant.annualIncome > 50000
       and applicant.employmentYears >= 2
    then instantApproval
end
```

### OR Logic

Any condition can be true:

```
rule flexibleApproval:
    if applicant.creditScore >= 650
       or applicant.annualIncome > 75000
       or applicant.employmentYears >= 5
    then conditionalApproval
end
```

### Mixed AND/OR

```
rule complexEligibility:
    if applicant.creditScore >= 700
       and applicant.age >= 21
       or applicant.annualIncome > 100000
    then approveApplication
end
```

**Operator Precedence**: `AND` binds tighter than `OR`

The above is equivalent to:
```
(creditScore >= 700 AND age >= 21) OR (annualIncome > 100000)
```

---

## Parentheses for Grouping

### Explicit Grouping

```
rule groupedConditions:
    if (applicant.creditScore >= 650 or applicant.annualIncome > 75000)
       and applicant.employmentYears >= 2
    then conditionalApproval
end
```

**Semantics**:
```
(creditScore >= 650 OR annualIncome > 75000) AND employmentYears >= 2
```

### Complex Grouping

```
rule premiumEligibility:
    if (applicant.creditScore >= 750 and applicant.accountAge > 5)
       or (applicant.annualIncome > 200000 and applicant.netWorth > 1000000)
    then premiumApproval
end
```

---

## Nested Attributes

### Single Level

```
rule employmentCheck:
    if applicant.employment.status = "FULL_TIME"
    then approveApplication
end
```

### Multi-Level

```
rule transactionValidation:
    if transaction.amount > 1000
       and transaction.merchant.category = "5411"
       and transaction.customer.risk.tier = "low"
    then flagForReview
end
```

### Array Access

```
rule addressCheck:
    if customer.addresses[0].country = "US"
       and customer.addresses[0].state = "CA"
    then applyCaliforniaRules
end
```

---

## Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equal | `status = "active"` |
| `!=` | Not equal | `status != "closed"` |
| `>` | Greater than | `amount > 1000` |
| `>=` | Greater or equal | `score >= 700` |
| `<` | Less than | `ratio < 0.3` |
| `<=` | Less or equal | `age <= 65` |

### String Comparisons

```
rule stringCheck:
    if applicant.employmentStatus = "EMPLOYED"
       and applicant.accountType != "RESTRICTED"
    then approveApplication
end
```

### Numeric Comparisons

```
rule numericCheck:
    if applicant.creditScore >= 700
       and applicant.monthlyIncome > 5000
       and applicant.debtRatio < 0.4
    then approveApplication
end
```

---

## Complex Business Rules

### Risk-Based Approval

```
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

### Transaction Fraud Detection

```
rule fraudDetection:
    if transaction.amount > 10000
       and transaction.location != customer.homeLocation
    then flagForReview

    if transaction.amount > 5000
       and transaction.isOnline = true
    then manualReview

    if transaction.merchantCategory = "ATM"
       and transaction.amount > 1000
    then approveTransaction
end
```

### Loan Underwriting

```
rule loanUnderwriting:
    if applicant.creditScore >= 800
       and applicant.debtToIncomeRatio < 0.3
    then approveWithBestRate

    if applicant.creditScore >= 720
       and applicant.employmentYears >= 5
    then approveWithStandardRate

    if applicant.creditScore >= 650
       and applicant.downPayment > 0.2
    then conditionalApproval

    if applicant.creditScore < 600
    then requireManualReview
end
```

---

## NOT Operator

### Workaround Pattern

NOT is not directly supported. Use comparison instead:

```
// Instead of:
// if not applicant.bankruptcyHistory then approveApplication

// Use:
rule bankruptcyCheck:
    if applicant.bankruptcyHistory = false
    then approveApplication
end
```

### Boolean Flag Check

```
rule flagCheck:
    if applicant.isFraudulent = false
       and applicant.isBlacklisted = false
    then processApplication
end
```

---

## Grammar (EBNF)

```ebnf
procedural_rule ::=
    "rule", identifier, ":",
    { rule_statement },
    "end" ;

rule_statement ::=
    "if", boolean_expression, "then", action_name ;

boolean_expression ::=
    comparison_expression
  | boolean_expression, "and", boolean_expression
  | boolean_expression, "or", boolean_expression
  | "(", boolean_expression, ")" ;

comparison_expression ::=
    attribute_path, comparison_operator, value ;

attribute_path ::=
    identifier, { ".", identifier } ;

comparison_operator ::=
    "=" | "!=" | ">" | ">=" | "<" | "<=" ;

action_name ::=
    identifier ;
```

---

## Code Generation

### Simple Rule

**DSL**:
```
rule creditCheck:
    if applicant.creditScore >= 700 then approveApplication
end
```

**Generated Java**:
```java
public String creditCheck(RuleContext context) {
    int creditScore = context.getInt("applicant.creditScore");
    if (creditScore >= 700) {
        return "approveApplication";
    }
    return null;
}
```

### Complex Rule

**DSL**:
```
rule riskAssessment:
    if applicant.creditScore >= 750
       and applicant.annualIncome > 60000
    then instantApproval

    if applicant.creditScore >= 650
       and applicant.employmentYears >= 2
    then standardApproval

    if applicant.creditScore < 600
    then rejectApplication
end
```

**Generated Java**:
```java
public String riskAssessment(RuleContext context) {
    int creditScore = context.getInt("applicant.creditScore");
    double annualIncome = context.getDouble("applicant.annualIncome");
    int employmentYears = context.getInt("applicant.employmentYears");

    if (creditScore >= 750 && annualIncome > 60000) {
        return "instantApproval";
    }
    if (creditScore >= 650 && employmentYears >= 2) {
        return "standardApproval";
    }
    if (creditScore < 600) {
        return "rejectApplication";
    }
    return null;
}
```

---

## When to Use Procedural Rules

| Scenario | Use Procedural Rules |
|----------|---------------------|
| Sequential priority logic | Yes |
| Complex boolean expressions | Yes |
| Few conditions, clear order | Yes |
| Many condition combinations | No (use decision table) |
| Need exhaustiveness checking | No (use decision table) |
| Visual matrix representation | No (use decision table) |

---

## Best Practices

1. **Order by priority**: Most important/specific rules first
2. **Use parentheses**: Make boolean logic explicit
3. **Keep rules focused**: One business decision per rule
4. **Include catch-all**: Add final rule for unmatched cases
5. **Test each path**: Each if-then is a test case

---

## Performance Characteristics

- **Compilation Time**: ~63ms average for complex rules
- **Execution Time**: ~0.67ms average
- **Memory Usage**: ~2KB per compiled rule
- **Complexity**: Unlimited AND/OR combinations

---

## Related Documents

- [decision-tables.md](./decision-tables.md) - Alternative paradigm
- [action-catalog.md](./action-catalog.md) - Available actions
- [../L4-Business-Rules.md](../L4-Business-Rules.md) - L4 overview
