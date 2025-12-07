# CCDSL → Nexflow Feature Matrix

> **Purpose**: Map existing ccdsl (Credit Card DSL) features to Nexflow layers
> **Status**: Analysis Document
> **Version**: 0.1.0
> **Last Updated**: 2025-01-XX

---

## 1. Executive Summary

This document analyzes the existing **ccdsl** (Credit Card Domain-Specific Language) work and maps its features to the **Nexflow** layered architecture. The goal is to identify reusable components, avoid duplicate work, and ensure consistency across the DSL ecosystem.

### Key Findings

| Category | ccdsl Features | Nexflow Mapping | Reusability |
|----------|---------------|------------------|-------------|
| Data Patterns | 9 mutation patterns | L2 Schema Registry | **High** - Direct import |
| Entity Definitions | 4 core entities | L2 Schema Registry | **High** - Domain examples |
| Decision Tables | Complete spec | L4 Business Rules | **High** - Direct import |
| Type System | Base + domain types | L2 Schema Registry | **Medium** - Needs extension |
| Module System | Import/export | All Layers | **Medium** - Architecture alignment |
| Workflow Defs | State machines | L1 Orchestration | **Low** - Different paradigm |
| BIAN Mapping | Banking domains | L2/L4 | **Medium** - Reference model |

---

## 2. Reusability Summary

### Overall Assessment

