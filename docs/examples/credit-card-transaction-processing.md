# Example: Credit Card Transaction Processing

> **Purpose**: Real-world validation of L1 Nexflow through complete credit card lifecycle
> **Status**: Reference Implementation Example
> **Version**: 0.1.0

---

## 1. Domain Overview

### 1.1 Transaction Lifecycle Phases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CREDIT CARD TRANSACTION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 1: AUTHORIZATION (Real-time, ~2-3 seconds)                           │
│  ════════════════════════════════════════════════                           │
│                                                                              │
│    Cardholder                                                                │
│        │                                                                     │
│        ▼                                                                     │
│    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐      │
│    │ SWIPE/ │───▶│MERCHANT│───▶│ACQUIRER│───▶│ CARD   │───▶│ ISSUER │      │
│    │  TAP   │    │  POS   │    │  BANK  │    │NETWORK │    │  BANK  │      │
│    └────────┘    └────────┘    └────────┘    └────────┘    └────────┘      │
│                                                                   │          │
│                                    ◀──────────────────────────────┘          │
│                                   APPROVED / DECLINED                        │
│                                                                              │
│  PHASE 2: CAPTURE (Batch, end of merchant day)                              │
│  ═════════════════════════════════════════════                              │
│                                                                              │
│    Merchant collects authorized transactions                                │
│    Submits batch to Acquirer (24-48 hrs after auth)                         │
│    Network routes to Issuer for clearing                                    │
│                                                                              │
│  PHASE 3: POSTING (Match & Post)                                            │
│  ═══════════════════════════════                                            │
│                                                                              │
│    Match capture to pending authorization                                   │
│    Release HOLD on credit line                                              │
│    Post actual transaction                                                  │
│    CREATE LEDGER ENTRIES (1 → N fan-out)                                    │
│                                                                              │
│  PHASE 4: SETTLEMENT (T+1 to T+3)                                           │
│  ════════════════════════════════                                           │
│                                                                              │
│    Money movement between banks                                             │
│    Issuer → Network → Acquirer → Merchant                                   │
│    Net of interchange and network fees                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Transaction State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRANSACTION STATES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌─────────────┐                                │
│                              │   SWIPE     │                                │
│                              │   EVENT     │                                │
│                              └──────┬──────┘                                │
│                                     │                                        │
│                                     ▼                                        │
│                        ┌────────────────────────┐                           │
│                        │    PENDING_AUTH        │                           │
│                        └───────────┬────────────┘                           │
│                                    │                                         │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│         │   DECLINED   │  │   APPROVED   │  │   REFERRED   │               │
│         └──────────────┘  │  (HOLD set)  │  └──────────────┘               │
│                           └───────┬──────┘                                  │
│                                   │                                          │
│                                   ▼ (24-48 hrs)                             │
│                          ┌──────────────┐                                   │
│                          │   CAPTURED   │◀── Merchant batch                 │
│                          └───────┬──────┘                                   │
│                                  │                                           │
│                     ┌────────────┼────────────┐                             │
│                     ▼            ▼            ▼                             │
│                ┌────────┐  ┌────────┐  ┌────────────┐                       │
│                │MATCHED │  │PARTIAL │  │ UNMATCHED  │                       │
│                └───┬────┘  └───┬────┘  │  (orphan)  │                       │
│                    │           │       └────────────┘                       │
│                    └─────┬─────┘                                            │
│                          ▼                                                   │
│                  ┌──────────────┐                                           │
│                  │    POSTED    │── Ledger entries created                  │
│                  └───────┬──────┘                                           │
│                          │                                                   │
│                          ▼                                                   │
│                  ┌──────────────┐                                           │
│                  │   SETTLED    │── Money moved                             │
│                  └──────────────┘                                           │
│                                                                              │
│  EXCEPTION FLOWS:                                                           │
│  • VOID: Cancel before capture                                              │
│  • REVERSAL: Cancel after capture, before settlement                        │
│  • CHARGEBACK: Dispute after settlement                                     │
│  • REFUND: Merchant-initiated return                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Ledger Entry Fan-Out (1 Transaction → N Entries)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEDGER EXPLOSION EXAMPLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT: Purchase $100 at Restaurant                                          │
│                                                                              │
│  OUTPUT (5-7 ledger entries):                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Entry 1: DR Cardholder Receivable    $100.00  (customer owes)          │ │
│  │ Entry 2: CR Interchange Income         $1.80  (issuer revenue)         │ │
│  │ Entry 3: CR Network Payable           $98.20  (owed to network)        │ │
│  │ Entry 4: DR Rewards Expense            $2.00  (2% cashback)            │ │
│  │ Entry 5: CR Rewards Liability          $2.00  (owed to customer)       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  IF Foreign Transaction (+2 entries):                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Entry 6: DR Cardholder Receivable     $3.00  (3% FX fee)               │ │
│  │ Entry 7: CR Foreign Transaction Fee   $3.00  (revenue)                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Fan-out ratio: 1 transaction → 5-10 ledger entries                         │
│  At scale: 1B transactions → 5-10B ledger entries                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Process DAG

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROCESS TOPOLOGY (DAG)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  REAL-TIME PATH                           BATCH PATH                        │
│  ══════════════                           ══════════                        │
│                                                                              │
│  pos_auth_requests                        merchant_capture_batches          │
│        │                                         │                          │
│        ▼                                         ▼                          │
│  ┌─────────────────┐                     ┌─────────────────┐               │
│  │ authorization   │                     │    capture      │               │
│  │    _request     │                     │   _ingestion    │               │
│  └────────┬────────┘                     └────────┬────────┘               │
│           │                                       │                         │
│  ┌────────┼────────┐                             │                         │
│  ▼        ▼        ▼                             │                         │
│ approved declined referred                       │                         │
│ _auths   _auths    _auths                        │                         │
│  │        │                                      │                         │
│  ▼        ▼                                      │                         │
│ ┌──────────────┐  ┌──────────────┐               │                         │
│ │authorization │  │authorization │               │                         │
│ │  _approved   │  │  _declined   │               │                         │
│ └──────┬───────┘  └──────────────┘               │                         │
│        │                                         │                         │
│        ▼                                         ▼                         │
│  pending_authorizations ─────────────▶  capture_events                     │
│                                             │                               │
│                           ┌─────────────────┘                              │
│                           ▼                                                 │
│                   ┌─────────────────┐                                      │
│                   │  auth_capture   │◀── CORRELATION (await)               │
│                   │    _matching    │    (up to 7 days)                    │
│                   └────────┬────────┘                                      │
│                            │                                                │
│                   ┌────────┼────────┬─────────────┐                        │
│                   ▼        ▼        ▼             ▼                        │
│              matched   partial   mismatch    orphan_auths                  │
│                _txns    _txns     _txns                                    │
│                   │                                                         │
│                   ▼                                                         │
│           ┌─────────────────┐                                              │
│           │  transaction    │                                              │
│           │    _posting     │                                              │
│           └────────┬────────┘                                              │
│                    │                                                        │
│           ┌────────┴────────┐                                              │
│           ▼                 ▼                                              │
│     ledger_trigger    balance_updates                                      │
│           │                 │                                              │
│           ▼                 ▼                                              │
│   ┌─────────────────┐  ┌─────────────────┐                                │
│   │    ledger       │  │   realtime      │                                │
│   │   _explosion    │  │   _balance      │                                │
│   └────────┬────────┘  └────────┬────────┘                                │
│            │                    │                                          │
│   ┌────────┴────────┐          │                                          │
│   ▼                 ▼          ▼                                          │
│ ledger_entries  gl_summaries  account_balance_updates                     │
│   │                                                                        │
│   └──────────────────────────────▶  daily_posted_transactions             │
│                                             │                              │
│                                             ▼                              │
│                                     ┌─────────────────┐                   │
│                                     │  settlement     │ (BATCH)           │
│                                     │    _batch       │                   │
│                                     └────────┬────────┘                   │
│                                              │                             │
│                                     ┌────────┴────────┐                   │
│                                     ▼                 ▼                   │
│                             settlement_files  settlement_status           │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. L1 Nexflow Implementation

