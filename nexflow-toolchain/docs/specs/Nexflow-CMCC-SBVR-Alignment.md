# Nexflow Theoretical Foundation: CMCC & SBVR Alignment

**Status**: Reference Document
**Created**: December 11, 2024
**Purpose**: Document the theoretical alignment between Nexflow DSL architecture and established business rules frameworks

---

## Executive Summary

Nexflow's 6-layer DSL architecture aligns with two complementary business rules frameworks:

- **SBVR** (Semantics of Business Vocabulary and Business Rules) - OMG standard for human-readable rule specification
- **CMCC** (Conceptual Model Completeness Conjecture) - Theory that 5 primitives express all computable business truth

Nexflow occupies a **sweet spot**: human-readable DSL (like SBVR) that compiles to structural code (like CMCC), eliminating runtime parsing risk.

---

## The Problem: Toolchain Drift

A cautionary tale from the CMCC article:

> "2:14 a.m. A payments platform lies dark because one flag — `Preferred Billing Account ≠ TRUE` — slipped past the parser. The rule 'Every active customer shall have a preferred billing account' was written, reviewed, approved… and then silently mis-parsed by the overnight deploy script. The outage cost $180K."

The root cause: **rules interpreted at runtime** through a chain of translations:

```
authoring → parsing → code-gen → DB migration → runtime triggers
         ↑                                      ↑
      DRIFT                                  DRIFT
```

Every hop in this chain invites semantic drift - the rule that was written is not the rule that executes.

---

## SBVR: The Human Interface

### What is SBVR?

