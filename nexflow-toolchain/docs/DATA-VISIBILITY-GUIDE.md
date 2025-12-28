#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Data Visibility and Flow Guide

How data moves through Nexflow layers and what each layer can see and change.

---

## Quick Reference

| Layer | Input | Output | Can See | Can Change |
|-------|-------|--------|---------|------------|
| **L1** (Process) | Kafka message | Kafka message | All schemas, transforms, rules | Flow routing only |
| **L2** (Schema) | N/A | Type definition | Other L2 schemas | N/A (defines structure) |
| **L3** (Transform) | Schema A | Schema B | Input fields, L0 functions | Add fields, modify values, compute new values |
| **L4** (Rules) | Schema | Decision result | Input fields | Nothing (returns new data) |
| **L0** (Hand-coded) | Any Java type | Any Java type | Full Java ecosystem | Anything (custom code) |

---

## The Data Flow Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STANDARD DATA FLOW PATTERN                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   KAFKA          L3              L4              L3              KAFKA       │
│   INPUT       TRANSFORM        RULES         TRANSFORM          OUTPUT      │
│                                                                              │
│  ┌──────┐    ┌──────────┐    ┌────────┐    ┌──────────┐      ┌──────┐      │
│  │Schema│    │ Enrich   │    │Evaluate│    │  Merge   │      │Schema│      │
│  │  A   │───►│ & Add    │───►│& Decide│───►│ Results  │─────►│  B   │      │
│  │      │    │ Fields   │    │        │    │          │      │      │      │
│  └──────┘    └──────────┘    └────────┘    └──────────┘      └──────┘      │
│                                                                              │
│  5 fields    8 fields       Decision      10 fields         10 fields      │
│              (+3 new)       + Score       (+2 from L4)                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight**: L4 rules return a **separate result** (decision, score, category). L3 transforms merge this result into the main record.

---

## Layer-by-Layer Data Visibility

### L2: Schema Layer (Defines Structure)

L2 **defines** data shapes. It doesn't process data - it declares what data looks like.

```
schema OrderInput {
    entity Order {
        order_id: string required      // Field 1
        customer_id: string required   // Field 2
        amount: decimal(10,2) required // Field 3
        currency: string = "USD"       // Field 4
        status: string                 // Field 5
    }
}
```

**What L2 can see**: Other L2 schemas (for composition/imports)
**What L2 can change**: Nothing - it only defines structure

---

### L3: Transform Layer (Changes Data)

L3 is where data transformation happens. It can:
- **See**: All fields from input schema
- **Add**: New computed fields
- **Modify**: Existing field values
- **Remove**: Fields (by not mapping them)
- **Call**: L0 custom functions

#### Example: Basic Field Transformation

```
transform OrderEnrichment {
    input Order           // L2 schema with 5 fields
    output EnrichedOrder  // L2 schema with 8 fields

    mapping
        // PASS-THROUGH: Copy unchanged
        order_id -> order_id
        customer_id -> customer_id

        // MODIFY: Transform existing field
        uppercase(status) -> status
        round(amount, 2) -> amount

        // ADD: Compute new fields
        amount * 0.1 -> tax_amount
        amount + tax_amount -> total_amount
        now() -> processed_at

        // REMOVE: Simply don't map 'currency' - it won't appear in output
    end
}
```

**Field Visibility in L3:**
```
┌─────────────────────────────────────────────────────────────┐
│                    L3 TRANSFORM VISIBILITY                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT (Order)              OUTPUT (EnrichedOrder)          │
│  ─────────────              ────────────────────            │
│  order_id      ─────────────► order_id                      │
│  customer_id   ─────────────► customer_id                   │
│  amount        ──┬──────────► amount (rounded)              │
│                  │                                          │
│  currency      ──┘ (dropped)                                │
│                                                              │
│  status        ─────────────► status (uppercased)           │
│                                                              │
│                  (computed) ► tax_amount                    │
│                  (computed) ► total_amount                  │
│                  (computed) ► processed_at                  │
│                                                              │
│  L3 can read: order_id, customer_id, amount, currency,      │
│               status                                         │
│  L3 can write: Any field in output schema                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### L4: Rules Layer (Returns Decisions)

L4 evaluates business rules and returns a **separate result type**. It does NOT modify the input record.

```
rules CreditDecision {
    input EnrichedOrder      // Can see all 8 fields
    output CreditResult      // Returns NEW type (not EnrichedOrder)

    decision_table
        hit_policy first

        | total_amount | customer_id    | -> decision      | risk_score |
        |--------------|----------------|------------------|------------|
        | < 100        | *              | "AUTO_APPROVE"   | 0.1        |
        | < 1000       | starts("VIP")  | "AUTO_APPROVE"   | 0.2        |
        | < 1000       | *              | "REVIEW"         | 0.5        |
        | >= 1000      | starts("VIP")  | "REVIEW"         | 0.7        |
        | >= 1000      | *              | "DECLINE"        | 0.9        |
    end
}
```

**L4 Output Schema (auto-generated or explicit):**
```
schema CreditResult {
    entity CreditResult {
        decision: string required
        risk_score: decimal(3,2) required
    }
}
```

**Field Visibility in L4:**
```
┌─────────────────────────────────────────────────────────────┐
│                    L4 RULES VISIBILITY                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT (EnrichedOrder)           OUTPUT (CreditResult)      │
│  ────────────────────            ────────────────────       │
│  order_id        (readable)                                 │
│  customer_id     (readable) ────► (used in condition)       │
│  amount          (readable)                                 │
│  status          (readable)                                 │
│  tax_amount      (readable)                                 │
│  total_amount    (readable) ────► (used in condition)       │
│  processed_at    (readable)                                 │
│                                                              │
│                              ────► decision (NEW)           │
│                              ────► risk_score (NEW)         │
│                                                              │
│  L4 can read: All input fields                              │
│  L4 can write: ONLY to its output type (CreditResult)       │
│  L4 CANNOT: Modify EnrichedOrder fields                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Merging L4 Results Back (L3 Again)