### 3.1 Process 1: Authorization Request (Real-time Entry Point)

```
process authorization_request

    // ═══ EXECUTION ═══
    parallelism 256
    partition by card_number

    time by request_timestamp
        watermark delay 2 seconds

    // ═══ INPUT ═══
    receive from pos_auth_requests
        schema auth_request_v1

    // ═══ PROCESSING ═══

    // Validate card status
    enrich using card_validation_lookup
        on card_number
        select card_status, expiry_date, card_type, product_code

    // Get account data for credit check
    enrich using account_lookup
        on account_id
        select credit_limit, available_credit, current_balance, risk_tier

    // Fraud scoring (velocity, location, merchant risk)
    transform using fraud_scoring_block

    // Authorization decision (L4 rules decide: approved/declined/referred)
    route using authorization_rules_v2

    // ═══ STATE ═══
    state
        uses account_balances
        uses velocity_counters
        local auth_metrics keyed by merchant_category
            type counter

    // ═══ RESILIENCE ═══
    on error
        transform failure dead_letter auth_transform_errors
        lookup failure    dead_letter auth_lookup_errors
        rule failure      dead_letter auth_rule_errors

    checkpoint every 30 seconds
        to auth_checkpoints

end
```

### 3.2 Process 2: Authorization Approved

```
process authorization_approved

    parallelism 128
    partition by account_id

    time by approved_timestamp
        watermark delay 1 second

    receive from approved_auths
        schema auth_approved_v1

    // Place hold on available credit
    transform using hold_placement_block

    // Create pending auth record for later matching
    transform using pending_auth_creation_block

    // Response to network (real-time)
    emit to auth_responses
        schema auth_response_v1

    // Store for capture matching (correlation source)
    emit to pending_authorizations
        schema pending_auth_v1

    state
        uses account_balances
        uses pending_auth_store

    checkpoint every 1 minute
        to approved_auth_checkpoints

end
```

