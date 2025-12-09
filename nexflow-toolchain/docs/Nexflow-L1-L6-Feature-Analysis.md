# Nexflow Toolchain - L1 to L6 Complete Feature Analysis

**Date**: December 8, 2024
**Purpose**: Comprehensive grammar vs code generator coverage analysis for all 6 DSL layers
**Reference**: COVENANT-Code-Generation-Principles.md

---

## Executive Summary

The Nexflow toolchain implements a **6-layer DSL architecture** designed for **zero developer Java coding**. This document provides a comprehensive analysis of grammar features vs generator implementation for each layer.

| Layer | DSL Name | Extension | Grammar Features | Implemented | Coverage | Status |
|-------|----------|-----------|------------------|-------------|----------|--------|
| **L1** | ProcDSL | `.proc` | 68 | 66 | **97%** | Production-Ready |
| **L2** | SchemaDSL | `.schema` | 95 | 72 | **76%** | Working |
| **L3** | TransformDSL | `.xform` | 62 | 38 | **61%** | Partial |
| **L4** | RulesDSL | `.rules` | 54 | 35 | **65%** | Partial |
| **L5** | Infrastructure | `.infra` | N/A | N/A | **0%** | Spec Only |
| **L6** | Compilation | N/A | N/A | N/A | **0%** | Not Implemented |

---

## Architecture Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NEXFLOW 6-LAYER ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  L6 - COMPILATION PIPELINE (Orchestrator)                        │   │
│  │  ────────────────────────────────────────                        │   │
│  │  Parses all DSLs → Resolves references → Generates final code    │   │
│  │  Status: ❌ NOT IMPLEMENTED                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                    ┌───────────────┼───────────────┐                    │
│                    ▼               ▼               ▼                    │
│  ┌────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐  │
│  │ L1 - ProcDSL       │ │ L2 - SchemaDSL   │ │ L3 - TransformDSL    │  │
│  │ ────────────       │ │ ──────────────   │ │ ─────────────────    │  │
│  │ Process Flow       │ │ Data Schemas     │ │ Transformations      │  │
│  │ (the "railroad")   │ │ (POJOs)          │ │ (MapFunction)        │  │
│  │                    │ │                  │ │                      │  │
│  │ Coverage: 97%      │ │ Coverage: 76%    │ │ Coverage: 61%        │  │
│  │ Status: ✅ Ready   │ │ Status: ✅ Work  │ │ Status: ⚠️ Partial   │  │
│  └────────────────────┘ └──────────────────┘ └──────────────────────┘  │
│                    │               │               │                    │
│                    ▼               │               ▼                    │
│  ┌────────────────────┐            │    ┌──────────────────────┐       │
│  │ L4 - RulesDSL      │            │    │ L5 - Infrastructure  │       │
│  │ ────────────       │            │    │ ─────────────────    │       │
│  │ Business Rules     │◄───────────┘    │ Physical Bindings    │       │
│  │ (ProcessFunction)  │                 │ (Kafka, MongoDB...)  │       │
│  │                    │                 │                      │       │
│  │ Coverage: 65%      │                 │ Coverage: 0%         │       │
│  │ Status: ⚠️ Partial │                 │ Status: ❌ Spec Only │       │
│  └────────────────────┘                 └──────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# L1 - Process Orchestration (ProcDSL)

## Overview

**Purpose**: Define the data flow "railroad" - structure only, NOT business logic

**Grammar**: `grammar/ProcDSL.g4` (539 lines, v0.4.0)
**Extension**: `.proc`
**Generator**: `backend/generators/flow/flow_generator.py`

## Coverage Summary

| Block | Grammar Features | Implemented | Coverage |
|-------|-----------------|-------------|----------|
| **Execution Block** | 8 | 6 | 75% |
| **Input Block** | 7 | 7 | **100%** |
| **Processing Block** | 7 | 7 | **100%** |
| **Window Block** | 4 | 4 | **100%** |
| **Join Block** | 4 | 4 | **100%** |
| **Correlation Block** | 8 | 8 | **100%** |
| **Output Block** | 4 | 4 | **100%** |
| **Completion Block** | 6 | 6 | **100%** |
| **State Block** | 10 | 10 | **100%** |
| **Resilience Block** | 10 | 10 | **100%** |
| **TOTAL** | **68** | **66** | **97%** |

