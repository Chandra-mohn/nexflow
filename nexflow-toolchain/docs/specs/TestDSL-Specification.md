#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# TestDSL Specification

## Overview

TestDSL is a domain-specific language for business-authored acceptance tests in Nexflow. It enables Subject Matter Experts (SMEs) to articulate expected system behavior independently of implementation, providing verification that DSL implementations match business intent.

---

## Design Principles

### Independent Specification

Tests are written **independently** of implementation. SMEs define expected behavior before or alongside rule development, not derived from existing code. This ensures tests verify business intent, not just implementation correctness.

### Schema-Aware Type Safety

Test data construction validates against schema definitions at compile time. Field names, types, and constraints are enforced - no runtime surprises from malformed test data.

### Zero Glue Code

Unlike Gherkin/Cucumber which requires step definitions in Java, TestDSL compiles directly to executable tests. The toolchain generates all harness code, maintaining the zero-code covenant.

### Logical Abstraction

Tests reference logical names (streams, stores) not physical infrastructure. The same test runs against mock infrastructure in CI and real infrastructure in integration environments.

---

## File Extension

`.test`

---

## Audience

- Business Analysts
- Risk Officers
- QA Engineers
- Compliance Officers

---

## Visibility Model

TestDSL has layered visibility into other Nexflow artifacts:

| Layer | Visible | How Used |
|-------|---------|----------|
| Schema | Always | Construct typed test data, validate fields |
| Rules | Yes | Invoke by name, assert outcomes |
| Transform | Yes | Invoke by name, verify mappings |
| Process | Yes | Invoke by name, mock streams |
| Infra | Logical names only | Mock streams/stores, never physical addresses |

### What Is NOT Visible

- Kafka broker addresses
- MongoDB connection strings
- Spark cluster configurations
- Parquet file paths
- Any physical infrastructure details

---

## Test Structure

### Basic Syntax

```
test "<description>"
    given <setup>
    when <action>
    then <assertions>
end
```

### Complete Example

```
test "high debt ratio declines application"
    given Application
        application_id = "APP-001"
        customer_id = "C123"
        debt_to_income = 0.50
        credit_score = 720

    when evaluate credit_decision_rules

    then CreditDecision
        outcome = "decline"
        reason contains "debt"
end
```

---

## Test Types

### Rule Tests

Test business logic in isolation:

```
test "minimum credit score requirement"
    given Applicant
        credit_score = 580
        debt_to_income = 0.30

    when evaluate credit_eligibility_rules

    then outcome = "decline"
    and reason = "credit_score_below_minimum"
end
```

### Transform Tests

Test data mapping correctness:

```
test "enrichment adds risk score"
    given Application
        customer_id = "C123"
        loan_amount = 50000

    and Customer from customer_store
        customer_id = "C123"
        credit_score = 720

    when transform enrich_application

    then EnrichedApplication
        risk_score exists
        risk_score >= 0
        customer_name = "Jane Doe"
end
```

### Process Tests

Test end-to-end flow behavior:

```
test "high value orders route to priority queue"
    given Order on orders_input
        order_id = "O1"
        total = 15000

    when process order_routing

    then expect Order on priority_orders
        order_id = "O1"
    and expect nothing on standard_orders
end
```

### Integration Tests

Test system boundaries with state:

```
test "customer lookup enriches application"
    given state customer_store contains
        Customer
            customer_id = "C123"
            name = "Jane Doe"
            credit_score = 750

    given Application on applications
        customer_id = "C123"
        loan_amount = 25000

    when process application_enrichment

    then expect EnrichedApplication on enriched_applications
        customer_name = "Jane Doe"
        credit_score = 750
end
```

---

## Data Sources

### Inline Data

```
given Order
    order_id = "O1"
    total = 100.00
    currency = "USD"
```

### File Reference

Supports CSV, JSON, Parquet:

```
given orders from file "test_data/orders.csv"

given applications from file "test_data/applications.json"

given transactions from file "test_data/q4_transactions.parquet"
```

### Logical Store Query

```
given customers from customer_store
    where region = "US"
    and status = "active"
```

### Snapshot Reference

```
given baseline from snapshot "prod_2024_01_15"
```

---

## Data Comparison Modes

### 1. Atomic (Row-Level)

Exact record matching - every row must match expected:

```
test "all applications processed correctly"
    given applications from file "test_data/applications.csv"

    when process credit_decisioning

    then expect decisions matches file "expected/decisions.csv"
        compare by application_id
        exact match on outcome, reason, score
        tolerance 0.01 on calculated_rate
end
```

