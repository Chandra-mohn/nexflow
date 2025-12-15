# Nexflow Code Generation Covenant

> **This document defines inviolable principles for all code generators in the Nexflow toolchain.**
>
> **Every contributor and AI assistant MUST read and follow these principles before modifying any generator.**

---

## The Zero-Code Imperative

### Foundational Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   DEVELOPERS WRITE ONLY DSL FILES.                                         │
│   THE TOOLCHAIN GENERATES 100% PRODUCTION-READY JAVA CODE.                 │
│   NO STUBS. NO TODOS. NO MANUAL IMPLEMENTATION REQUIRED.                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What This Means

1. **Generated code must compile** without modification
2. **Generated code must run** without additional implementation
3. **Generated code must be production-ready** - not scaffolding

---

## The Six-Layer Contract

Each layer has a specific responsibility. Generators MUST respect layer boundaries.

### Layer Responsibilities

| Layer | Responsibility | GENERATES | NEVER GENERATES |
|-------|---------------|-----------|-----------------|
| **L1** | Process Orchestration | Pipeline DAG, operator wiring | Business logic, transformation code |
| **L2** | Schema Registry | POJOs, builders, validators | Processing logic |
| **L3** | Transform Catalog | MapFunction implementations | Routing decisions, rules |
| **L4** | Business Rules | ProcessFunction, decision tables | Data structure definitions |
| **L5** | Infrastructure | Configuration, connection strings | Application code |
| **L6** | Compilation | Orchestrates all, final artifacts | N/A - coordinates others |

### Cross-Layer Reference Rules

```
L1 references L2, L3, L4 by NAME only
    ↓
L6 resolves names to GENERATED code
    ↓
Final output: Complete, wired, executable
```

**Example**:
```proc
# L1 says:
transform using normalize_amount    # Name reference only

# L6 resolves to:
.map(new NormalizeAmountFunction()) # L3-generated class
```

---

## Forbidden Patterns

### ❌ NEVER Generate Stubs

```java
// FORBIDDEN - This violates the covenant
// [STUB] Enrich: customer_lookup
// Requires: CustomerLookupAsyncFunction implementing AsyncFunction
DataStream<Transaction> enriched = inputStream;  // Pass-through stub
```

### ❌ NEVER Generate TODOs for Core Functionality

```java
// FORBIDDEN - This violates the covenant
// TODO: Implement transform logic
public Map<String, Object> map(Transaction value) {
    return null;  // Developer must implement
}
```

### ❌ NEVER Generate Placeholder Returns

```java
// FORBIDDEN - This violates the covenant
private String getRow1Result(Input input) {
    return null;  // Should return actual decision value
}
```

### ❌ NEVER Generate Always-True Conditions

```java
// FORBIDDEN - This violates the covenant
if (true) {  // Should be actual business condition
    applyAction();
}
```

---

## Required Patterns

### ✅ Generate Complete Operator Wiring

```java
// CORRECT - L1 wires to L3-generated function
DataStream<Map<String, Object>> transformed = inputStream
    .map(new NormalizeAmountFunction())  // Complete L3 implementation
    .name("transform-normalize_amount");
```

### ✅ Generate Complete Decision Logic

```java
// CORRECT - L4 returns actual decision values
private String getRow1Result(FraudCheckInput input) {
    return "block";  // Actual value from DSL
}
```

### ✅ Generate Complete Condition Evaluation

```java
// CORRECT - L4 generates actual conditions
if (input.getAmount().compareTo(new BigDecimal("10000")) > 0
    && "high".equals(input.getRiskTier())) {
    return blockTransaction();
}
```

### ✅ Generate Type-Safe Pipeline Flow

```java
// CORRECT - Types flow consistently through pipeline
DataStream<Transaction> source = ...;           // L2 type
DataStream<EnrichedTxn> enriched = ...;         // L2 type
DataStream<Map<String, Object>> transformed = ...; // L3 output type
DataStream<RoutedEvent> routed = ...;           // L4 output type
```

---

## Generator Checklist

Before committing ANY generator change, verify:

### L1 Generator (job_generator.py)
- [ ] All operators wire to generated classes (no stubs)
- [ ] Type flow is consistent source → operators → sink
- [ ] Imports include all referenced L2/L3/L4 classes
- [ ] No `[STUB]` or `[TODO]` comments for core functionality

### L2 Generator (schema/)
- [ ] POJOs compile independently
- [ ] All fields have correct Java types
- [ ] Builders work correctly
- [ ] Serializable implementation is complete

### L3 Generator (transform/)
- [ ] MapFunction compiles and runs
- [ ] Input/output types match L2 schemas
- [ ] All expressions generate executable code
- [ ] No placeholder returns or stub methods

### L4 Generator (rules/)
- [ ] Decision tables return actual values
- [ ] Procedural conditions evaluate correctly
- [ ] ProcessFunction implementation is complete
- [ ] All actions map to executable code

### L5 Parser (when implemented)
- [ ] All logical names resolve to physical resources
- [ ] Environment variables are properly substituted
- [ ] Secret references are valid

### L6 Compiler (when implemented)
- [ ] Cross-layer references all resolve
- [ ] Generated code compiles as a unit
- [ ] No unresolved dependencies
- [ ] Final artifact is deployable

---

## Dependency Resolution Protocol

When a layer references another:

```
1. REFERENCE: L1 says "transform using X"
       ↓
2. RESOLVE: Find L3 definition for X
       ↓
3. GENERATE: L3 generator creates XFunction.java
       ↓
4. WIRE: L1 generator imports and instantiates XFunction
       ↓
5. VALIDATE: Compilation confirms types match
```

### Resolution Failures

If a reference cannot be resolved:

```
❌ DO NOT: Generate a stub
❌ DO NOT: Generate a pass-through
❌ DO NOT: Generate a TODO comment

✅ DO: Fail compilation with clear error message
✅ DO: Report: "L1 references 'transform using X' but no L3 definition found for 'X'"
✅ DO: List required DSL file that must be created
```

---

## The Compilation Contract

### Pre-Conditions
- All DSL files exist and parse successfully
- Cross-layer references are resolvable
- L5 infrastructure bindings are complete

### Post-Conditions
- Generated Java compiles with `mvn compile`
- Generated job runs with `flink run`
- No manual code changes required
- No external dependencies unspecified in L5

### Invariants (Always True)
- Layer boundaries are respected
- Types flow consistently
- All operators have complete implementations
- Business logic lives in L3/L4, never L1

---

## Violation Response

When a generator violates this covenant:

1. **Stop** - Do not proceed with further generation
2. **Report** - Clearly identify the violation
3. **Fix** - Modify the generator, not the generated code
4. **Verify** - Run full compilation test
5. **Document** - Update this covenant if new patterns emerge

---

## Covenant Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2024-12-08 | Initial covenant established |

---

## Signatures

This covenant is binding for all code generation work in the Nexflow toolchain.

```
Established: December 8, 2024
Purpose: Ensure zero-code generation across all layers
Scope: All generators in backend/generators/
Authority: This document overrides convenience shortcuts
```

---

*"The measure of a code generator is not what it can generate, but what it refuses to leave incomplete."*