## Grammar → Generator Mapping

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ProcDSL.g4                        FlowGenerator                         │
│  ───────────                       ─────────────                         │
│                                                                          │
│  executionBlock ─────────────────► _generate_main_method()               │
│    ├─ parallelism                  env.setParallelism()                  │
│    ├─ partition by                 .keyBy()                              │
│    ├─ time by                      WatermarkStrategy                     │
│    ├─ watermark delay              forBoundedOutOfOrderness()            │
│    └─ late data to                 OutputTag + sideOutputLateData()      │
│                                                                          │
│  inputBlock ─────────────────────► SourceGeneratorMixin                  │
│    ├─ receive from                 KafkaSource.builder()                 │
│    ├─ receive alias from           Stream aliasing support               │
│    ├─ schema                       JsonDeserializationSchema<T>          │
│    ├─ project [fields]             Map<String,Object> + direct getters   │
│    ├─ project except [fields]      Reflection-based exclusion            │
│    ├─ store in buffer              _stored_streams tracking              │
│    └─ match from X on [fields]     KeyedStream.connect().process()       │
│                                                                          │
│  processingBlock ────────────────► OperatorGeneratorMixin                │
│    ├─ enrich using                 AsyncDataStream.unorderedWait()       │
│    ├─ transform using              .map(new XFunction())                 │
│    ├─ route using                  .process(new XRouter())               │
│    ├─ aggregate using              .aggregate(new XAggregator())         │
│    └─ merge                        .union()                              │
│                                                                          │
│  windowBlock ────────────────────► WindowGeneratorMixin                  │
│    ├─ tumbling                     TumblingEventTimeWindows.of()         │
│    ├─ sliding                      SlidingEventTimeWindows.of()          │
│    └─ session                      EventTimeSessionWindows.withGap()     │
│                                                                          │
│  correlationBlock ───────────────► OperatorGeneratorMixin._wire_await()  │
│    ├─ await until                  KeyedCoProcessFunction                │
│    └─ hold                         KeyedProcessFunction + ListState      │
│                                                                          │
│  outputBlock ────────────────────► SinkGeneratorMixin                    │
│    └─ emit to                      KafkaSink.builder()                   │
│                                                                          │
│  completionBlock ────────────────► _wire_completion_block()              │
│    ├─ on commit                    CompletionEvent.success()             │
│    └─ on commit failure            CompletionEvent.failure()             │
│                                                                          │
│  stateBlock ─────────────────────► StateGeneratorMixin                   │
│    ├─ local (counter/gauge)        ValueState<Long/Double>               │
│    ├─ local (map/list)             MapState/ListState                    │
│    └─ ttl                          StateTtlConfig                        │
│                                                                          │
│  resilienceBlock ────────────────► ResilienceGeneratorMixin              │
│    ├─ on error                     try-catch + OutputTag DLQ             │
│    └─ checkpoint                   enableCheckpointing()                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Feature Matrix

### Fully Supported Features (100% Coverage)

| Feature | Grammar | Generator | Flink API |
|---------|---------|-----------|-----------|
| `enrich using X on [fields]` | EnrichDecl | `_wire_enrich` | AsyncDataStream |
| `transform using X` | TransformDecl | `_wire_transform` | `.map()` |
| `route using X` | RouteDecl | `_wire_route` | `.process()` + OutputTags |
| `aggregate using X` | AggregateDecl | `_wire_aggregate` | `.aggregate()` |
| `merge X, Y` | MergeDecl | `_wire_merge` | `.union()` |
| `window tumbling D` | WindowDecl | `_wire_window` | TumblingEventTimeWindows |
| `window sliding D every E` | WindowDecl | `_get_window_assigner` | SlidingEventTimeWindows |
| `window session gap D` | WindowDecl | `_get_window_assigner` | EventTimeSessionWindows |
| `await X until Y arrives` | AwaitDecl | `_wire_await` | KeyedCoProcessFunction |
| `hold X [in buffer]` | HoldDecl | `_wire_hold` | KeyedProcessFunction |
| `on commit emit to X` | OnCommitDecl | `_wire_completion_block` | CompletionEvent |
| `late data to X` | LateDataDecl | `_wire_window` | sideOutputLateData |
| `receive alias from X` | ReceiveDecl.alias | `_generate_source` | Stream variable aliasing |
| `project [fields]` | ProjectClause | `_generate_projection` | Map<String,Object> + direct getters |
| `project except [fields]` | ProjectClause | `_generate_projection` | Reflection-based exclusion |
| `store in buffer` | StoreAction | `_generate_store_action` | Buffer tracking for correlation |
| `match from X on [fields]` | MatchAction | `_generate_match_action` | KeyedStream.connect().process() |

### Partially Supported Features

| Feature | Grammar | Gap | Priority |
|---------|---------|-----|----------|
| `partition by` | PartitionDecl | keyBy in source only | P4 |

### Missing Features (Deferred by Design)

| Feature | Grammar | Impact | Priority | Rationale |
|---------|---------|--------|----------|-----------|
| `mode batch/micro_batch` | ModeDecl | Batch processing | P2 | Streaming-first design |

---

