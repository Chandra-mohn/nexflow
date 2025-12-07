# Chapter 2: The Credit Card Processing Challenge

> **Source**: Adapted from `docs/examples/credit-card-transaction-processing.md`
> **Status**: Draft

---

## The Scale of the Problem

Every second, millions of credit card transactions flow through financial systems worldwide. Behind each tap, swipe, or online purchase lies a complex processing pipeline that must:

- **Validate** the transaction against fraud rules
- **Enrich** it with customer and merchant data
- **Route** it through authorization workflows
- **Settle** it with acquiring banks
- **Report** it for regulatory compliance

For a major credit card processor, this translates to staggering numbers:

| Metric | Scale |
|--------|-------|
| **Input Records** | ~1 billion per processing window |
| **Output Records** | ~20-22 billion (fan-out from enrichment) |
| **Processing Window** | 2 hours |
| **Fields per Record** | ~5,000 |
| **Record Size** | ~1 MB average |
| **Concurrent Stages** | ~50 |

This isn't a theoretical exercise—it's the daily reality for enterprise financial systems.

---

## Why This Domain?

We chose credit card processing as our proving ground for several reasons:

### 1. Genuine Complexity

Credit card processing isn't artificially complex—it's genuinely hard:

- **Multi-stage pipelines**: A single transaction touches authorization, fraud detection, enrichment, settlement, and reporting
- **Time sensitivity**: Fraud detection must happen in milliseconds; settlement can batch over hours
- **Data variety**: Structured events, lookup tables, streaming aggregations, and complex joins
- **Regulatory requirements**: PCI-DSS, SOX, regional compliance rules

### 2. Clear Team Boundaries

The domain naturally separates into team responsibilities:

| Team | Responsibility | Nexflow Layer |
|------|---------------|----------------|
| Data Engineering | Pipeline orchestration | L1 `.proc` |
| Data Governance | Schema management | L2 `.schema` |
| Analytics Engineering | Transformations | L3 `.xform` |
| Risk/Compliance | Business rules | L4 `.rules` |
| Platform/DevOps | Infrastructure | L5 `.infra` |

This maps perfectly to our file extension strategy.

### 3. Representative Patterns

Almost every stream processing pattern appears in credit card processing:

- **Enrichment joins**: Transaction + Customer + Merchant
- **Windowed aggregations**: Hourly/daily summaries
- **Complex event processing**: Fraud pattern detection
- **State management**: Customer profiles, velocity tracking
- **Fan-out**: One transaction → multiple downstream events

If Nexflow handles credit cards, it handles most enterprise streaming use cases.

---

## A Day in the Life of a Transaction

Let's follow a single credit card transaction through the system:

### 10:32:15 AM — The Tap

Sarah taps her card at a coffee shop. The point-of-sale terminal sends an authorization request:

```json
{
  "transaction_id": "txn_abc123",
  "card_id": "card_xyz789",
  "amount": 5.75,
  "currency": "USD",
  "merchant_id": "merch_coffee_001",
  "merchant_category": "5814",
  "timestamp": "2024-01-15T10:32:15Z",
  "location": "New York, NY"
}
```

### Stage 1: Authorization Enrichment

The raw transaction enters the first pipeline stage:

```
process authorization_enrichment
  receive events from auth_requests
    schema auth_request_schema

  enrich using customers on card_id
    select customer_name, credit_limit, risk_tier, home_location

  enrich using merchants on merchant_id
    select merchant_name, merchant_risk_score, fraud_history

  transform using normalize_amount

  emit to enriched_auths
end
```

The 50-byte event becomes a 2KB enriched record with customer profile, merchant details, and normalized amounts.

### Stage 2: Fraud Screening

The enriched transaction flows to fraud detection:

```
process fraud_screening
  receive events from enriched_auths

  route using fraud_detection_rules

  emit approved to approved_auths
  emit flagged to manual_review_queue
  emit blocked to blocked_transactions
end
```

The fraud rules evaluate:
- Is the amount unusual for this customer?
- Is the location consistent with recent activity?
- Is the merchant category high-risk?
- Does velocity exceed thresholds?

### Stage 3: Settlement Aggregation

Approved transactions aggregate for settlement:

```
process settlement_aggregation
  receive events from approved_auths

  window tumbling 1 hour

  aggregate using settlement_summary

  emit to hourly_settlements
end
```

One hour of transactions becomes a single settlement record per merchant.

### The Fan-Out Effect

That single coffee purchase generates:
- 1 enriched authorization event
- 1 fraud screening result
- 1 settlement contribution
- 1 customer activity update
- 1 merchant activity update
- Multiple compliance records
- Analytics events for reporting

**1 transaction → 10-20 downstream records**

Multiply by 1 billion transactions, and you understand the 20B output figure.

---

## The Technical Challenges

### Challenge 1: Schema Explosion

With ~5,000 fields per record, schema management becomes critical:

```
// A simplified view of the enriched transaction schema
schema enriched_auth_schema
  // Transaction core (20 fields)
  transaction_id, card_id, amount, currency, ...

  // Customer enrichment (200 fields)
  customer_name, credit_limit, credit_score, risk_tier,
  address_line_1, address_line_2, city, state, zip,
  phone_primary, phone_secondary, email,
  account_open_date, last_activity_date,
  // ... 180 more fields

  // Merchant enrichment (150 fields)
  merchant_name, merchant_category, risk_score,
  // ... 145 more fields

  // Derived fields (100 fields)
  amount_usd, risk_score_composite, velocity_1h, velocity_24h,
  // ... 95 more fields

  // ... continues for thousands more fields
end
```

Without a schema registry, this becomes unmanageable.

### Challenge 2: Rule Complexity

Fraud detection rules aren't simple thresholds:

```
decision_table fraud_screening
  hit_policy first_match

  conditions
    amount_vs_average: range        // > 10x average?
    location_distance: range        // > 500 miles from home?
    merchant_risk: equals           // high-risk category?
    velocity_1h: range              // > 5 transactions/hour?
    time_since_last: range          // < 1 minute since last?
  end

  rules
    | amount     | location | merchant | velocity | time    | → action        |
    |------------|----------|----------|----------|---------|-----------------|
    | > 10x      | > 500mi  | *        | *        | *       | block           |
    | > 5x       | > 100mi  | high     | *        | *       | block           |
    | > 5x       | *        | *        | > 10     | *       | manual_review   |
    | *          | > 500mi  | *        | *        | < 1min  | manual_review   |
    | *          | *        | high     | > 5      | *       | flag            |
    | *          | *        | *        | *        | *       | approve         |
  end
end
```

These rules must be:
- **Readable** by risk analysts (not just engineers)
- **Auditable** for compliance
- **Testable** before production
- **Versioned** for rollback

### Challenge 3: Time Semantics

Not all transactions arrive in order:

```
10:32:15 — Transaction occurs at coffee shop
10:32:16 — POS sends to acquirer
10:32:17 — Acquirer sends to network
10:32:18 — Network sends to issuer (arrives in our system)
10:32:45 — Delayed batch of transactions arrives (from 10:31:xx)
```

The system must handle:
- **Watermarks**: How long to wait for late data?
- **Reordering**: Process in event time, not arrival time
- **Late arrivals**: What to do with transactions that arrive after the window closes?

```
process authorization_enrichment
  time by event_timestamp
    watermark delay 30 seconds
    late data to late_arrivals
    allowed lateness 5 minutes
  ...
end
```

### Challenge 4: State at Scale

Fraud detection requires state:

```
// Per-customer state
customer_velocity = {
  transactions_1h: count,
  transactions_24h: count,
  amount_1h: sum,
  amount_24h: sum,
  last_location: string,
  last_timestamp: timestamp
}

// 100 million customers × 100 bytes = 10 GB of state
// Must be checkpointed, recovered, and queryable
```

State backends must handle:
- **100M+ keys** (one per customer)
- **Incremental checkpoints** (can't snapshot 10GB every minute)
- **Fast lookups** (sub-millisecond for enrichment)
- **Fault tolerance** (recover on node failure)

---

## Why Existing Tools Fall Short

### Raw Flink/Spark

Writing this in raw Flink SQL or Spark:

```sql
-- Flink SQL for authorization enrichment
INSERT INTO enriched_auths
SELECT
  t.transaction_id,
  t.card_id,
  t.amount,
  t.currency,
  c.customer_name,
  c.credit_limit,
  c.risk_tier,
  -- ... 200 more columns from customer
  m.merchant_name,
  m.merchant_risk_score,
  -- ... 150 more columns from merchant
  t.amount * COALESCE(fx.rate, 1.0) as amount_usd
FROM auth_requests t
LEFT JOIN customers FOR SYSTEM_TIME AS OF t.proc_time AS c
  ON t.card_id = c.card_id
LEFT JOIN merchants FOR SYSTEM_TIME AS OF t.proc_time AS m
  ON t.merchant_id = m.merchant_id
LEFT JOIN fx_rates FOR SYSTEM_TIME AS OF t.proc_time AS fx
  ON t.currency = fx.currency
```

Problems:
- Business logic buried in SQL
- Schema changes require SQL rewrites
- No separation between orchestration and rules
- Risk analysts can't read or modify this

### Existing DSLs

Other stream processing DSLs either:
- **Too simple**: Can't handle complex joins and state
- **Too coupled**: Tie you to specific infrastructure
- **Too narrow**: Focus on one aspect (just rules, just ETL)

---

## What We Need

The credit card challenge demands:

1. **Layered abstraction**: Orchestration separate from rules separate from schemas
2. **Team-appropriate interfaces**: Risk analysts edit rules, not pipelines
3. **Scale-aware design**: Built for billions, not demos
4. **Time-first semantics**: Event time, watermarks, late data as first-class concepts
5. **Infrastructure independence**: Same logic deploys to Flink, Spark, or future engines

This is what Nexflow provides.

---

## Summary

Credit card processing at enterprise scale is the ideal proving ground for a stream processing DSL:
- **Genuine complexity** that exposes architectural weaknesses
- **Clear team boundaries** that validate separation of concerns
- **Representative patterns** that transfer to other domains

In the next chapter, we'll examine why existing solutions—despite their power—leave a gap that Nexflow fills.