**Use cases**: Regression testing, migration validation, audit verification

### 2. Aggregate (Summary-Level)

Statistical validation without row-by-row comparison:

```
test "daily settlement totals balance"
    given trades from file "test_data/eod_trades.csv"

    when process settlement_aggregation

    then expect settlements
        count = 1547
        sum(amount) = 15_847_293.50
        sum(amount) by currency
            USD = 10_500_000.00
            EUR = 5_347_293.50
        count where status = "settled" >= 1500
        count where status = "failed" <= 47
end
```

**Use cases**: Reconciliation, EOD balancing, regulatory reporting validation

### 3. Hybrid (Atomic + Aggregate)

Combined validation for both row integrity and summary correctness:

```
test "order fulfillment completeness"
    given orders from file "test_data/orders.csv"

    when process order_fulfillment

    then expect fulfilled_orders
        // Aggregate checks
        count = count(orders)
        sum(total) = sum(orders.total)

        // Atomic spot-checks
        record where order_id = "ORD-001"
            status = "shipped"
            shipped_date exists

        record where order_id = "ORD-999"
            status = "cancelled"
            cancel_reason = "out_of_stock"

        // Distribution checks
        count by status
            shipped >= 900
            cancelled <= 100
end
```

**Use cases**: Data quality validation, transformation verification

---

## Comparison Operators

### Equality and Bounds

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Exact match | `count = 1000` |
| `~=` | Approximate with tolerance | `sum(amount) ~= 1000000 tolerance 0.01%` |
| `>=` | Greater than or equal | `count >= 950` |
| `<=` | Less than or equal | `error_count <= 10` |
| `>` | Greater than | `score > 600` |
| `<` | Less than | `latency < 100` |
| `between` | Range inclusive | `avg(score) between 600 and 800` |

### Matching and Containment

| Operator | Description | Example |
|----------|-------------|---------|
| `matches` | Pattern or file match | `matches file "expected.csv"` |
| `contains` | Substring or subset | `reason contains "debt"` |
| `contains all from` | All records present | `contains all from "required_ids.csv"` |
| `contains none from` | No records present | `contains none from "blacklist.csv"` |
| `exists` | Field is present | `shipped_date exists` |
| `not exists` | Field is absent | `error_message not exists` |

---

## Assertion Keywords

### Row-Level Assertions

```
exact match on <fields>
compare by <key_fields>
tolerance <value> on <numeric_fields>
ignore <fields>
```

### Aggregate Assertions

```
count [where <condition>]
sum(<field>) [by <group_fields>]
avg(<field>) [by <group_fields>]
min(<field>)
max(<field>)
distinct(<field>)
```

### Distribution Assertions

```
count by <field>
percent by <field>
histogram <field> buckets <n>
```

### Existence Assertions

```
record where <condition> exists
record where <condition> not exists
contains all from <source>
contains none from <source>
```

### Comparison Targets

```
matches file <path>
matches snapshot <name>
matches query <logical_store> where <condition>
```

---

## Large Dataset Handling

For production-scale validation:

```
test "quarterly reconciliation"
    mode streaming
    parallelism 8

    given transactions from file "q4_transactions.parquet"
        partition by region

    when process quarterly_aggregation

    then expect quarterly_summary
        compare aggregate only
        sum(amount) by region matches file "expected_q4_totals.csv"
            tolerance 0.001%
end
```

### Performance Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode streaming` | Process without loading all in memory | `batch` |
| `parallelism <n>` | Parallel comparison threads | `1` |
| `compare aggregate only` | Skip row-level for large datasets | `false` |
| `partition by <field>` | Partition data for parallel processing | none |
| `sample <n>` | Random sample for spot-checks | all |

---

## Diff Reporting

When comparisons fail, TestDSL generates actionable diff reports:

```
test "migration data integrity" FAILED

ATOMIC DIFF (first 10 mismatches):
+------------------+------------------+------------------+
| application_id   | expected_outcome | actual_outcome   |
+------------------+------------------+------------------+
| APP-1234         | approve          | decline          |
| APP-5678         | decline          | approve          |
+------------------+------------------+------------------+

AGGREGATE DIFF:
+------------------+------------------+------------------+
| metric           | expected         | actual           |
+------------------+------------------+------------------+
| count            | 10000            | 9998             |
| sum(amount)      | 5000000.00       | 4999847.50       |
| approve_rate     | 0.75             | 0.73             |
+------------------+------------------+------------------+

ROOT CAUSE HINTS:
- 2 records missing (APP-9901, APP-9902)
- 152.50 amount variance traced to APP-1234
```