# L2 - Schema Registry (SchemaDSL)

## Overview

**Purpose**: Define data structures, types, constraints, and streaming annotations

**Grammar**: `grammar/SchemaDSL.g4` (716 lines, v1.0.0)
**Extension**: `.schema`
**Generator**: `backend/generators/schema_generator.py`

## Coverage Summary

| Block | Grammar Features | Implemented | Coverage |
|-------|-----------------|-------------|----------|
| **Pattern Declaration** | 9 | 5 | 56% |
| **Version Block** | 6 | 2 | 33% |
| **Identity Block** | 3 | 3 | **100%** |
| **Streaming Block** | 18 | 8 | 44% |
| **Fields Block** | 8 | 8 | **100%** |
| **Type System** | 12 | 10 | 83% |
| **Field Qualifiers** | 10 | 8 | 80% |
| **State Machine Block** | 8 | 0 | 0% |
| **Parameters Block** | 4 | 0 | 0% |
| **Entries Block** | 3 | 0 | 0% |
| **Rule Block** | 4 | 0 | 0% |
| **Migration Block** | 2 | 0 | 0% |
| **Type Alias Block** | 3 | 3 | **100%** |
| **PII/Voltage** | 5 | 5 | **100%** |
| **TOTAL** | **95** | **72** | **76%** |

## Grammar → Generator Mapping