### 3.3 Process 3: Authorization Declined

```
process authorization_declined

    parallelism 64
    partition by account_id

    time by declined_timestamp
        watermark delay 1 second

    receive from declined_auths
        schema auth_declined_v1

    // Log decline for compliance/analytics
    transform using decline_logging_block

    // Response to network
    emit to auth_responses
        schema auth_response_v1

    // Analytics stream
    emit to decline_analytics
        schema decline_event_v1

    checkpoint every 1 minute
        to declined_auth_checkpoints

end
```

### 3.4 Process 4: Capture Ingestion (Batch Entry Point)

```
process capture_ingestion

    parallelism 64
    partition by merchant_id

    time by batch_timestamp
        watermark delay 1 hour
        late data to late_captures
        allowed lateness 24 hours

    receive from merchant_capture_batches
        schema capture_batch_v1

    // Explode batch file to individual capture records
    transform using capture_explosion_block

    // Validate each capture record
    transform using capture_validation_block

    // Route valid captures for matching
    emit to capture_events
        schema capture_event_v1

    on error
        transform failure dead_letter capture_errors

    checkpoint every 5 minutes
        to capture_checkpoints

end
```

### 3.5 Process 5: Auth-Capture Matching (Correlation)

```
process auth_capture_matching

    parallelism 128
    partition by authorization_code

    time by event_timestamp
        watermark delay 1 minute

    // Two input streams for correlation
    receive auths from pending_authorizations
        schema pending_auth_v1

    receive captures from capture_events
        schema capture_event_v1

    // Await capture for each authorization
    // Authorizations may wait up to 7 days for matching capture
    await auths
        until capture arrives
            matching on authorization_code
        timeout 7 days
            emit to orphan_authorizations

    // Validate match quality (amounts, dates)
    transform using match_validation_block

    // Route based on match result (L4 rules: exact/partial/mismatch)
    route using match_quality_rules

    state
        uses pending_auth_store

    on error
        correlation failure dead_letter matching_errors

    checkpoint every 5 minutes
        to matching_checkpoints

end
```

### 3.6 Process 6: Transaction Posting

```
process transaction_posting

    parallelism 64
    partition by account_id

    time by match_timestamp
        watermark delay 5 seconds

    receive from matched_transactions
        schema matched_txn_v1

    // Release the credit hold
    transform using hold_release_block

    // Post transaction to account
    transform using transaction_post_block

    // Trigger downstream processes
    emit to ledger_trigger
        schema ledger_trigger_v1

    emit to balance_updates
        schema balance_update_v1

    state
        uses account_balances
        uses pending_auth_store

    checkpoint every 1 minute
        to posting_checkpoints

end
```

### 3.7 Process 7: Ledger Explosion (1 → N Fan-Out)

```
process ledger_explosion

    parallelism 128
    partition by account_id

    time by posting_timestamp
        watermark delay 5 seconds

    receive from ledger_trigger
        schema ledger_trigger_v1

    // Get fee schedule for this product/merchant
    enrich using fee_schedule_lookup
        on product_code, merchant_category
        select interchange_rate, network_fee, fx_fee_rate

    // Get rewards configuration
    enrich using rewards_schedule_lookup
        on product_code, merchant_category
        select rewards_rate, rewards_cap, bonus_categories

    // Apply ledger explosion rules
    // L4 rules determine which entries to generate
    // 1 transaction → 5-10 ledger entries
    aggregate using ledger_entry_rules

    // Each entry to ledger system
    emit to ledger_entries
        schema ledger_entry_v1

    // Summary for general ledger
    emit to gl_summaries
        schema gl_summary_v1

    checkpoint every 1 minute
        to ledger_checkpoints

end
```

### 3.8 Process 8: Real-time Balance Aggregation

```
process realtime_balance

    parallelism 64
    partition by account_id

    time by update_timestamp
        watermark delay 2 seconds

    receive from balance_updates
        schema balance_update_v1

    // Micro-batch aggregation for balance updates
    window tumbling 10 seconds
        allowed lateness 30 seconds
        late data to late_balance_updates

    // Aggregate balance changes
    aggregate using balance_aggregation_rules

    emit to account_balance_updates
        schema account_balance_v1

    state
        uses account_balances

    checkpoint every 30 seconds
        to balance_checkpoints

end
```

