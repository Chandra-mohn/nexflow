# Nexflow Toolchain - L1-L6 Code Generation Status

**Date**: December 12, 2025 (Updated)
**Project**: nexflow-toolchain
**Purpose**: Comprehensive status of DSL-to-Java code generation capabilities

---

## Executive Summary

The Nexflow toolchain implements a **6-layer DSL architecture** (L1-L6) designed for **zero developer Java coding** - the complete streaming pipeline should be generated from DSL files.

| Layer | DSL Name | Extension | Purpose | Code Generation Status |
|-------|----------|-----------|---------|------------------------|
| **L1** | ProcDSL | `.proc` | Process Orchestration (the "railroad") | ⚠️ Partial - operators wired, inline route needs work |
| **L2** | SchemaDSL | `.schema` | Schema Registry (data structures) | ✅ Working - Java Records |
| **L3** | TransformDSL | `.xform` | Transform Catalog (transformations) | ✅ Working - with collections |
| **L4** | RulesDSL | `.rules` | Business Rules (decision logic) | ✅ Working - decision tables + rules |
| **L5** | Infrastructure | `.infra` (YAML) | Infrastructure Binding | ❌ Specification only |
| **L6** | Compilation | N/A | Compilation Pipeline | ❌ Not implemented |

---

## The Zero-Code Vision

### Key Principle
> **Developers write ONLY DSL files. The toolchain generates 100% production-ready Java code.**

Each layer handles its domain:
- **L1**: Flow structure (sources, sinks, operator sequence)
- **L2**: Data types (POJOs, validation)
- **L3**: Data transformations (MapFunction implementations)
- **L4**: Business rules (ProcessFunction, routing logic)
- **L5**: Physical infrastructure (Kafka topics, MongoDB collections, etc.)
- **L6**: Orchestrates compilation, combines all layer outputs

### Current Gap
The L1 generator currently produces **`[STUB]` comments** instead of wiring complete implementations from L3/L4. This violates the zero-code principle.

---

## Layer Architecture

### How Layers Connect

```
┌─────────────────────────────────────────────────────────────────────────┐
│  L1 (.proc) - The Railroad                                              │
│  ───────────────────────────                                            │
│  receive events from auth_events                                        │
│      schema auth_event_schema              → L2 resolves structure      │
│  enrich using customer_lookup              → L3 + L5 resolves lookup    │
│  transform using normalize_amount          → L3 generates MapFunction   │
│  route using fraud_rules                   → L4 generates ProcessFunction│
│  emit to processed_transactions            → L5 resolves physical topic │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  L6 Compilation Pipeline (NOT YET IMPLEMENTED)                          │
│  ─────────────────────────────────────────────                          │
│  1. Parse all DSL files (L1, L2, L3, L4)                               │
│  2. Build cross-layer dependency graph                                  │
│  3. Apply L5 infrastructure bindings                                    │
│  4. Generate complete code for each layer                               │
│  5. Wire L1 operators to L3/L4 generated classes                        │
│  6. Output: Complete Flink job + all operators + schemas                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Operator Resolution Map

| L1 Operator | Resolved By | Generated Class Pattern |
|-------------|-------------|-------------------------|
| `receive...schema X` | L2 Schema Generator | `X.java` (POJO) |
| `transform using X` | L3 Transform Generator | `XFunction implements MapFunction` |
| `route using X` | L4 Rules Generator | `XRouter implements ProcessFunction` |
| `enrich using X` | L3 + L5 Binding | `XAsyncFunction implements AsyncFunction` |
| `aggregate using X` | L4 Rules Generator | `XAggregator implements AggregateFunction` |
| `emit to X` | L5 Infrastructure | Physical topic/collection binding |

---

## Layer Details

### L1 - Process Orchestration (ProcDSL)

**Purpose**: Define the data flow "railroad" - structure only, NOT business logic

**Grammar**: `ProcDSL.g4` (539 lines)

**DSL Example**:
```proc
process fraud_detection
    parallelism hint 8
    partition by customer_id
    time by event_timestamp
        watermark delay 5 seconds
    mode stream

    receive transactions from kafka_transactions
        schema transaction

    enrich using customer_lookup on card_id
    transform using normalize_amount
    route using fraud_rules
    window tumbling 1 minute
    aggregate using fraud_summary

    emit to processed_transactions
    emit to fraud_alerts
end
```

**Current Status**: ⚠️ **Partial** (Updated Dec 12, 2025)

| Feature | Status | Notes |
|---------|--------|-------|
| Job class structure | ✅ | Main class, constants, env setup |
| Kafka source | ✅ | With JSON deserializer |
| Kafka sink | ✅ | With JSON serializer |
| Transform wiring | ✅ | Generates `map(new TransformClass())` |
| Checkpoint config | ✅ | Exactly-once semantics |
| Enrich operator | ✅ | Generates AsyncDataStream.unorderedWait() |
| Route using | ✅ | Generates `.process(new RulesClass())` |
| Route when (inline) | ⚠️ | TODO: condition evaluation |
| Aggregate operator | ✅ | Generates `.aggregate(new AggregatorClass())` |
| Merge operator | ✅ | Generates stream union |
| Window operator | ⚠️ | Basic tumbling window only |

**Generated Example** (current state):
```java
// Transform: normalize_amount
DataStream<TransformResult> transformed1Stream = enrichedStream
    .map(new NormalizeAmountTransform())
    .name("transform-normalize_amount");