Since L4 returns a separate result, you need another L3 transform to merge it:

```
transform MergeDecision {
    input EnrichedOrder, CreditResult   // Two inputs
    output FinalOrder                    // Combined output

    mapping
        // From EnrichedOrder
        order_id -> order_id
        customer_id -> customer_id
        amount -> amount
        status -> status
        tax_amount -> tax_amount
        total_amount -> total_amount
        processed_at -> processed_at

        // From CreditResult (L4 output)
        decision -> credit_decision
        risk_score -> risk_score
    end
}
```

---

### L1: Process Layer (Orchestrates Flow)

L1 wires everything together. It can see all types but doesn't transform data itself.

```
process OrderProcessor {
    // RECEIVE: Kafka → Order (L2 schema)
    receive Order from kafka "orders-input"
        format confluent_avro
        consumer_group "order-processors"

    // TRANSFORM: Order → EnrichedOrder (L3)
    transform using OrderEnrichment

    // EVALUATE: EnrichedOrder → CreditResult (L4)
    // Note: This returns CreditResult, not modified EnrichedOrder
    evaluate using CreditDecision

    // TRANSFORM: EnrichedOrder + CreditResult → FinalOrder (L3)
    transform using MergeDecision

    // ROUTE: Based on field values
    route by credit_decision
        when "AUTO_APPROVE" -> emit to kafka "approved-orders"
        when "REVIEW" -> emit to kafka "review-queue"
        when "DECLINE" -> emit to kafka "declined-orders"
    end
}
```

**L1 Visibility:**
```
┌─────────────────────────────────────────────────────────────┐
│                    L1 PROCESS VISIBILITY                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  L1 CAN SEE:                                                │
│  ─────────────                                              │
│  • All L2 schema names (Order, EnrichedOrder, FinalOrder)   │
│  • All L3 transform names (OrderEnrichment, MergeDecision)  │
│  • All L4 rules names (CreditDecision)                      │
│  • Field names for routing (credit_decision)                │
│  • Kafka topics, formats, consumer groups                   │
│                                                              │
│  L1 CAN CHANGE:                                             │
│  ──────────────                                             │
│  • Flow routing (which sink based on field values)          │
│  • Parallelism, windowing, error handling                   │
│                                                              │
│  L1 CANNOT:                                                 │
│  ───────────                                                │
│  • Modify field values (that's L3's job)                    │
│  • Evaluate business rules (that's L4's job)                │
│  • Define data structure (that's L2's job)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Example: Order Processing Pipeline

### File Structure
```
src/
├── schema/
│   ├── order_input.schema      # L2: Input from Kafka
│   ├── enriched_order.schema   # L2: After first transform
│   ├── credit_result.schema    # L2: L4 output type
│   └── final_order.schema      # L2: Output to Kafka
├── transform/
│   ├── enrich_order.xform      # L3: Add computed fields
│   └── merge_decision.xform    # L3: Combine record + decision
├── rules/
│   └── credit_decision.rules   # L4: Business rules
└── flow/
    └── order_processor.proc    # L1: Orchestration