### 3.9 Process 9: Settlement Batch (Daily)

```
process settlement_batch

    mode batch

    receive from daily_posted_transactions
        schema posted_txn_v1

    // Aggregate by settlement date and network
    aggregate using settlement_aggregation_rules

    // Calculate net positions
    transform using net_position_block

    // Generate settlement files for networks
    emit to settlement_files
        schema settlement_file_v1

    // Update transaction status
    emit to settlement_status_updates
        schema settlement_status_v1

end
```

---

## 4. Pattern Validation

### 4.1 L1 Constructs Used

| Pattern | Process | L1 Construct |
|---------|---------|--------------|
| Real-time streaming | authorization_request | Default `mode stream` |
| Batch processing | settlement_batch | `mode batch` |
| Parallel enrichment | authorization_request | Multiple `enrich using` |
| Routing delegation | authorization_request | `route using` (L4 decides) |
| Correlation (await) | auth_capture_matching | `await` with `timeout` |
| Windowed aggregation | realtime_balance | `window tumbling` |
| Fan-out (1→N) | ledger_explosion | `aggregate using` + multi-emit |
| Shared state | authorization_request | `state uses` |
| Local state | authorization_request | `state local` |
| Late data handling | capture_ingestion | `late data to`, `allowed lateness` |
| Error handling | authorization_request | `on error` block |
| Checkpointing | all processes | `checkpoint every` |

### 4.2 Scale Validation

| Metric | Value | L1 Support |
|--------|-------|------------|
| Input volume | 1B auths/window | `parallelism 256` + partitioning |
| Fan-out ratio | 1:5-10 (ledger) | `aggregate using` handles explosion |
| Output volume | 5-10B ledger entries | Multiple parallel emit targets |
| Correlation window | 7 days | `await timeout 7 days` |
| Latency (auth) | < 3 seconds | Real-time path, minimal hops |
| Latency (posting) | Hours-days | Async correlation handles this |

---

## 5. L1 DSL Scrutiny: Gaps Identified

### 5.1 Issues Found During Validation

| Issue | Description | Severity | Proposed Fix |
|-------|-------------|----------|--------------|
| **Multi-field partition** | `partition by card_number` but need `partition by authorization_code` for matching | Medium | Support `partition by field1, field2` |
| **Multi-field enrichment key** | `enrich on product_code, merchant_category` not in grammar | Medium | Update grammar for composite keys |
| **Conditional emit** | Can't express "emit X only if condition Y" | Low | L4 handles via routing? Or add `emit when`? |
| **Process ordering** | No way to express "process A must complete before B" | Low | Implicit via stream dependencies? Or add `depends on`? |
| **Retry semantics** | `retry 3` but no backoff specification | Low | Add `retry 3 with backoff exponential` |
| **Metrics declaration** | No way to declare custom metrics | Medium | Add `metrics` block? Or leave to L5? |
| **Schema projection** | Can't specify "only these fields from input" | Medium | Add `project` clause to `receive`? |

### 5.2 Grammar Updates Needed

```
// Multi-field partition
partitionDecl
    : 'partition' 'by' fieldList      // Changed from fieldPath
    ;

// Multi-field enrichment key
enrichDecl
    : 'enrich' 'using' IDENTIFIER
        'on' fieldList                 // Changed from fieldPath
        selectClause?
    ;

// Schema projection (new)
receiveDecl
    : 'receive' (IDENTIFIER 'from')? IDENTIFIER
        schemaDecl?
        projectClause?                 // NEW
        storeAction?
    ;

projectClause
    : 'project' fieldList
    | 'project' 'except' fieldList
    ;
```

### 5.3 Deferred Questions

| Question | Options | Recommendation |
|----------|---------|----------------|
| Custom metrics | L1 `metrics` block vs L5 binding | Defer to L5 |
| Process dependencies | Explicit `depends on` vs implicit streams | Implicit (via stream topology) |
| Conditional emit | `emit when` vs L4 routing | L4 routing (keep L1 pure) |
| Retry backoff | L1 syntax vs L5 config | L5 config |

---

## 6. Summary

### 6.1 L1 DSL Validation Result

| Aspect | Status | Notes |
|--------|--------|-------|
| **Completeness** | ✅ 90% | Handles full credit card lifecycle |
| **Expressiveness** | ✅ Good | Natural, readable process definitions |
| **Layer separation** | ✅ Clean | No business logic leaked into L1 |
| **Scale patterns** | ✅ Supported | Parallelism, partitioning, fan-out |
| **Correlation** | ✅ Working | `await` handles auth-capture matching |
| **Grammar gaps** | ⚠️ Minor | Multi-field keys, projection needed |

### 6.2 Files Updated

This validation resulted in:
- This example document created
- Grammar gaps identified (Section 5.2)
- Minor L1 spec updates needed

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Initial credit card example |