```
┌────────────────────────────────────────────────────┐
│  ccdsl → Nexflow Reusability                      │
├────────────────────────────────────────────────────┤
│                                                    │
│  Direct Import:     ~45%  ████████████░░░░░░░░    │
│  Adapt/Reference:   ~25%  ██████░░░░░░░░░░░░░░    │
│  Not Applicable:    ~30%  ████████░░░░░░░░░░░░    │
│                                                    │
│  TOTAL LEVERAGEABLE: ~70%                         │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Quantitative Breakdown

| Category | ccdsl Content | Reusability | Estimate |
|----------|--------------|-------------|----------|
| **Data Mutation Patterns** | 9 patterns | ✅ Direct import | **100%** |
| **Decision Tables Spec** | Complete spec (~40% of ccdsl) | ✅ Direct import | **95%** |
| **Entity Definitions** | 4 core entities | ✅ As examples | **100%** |
| **Type System** | Base + domain types | ✅ Foundation | **90%** |
| **Field Constraints** | Validation rules | ✅ Direct import | **95%** |
| **Module System** | Namespaces, imports | ⚠️ Adapt | **60%** |
| **Workflow/State Machines** | Entity lifecycles | ⚠️ Reference only | **30%** |
| **BIAN Mapping** | Domain alignment | ⚠️ Reference | **50%** |
| **CRUD Operations** | Batch-oriented | ❌ Not applicable | **0%** |

### Leverage Categories

| Leverage Level | Percentage | Components |
|----------------|------------|------------|
| **Direct Import** | ~45% | Decision tables, mutation patterns, types, entities, constraints |
| **Adapt/Reference** | ~25% | Module system, state machines → correlation patterns, BIAN domains |
| **Not Applicable** | ~30% | CRUD operations, synchronous calls, batch-only workflows |

### Value Assessment

The **~70% leverageable** content represents significant value:

1. **Decision Tables Specification** (~40% of ccdsl substance)
   - Maps almost perfectly to L4 Business Rules
   - Complete condition/action type system
   - Exhaustiveness checking algorithms
   - Code generation patterns

2. **Data Mutation Patterns** (9 patterns)
   - Direct foundation for L2 Schema Registry
   - Streaming-compatible with minor annotations

3. **Type System + Entities**
   - Production-tested credit card domain types
   - Canonical examples for validation

The **~30% not applicable** is fundamentally batch/CRUD-oriented, which Nexflow intentionally doesn't cover (streaming-first paradigm).

---

## 3. Detailed Feature Matrix

### 3.1 Data Mutation Patterns

ccdsl defines 9 data mutation patterns. These map directly to L2 Schema Registry schema behaviors.

| Pattern | ccdsl Definition | Nexflow Layer | Reusability | Notes |
|---------|-----------------|----------------|-------------|-------|
| `master_data` | Long-lived reference entities, infrequent updates | L2 Schema | ✅ **Direct** | Customer, merchant profiles |
| `immutable_ledger` | Append-only, no updates/deletes | L2 Schema | ✅ **Direct** | Transaction logs, audit trails |
| `versioned_configuration` | Track all versions with effective dates | L2 Schema | ✅ **Direct** | Rate tables, fee schedules |
| `operational_parameters` | Frequently updated system params | L2 Schema | ✅ **Direct** | Limits, thresholds |
| `event_log` | Immutable event stream | L2 Schema | ✅ **Direct** | Auth events, state changes |
| `state_machine` | Lifecycle state transitions | L2 Schema + L1 | ⚠️ **Adapt** | Card status, dispute lifecycle |
| `temporal_data` | Time-bounded validity | L2 Schema | ✅ **Direct** | Promotions, offers |
| `reference_data` | Slowly changing lookups | L2 Schema | ✅ **Direct** | Country codes, MCC codes |
| `business_logic` | Rules and calculations | L4 Rules | ✅ **Direct** | Fee calc, risk scoring |

**Recommendation**: Import all 9 patterns into L2-Schema-Registry.md as schema behavior annotations.

### 3.2 Entity Definitions

ccdsl defines credit card domain entities with fields, types, and mutation patterns.

| Entity | ccdsl Fields | Nexflow Layer | Reusability | Notes |
|--------|-------------|----------------|-------------|-------|
| `customer` | 12 fields (id, status, risk_score, etc.) | L2 Schema | ✅ **Direct** | Master data example |
| `card_account` | 15 fields (card_number, status, limits, etc.) | L2 Schema | ✅ **Direct** | State machine example |
| `transaction` | 18 fields (auth_code, amount, MCC, etc.) | L2 Schema | ✅ **Direct** | Immutable ledger example |
| `fee_transaction` | 10 fields (fee_type, amount, etc.) | L2 Schema | ✅ **Direct** | Derived record example |

**Entity Structure from ccdsl**:
```
entity customer {
    mutation_pattern: master_data

    fields {
        customer_id: uuid [primary_key]
        status: customer_status
        credit_score: integer [range: 300..850]
        risk_tier: risk_tier
        // ... more fields
    }

    behaviors {
        on_create: validate_customer_data
        on_update: recalculate_risk_tier
    }
}
```

**Recommendation**: Use these as canonical examples in L2 documentation and validation test cases.

### 3.3 Decision Tables Specification

ccdsl has a comprehensive decision tables specification that maps directly to L4 Business Rules.

| Feature | ccdsl Capability | Nexflow Layer | Reusability | Notes |
|---------|-----------------|----------------|-------------|-------|
| Condition Types | `equals`, `range`, `in_set`, `pattern`, `null_check`, `any` | L4 Rules | ✅ **Direct** | Complete condition set |
| Action Types | `assign`, `calculate`, `lookup`, `call`, `emit` | L4 Rules | ✅ **Direct** | Complete action set |
| Table Structures | Single-hit, multi-hit, first-match | L4 Rules | ✅ **Direct** | All major paradigms |
| Exhaustiveness | Gap detection, overlap detection | L4 Rules | ✅ **Direct** | Critical for correctness |
| Code Generation | Java, SQL, Python targets | L6 Compiler | ✅ **Direct** | Multi-target support |
| Optimization | Row ordering, condition grouping | L6 Compiler | ✅ **Direct** | Performance patterns |

**Decision Table Example from ccdsl**:
```
decision_table transaction_fee_calculation {
    input: transaction
    output: fee_amount, fee_type
    hit_policy: first_match

    conditions {
        transaction_type: equals
        merchant_category: in_set
        amount_range: range
    }

    actions {
        fee_amount: calculate
        fee_type: assign
    }

    rules {
        | transaction_type | merchant_category | amount_range | fee_amount | fee_type |
        |-----------------|-------------------|--------------|------------|----------|
        | "purchase"      | ["5411","5412"]   | 0..100       | amount*0.01| "swipe"  |
        | "purchase"      | ["5411","5412"]   | 100..        | 1.00       | "flat"   |
        | "cash_advance"  | *                 | *            | amount*0.03| "cash"   |
    }
}
```

**Recommendation**: Import entire decision tables specification into L4-Business-Rules.md.

### 3.4 Type System

ccdsl defines base types and domain-specific types.

| Type Category | ccdsl Types | Nexflow Layer | Reusability | Notes |
|---------------|-------------|----------------|-------------|-------|
| **Base Types** | `string`, `integer`, `decimal`, `boolean`, `date`, `timestamp`, `uuid` | L2 Schema | ✅ **Direct** | Standard types |
| **Constrained Types** | `[range: min..max]`, `[length: n]`, `[pattern: regex]` | L2 Schema | ✅ **Direct** | Validation constraints |
| **Domain Types** | `currency_code`, `country_code`, `mcc_code`, `card_number` | L2 Schema | ✅ **Direct** | Credit card specific |
| **Enum Types** | `customer_status`, `card_status`, `transaction_type` | L2 Schema | ✅ **Direct** | Controlled vocabularies |
| **Collection Types** | `list<T>`, `set<T>`, `map<K,V>` | L2 Schema | ✅ **Direct** | Container types |

**Recommendation**: Adopt type system as foundation for L2 schema definitions.

### 3.5 Module System

ccdsl has a module system for organizing definitions.

| Feature | ccdsl Capability | Nexflow Layer | Reusability | Notes |
|---------|-----------------|----------------|-------------|-------|
| Namespaces | `module credit_card.authorization` | All Layers | ⚠️ **Adapt** | Need cross-layer consistency |
| Imports | `import credit_card.entities.*` | All Layers | ⚠️ **Adapt** | Reference resolution |
| Exports | `export { customer, transaction }` | All Layers | ⚠️ **Adapt** | Public API definition |
| Versioning | Module version declarations | All Layers | ⚠️ **Adapt** | Version compatibility |

**Recommendation**: Adapt module system to work across L1-L4 layers with unified namespace resolution.

### 3.6 Workflow Definitions

ccdsl defines workflows differently than Nexflow's streaming orchestration.

| Feature | ccdsl Capability | Nexflow Layer | Reusability | Notes |
|---------|-----------------|----------------|-------------|-------|
| State Machines | Entity lifecycle states | L1 + L2 | ⚠️ **Adapt** | Different paradigm |
| Transitions | Guard conditions, actions | L4 Rules | ⚠️ **Adapt** | Can inform correlation |
| Events | State change triggers | L1 Orchestration | ⚠️ **Adapt** | Map to stream events |

**ccdsl Workflow Example**:
```
workflow card_activation {
    entity: card_account

    states {
        issued -> pending_activation
        pending_activation -> active | cancelled
        active -> suspended | closed
        suspended -> active | closed
    }

    transitions {
        issued -> pending_activation {
            trigger: card_mailed
            action: send_activation_reminder
        }
    }
}
```

**Recommendation**: Use as reference for L1 state blocks and correlation patterns, but don't import directly. Nexflow's streaming-first model is fundamentally different.

### 3.7 BIAN Domain Mapping

ccdsl references Banking Industry Architecture Network (BIAN) domains.

| BIAN Domain | ccdsl Coverage | Nexflow Layer | Reusability | Notes |
|-------------|---------------|----------------|-------------|-------|
| Card Authorization | Full | L1 Examples | ✅ **Direct** | Primary use case |
| Card Clearing | Partial | L1 Examples | ✅ **Direct** | Settlement flows |
| Card Billing | Partial | L1 Examples | ⚠️ **Adapt** | Batch-oriented |
| Fraud Detection | Mentioned | L4 Rules | ⚠️ **Adapt** | Rules integration |
| Customer Management | Partial | L2 Schema | ✅ **Direct** | Entity definitions |

**Recommendation**: Use BIAN mapping as validation framework for domain completeness.

---

## 3. Integration Recommendations

### 3.1 Immediate Imports (High Reusability)

These components can be imported directly into Nexflow with minimal modification:

| Component | Source | Target | Action |
|-----------|--------|--------|--------|
| 9 Data Mutation Patterns | `CORE_DSL_SPECIFICATION.md` | L2-Schema-Registry.md | Copy definitions, add streaming context |
| Decision Tables Spec | `DSL_DECISION_TABLES.md` | L4-Business-Rules.md | Copy entire specification |
| Entity Definitions | `CREDIT_CARD_DOMAIN.md` | L2 Examples | Use as canonical examples |
| Type System | `CORE_DSL_SPECIFICATION.md` | L2-Schema-Registry.md | Adopt as type foundation |
| Condition/Action Types | `DSL_DECISION_TABLES.md` | L4-Business-Rules.md | Direct import |

### 3.2 Adaptations Required (Medium Reusability)

These components need modification to fit Nexflow's streaming paradigm:

| Component | Adaptation Needed | Target Layer |
|-----------|-------------------|--------------|
| Module System | Cross-layer namespace resolution | L1-L4 |
| State Machines | Map to streaming correlation patterns | L1 |
| BIAN Domains | Add streaming-specific service boundaries | L2/L4 |
| Validation Rules | Adapt for streaming context | L3/L4 |

### 3.3 Reference Only (Low Reusability)

These components serve as reference but don't map directly:

| Component | Reason | Use As |
|-----------|--------|--------|
| Batch Workflows | Different execution model | Design reference |
| CRUD Operations | Not streaming-native | Background context |
| Synchronous Calls | Streaming is async-first | Anti-pattern reference |

---

## 4. Layer-by-Layer Import Plan

### 4.1 L2 Schema Registry

**Import from ccdsl**:
```yaml
data_mutation_patterns:
  source: CORE_DSL_SPECIFICATION.md § "Data Mutation Patterns"
  action: Direct import + streaming annotations

