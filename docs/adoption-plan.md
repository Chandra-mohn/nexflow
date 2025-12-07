# Nexflow Adoption Plan: ccdsl + rules_engine Integration

> **Purpose**: Step-by-step plan to integrate existing DSL assets into Nexflow
> **Status**: ✅ COMPLETE
> **Version**: 1.0.0
> **Completed**: 2025-11-27

---

## Overview

This plan integrates assets from two existing projects:
- **ccdsl** (~70% reusable) → Primarily L2 Schema + L4 Decision Tables
- **rules_engine** (~85% reusable) → Primarily L4 Procedural Rules + L6 Code Gen

### File Extensions (Decided)

| Extension | Layer | Owner |
|-----------|-------|-------|
| `.proc` | L1 Process Orchestration | Data Engineering |
| `.schema` | L2 Schema Registry | Data Governance |
| `.xform` | L3 Transform Catalog | Data Engineering |
| `.rules` | L4 Business Rules | Business/Risk Team |
| `.infra` | L5 Infrastructure Binding | Platform/DevOps |

> **See**: [`file-organization-spec.md`](./file-organization-spec.md) for complete specification

```
┌─────────────────────────────────────────────────────────────────┐
│                     Adoption Execution Plan                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: L4 Business Rules     ██████████  ✅ COMPLETE         │
│  Phase 2: L2 Schema Registry    ██████████  ✅ COMPLETE         │
│  Phase 3: L3 Transform Catalog  ██████████  ✅ COMPLETE         │
│  Phase 4: L6 Code Gen Patterns  ██████████  ✅ COMPLETE         │
│                                                                  │
│  Total Tasks: 12 → All Complete                                 │
│  Actual Sessions: 3                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: L4 Business Rules (Highest Value)

**Goal**: Unify decision tables (ccdsl) + procedural rules (rules_engine) into complete L4 spec.

**Structure**: Modular documentation for token efficiency

```
docs/
├── L4-Business-Rules.md              # Overview (~200 lines)
└── L4/
    ├── decision-tables.md            # From ccdsl
    ├── procedural-rules.md           # From rules_engine
    ├── condition-types.md            # From ccdsl
    ├── action-types.md               # From ccdsl
    ├── action-catalog.md             # From rules_engine
    └── examples/
        ├── fraud-detection.rules
        └── credit-approval.rules
```

### Task 1.1: Create L4 Overview ✅
**Target**: `L4-Business-Rules.md` (~200 lines)
- [x] Purpose and scope
- [x] Two paradigms: decision tables vs procedural rules
- [x] How L1 references L4 (`route using`, `transform using`)
- [x] Links to detailed modules

### Task 1.2: Import Decision Tables Specification ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/DSL_DECISION_TABLES.md`
**Target**: `L4/decision-tables.md`
- [x] Table syntax and structure
- [x] Hit policies: `single_hit`, `multi_hit`, `first_match`
- [x] Exhaustiveness: gap detection, overlap detection
- [x] Code generation patterns

### Task 1.3: Import Condition Types ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/DSL_DECISION_TABLES.md`
**Target**: `L4/condition-types.md`
- [x] `equals`, `range`, `in_set`, `pattern`, `null_check`, `any`
- [x] Semantics and examples for each

### Task 1.4: Import Action Types ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/DSL_DECISION_TABLES.md`
**Target**: `L4/action-types.md`
- [x] `assign`, `calculate`, `lookup`, `call`, `emit`
- [x] Semantics and examples for each

### Task 1.5: Import Procedural Rules Grammar ✅
**Source**: `/Users/chandramohn/workspace/rules_engine/COMPLEX_RULES_SAMPLES.md`
**Target**: `L4/procedural-rules.md`
- [x] If-then-elseif-else-endif structure
- [x] AND/OR/parentheses boolean logic
- [x] Nested attribute access patterns
- [x] Multi-step rule examples

### Task 1.6: Import Action Catalog ✅
**Source**: `/Users/chandramohn/workspace/rules_engine/ACTIONS_CATALOG.md`
**Target**: `L4/action-catalog.md`
- [x] 20 credit card domain actions
- [x] Action interface pattern
- [x] Action registry pattern
- [x] Context data requirements per action

### Task 1.7: Create Examples ✅
**Target**: `L4/examples/`
- [x] `fraud-detection.rules` - Decision table example
- [x] `credit-approval.rules` - Procedural rules example

---

## Phase 2: L2 Schema Registry (Foundation)

**Goal**: Import data patterns and types, define schema DSL syntax.

**Structure**: Modular documentation for token efficiency

```
docs/
├── L2-Schema-Registry.md             # Overview (~200 lines)
└── L2/
    ├── mutation-patterns.md          # 9 patterns from ccdsl
    ├── type-system.md                # Types from ccdsl
    ├── streaming-annotations.md      # Native Nexflow
    ├── schema-evolution.md           # Native Nexflow
    └── examples/
        ├── customer.schema
        ├── transaction.schema
        └── card_account.schema
```