---

## Test Organization

### Test Suites

Group related tests:

```
suite "Credit Decisioning"

    test "approve high credit score"
        ...
    end

    test "decline low credit score"
        ...
    end

    test "decline high debt ratio"
        ...
    end

end
```

### Tags and Filtering

```
test "regulatory compliance check"
    tags [compliance, audit, quarterly]
    ...
end
```

Run filtered:
```
nexflow test --tags compliance
nexflow test --tags "audit and quarterly"
```

### Setup and Teardown

```
suite "Order Processing"

    before each
        given state inventory_store contains
            Product { sku = "SKU-001", quantity = 100 }
    end

    after each
        clear state inventory_store
    end

    test "order reduces inventory"
        ...
    end

end
```

---

## Execution Model

### Test Isolation

Each test runs in isolation:
- Fresh mock streams
- Clean state stores
- No side effects between tests

### Parallel Execution

Tests within a suite can run in parallel unless marked:
```
test "sequential dependency test"
    sequential
    ...
end
```

### Timeout Control

```
test "long running aggregation"
    timeout 5 minutes
    ...
end
```

---

## Integration with CI/CD

### Command Line

```bash
# Run all tests
nexflow test

# Run specific test file
nexflow test src/test/credit_rules.test

# Run with coverage
nexflow test --coverage

# Generate JUnit XML report
nexflow test --report junit --output test-results.xml

# Run tagged tests
nexflow test --tags "smoke and not slow"
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
| 2 | Test compilation error |
| 3 | Test execution error |

---

## Examples

### Financial Services: Credit Decision

```
test "standard credit approval flow"
    given CreditApplication
        application_id = "APP-2024-001"
        customer_id = "CUST-500"
        requested_amount = 25000
        term_months = 36

    and Customer from customer_store
        customer_id = "CUST-500"
        credit_score = 750
        annual_income = 85000
        existing_debt = 15000

    when process credit_decisioning

    then expect CreditDecision on decisions_output
        application_id = "APP-2024-001"
        outcome = "approve"
        approved_amount = 25000
        interest_rate between 5.5 and 7.5

    and expect persist to decision_audit_store
        application_id = "APP-2024-001"
        decision_timestamp exists
end
```

### Financial Services: EOD Reconciliation

```
test "end of day trade reconciliation"
    given trades from file "test_data/trading_day_2024_01_15.csv"

    when process eod_reconciliation
        with business_date = "2024-01-15"

    then expect ReconciliationReport
        trade_count = 15847
        total_volume = 2_450_000_000.00
        total_volume by asset_class
            equity = 1_200_000_000.00
            fixed_income = 850_000_000.00
            derivatives = 400_000_000.00

        unmatched_count = 0
        break_amount = 0.00

        settlement_status by status
            settled = 15800
            pending = 47
            failed = 0
end
```

### E-Commerce: Order Routing

```
test "high value international orders route to fraud check"
    given Order on orders_input
        order_id = "ORD-99001"
        customer_country = "NG"
        total = 5000.00
        payment_method = "credit_card"

    when process order_routing

    then expect Order on fraud_review_queue
        order_id = "ORD-99001"
        fraud_score exists
        review_priority = "high"

    and expect nothing on standard_fulfillment_queue
end
```

---

## Relationship to Other Layers

| Layer | Extension | TestDSL Interaction |
|-------|-----------|---------------------|
| Schema | `.schema` | Validates test data construction |
| Rules | `.rules` | Target of `evaluate` action |
| Transform | `.xform` | Target of `transform` action |
| Process | `.proc` | Target of `process` action |
| Infra | `.infra` | Provides logical names for mocking |
| Test | `.test` | This specification |

---

## Future Considerations

### Property-Based Testing

Generate test cases from schema constraints:
```
test "all valid applications get a decision"
    given Application generated from schema
        where loan_amount between 1000 and 1000000
        and credit_score between 300 and 850

    samples 1000

    when evaluate credit_decision_rules

    then outcome in ["approve", "decline", "refer"]
    and reason exists
end
```

### Mutation Testing

Verify test quality by mutating rules:
```
nexflow test --mutation-testing credit_rules.test
```

### Visual Test Reports

Interactive HTML reports with:
- Test execution timeline
- Data flow visualization
- Failure drill-down
- Historical trends