[SBVR](https://www.omg.org/spec/SBVR/About-SBVR/) (Semantics of Business Vocabulary and Business Rules) is an OMG standard that:

- Isolates **meaning from mechanics**
- Defines **vocabulary** shared between business and IT
- Specifies **modality** (obligatory, permitted, prohibited)
- Uses **structured natural language** for rule expression

### RuleSpeak Notation

RuleSpeak is a notation that maps to SBVR, making rules readable:

```
"It is obligatory that each invoice has exactly one buyer."
"Each rental must reference a vehicle."
"If the renter is under 25 years old, an under-age surcharge applies."
```

### SBVR's Limitation

> "Behind the curtain, a parser still translates prose into constraints."

Ambiguity problems:
- "shall" vs. "must" vs. "is required to" — same modality?
- Internationalization: one rule, seven languages, endless synonyms
- Every parsing step is a potential translation error

---

## CMCC: The Machine Substrate

### What is CMCC?

The **Conceptual Model Completeness Conjecture** proposes that every computable business truth emerges from just **5 primitives**:

| Primitive | Name | Meaning |
|-----------|------|---------|
| **S** | Schema | Entities and fields |
| **D** | Data | Asserted records |
| **L** | Lookups | Pointers/relationships between entities |
| **A** | Aggregations | Totals, counts, sums |
| **F** | Formulas (Lambda Fields) | Derived/computed facts |

### The Key Insight

> "No grammar, no parser. Truth lives in structure."

If a `Rental.vehicleId` is `NOT NULL` and references `Vehicle.id`, the rule "Each rental must reference a vehicle" **enforces itself**. There's nothing to parse — the structure IS the rule.

### CMCC Examples

**Referential Integrity:**
```
RuleSpeak: Each rental must reference a vehicle.
CMCC:
  S: Rental.vehicleId (UUID)
  L: Rental.vehicleId → Vehicle.id (required)
  Enforcement: model rejects any Rental without a vehicleId
```

**Conditional Obligation:**
```
RuleSpeak: If the renter is under 25 years old, an under-age surcharge applies.
CMCC:
  S: Customer.age (Number)
  F: underage_surcharge_applies = age < 25
  Enforcement: field evaluates to TRUE automatically
```

**Temporal Calculation:**
```
RuleSpeak: A loyalty tier upgrade becomes effective the month after earning 1000 points.
CMCC:
  S: PointAward(date, points)
  A: points_this_month = SUM(points WHERE month == NOW())
  F: tier_upgrade_date = FIRST_DAY_OF_NEXT_MONTH IF points_this_month >= 1000
  Enforcement: upgrade date materializes; no imperative code schedules it
```

---

## SBVR + CMCC: Better Together

The article makes a crucial point:

> "CMCC doesn't supplant SBVR/RuleSpeak — it gives it a **lossless storage kernel**."
>
> "Think of CMCC as the **database** to SBVR's **language** — two sides of the same coin."

### Complementary Roles

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SBVR + CMCC RELATIONSHIP                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   SBVR / RuleSpeak                    CMCC                              │
│   ══════════════════                  ════                              │
│   Human-readable surface              Machine-executable substrate       │
│   "It is obligatory that..."          S-D-L-A-F primitives              │
│   Natural language facade             Pure data structure               │
│   Policy communication                Runtime enforcement               │
│   Governance & compliance             Deterministic execution           │
│                                                                          │
│                        ┌─────────────┐                                  │
│   SBVR Sentence ──────►│  ROUND-TRIP │◄────── CMCC Model                │
│                        │   FIDELITY  │                                  │
│                        └─────────────┘                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Properties of the Relationship

| Property | Description |
|----------|-------------|
| **Round-trip fidelity** | Any CMCC model renders as RuleSpeak and regenerates with zero loss |
| **Tool-chain amplification** | CMCC schema feeds SBVR engines for compliance/simulation |
| **Governance harmony** | SBVR = policy surface; CMCC = ACID runtime |
| **Shared DNA** | Both insist on declarative truth and pre-defined vocabulary |

---

## Nexflow's Position: The Sweet Spot

Nexflow combines the best of both approaches:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NEXFLOW'S ARCHITECTURAL POSITION                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐   BUILD   ┌──────────────────────┐           │
│  │  NEXFLOW DSL         │   TIME    │  GENERATED JAVA      │           │
│  │  (like SBVR)         │ ────────► │  (like CMCC)         │           │
│  │                      │           │                      │           │
│  │  Human-readable      │  Parser   │  Structure IS truth  │           │
│  │  Declarative         │  runs     │  No runtime parsing  │           │
│  │  Business vocabulary │  ONCE     │  Self-enforcing      │           │
│  │  Type-inferred       │           │  Compile-time safe   │           │
│  └──────────────────────┘           └──────────────────────┘           │
│                                                                          │
│  KEY INSIGHT: The parser runs at BUILD time, not RUNTIME.               │
│  If the generated code compiles, the rule is correctly encoded.         │
│  There's nothing left to mis-parse at 2:14 AM.                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### How Nexflow Eliminates Toolchain Drift

| Traditional Approach | Nexflow Approach |
|---------------------|------------------|
| Rules parsed at runtime | Rules compiled to Java |
| Multiple translation hops | Single generation step |
| Drift at each stage | Generated code = source of truth |
| Runtime interpretation | Static type checking |
| Late failure (2 AM) | Compile-time failure |

---

## CMCC Primitive Mapping to Nexflow

### Complete Mapping Table

| CMCC | Name | Nexflow Layer | Implementation | Status |
|------|------|---------------|----------------|--------|
| **S** | Schema | L2 SchemaDSL | `fields { }` block | ✅ Complete |
| **D** | Data | L2 reference_data | `entries { }` block | ✅ Complete |
| **L** | Lookups | L2 + L4 | Relationships, service lookups | ⚠️ Enhance |
| **A** | Aggregations | L1 + L4 | `aggregate using`, decision tables | ⚠️ Enhance |
| **F** | Formulas | L2 computed | `computed { }` block (proposed) | 📋 Planned |

### Detailed Mapping

#### S (Schema) → L2 SchemaDSL ✅

```
// CMCC: S - Schema defines entities and fields
// Nexflow L2:
schema Transaction pattern event_log {
    fields {
        transaction_id: string required
        amount: decimal
        customer_id: string
        timestamp: datetime
    }
}

// Generated: Java Record (structure IS the schema)
public record Transaction(
    String transactionId,
    BigDecimal amount,
    String customerId,
    Instant timestamp
) implements Serializable { }
```

#### D (Data) → L2 reference_data Pattern ✅

```
// CMCC: D - Data as asserted records
// Nexflow L2:
schema CountryCodes pattern reference_data {
    entries {
        US { name: "United States", currency: "USD" }
        UK { name: "United Kingdom", currency: "GBP" }
        JP { name: "Japan", currency: "JPY" }
    }
}

// Generated: Static lookup (data IS the model)
public enum CountryCodes {
    US("United States", "USD"),
    UK("United Kingdom", "GBP"),
    JP("Japan", "JPY");
    // ...
}
```

#### L (Lookups) → L2 Relationships + L4 Services ⚠️

```
// CMCC: L - Pointers between entities
// Nexflow L2 (PROPOSED enhancement):
schema Rental {
    fields {
        vehicle_id: uuid required
        customer_id: uuid required
    }

    relationships {
        vehicle: Vehicle via vehicle_id required    // L primitive
        customer: Customer via customer_id required // L primitive
    }
}

// Nexflow L4 (existing):
services {
    bureau: cached(5m) BureauService.lookup(customer_id) -> BureauData
}
```

#### A (Aggregations) → L1 aggregate + L4 ⚠️

```
// CMCC: A - Totals and counts
// Nexflow L1:
process fraud_detection {
    aggregate using fraud_score_aggregator
        window tumbling 1h
}

// PROPOSED: Declarative aggregations in L2
schema CustomerMetrics {
    aggregations {
        total_spent: sum(transactions.amount)
        order_count: count(transactions)
    }
}
```

#### F (Formulas/Lambda Fields) → L2 computed 📋

```
// CMCC: F - Derived facts
// Nexflow L2 (PROPOSED):
schema FraudAnalysis {
    fields {
        ml_score: decimal
        rule_score: decimal
        velocity_score: decimal
    }

    computed {
        // F primitives - derived facts that materialize automatically
        combined_fraud_score = (ml_score * 0.4)
                             + (rule_score * 0.3)
                             + (velocity_score * 0.3)

        risk_category = when combined_fraud_score > 0.8 then "HIGH"
                        when combined_fraud_score > 0.5 then "MEDIUM"
                        else "LOW"

        requires_review = combined_fraud_score > 0.6
                         and risk_category != "LOW"
    }
}

// Generated: Methods on Record (formula IS the code)
public record FraudAnalysis(...) {
    public BigDecimal combinedFraudScore() {
        return mlScore.multiply(new BigDecimal("0.4"))
            .add(ruleScore.multiply(new BigDecimal("0.3")))
            .add(velocityScore.multiply(new BigDecimal("0.3")));
    }

    public String riskCategory() {
        BigDecimal score = combinedFraudScore();
        if (score.compareTo(new BigDecimal("0.8")) > 0) return "HIGH";
        if (score.compareTo(new BigDecimal("0.5")) > 0) return "MEDIUM";
        return "LOW";
    }
}
```

---

## The Three-Layer View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NEXFLOW → CMCC → SBVR                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LAYER 1: SBVR (Human Communication)                                    │
│  ═══════════════════════════════════                                    │
│  "It is obligatory that each transaction has a valid customer."         │
│  "If the fraud score exceeds 0.8, the transaction requires review."     │
│                                                                          │
│  Purpose: Policy documents, compliance audits, stakeholder comms        │
│                                                                          │
│                              ▼                                          │
│                                                                          │
│  LAYER 2: NEXFLOW DSL (Developer Interface)                             │
│  ══════════════════════════════════════════                             │
│  schema Transaction {                                                   │
│      fields { customer_id: string required }                            │
│      computed { requires_review = fraud_score > 0.8 }                   │
│  }                                                                      │
│                                                                          │
│  Purpose: Type-safe authoring, IDE support, version control             │
│                                                                          │
│                              ▼                                          │
│                                                                          │
│  LAYER 3: CMCC (Runtime Structure)                                      │
│  ═════════════════════════════════                                      │
│  S: Transaction.customerId (String, required)                           │
│  F: requiresReview() = fraudScore > 0.8                                 │
│                                                                          │
│  Purpose: Self-enforcing structure, no parsing, deterministic           │
│                                                                          │
│  GENERATED AS: Java Records with computed methods                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Benefits of This Architecture

### 1. Elimination of Runtime Parsing

| Risk | Mitigation |
|------|------------|
| Parser bugs at 2 AM | Parser runs at build time only |
| Semantic drift | Generated code IS the specification |
| Version mismatch | Single source of truth in DSL |
| Late failure | Compile-time type checking |

### 2. Human-Readable Authoring

- Business analysts can read/review DSL
- Version control shows meaningful diffs
- IDE support for validation and completion
- Documentation generated from source

### 3. Machine-Verifiable Truth

- Type inference eliminates annotation errors
- Required fields enforced by structure
- Computed fields are just methods
- No interpretation layer at runtime

### 4. Round-Trip Capability

```
Nexflow DSL ──► Generated Java ──► (could generate) ──► SBVR/RuleSpeak
     ▲                                                        │
     └────────────────── Documentation ◄──────────────────────┘
```

---

## Recommendations for Nexflow Evolution

### Priority 1: Implement L2 Computed Fields (F Primitive)

The `computed` block directly implements CMCC's Lambda Fields:
- Derived facts that materialize automatically
- No imperative code, just declarations
- Self-documenting business logic

### Priority 2: Add L2 Relationships Block (L Primitive)

Explicit relationship declarations:
```
relationships {
    customer: Customer via customer_id required
}
```
- Generates navigation methods
- Enforces referential integrity
- Maps directly to CMCC lookups

### Priority 3: Consider Declarative Aggregations (A Primitive)

Beyond operational L1 aggregations:
```
aggregations {
    total_spent: sum(transactions.amount)
}
```
- Pre-computed metrics as schema properties
- Materialized views in the model

### Priority 4: SBVR Documentation Generation

Auto-generate RuleSpeak from DSL:
```
schema Transaction → "It is obligatory that each Transaction has a customer_id."
computed requires_review → "If fraud_score > 0.8, review is required."
```

---

## References

- [SBVR Specification (OMG)](https://www.omg.org/spec/SBVR/About-SBVR/)
- [RuleSpeak Business Rule Notation](https://www.brcommunity.com/articles.php?id=b282)
- [SBVR, RuleSpeak & the CMCC (Medium)](https://medium.com/business-rules-requirements-with-the-cmcc/sbvr-rulespeak-the-cmcc-when-business-rules-stop-talking-and-simply-are-5bfab6695093)
- [SBVR Wikipedia](https://en.wikipedia.org/wiki/Semantics_of_Business_Vocabulary_and_Business_Rules)

---

## Glossary

| Term | Definition |
|------|------------|
| **SBVR** | Semantics of Business Vocabulary and Business Rules - OMG standard |
| **RuleSpeak** | Notation for expressing SBVR rules in structured English |
| **CMCC** | Conceptual Model Completeness Conjecture - 5-primitive theory |
| **S-D-L-A-F** | Schema, Data, Lookups, Aggregations, Formulas - CMCC primitives |
| **Modality** | Obligatory, permitted, prohibited - rule enforcement levels |
| **Lambda Field** | CMCC term for computed/derived field |
| **Toolchain Drift** | Semantic changes introduced by translation hops |

---

*Document created December 11, 2024*
*Reference: RFC-Method-Implementation-Strategy.md*
