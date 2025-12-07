# L4: Decision Tables Specification

> **Source**: Adapted from ccdsl/DSL_DECISION_TABLES.md
> **Status**: Complete Specification

---

## Overview

Decision tables provide a tabular, visual way to express complex conditional logic with multiple conditions and actions. They are industry-proven (DMN, Drools) and ideal for credit card business rules.

**Key Capabilities**:
- Exact matching and range conditions
- Complex expressions (AND, OR, NOT)
- Function calls in conditions
- Return values (lookup tables)
- Executable actions (workflow integration)
- Multiple action columns
- First-match semantics with optional priorities
- Exhaustiveness checking and overlap detection

---

## Basic Syntax

### Minimal Decision Table

```
decision_table determine_action
  given:
    - status: number

  decide:
    | status | action    |
    |--------|-----------|
    | 200    | Proceed   |
    | 400    | Retry     |
    | 500    | Error     |

  return:
    - action: text
end
```

### Full-Featured Decision Table

```
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
    | priority | credit_score | debt_ratio | account_age | annual_income | decision | credit_limit      | review_required |
    |----------|--------------|------------|-------------|---------------|------------|-------------------|-----------------|
    | 1        | >= 800       | < 0.2      | > 5         | > $100,000    | Approve    | $50,000           | no              |
    | 2        | >= 750       | < 0.3      | > 3         | > $75,000     | Approve    | $30,000           | no              |
    | 3        | >= 700       | < 0.35     | > 2         | > $50,000     | Approve    | $20,000           | yes             |
    | 4        | >= 650       | < 0.4      | > 2         | > $40,000     | Review     | calculate_limit() | yes             |
    | 5        | >= 600       | < 0.35     | > 5         | *             | Review     | $10,000           | yes             |
    | 6        | *            | *          | *           | *             | Deny       | $0                | no              |

  return:
    - decision: text
    - credit_limit: money
    - review_required: boolean
end
```

**Key Elements**:
- `priority`: Optional explicit ordering (lower number = higher priority)
- Multiple condition columns: All must match (AND logic)
- Action columns follow condition columns (no separator needed)
- Multiple action columns: All are evaluated/executed
- Wildcard `*`: Matches any value (default case)

---

## Hit Policies

### first_match (Default)

Stop at first matching rule. Most common policy.

```
decision_table get_fee
  hit_policy first_match

  decide:
    | account_type | fee   |
    |--------------|-------|
    | premier      | $10   |
    | standard     | $25   |
    | *            | $35   |
  end
end
```

### single_hit

Exactly one rule must match. Error if multiple or none match.

```
decision_table validate_status
  hit_policy single_hit

  decide:
    | status   | valid   |
    |----------|---------|
    | active   | true    |
    | pending  | true    |
    | closed   | false   |
  end
end
```

### multi_hit

Execute all matching rules. Used for aggregation or multiple actions.

```
decision_table apply_discounts
  hit_policy multi_hit

  decide:
    | customer_type | amount   | discount   |
    |---------------|----------|------------|
    | premier       | *        | 10%        |
    | *             | > $1000  | 5%         |
    | *             | *        | 0%         |
  end
end
```

---

## Return Values vs Executable Actions

### Return Values (Lookup Tables)

```
decision_table get_interest_rate
  given:
    - credit_score: number

  decide:
    | credit_score | interest_rate   |
    |--------------|-----------------|
    | >= 800       | 3.5%            |
    | >= 750       | 4.5%            |
    | >= 700       | 5.5%            |
    | >= 650       | 7.5%            |
    | *            | 12.0%           |

  return:
    - interest_rate: percentage
end

// Usage in L1:
// rate = get_interest_rate(customer.credit_score)
```

### Executable Actions

```
decision_table handle_payment_response
  given:
    - result: text
    - status: number
    - payment: payment

  decide:
    | result  | status | execute                           |
    |---------|--------|-----------------------------------|
    | success | 200    | complete_payment(payment)         |
    | failure | 400    | schedule_retry(payment, 5min)     |
    | failure | 500    | schedule_retry(payment, 30min)    |
    | pending | 102    | mark_as_pending(payment)          |
    | error   | *      | alert_operations(payment, status) |

  execute: yes
end

// Usage in L1:
// handle_payment_response(result, status, payment)
// Action is executed directly based on matching row
```

### Mixed: Returns + Actions

```
decision_table approve_and_notify
  given:
    - credit_score: number
    - application: application

  decide:
    | credit_score | decision | credit_limit | execute_notification           |
    |--------------|------------|--------------|--------------------------------|
    | >= 750       | Approve    | $30,000      | send_approval_email(application) |
    | >= 650       | Review     | $15,000      | assign_to_reviewer(application)  |
    | < 650        | Deny       | $0           | send_denial_email(application)   |

  return:
    - decision: text
    - credit_limit: money

  execute: notification
end
```

---

## Computed Actions

### Expressions in Actions