```
┌──────────────────────────────────────────────────────────────────────────┐
│  SchemaDSL.g4                      SchemaGenerator                       │
│  ────────────                      ───────────────                       │
│                                                                          │
│  schemaDefinition ───────────────► PojoGeneratorMixin                    │
│    ├─ pattern                      (semantic only, no code gen)          │
│    ├─ version                      (header comment)                      │
│    └─ retention                    (metadata annotation)                 │
│                                                                          │
│  identityBlock ──────────────────► generate_pojo()                       │
│    └─ identityField                Primary key fields in POJO            │
│                                                                          │
│  streamingBlock ─────────────────► generate_pojo()                       │
│    ├─ key_fields                   getCorrelationKey() method            │
│    ├─ time_field                   Timestamp field getter                │
│    ├─ time_semantics               (metadata annotation)                 │
│    └─ watermark_*                  (used by L1, not in POJO)             │
│                                                                          │
│  fieldsBlock ────────────────────► generate_pojo()                       │
│    └─ fieldDecl                    private field + getter/setter         │
│                                                                          │
│  fieldType ──────────────────────► _get_field_java_type()                │
│    ├─ baseType                     String, Integer, BigDecimal, etc.     │
│    ├─ collectionType               List<T>, Set<T>, Map<K,V>             │
│    └─ customType                   Nested POJO reference                 │
│                                                                          │
│  fieldQualifier ─────────────────► generate_pojo()                       │
│    ├─ required/optional            (validation annotations)              │
│    ├─ unique                       (constraint annotation)               │
│    ├─ cannot_change                (immutability marker)                 │
│    ├─ encrypted                    (Voltage integration)                 │
│    └─ pii.profile                  PiiHelperGeneratorMixin               │
│                                                                          │
│  constraint ─────────────────────► (validation code in Builder)          │
│    ├─ range                        BigDecimal range validation           │
│    ├─ length                       String length validation              │
│    ├─ pattern                      Regex validation                      │
│    └─ values                       Enum-like validation                  │
│                                                                          │
│  typeAliasBlock ─────────────────► (type mapping resolution)             │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Feature Matrix

### Fully Supported Features

| Feature | Grammar | Generator | Java Output |
|---------|---------|-----------|-------------|
| `identity` block | identityBlock | generate_pojo | Primary key fields |
| `fields` block | fieldsBlock | generate_pojo | All POJO fields |
| Base types | baseType | _get_field_java_type | String, Integer, BigDecimal, etc. |
| Collection types | collectionType | _get_field_java_type | List<T>, Set<T>, Map<K,V> |
| `pii.profile` | piiModifier | PiiHelperGeneratorMixin | Voltage encryption |
| `key_fields` | keyFieldsDecl | generate_pojo | getCorrelationKey() method |
| Type aliases | typeAliasBlock | Type resolution | Custom type mapping |

### Partially Supported Features

| Feature | Grammar | Gap | Notes |
|---------|---------|-----|-------|
| 9 mutation patterns | patternDecl | Only semantic validation | master_data, event_log, etc. |
| Streaming annotations | streamingBlock | Partial - key_fields, time_field only | Watermark handled by L1 |
| Constraints | constraintSpec | Builder validation only | Runtime validation |
| Version block | versionBlock | Comment only | No migration support |

### Missing Features (Pattern-Specific)

| Feature | Grammar | Impact | Priority |
|---------|---------|--------|----------|
| `state_machine` block | stateMachineBlock | Workflow patterns | P3 |
| `parameters` block | parametersBlock | operational_parameters pattern | P3 |
| `entries` block | entriesBlock | reference_data pattern | P4 |
| `rule` block | ruleBlock | business_logic pattern | P4 |
| `migration` block | migrationBlock | Schema evolution | P2 |

---

# L3 - Transform Catalog (TransformDSL)

## Overview

**Purpose**: Define data transformations (pure functions, field mappings)

**Grammar**: `grammar/TransformDSL.g4` (597 lines, v1.0.0)
**Extension**: `.xform`
**Generator**: `backend/generators/transform/transform_generator.py`

## Coverage Summary

| Block | Grammar Features | Implemented | Coverage |
|-------|-----------------|-------------|----------|
| **Transform Structure** | 6 | 6 | **100%** |
| **Transform Block Structure** | 8 | 5 | 63% |
| **Input/Output Spec** | 4 | 3 | 75% |
| **Apply Block** | 3 | 3 | **100%** |
| **Mappings Block** | 2 | 2 | **100%** |
| **Compose Block** | 5 | 1 | 20% |
| **Validation Blocks** | 8 | 4 | 50% |
| **Expression Language** | 18 | 10 | 56% |
| **Error Handling** | 6 | 4 | 67% |
| **Type System** | 8 | 8 | **100%** |
| **TOTAL** | **62** | **38** | **61%** |

## Grammar → Generator Mapping

```
┌──────────────────────────────────────────────────────────────────────────┐
│  TransformDSL.g4                   TransformGenerator                    │
│  ───────────────                   ──────────────────                    │
│                                                                          │
│  transformDef ───────────────────► _generate_transform()                 │
│    ├─ purityDecl                   (metadata only)                       │
│    ├─ cacheDecl                    CacheGeneratorMixin                   │
│    ├─ inputSpec                    MapFunction<InputType, ...>           │
│    ├─ outputSpec                   MapFunction<..., OutputType>          │
│    ├─ validateInputBlock           ValidationGeneratorMixin              │
│    ├─ applyBlock                   FunctionGeneratorMixin.map() body     │
│    ├─ validateOutputBlock          ValidationGeneratorMixin              │
│    └─ onErrorBlock                 ErrorGeneratorMixin                   │
│                                                                          │
│  transformBlockDef ──────────────► _generate_transform_block()           │
│    ├─ useBlock                     (import resolution)                   │
│    ├─ invariantBlock               ValidationGeneratorMixin              │
│    ├─ mappingsBlock                MappingGeneratorMixin                 │
│    ├─ composeBlock                 ❌ NOT IMPLEMENTED                    │
│    └─ onChangeBlock                ❌ NOT IMPLEMENTED                    │
│                                                                          │
│  applyBlock ─────────────────────► generate_apply_body()                 │
│    ├─ assignment                   result.put("field", value)            │
│    └─ localAssignment              local variable declaration            │
│                                                                          │
│  expression ─────────────────────► ExpressionGeneratorMixin              │
│    ├─ arithmetic (+,-,*,/,%)       Java operators                        │
│    ├─ comparison (==,!=,<,>)       Java operators                        │
│    ├─ logical (and, or, not)       && || !                               │
│    ├─ whenExpression               ternary ?: chains                     │
│    ├─ functionCall                 Method call generation                │
│    ├─ fieldPath                    get() chains for nested fields        │
│    ├─ optionalChainExpression      ❌ NOT IMPLEMENTED (?.)               │
│    └─ indexExpression              ❌ NOT IMPLEMENTED ([n])              │
│                                                                          │
│  mappingsBlock ──────────────────► MappingGeneratorMixin                 │
│    └─ mapping                      result.put() statements               │
│                                                                          │
│  validationRule ─────────────────► ValidationGeneratorMixin              │
│    └─ validationMessage            Validation exception with message     │
│                                                                          │
│  onErrorBlock ───────────────────► ErrorGeneratorMixin                   │
│    ├─ reject                       throw exception                       │
│    ├─ skip                         return null                           │
│    ├─ use_default                  return default value                  │
│    └─ emit_to                      Side output                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Feature Matrix

### Fully Supported Features

| Feature | Grammar | Generator | Java Output |
|---------|---------|-----------|-------------|
| Simple transform | transformDef | _generate_transform | MapFunction class |
| Apply block | applyBlock | generate_apply_body | map() method body |
| Field assignment | assignment | ExpressionGeneratorMixin | result.put() |
| Basic expressions | arithmeticOp, comparisonOp | ExpressionGeneratorMixin | Java operators |
| When-otherwise | whenExpression | ExpressionGeneratorMixin | Ternary chains |
| Function calls | functionCall | ExpressionGeneratorMixin | Method calls |