entity_definitions:
  source: CREDIT_CARD_DOMAIN.md
  action: Use as canonical examples

type_system:
  source: CORE_DSL_SPECIFICATION.md § "Type System"
  action: Adopt as foundation, extend for streaming

field_constraints:
  source: CORE_DSL_SPECIFICATION.md § "Field Attributes"
  action: Direct import
```

### 4.2 L3 Transform Catalog

**Import from ccdsl**:
```yaml
validation_patterns:
  source: CORE_DSL_SPECIFICATION.md § "Behaviors"
  action: Adapt to streaming transforms

calculation_patterns:
  source: DSL_DECISION_TABLES.md § "Action Types"
  action: Map to UDF signatures
```

### 4.3 L4 Business Rules

**Import from ccdsl**:
```yaml
decision_tables:
  source: DSL_DECISION_TABLES.md (entire document)
  action: Direct import

condition_types:
  source: DSL_DECISION_TABLES.md § "Condition Types"
  action: Direct import

action_types:
  source: DSL_DECISION_TABLES.md § "Action Types"
  action: Direct import

exhaustiveness_checking:
  source: DSL_DECISION_TABLES.md § "Completeness Validation"
  action: Direct import

code_generation:
  source: DSL_DECISION_TABLES.md § "Code Generation"
  action: Integrate with L6 compiler