### Task 2.1: Create L2 Overview ✅
**Target**: `L2-Schema-Registry.md` (~200 lines)
- [x] Purpose and scope
- [x] Schema declaration syntax overview
- [x] How L1 references L2 (`schema auth_event_schema`)
- [x] Links to detailed modules

### Task 2.2: Import Data Mutation Patterns ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/core/CORE_DSL_SPECIFICATION.md`
**Target**: `L2/mutation-patterns.md`
- [x] `master_data` - Long-lived reference entities
- [x] `immutable_ledger` - Append-only records
- [x] `versioned_configuration` - Effective-dated configs
- [x] `operational_parameters` - Frequently updated params
- [x] `event_log` - Immutable event stream
- [x] `state_machine` - Lifecycle state transitions
- [x] `temporal_data` - Time-bounded validity
- [x] `reference_data` - Slowly changing lookups
- [x] `business_logic` - Rules and calculations

### Task 2.3: Import Type System ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/core/CORE_DSL_SPECIFICATION.md`
**Target**: `L2/type-system.md`
- [x] Base types: `string`, `integer`, `decimal`, `boolean`, `date`, `timestamp`, `uuid`
- [x] Constrained types: `[range: min..max]`, `[length: n]`, `[pattern: regex]`
- [x] Domain types: `currency_code`, `country_code`, `mcc_code`, `card_number`
- [x] Collection types: `list<T>`, `set<T>`, `map<K,V>`

### Task 2.4: Define Streaming Annotations ✅
**Target**: `L2/streaming-annotations.md`
**Native Nexflow Work**:
- [x] `key_fields` - Partition key specification
- [x] `time_field` - Event time field
- [x] `watermark_delay` - Watermark configuration
- [x] `late_data_handling` - Late arrival policy

### Task 2.5: Define Schema Evolution ✅
**Target**: `L2/schema-evolution.md`
**Native Nexflow Work**:
- [x] Versioning syntax
- [x] Compatibility rules (backward, forward, full)
- [x] Migration patterns

### Task 2.6: Create Entity Examples ✅
**Source**: ccdsl + rules_engine
**Target**: `L2/examples/`
- [x] `customer.schema` - Master data example
- [x] `transaction.schema` - Event log example
- [x] `card_account.schema` - State machine example

---

## Phase 3: L3 Transform Catalog (Reference)

**Goal**: Reference calculation patterns, define transform interface.

**Structure**: Modular documentation for token efficiency

```
docs/
├── L3-Transform-Catalog.md              # Overview (~200 lines)
└── L3/
    ├── expression-patterns.md           # From rules_engine
    ├── validation-patterns.md           # From ccdsl
    ├── transform-syntax.md              # Native Nexflow
    ├── builtin-functions.md             # Standard library
    └── examples/
        ├── normalize-amount.xform
        └── calculate-risk-score.xform
```

### Task 3.1: Create L3 Overview ✅
**Target**: `L3-Transform-Catalog.md` (~200 lines)
- [x] Purpose and scope
- [x] Transform vs calculation distinction
- [x] How L1 references L3 (`transform using`)
- [x] Links to detailed modules

### Task 3.2: Reference Expression Patterns ✅
**Source**: `/Users/chandramohn/workspace/rules_engine/rules-dsl/backend/grammar_parser/function_registry.py`
**Target**: `L3/expression-patterns.md`
- [x] Math expression parser (Shunting Yard)
- [x] Type-safe value comparison
- [x] Nested attribute resolution

### Task 3.3: Reference Validation Patterns ✅
**Source**: `/Users/chandramohn/workspace/ccdsl/core/CORE_DSL_SPECIFICATION.md`
**Target**: `L3/validation-patterns.md`
- [x] `on_create` / `on_update` behaviors
- [x] `validate_*` patterns
- [x] `recalculate_*` patterns

### Task 3.4: Define L3 Transform Syntax ✅
**Target**: `L3/transform-syntax.md`
**Native Nexflow Work**:
- [x] Transform declaration syntax
- [x] Input/output type signatures
- [x] Purity and side-effect annotations
- [x] Composition patterns

### Task 3.5: Define Builtin Functions ✅
**Target**: `L3/builtin-functions.md`
- [x] Math functions (abs, round, min, max, etc.)
- [x] String functions (trim, upper, lower, concat, etc.)
- [x] Date/time functions (now, date_diff, format, etc.)
- [x] Type conversion functions (to_string, to_decimal, etc.)

### Task 3.6: Create Examples ✅
**Target**: `L3/examples/`
- [x] `normalize-amount.xform` - Currency conversion example
- [x] `calculate-risk-score.xform` - Multi-factor calculation

---

## Phase 4: L6 Code Gen Patterns (Reference Only)