### Partially Supported Features

| Feature | Grammar | Gap | Notes |
|---------|---------|-----|-------|
| Block transforms | transformBlockDef | Missing input POJO gen | P2 |
| Validation blocks | validateInputBlock | Basic validation only | P2 |
| Error handling | onErrorBlock | Missing emit_to side output | P3 |
| Caching | cacheDecl | TTL only, no key-based | P3 |

### Missing Features

| Feature | Grammar | Impact | Priority |
|---------|---------|--------|----------|
| Transform composition | composeBlock | No sequential/parallel/conditional | P2 |
| Optional chaining | optionalChainExpression | No ?. operator | P2 |
| Index expressions | indexExpression | No array[n] access | P3 |
| On change triggers | onChangeBlock | No recalculation | P4 |
| Null coalescing | ?? operator | Limited null handling | P3 |

---

# L4 - Business Rules (RulesDSL)

## Overview

**Purpose**: Define decision logic (decision tables, procedural rules)

**Grammar**: `grammar/RulesDSL.g4` (622 lines, v1.1.0)
**Extension**: `.rules`
**Generator**: `backend/generators/rules/rules_generator.py`

## Coverage Summary

| Block | Grammar Features | Implemented | Coverage |
|-------|-----------------|-------------|----------|
| **Decision Table Structure** | 6 | 6 | **100%** |
| **Hit Policies** | 3 | 3 | **100%** |
| **Given Block** | 4 | 4 | **100%** |
| **Decide Block (Matrix)** | 6 | 5 | 83% |
| **Condition Types** | 8 | 6 | 75% |
| **Action Types** | 6 | 4 | 67% |
| **Return/Execute Spec** | 4 | 2 | 50% |
| **Procedural Rules** | 7 | 5 | 71% |
| **Boolean Expressions** | 6 | 5 | 83% |
| **Value Expressions** | 4 | 4 | **100%** |
| **TOTAL** | **54** | **35** | **65%** |

## Grammar → Generator Mapping