```

---

## 5. Gap Analysis

### 5.1 Features in ccdsl NOT in Nexflow

| Feature | ccdsl Has | Nexflow Status | Recommendation |
|---------|-----------|-----------------|----------------|
| Entity CRUD operations | ✅ | ❌ Not applicable | Skip - streaming paradigm |
| Synchronous lookups | ✅ | ⚠️ Async only | Keep async, add timeout patterns |
| Batch workflows | ✅ | ⚠️ Micro-batch mode | Sufficient for batch needs |
| Schema migrations | ✅ | ❌ Not defined | Consider for L2 |
| Audit logging DSL | ✅ | ❌ Not defined | Consider for L2/L3 |

### 5.2 Features in Nexflow NOT in ccdsl

| Feature | Nexflow Has | ccdsl Status | Notes |
|---------|--------------|--------------|-------|
| Streaming orchestration | ✅ | ❌ | Core Nexflow value |
| Event-time processing | ✅ | ❌ | Watermarks, late data |
| Correlation patterns | ✅ | ❌ | Await/hold semantics |
| Backpressure handling | ✅ | ❌ | Streaming-specific |
| Checkpointing | ✅ | ❌ | Streaming-specific |
| Parallelism hints | ✅ | ❌ | Streaming-specific |
| Window operations | ✅ | ❌ | Tumbling, sliding, session |

---

## 6. Unified Architecture Vision

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nexflow Unified Architecture                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 L1: Process Orchestration                │    │
│  │         (Streaming pipelines, correlation, windows)      │    │
│  │                    [Nexflow Native]                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│  ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐       │
│  │  L2: Schema     │ │ L3: Transform│ │ L4: Business    │       │
│  │  Registry       │ │ Catalog      │ │ Rules           │       │
│  │                 │ │              │ │                 │       │
│  │ [ccdsl imports]:│ │ [ccdsl ref]: │ │ [ccdsl imports]:│       │
│  │ • 9 mutation    │ │ • Validation │ │ • Decision      │       │
│  │   patterns      │ │   patterns   │ │   tables        │       │
│  │ • Type system   │ │ • Calc       │ │ • Condition     │       │
│  │ • Entity defs   │ │   patterns   │ │   types         │       │
│  │ • Constraints   │ │              │ │ • Action types  │       │
│  └─────────────────┘ └─────────────┘ └─────────────────┘       │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              ▼                               ▼                  │
│  ┌─────────────────────────┐ ┌─────────────────────────┐       │
│  │  L5: Infrastructure     │ │  L6: Compilation        │       │
│  │  Binding                │ │  Pipeline               │       │
│  │  [Nexflow Native]      │ │  [+ ccdsl code gen]     │       │
│  └─────────────────────────┘ └─────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Next Steps

### Immediate Actions

1. **L2 Schema Registry**:
   - Import 9 data mutation patterns
   - Import type system definitions
   - Add streaming-specific annotations

2. **L4 Business Rules**:
   - Import complete decision tables specification
   - Map condition/action types to L1 references
   - Define code generation integration with L6

### Future Considerations

3. **Module System Unification**:
   - Design cross-layer namespace resolution
   - Version compatibility rules

4. **Business Rules DSL Integration**:
   - User mentioned separate business rules DSL work
   - Plan integration when ready

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Initial feature matrix |