```
decision_table calculate_dynamic_fee
  given:
    - balance: money
    - days_late: number

  decide:
    | balance      | days_late | fee_amount                      |
    |--------------|-----------|----------------------------------|
    | > $10,000    | 1-7       | balance * 0.01                  |
    | > $10,000    | 8-30      | $15 + (days_late - 7) * $2      |
    | <= $10,000   | 1-7       | $35                             |
    | <= $10,000   | 8-30      | $35 + (days_late - 7) * $3      |

  return:
    - fee_amount: money
end
```

### Function Calls in Actions

```
decision_table assign_credit_limit
  given:
    - credit_score: number
    - annual_income: money
    - customer: customer

  decide:
    | credit_score | annual_income | credit_limit                          |
    |--------------|---------------|---------------------------------------|
    | >= 800       | *             | calculate_premium_limit(customer)     |
    | >= 700       | > $100,000    | min(annual_income * 0.3, $50,000)    |
    | >= 700       | <= $100,000   | annual_income * 0.2                  |
    | >= 650       | *             | calculate_standard_limit(customer)    |
    | *            | *             | $5,000                               |

  return:
    - credit_limit: money
end
```

---

## Grammar (EBNF)

```ebnf
decision_table_definition ::=
    "decision_table", identifier,
    [ "hit_policy", hit_policy_type ],
    [ "description", string_literal ],
    "given", ":", { input_parameter },
    "decide", ":", decision_matrix,
    [ return_specification | execute_specification | hybrid_specification ],
    "end" ;

hit_policy_type ::=
    "first_match" | "single_hit" | "multi_hit" ;

input_parameter ::=
    "-", identifier, ":", type_spec ;

decision_matrix ::=
    table_header,
    { table_row } ;

table_header ::=
    "|", [ "priority", "|" ], { condition_column, "|" }, "→", { action_column, "|" } ;

table_row ::=
    "|", [ integer, "|" ], { condition_cell, "|" }, "→", { action_cell, "|" } ;

return_specification ::=
    "return", ":", { return_parameter } ;

execute_specification ::=
    "execute", ":", ( "yes" | identifier | "multi" ) ;
```

---

## Code Generation

### Match Statement (Simple)

**DSL**:
```
decision_table get_fee
  given:
    - account_type: text
    - days_late: number

  decide:
    | account_type | days_late | fee      |
    |--------------|-----------|----------|
    | premier      | 1-7       | $15      |
    | premier      | 8-30      | $25      |
    | standard     | 1-7       | $35      |
    | *            | *         | $50      |

  return:
    - fee: money
end
```

**Generated Java (Flink)**:
```java
public Money getFee(String accountType, int daysLate) {
    if ("premier".equals(accountType) && daysLate >= 1 && daysLate <= 7) {
        return Money.dollars(15);
    }
    if ("premier".equals(accountType) && daysLate >= 8 && daysLate <= 30) {
        return Money.dollars(25);
    }
    if ("standard".equals(accountType) && daysLate >= 1 && daysLate <= 7) {
        return Money.dollars(35);
    }
    return Money.dollars(50);  // default
}
```

### Complex Conditions

**DSL**:
```
decision_table route_transaction
  given:
    - amount: money
    - risk_score: number

  decide:
    | condition                                | processor   |
    |------------------------------------------|-------------|
    | amount > $10,000 AND risk_score > 70     | manual      |
    | amount > $10,000                         | review      |
    | *                                        | standard    |

  return:
    - processor: text
end
```

**Generated Java**:
```java
public String routeTransaction(Money amount, int riskScore) {
    if (amount.greaterThan(Money.dollars(10000)) && riskScore > 70) {
        return "manual";
    }
    if (amount.greaterThan(Money.dollars(10000))) {
        return "review";
    }
    return "standard";
}
```

---

## Validation

### Exhaustiveness Checking

Warn if no wildcard row exists:

```
WARNING: Decision table 'get_fee' may not be exhaustive
  Missing cases for: account_type NOT IN (premier, standard)

  Suggestion: Add wildcard row:
  | *  | *  | $50 |
```

### Overlap Detection

Error if multiple rows can match:

```
ERROR: Decision table 'calculate_fee' has overlapping rules
  Row 2: | premier | 1-7  | $15 |
  Row 3: | premier | 1-10 | $20 |

  Conflict: days_late = 5 matches both rows

  Fix: Add explicit priority or make conditions mutually exclusive
```

### Type Checking

```
ERROR: Type mismatch in decision table 'approve_credit'
  Column 'credit_score' expects: number
  Row 3 has: "high" (text)
```

---

## Best Practices

1. **Always include default case**: Use `*` wildcard in last row
2. **Order by specificity**: Most specific conditions first
3. **Use explicit priorities**: When row ordering isn't sufficient
4. **Keep tables focused**: One table = one decision
5. **Document complex conditions**: Add description for clarity
6. **Test each row**: Each row is a test case

---

## Related Documents

- [condition-types.md](./condition-types.md) - Detailed condition syntax
- [action-types.md](./action-types.md) - Action column types
- [../L4-Business-Rules.md](../L4-Business-Rules.md) - L4 overview