```
┌──────────────────────────────────────────────────────────────────────────┐
│  RulesDSL.g4                       RulesGenerator                        │
│  ───────────                       ──────────────                        │
│                                                                          │
│  decisionTableDef ───────────────► DecisionTableGeneratorMixin           │
│    ├─ hitPolicyDecl                evaluate() method structure           │
│    │   ├─ first_match              Return on first match                 │
│    │   ├─ single_hit               Validate single match                 │
│    │   └─ multi_hit                Collect all matches                   │
│    ├─ givenBlock                   Input parameter class                 │
│    ├─ decideBlock                  Row matching methods                  │
│    ├─ returnSpec                   Return type/fields                    │
│    └─ executeSpec                  ❌ PARTIAL                            │
│                                                                          │
│  tableMatrix ────────────────────► generate_decision_table_class()       │
│    ├─ tableHeader                  Column names                          │
│    ├─ tableSeparator               (parsing only)                        │
│    ├─ tableRow                     rowNMatches(), getRowNResult()        │
│    └─ priorityCell                 Priority ordering                     │
│                                                                          │
│  condition ──────────────────────► ConditionGeneratorMixin               │
│    ├─ * (wildcard)                 return true                           │
│    ├─ exactMatch                   .equals(value)                        │
│    ├─ rangeCondition               >= lower && <= upper                  │
│    ├─ setCondition (IN)            Arrays.asList().contains()            │
│    ├─ patternCondition             .matches(regex)                       │
│    ├─ nullCondition                == null / != null                     │
│    ├─ comparisonCondition          Comparison operators                  │
│    └─ expressionCondition          ❌ PARTIAL (complex booleans)         │
│                                                                          │
│  action ─────────────────────────► ActionGeneratorMixin                  │
│    ├─ * (no action)                return null                           │
│    ├─ assignAction                 return literal                        │
│    ├─ calculateAction              return expression result              │
│    ├─ lookupAction                 ❌ NOT IMPLEMENTED                    │
│    ├─ callAction                   ❌ PARTIAL                            │
│    └─ emitAction                   ❌ NOT IMPLEMENTED                    │
│                                                                          │
│  proceduralRuleDef ──────────────► ProceduralGeneratorMixin              │
│    ├─ ruleStep (if-then-else)      if/else if/else chains               │
│    ├─ block                        Nested blocks                         │
│    ├─ actionSequence               Action method calls                   │
│    └─ returnStatement              return statement                      │
│                                                                          │
│  booleanExpr ────────────────────► generate_boolean_expression()         │
│    ├─ AND/OR                       && / ||                               │
│    ├─ NOT                          !                                     │
│    └─ comparisonExpr               Comparison operators                  │
│                                                                          │
│  valueExpr ──────────────────────► generate_value_expression()           │
│    ├─ arithmetic                   +, -, *, /, %                         │
│    ├─ fieldPath                    getter chains                         │
│    ├─ functionCall                 Method calls                          │
│    └─ literal                      Java literals                         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Feature Matrix

### Fully Supported Features

| Feature | Grammar | Generator | Java Output |
|---------|---------|-----------|-------------|
| Decision table structure | decisionTableDef | generate_decision_table_class | Table evaluator class |
| Hit policies | hitPolicyDecl | evaluate() | first_match, single_hit, multi_hit |
| Given block | givenBlock | Input class | Input parameter class |
| Wildcard condition | * | generate_condition | return true |
| Exact match | exactMatch | generate_condition | .equals() |
| Range condition | rangeCondition | generate_condition | >= && <= |
| IN condition | setCondition | generate_condition | contains() |
| Procedural if-then-else | ruleStep | generate_procedural_rule | if/else chains |

### Partially Supported Features

| Feature | Grammar | Gap | Notes |
|---------|---------|-----|-------|
| Pattern matching | patternCondition | Basic regex only | P3 |
| Function calls | callAction | Limited actions | P2 |
| Return spec | returnSpec | Single return only | P2 |
| Expression conditions | expressionCondition | Complex nested | P3 |

### Missing Features

| Feature | Grammar | Impact | Priority |
|---------|---------|--------|----------|
| Lookup action | lookupAction | No external lookup | P2 |
| Emit action | emitAction | No side output emit | P2 |
| Execute spec | executeSpec | No action execution | P3 |
| Money/percentage types | MONEY_LITERAL, PERCENTAGE_LITERAL | Type formatting | P3 |
| as_of lookup | AS_OF | Temporal lookups | P4 |

---

# L5 - Infrastructure Binding

## Overview

**Purpose**: Map logical names to physical infrastructure (Kafka topics, MongoDB, Redis, etc.)

**Format**: YAML (`.infra`)
**Generator**: **NOT IMPLEMENTED** - Specification only

## Specification Features

| Category | Features | Status |
|----------|----------|--------|
| **Stream Bindings** | Kafka, Kinesis, Pulsar topics | ❌ Spec Only |
| **Lookup Bindings** | MongoDB, Redis, PostgreSQL | ❌ Spec Only |
| **State Backends** | RocksDB, HashMap | ❌ Spec Only |
| **Checkpoint Storage** | S3, HDFS, GCS | ❌ Spec Only |
| **Resource Allocation** | Parallelism, memory, CPU | ❌ Spec Only |
| **Secret Management** | Vault, AWS Secrets Manager | ❌ Spec Only |
| **Environment Profiles** | dev, staging, prod | ❌ Spec Only |

## Example Specification

```yaml
# production.infra
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}
    serialization: json

  processed_transactions:
    type: kafka
    topic: prod.transactions.processed
    brokers: ${KAFKA_BROKERS}

lookups:
  customers:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers
    cache_ttl: 5m

state:
  backend: rocksdb
  checkpoint:
    type: s3
    path: s3://flink-checkpoints/prod/
    interval: 1m

resources:
  parallelism: 16
  task_slots: 4
  heap_memory: 4g
```

## Required Implementation

1. **YAML Parser** for `.infra` files
2. **Binding resolution** in L1 generator
3. **Environment variable substitution** (${VAR})
4. **Profile selection** (dev/staging/prod)
5. **Secret reference validation**

---

# L6 - Compilation Pipeline

## Overview

**Purpose**: Orchestrate all generators to produce complete, deployable artifacts

**Generator**: **NOT IMPLEMENTED**

## Specification

```
┌─────────────────────────────────────────────────────────────────────────┐
│  L6 Compilation Pipeline                                                 │
│  ───────────────────────                                                 │
│                                                                          │
│  Phase 1: LEXING                                                         │
│    ├─ Parse .proc files (L1)                                            │
│    ├─ Parse .schema files (L2)                                          │
│    ├─ Parse .xform files (L3)                                           │
│    ├─ Parse .rules files (L4)                                           │
│    └─ Parse .infra files (L5)                                           │
│                                                                          │
│  Phase 2: AST BUILDING                                                   │
│    ├─ Build unified cross-layer AST                                     │
│    └─ Validate syntax for each layer                                    │
│                                                                          │
│  Phase 3: SEMANTIC ANALYSIS                                              │
│    ├─ Resolve cross-layer references                                    │
│    │   └─ L1 "transform using X" → L3 definition for X                  │
│    ├─ Type checking across layers                                       │
│    └─ Dependency graph construction                                     │
│                                                                          │
│  Phase 4: IR GENERATION                                                  │
│    ├─ Generate intermediate representation                              │
│    └─ Optimize (dead code, constant folding)                            │
│                                                                          │
│  Phase 5: CODE GENERATION                                                │
│    ├─ L2 → Schema POJOs                                                 │
│    ├─ L3 → Transform MapFunctions                                       │
│    ├─ L4 → Rules ProcessFunctions                                       │
│    ├─ L1 → Job class with all wiring                                    │
│    └─ L5 → Configuration injection                                      │
│                                                                          │
│  Phase 6: ARTIFACT PACKAGING                                             │
│    ├─ Compile Java code                                                 │
│    ├─ Package JAR with dependencies                                     │
│    └─ Generate deployment manifests                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Required for Zero-Code