```

### Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  KAFKA INPUT: orders-input                                                  │
│  ┌─────────────────────┐                                                    │
│  │ Order               │                                                    │
│  │ ─────               │                                                    │
│  │ order_id: "ORD-123" │                                                    │
│  │ customer_id: "VIP1" │                                                    │
│  │ amount: 500.00      │                                                    │
│  │ currency: "USD"     │                                                    │
│  │ status: "pending"   │                                                    │
│  └──────────┬──────────┘                                                    │
│             │                                                                │
│             ▼                                                                │
│  L3 TRANSFORM: OrderEnrichment                                              │
│  ┌─────────────────────┐                                                    │
│  │ EnrichedOrder       │                                                    │
│  │ ─────────────       │                                                    │
│  │ order_id: "ORD-123" │  (passed through)                                  │
│  │ customer_id: "VIP1" │  (passed through)                                  │
│  │ amount: 500.00      │  (passed through)                                  │
│  │ status: "PENDING"   │  (uppercased)                                      │
│  │ tax_amount: 50.00   │  (computed: amount * 0.1)                          │
│  │ total_amount: 550.00│  (computed: amount + tax)                          │
│  │ processed_at: now() │  (computed: current time)                          │
│  └──────────┬──────────┘                                                    │
│             │                                                                │
│             ▼                                                                │
│  L4 RULES: CreditDecision                                                   │
│  ┌─────────────────────┐    ┌─────────────────────┐                         │
│  │ EnrichedOrder       │    │ CreditResult        │                         │
│  │ (input - read only) │───►│ (output - new data) │                         │
│  │                     │    │ ─────────────       │                         │
│  │ total_amount: 550   │    │ decision: "AUTO_    │                         │
│  │ customer_id: "VIP1" │    │           APPROVE"  │                         │
│  │                     │    │ risk_score: 0.2     │                         │
│  └─────────────────────┘    └──────────┬──────────┘                         │
│             │                          │                                     │
│             └───────────┬──────────────┘                                     │
│                         │                                                    │
│                         ▼                                                    │
│  L3 TRANSFORM: MergeDecision                                                │
│  ┌─────────────────────────────┐                                            │
│  │ FinalOrder                  │                                            │
│  │ ──────────                  │                                            │
│  │ order_id: "ORD-123"         │  (from EnrichedOrder)                      │
│  │ customer_id: "VIP1"         │  (from EnrichedOrder)                      │
│  │ amount: 500.00              │  (from EnrichedOrder)                      │
│  │ status: "PENDING"           │  (from EnrichedOrder)                      │
│  │ tax_amount: 50.00           │  (from EnrichedOrder)                      │
│  │ total_amount: 550.00        │  (from EnrichedOrder)                      │
│  │ processed_at: 2025-01-15... │  (from EnrichedOrder)                      │
│  │ credit_decision: "AUTO_APP" │  (from CreditResult)                       │
│  │ risk_score: 0.2             │  (from CreditResult)                       │
│  └──────────┬──────────────────┘                                            │
│             │                                                                │
│             ▼                                                                │
│  L1 ROUTE: by credit_decision                                               │
│             │                                                                │
│             ├──► "AUTO_APPROVE" ──► approved-orders                         │
│             ├──► "REVIEW"       ──► review-queue                            │
│             └──► "DECLINE"      ──► declined-orders                         │
│                                                                              │
│  KAFKA OUTPUT: approved-orders                                              │
│  ┌─────────────────────────────┐                                            │
│  │ FinalOrder (9 fields)       │                                            │
│  └─────────────────────────────┘                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: What Each Layer Can Do

| Action | L1 | L2 | L3 | L4 | L0 |
|--------|----|----|----|----|-----|
| Read input fields | ✗ | ✗ | ✅ | ✅ | ✅ |
| Add new fields | ✗ | ✅ (define) | ✅ | ✗ | ✅ |
| Modify field values | ✗ | ✗ | ✅ | ✗ | ✅ |
| Remove fields | ✗ | ✗ | ✅ | ✗ | ✅ |
| Return decisions | ✗ | ✗ | ✗ | ✅ | ✅ |
| Route messages | ✅ | ✗ | ✗ | ✗ | ✗ |
| Define data structure | ✗ | ✅ | ✗ | ✗ | ✅ |
| Call custom Java code | ✗ | ✗ | ✅ | ✗ | N/A |

---

## Common Patterns

### Pattern 1: Enrich → Evaluate → Merge
```
receive A → transform (A→B) → evaluate (B→Result) → transform (B+Result→C) → emit C
```

### Pattern 2: Multiple Rule Evaluations
```
receive A
  → transform (A→B)
  → evaluate CreditRules (B→CreditResult)
  → evaluate FraudRules (B→FraudResult)
  → transform (B+CreditResult+FraudResult→C)
  → emit C
```

### Pattern 3: Conditional Transformation
```
receive A
  → evaluate CategoryRules (A→Category)
  → route by category
      when "PREMIUM" → transform PremiumEnrich → emit to premium-topic
      when "STANDARD" → transform StandardEnrich → emit to standard-topic
```

---

## Key Takeaways

1. **L2 defines, L3 transforms, L4 decides, L1 orchestrates**
2. **L4 returns NEW data** - it never modifies the input record
3. **Use L3 to merge** L4 results back into your main record
4. **L1 sees type names** but doesn't see or modify field values
5. **Data flows forward** - each step sees the output of the previous step
