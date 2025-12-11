# L1 & L3 Generator Implementation Plan

## Current Status

### What Works
- **L2 Schema Generator**: Complete - generates POJOs, Builders, PII helpers, Migration helpers, State machines
- **L4 Rules Generator**: Complete - generates Decision tables, Rule outputs, Procedural rules
- **Build Pipeline**: Complete - parse → validate → generate → verify (Maven)
- **pom.xml Generation**: Complete

### What Needs Work
- **L1 Flow Generator**: Partially implemented but has AST mismatches
- **L3 Transform Generator**: Partially implemented but needs verification

## Problem Analysis

### AST Structure Mismatch (v0.5.0+ Grammar)

The grammar was updated to v0.5.0+ but generators weren't synchronized:

**Expected by Generators:**
```python
process.input.receives  # expects InputBlock container
process.output.emits    # expects OutputBlock container
```

**Actual AST (v0.5.0+):**
```python
process.receives  # List[ReceiveDecl] directly
process.emits     # List[EmitDecl] directly
```

The backward compatibility properties return single items, not containers:
```python
process.input   # returns ReceiveDecl (first receive), NOT InputBlock
process.output  # returns EmitDecl (first emit), NOT OutputBlock
```

---

## Implementation Plan

### Phase 1: Fix AST/Generator Alignment (Priority: HIGH)

**Option A: Update Generators to Use New AST Structure** (Recommended)
- Modify all `process.input.receives` → `process.receives`
- Modify all `process.output.emits` → `process.emits`
- Update similar patterns throughout flow generator mixins
- Estimated: ~50 changes across 10 files

**Option B: Add Compatibility Wrappers in AST**
- Create InputBlock/OutputBlock wrapper classes
- Return wrappers from `process.input`/`process.output`
- More complex, maintains two mental models

**Files to Update (Option A):**
```
backend/generators/flow/
├── job_imports.py         # process.input.receives → process.receives
├── job_generator.py       # process.input.receives → process.receives
├── source_generator.py    # process.input.receives → process.receives
├── flow_generator.py      # process.input.receives → process.receives
├── job_sinks.py          # process.input.receives → process.receives
├── job_operators.py      # check for similar patterns
├── job_correlation.py    # check for similar patterns
└── state_generator.py    # check for similar patterns
```

### Phase 2: Complete L1 Flow Generator

**What L1 Should Generate:**

1. **FlinkJob Main Class** (`{ProcessName}Job.java`)
   - Main entry point with `main()` method
   - StreamExecutionEnvironment setup
   - Checkpointing configuration
   - Source → Operators → Sink pipeline assembly

2. **Source Functions** (`{ProcessName}Source.java`)
   - Kafka source configuration from `receive` blocks
   - Schema registry integration
   - Deserialization setup

3. **Process Functions** (`{ProcessName}ProcessFunction.java`)
   - KeyedProcessFunction for stateful processing
   - State management from `state` block
   - Timer handling for `hold`/`await` patterns

4. **Sink Functions** (`{ProcessName}Sink.java`)
   - Kafka sink configuration from `emit` blocks
   - Serialization setup
   - Exactly-once delivery setup

5. **Operator Chain Assembly**
   - `transform using X` → call transform function
   - `enrich using Y` → async enrichment operator
   - `route using Z` → split/select operators
   - `window tumbling 5m` → window operator
   - `join with X on ...` → join operator

**DSL to Flink Mapping:**
```
receive from source_x        → KafkaSource<T>
  schema card_transaction    → CardTransaction.class

transform using validate     → .process(ValidateFunction)

enrich using bureau_lookup   → AsyncDataStream.unorderedWait(...)

route using simple_approval  → .getSideOutput(approved), .getSideOutput(declined)

emit to approved_sink        → KafkaSink<T>
```

### Phase 3: Complete L3 Transform Generator

**What L3 Should Generate:**

1. **Transform Function Class** (`{TransformName}Function.java`)
   - Implements Flink's MapFunction or ProcessFunction
   - Field mapping logic from DSL
   - Type conversion handling

2. **Transform Processor** (`{TransformName}Processor.java`)
   - Batch processing variant
   - Used for non-streaming contexts

**DSL to Java Mapping:**
```dsl
transform validate_basic {
    input: card_transaction
    output: validated_transaction

    map {
        transaction_id -> transaction_id
        validated = true
        validation_timestamp = now()
    }
}
```

Generates:
```java
public class ValidateBasicFunction
    implements MapFunction<CardTransaction, ValidatedTransaction> {

    @Override
    public ValidatedTransaction map(CardTransaction input) {
        return ValidatedTransaction.builder()
            .transactionId(input.getTransactionId())
            .validated(true)
            .validationTimestamp(Instant.now())
            .build();
    }
}
```

### Phase 4: Integration & Testing

1. **End-to-End Test**
   - Build simple example → verify all Java files generated
   - Run Maven compile → verify compilation success
   - Unit tests for generated code

2. **Complex Example Test**
   - Multi-process flow
   - Joins, windows, state management
   - Error handling patterns

---

## Effort Estimation

| Phase | Description | Files | Estimated Effort |
|-------|-------------|-------|------------------|
| 1 | Fix AST/Generator Alignment | 10 | 2-4 hours |
| 2 | Complete L1 Flow Generator | 15 | 8-16 hours |
| 3 | Complete L3 Transform Generator | 8 | 4-8 hours |
| 4 | Integration Testing | 5 | 4-8 hours |
| **Total** | | ~38 | **18-36 hours** |

---

## Priority Order

1. **Phase 1** - Fix AST alignment (blocks all other work)
2. **Phase 2** - L1 Flow Generator (highest value - generates most code)
3. **Phase 3** - L3 Transform Generator
4. **Phase 4** - Integration testing

---

## Quick Win: Phase 1 Implementation

To unblock L1 generation immediately, update these patterns:

```python
# OLD (broken)
if process.input and process.input.receives:
    for receive in process.input.receives:

# NEW (fixed)
if process.receives:
    for receive in process.receives:
```

This single pattern fix across ~10 files will unblock L1 generation.