| Component | Status | Impact |
|-----------|--------|--------|
| Multi-DSL parser | ❌ Partial (individual parsers exist) | Critical |
| Cross-layer reference resolution | ❌ Not implemented | Critical |
| Unified AST | ❌ Not implemented | Critical |
| L5 binding application | ❌ Not implemented | High |
| Deployment artifact generation | ❌ Not implemented | Medium |

---

# Recommendations

## Priority Roadmap

### Phase 1: Production Hardening (COMPLETE ✅)
- [x] L1 Correlation block (await/hold)
- [x] L1 Completion block (on commit)
- [x] L1 Late data handling
- [x] L1 Input Block (stream aliasing, projection, store/match)
- [x] L1 Join types (inner/left/right/outer) ✅ **NEW**
- [x] L1 Fanout strategies (broadcast/round_robin) ✅ **NEW**
- [x] L1 Correlation error handler ✅ **NEW**
- [x] L1 Retry with exponential backoff ✅ **NEW**
- [x] L1 State cleanup strategies (on_access/background) ✅ **NEW**
- [x] L1 Buffer types (FIFO/LIFO/PRIORITY) ✅ **NEW**
- [x] L1 Backpressure alerting with Prometheus ✅ **NEW**

### Phase 1.5: L3/L4 Enhancement (Current Priority)
- [ ] L3 Transform composition (sequential)
- [ ] L4 Lookup actions

### Phase 2: L5 Implementation
- [ ] YAML parser for `.infra` files
- [ ] Binding resolution in L1 generator
- [ ] Environment profiles

### Phase 3: L6 Orchestration
- [ ] Master compiler implementation
- [ ] Cross-layer dependency graph
- [ ] Complete zero-code generation

### Phase 4: Advanced Features
- [ ] L1 Batch/micro-batch mode
- [ ] L2 Schema migration
- [ ] L3 Transform composition (parallel, conditional)
- [ ] L4 Complex expression conditions

## Coverage Improvement Targets

| Layer | Current | Target (Phase 1.5) | Target (Phase 2) |
|-------|---------|-------------------|------------------|
| L1 | **97%** ✅ | 97% (complete) | 97% |
| L2 | 76% | 80% | 85% |
| L3 | 61% | 70% | 80% |
| L4 | 65% | 75% | 85% |
| L5 | 0% | 50% | 80% |
| L6 | 0% | 0% | 60% |

---

# Phase 3 Production Features (December 8, 2024)

## Newly Implemented L1 Features

The following 7 features were implemented to bring L1 from 87% to 97% coverage:

### 1. Join Types (Left/Right/Outer)

| Join Type | Flink Implementation | Use Case |
|-----------|---------------------|----------|
| `inner` | `intervalJoin` | Efficient stream-to-stream matching |
| `left` | `coGroup` with window | Keep all left records, nulls for missing right |
| `right` | `coGroup` with window | Keep all right records, nulls for missing left |
| `outer` | `coGroup` with window | Keep all records from both sides |

**Generated Code Pattern**:
```java
// Left join using coGroup
leftStream.coGroup(rightStream)
    .where(e -> e.getCorrelationKey(leftKeyFields))
    .equalTo(e -> e.getCorrelationKey(rightKeyFields))
    .window(TumblingEventTimeWindows.of(Time.seconds(interval)))
    .apply(new LeftJoinCoGroupFunction())
```

### 2. Fanout Strategies

| Strategy | Flink Method | Effect |
|----------|--------------|--------|
| `broadcast` | `.broadcast()` | Send to all downstream partitions |
| `round_robin` | `.rebalance()` | Load-balanced distribution |

### 3. Correlation Error Handler

Specialized error handling for await/hold correlation failures:
- **timeout**: Await timeout expiration
- **mismatch**: No matching buffer entry found

```java
// Special OutputTag for correlation failures
private static final OutputTag<CorrelationFailure> correlationFailureDlqTag =
    new OutputTag<CorrelationFailure>("dlq") {};
```

### 4. Retry with Exponential Backoff

Actual retry logic instead of comment-only placeholders:

```java
private static final int TRANSFORM_FAILURE_MAX_RETRIES = 3;
private static final long TRANSFORM_FAILURE_RETRY_DELAY_MS = 1000;

// Exponential backoff: delay * (1L << retryCount)
long delay = RETRY_DELAY_MS * (1L << retryCount);
```

### 5. State Cleanup Strategies

| Strategy | Flink Method | Behavior |
|----------|--------------|----------|
| `on_checkpoint` | `.cleanupFullSnapshot()` | Clean during checkpoint (default) |
| `on_access` | `.cleanupIncrementally(10, true)` | Lazy cleanup on state access |
| `background` | `.cleanupInRocksdbCompactFilter(1000)` | Proactive RocksDB compaction |

### 6. Buffer Type Priority

Full support for all buffer retrieval patterns:

| Type | Implementation | Order |
|------|----------------|-------|
| `FIFO` | List iteration | First-in, first-out |
| `LIFO` | `Collections.reverse()` | Last-in, first-out |
| `PRIORITY` | Sort by priority field | Highest priority first |

### 7. Backpressure Alerting

Complete alerting implementation with Flink metrics:

```java
// Backpressure duration tracking
private transient Gauge<Long> backpressureDurationGauge;
private transient Counter backpressureAlertCounter;

// Alert when threshold exceeded
if (backpressureDurationMs > alertThresholdMs) {
    backpressureAlertCounter.inc();
    LOG.warn("Backpressure alert: sustained for > {}s", threshold);
}
```

**Prometheus Integration**:
```yaml
- alert: FlinkBackpressureAlert
  expr: flink_taskmanager_job_task_backpressureDurationMs > 30000
  for: 30s
  labels:
    severity: warning
```

---

# Performance Optimizations in Generated Java Code

## L1 Input Block - Performance Characteristics

The recently implemented Input Block features include several performance optimizations in the generated Java code:

### 1. Field Projection Optimization

| Feature | Strategy | Runtime Impact |
|---------|----------|----------------|
| `project [fields]` | Direct getters + pre-sized HashMap | **O(1)** per field |
| `project except [fields]` | Reflection-based exclusion | **O(n)** where n = total fields |

**Generated code pattern** (project [fields]):
```java
// Pre-sized HashMap - avoids resize operations
Map<String, Object> projected = new HashMap<>(3);  // Known size at compile time
projected.put("field1", event.getField1());         // Direct getter - no reflection
projected.put("field2", event.getField2());
projected.put("field3", event.getField3());
```

**Trade-off**: `project except` uses reflection (slower) vs `project` uses direct getters (faster)

### 2. Key Selector Optimization

| Scenario | Generated Code | Performance |
|----------|---------------|-------------|
| Single key field | `event -> event.getField().toString()` | Minimal overhead |
| Composite key | `event -> getA() + ":" + getB()` | String concat (JVM optimized) |

Key selectors run on **every record** - efficiency is critical for throughput.

### 3. Correlation Key Method (Schema POJOs)

The `getCorrelationKey()` method generated in schema POJOs uses compile-time switch optimization:

```java
public String getCorrelationKey(String[] fields) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < fields.length; i++) {
        if (i > 0) sb.append(":");
        switch (fields[i]) {  // JVM optimizes to jump table
            case "transaction_id": sb.append(getTransactionId()); break;
            case "customer_id": sb.append(getCustomerId()); break;
            // ... direct field access, no reflection
        }
    }
    return sb.toString();
}
```

| Optimization | Benefit |
|--------------|---------|
| Switch statement | JVM optimizes to jump table |
| StringBuilder | Single allocation, no intermediate strings |
| No reflection | Direct field access via getters |

### 4. Flink Operator Naming

```java
.name("project-orders")
.name("match-payments-from-orders_buffer")
```

| Benefit | Impact |
|---------|--------|
| Metrics clarity | Easy identification in Flink UI |
| Debugging | Operator names in stack traces |
| No runtime cost | Metadata only |

## Performance Summary Table

| Feature | Strategy | Complexity | Memory Impact |
|---------|----------|------------|---------------|
| Stream aliasing | Variable naming only | O(1) | None |
| `project [fields]` | Direct getters | O(k) | Reduced footprint |
| `project except` | Reflection | O(n) | Reduced footprint |
| `store in buffer` | ListState tracking | O(1) | State backend |
| `match from buffer` | KeyedStream.connect | O(1) | Hash partitioning |
| `getCorrelationKey()` | Switch + StringBuilder | O(k) | Minimal |

---

*Document generated December 8, 2024*
*Updated: Phase 3 Production Features - L1 at 97% coverage*
*Reference: grammar/*.g4, backend/generators/*_generator.py*
*Nexflow Toolchain v0.4.0*