**Goal**: Reference existing code generation patterns for UDF compilation.

### Task 4.1: Reference Code Gen Architecture ✅
**Source**:
- `/Users/chandramohn/workspace/rules_engine/CURRENT_STATE_SUMMARY.md`
- `/Users/chandramohn/workspace/rules_engine/rules-dsl/backend/grammar_parser/template_code_generator.py`
**Target**: `L6-Compilation-Pipeline.md` Section 7

**Patterns to Reference**:
- [x] ANTLR visitor pattern for AST traversal
- [x] Template-based code generation
- [x] Type-safe comparison generation
- [x] Action framework and context patterns

---

## Execution Order

```
Session 1: Phase 1 (L4 Business Rules)
├── Task 1.1: Create L4 Overview
├── Task 1.2: Import Decision Tables Spec
├── Task 1.3: Import Condition Types
├── Task 1.4: Import Action Types
├── Task 1.5: Import Procedural Rules Grammar
├── Task 1.6: Import Action Catalog
└── Task 1.7: Create Examples

Session 2: Phase 2 (L2 Schema Registry)
├── Task 2.1: Create L2 Overview
├── Task 2.2: Import Data Mutation Patterns
├── Task 2.3: Import Type System
├── Task 2.4: Define Streaming Annotations
├── Task 2.5: Define Schema Evolution
└── Task 2.6: Create Entity Examples

Session 3: Phase 3 + 4 (L3 Transform + L6 Reference)
├── Task 3.1: Create L3 Overview
├── Task 3.2: Reference Expression Patterns
├── Task 3.3: Reference Validation Patterns
├── Task 3.4: Define L3 Transform Syntax
├── Task 3.5: Define Builtin Functions
├── Task 3.6: Create Examples
└── Task 4.1: Reference Code Gen (already done)
```

---

## Expected Outcome

### After Phase 1 (L4)
```
L4 Business Rules: 5% → 90%
- Complete decision table specification
- Complete procedural rules specification
- 20 action examples
- Unified L4 reference for L1 DSL
```

### After Phase 2 (L2)
```
L2 Schema Registry: 10% → 80%
- 9 data mutation patterns
- Complete type system
- 5+ entity examples
- Schema DSL syntax defined
```

### After Phase 3 (L3)
```
L3 Transform Catalog: 5% → 95%
- Expression patterns documented
- Validation patterns documented
- Transform DSL syntax defined
- Domain-specific functions (card ops, financial, risk)
- Window/aggregate functions for streaming
- Format-agnostic structured data functions
```

### Final State (Achieved + L5 Update)
```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Nexflow Progress After Full Adoption + L5            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  L1 Orchestration    ████████████████████████████████████░░░░  90% ✅   │
│  L2 Schema Registry  ████████████████████████████████░░░░░░░░  80% ✅   │
│  L3 Transform        ██████████████████████████████████████░░  95% ✅   │
│  L4 Business Rules   ████████████████████████████████████░░░░  90% ✅   │
│  L5 Infrastructure   ████████████████████████████████████░░░░  90% ✅   │
│  L6 Compilation      ████████████████████████████░░░░░░░░░░░░  70% ✅   │
│                                                                          │
│  OVERALL: 34% → 67% → 87%  (+53% total acceleration)                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Next Steps: Option A (Towns Anatomy)

With the adoption plan + L5 complete, **Option A (Towns Anatomy)** status:
- L2: ✅ Schema DSL syntax complete, streaming annotations complete
- L3: ✅ Transform catalog with builtin functions complete
- L4: ✅ Complete from adoption
- L5: ✅ Infrastructure Binding specification complete (2025-11-27)

### L5 Deliverables (2025-11-27)
- `L5-Infrastructure-Binding.md` - Complete overview (~650 lines)
- `L5/stream-bindings.md` - Kafka, Kinesis, Pulsar configurations
- `L5/lookup-bindings.md` - MongoDB, Redis, PostgreSQL, Cassandra, Elasticsearch
- `L5/state-checkpoints.md` - RocksDB, HashMap, S3, HDFS checkpoint storage
- `L5/resource-allocation.md` - Parallelism, memory, CPU configuration
- `L5/secret-management.md` - Vault, AWS Secrets Manager, Kubernetes secrets
- `L5/deployment-targets.md` - Kubernetes, YARN, Standalone, Docker Compose
- `L5/examples/development.infra` - Local development configuration
- `L5/examples/production.infra` - Full production binding
- `L5/examples/multi-region.infra` - Multi-region with DR

### Remaining Work
1. L3 domain-specific function expansion (financial calculations)
2. End-to-end integration examples (L1→L6 complete pipeline)
3. Grammar files (ANTLR4 .g4 files for all layers)

---

## Quick Start Command

To begin execution:
```
"Let's start Phase 1, Task 1.1: Import Decision Tables from ccdsl"
```