// Route: using fraud_rules (L4 wired)
SingleOutputStreamOperator<RoutedRecord> routed2Stream = transformed1Stream
    .process(new FraudRulesRules())
    .name("route-fraud_rules");
```

**Remaining Work**: Inline `route when <condition>` needs condition expression parsing.

---

### L2 - Schema Registry (SchemaDSL)

**Purpose**: Define data structures, types, and constraints

**Grammar**: `SchemaDSL.g4` (716 lines)
**Extension**: `.schema`

**Status**: ✅ **Working**

Generates complete POJOs with:
- All fields with correct Java types
- Getters and setters
- toString() method
- Serializable implementation
- Builder pattern support

---

### L3 - Transform Catalog (TransformDSL)

**Purpose**: Define data transformations (pure functions)

**Grammar**: `TransformDSL.g4` (597 lines)
**Extension**: `.xform`

**Status**: ⚠️ **Partial**

| Transform Type | Status | Notes |
|----------------|--------|-------|
| Simple transform | ✅ | Compiles after recent fixes |
| Expression-level | ✅ | Multi-input calculations work |
| Block transform | ❌ | Missing input POJO generation |
| Composition | ❌ | Not implemented |
| Impure (external calls) | ❌ | Not implemented |

**Generated**: `MapFunction<InputType, Map<String, Object>>` implementations

---

### L4 - Business Rules (RulesDSL)

**Purpose**: Define decision logic (decision tables, procedural rules)

**Grammar**: `RulesDSL.g4` (622 lines)
**Extension**: `.rules`

**Status**: ✅ **Working** (Dec 12, 2025)

| Component | Status |
|-----------|--------|
| Decision table structure | ✅ Generates correctly |
| Row matching logic | ✅ Generates correctly |
| Result values | ✅ Returns action values correctly |
| Procedural conditions | ✅ String comparison uses `.equals()` |
| Collection operations | ✅ RFC implemented |

**Recent Fixes**:
- Decision table result values now return correctly (e.g., `"low"`, `"high"`, `"medium"`)
- Procedural rule string comparisons now use `.equals()` instead of `==`
  ```java
  // Before (bug): status() == "pending"
  // After (fixed): "pending".equals(status())
  ```

---

### L5 - Infrastructure Binding

**Purpose**: Map logical names to physical infrastructure

**Format**: YAML (`.infra`)

**Status**: ❌ **Specification Only** - No parser/generator implemented

**Specification Defines**:
- Stream bindings (Kafka, Kinesis, Pulsar)
- Lookup bindings (MongoDB, Redis, PostgreSQL)
- State backends (RocksDB, HashMap)
- Checkpoint storage (S3, HDFS, GCS)
- Resource allocation (parallelism, memory, CPU)
- Secret management (Vault, AWS Secrets Manager)
- Environment profiles (dev, staging, prod)

**Example**:
```yaml
# production.infra
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}

lookups:
  customers:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers
```

---

### L6 - Compilation Pipeline

**Purpose**: Orchestrate all generators to produce complete artifacts

**Status**: ❌ **Not Implemented**

**Specification Defines**:
- Multi-phase compilation (Lexing → Parsing → AST → Semantic → IR → CodeGen)
- Cross-layer dependency resolution
- Flink SQL generation
- Spark code generation
- UDF generation from L4 rules

**Required for Zero-Code**:
1. Parse all DSL files
2. Build unified cross-layer AST
3. Resolve all references (L1 → L2, L3, L4)
4. Apply L5 infrastructure bindings
5. Generate complete code for each layer
6. Wire all components together

---

## Priority Roadmap

### Phase 1: L1 Compilable Pipeline (Current Focus)
- [x] Fix Kafka source with JSON deserializer
- [x] Fix Kafka sink with JSON serializer
- [x] Wire transform operators
- [ ] Fix type flow through pipeline
- [ ] Generate complete (not stub) operator wiring

### Phase 2: L4 Decision Logic
- [ ] Fix decision table result generation
- [ ] Fix procedural rule conditions
- [ ] Generate ProcessFunction implementations

### Phase 3: L5 Infrastructure Binding
- [ ] Implement YAML parser for `.infra` files
- [ ] Create binding resolution in L1 generator
- [ ] Support environment profiles

### Phase 4: L6 Compilation Orchestration
- [ ] Implement master compiler
- [ ] Cross-layer dependency graph
- [ ] Complete zero-code generation

---

## File Locations

### Specifications
```
/Users/chandramohn/workspace/nexflow/docs/
├── L1-Process-Orchestration-DSL.md
├── L2-Schema-Registry.md
├── L3-Transform-Catalog.md
├── L4-Business-Rules.md
├── L5-Infrastructure-Binding.md
└── L6-Compilation-Pipeline.md
```

### Grammar Files
```
grammar/
├── ProcDSL.g4      # L1
├── SchemaDSL.g4    # L2
├── TransformDSL.g4 # L3
└── RulesDSL.g4     # L4
```

### Code Generators
```
backend/generators/
├── flow/       # L1 - 9 modules
├── schema/     # L2 - 4 modules
├── transform/  # L3 - 8 modules
└── rules/      # L4 - 6 modules
```

### Generated Output
```
generated/flink/src/main/java/nexflow/flink/
├── flow/       # Job classes
├── schema/     # POJOs
├── transform/  # MapFunction implementations
└── rules/      # ProcessFunction/decision tables
```

---

*Document updated December 8, 2024 - Corrected L5/L6 understanding based on spec review*
