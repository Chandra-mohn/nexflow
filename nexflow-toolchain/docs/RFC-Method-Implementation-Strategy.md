# RFC: Method Implementation Strategy for Nexflow DSL

**Status**: Draft
**Created**: December 11, 2024
**Authors**: Design Discussion
**Relates To**: COVENANT-Code-Generation-Principles.md, Nexflow-CMCC-SBVR-Alignment.md

---

## Problem Statement

Generated Java code from Nexflow DSL contains method calls that have no implementations:

```java
// Generated from L4 procedural rules - but these methods don't exist:
if (hasFlag("income_variance_high")) { ... }
var bureauData = getBureauData().getEstimatedIncome();
if (getCombinedFraudScore() > 0.8) { ... }
addRiskFactor("unusual_hour", 15);
```

This violates the **zero developer Java coding** covenant - users must write Java to implement these methods.

---

## Method Categories

### Category 1: Built-in Functions
**Examples**: `hour()`, `dayOfWeek()`, `abs()`, `length()`, `append()`, `min()`, `max()`

**Characteristics**:
- Pure functions with no external dependencies
- Standard operations available in most languages
- Should "just work" without user configuration

**Current Gap**: Generated code assumes these exist but doesn't provide them.

---

### Category 2: Computed Properties
**Examples**: `getCombinedFraudScore()`, `getTotalRiskScore()`, `getRiskCategory()`

**Characteristics**:
- Derived from other fields via calculation
- Belong to a schema/POJO
- Deterministic - same inputs always produce same output

**Current Gap**: No way to declare computed fields in L2 SchemaDSL.

---

### Category 3: State Operations
**Examples**: `hasFlag()`, `addFlag()`, `getDecision()`, `setDecision()`, `getScore()`

**Characteristics**:
- Query or mutate process state
- Accumulated during stream processing
- Scoped to a process instance (keyed state in Flink)

**Current Gap**: L1 state block declares state types but doesn't generate accessor methods.

---

### Category 4: External Service Calls
**Examples**: `getMlFraudScore()`, `getBureauData()`, `lookupOccupationMedian()`

**Characteristics**:
- Call external systems (ML models, databases, APIs)
- May be async, cached, or have fallback values
- Implementation lives outside DSL scope

**Current Gap**: No way to declare service dependencies in DSL.

---

### Category 5: Action Methods
**Examples**: `addRiskFactor()`, `addReviewReason()`, `routeToPremium()`

**Characteristics**:
- Side-effecting operations
- May emit to side outputs, update state, or trigger external calls
- Often domain-specific business actions

**Current Gap**: Generated as stubs with `throw UnsupportedOperationException`.

---

## Proposed Solutions

### Solution 1: L0 Runtime Library (Built-in Functions)

**Approach**: Auto-generate `NexflowRuntime.java` with every build.

**Grammar Impact**: None - purely generator enhancement.

**Generated Output**:
```java
package com.nexflow.runtime;

import java.time.*;
import java.math.BigDecimal;
import java.util.*;

public final class NexflowRuntime {

    // =========================================================================
    // Time Functions
    // =========================================================================

    public static int hour(Instant timestamp) {
        return timestamp.atZone(ZoneOffset.UTC).getHour();
    }

    public static int dayOfWeek(Instant timestamp) {
        return timestamp.atZone(ZoneOffset.UTC).getDayOfWeek().getValue();
    }

    public static Instant now() {
        return Instant.now();
    }

    // =========================================================================
    // Math Functions
    // =========================================================================

    public static BigDecimal abs(BigDecimal value) {
        return value == null ? null : value.abs();
    }

    public static <T extends Comparable<T>> T min(T a, T b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) <= 0 ? a : b;
    }

    public static <T extends Comparable<T>> T max(T a, T b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) >= 0 ? a : b;
    }

    // =========================================================================
    // Collection Functions
    // =========================================================================

    public static int length(Collection<?> collection) {
        return collection == null ? 0 : collection.size();
    }

    public static int length(String str) {
        return str == null ? 0 : str.length();
    }

    public static <T> void append(List<T> list, T item) {
        if (list != null && item != null) {
            list.add(item);
        }
    }

    public static <T> T first(List<T> list) {
        return (list == null || list.isEmpty()) ? null : list.get(0);
    }

    public static <T> T last(List<T> list) {
        return (list == null || list.isEmpty()) ? null : list.get(list.size() - 1);
    }

    // =========================================================================
    // String Functions
    // =========================================================================

    public static String upper(String str) {
        return str == null ? null : str.toUpperCase();
    }

    public static String lower(String str) {
        return str == null ? null : str.toLowerCase();
    }

    public static String trim(String str) {
        return str == null ? null : str.trim();
    }

    public static String concat(String... parts) {
        if (parts == null) return null;
        StringBuilder sb = new StringBuilder();
        for (String part : parts) {
            if (part != null) sb.append(part);
        }
        return sb.toString();
    }
}
```

**Usage in Generated Code**:
```java
import static com.nexflow.runtime.NexflowRuntime.*;

// Before: hour(getTransactionTime())  -- undefined
// After:  hour(getTransactionTime())  -- resolved via static import
if (hour(getTransactionTime()) >= 1 && hour(getTransactionTime()) <= 5) {
    isUnusualTime = true;
}
```

---

### Solution 2: L2 Computed Fields

**Approach**: Add `computed` block to SchemaDSL grammar.

**Grammar Addition**:
```antlr
computedBlock
    : COMPUTED LBRACE computedField+ RBRACE
    ;

computedField
    : fieldName EQUALS expression
    ;
```

**DSL Syntax**:
```
schema FraudAnalysis pattern event_log {
    version 1.0

    fields {
        ml_score: decimal
        rule_score: decimal
        velocity_score: decimal
    }

    computed {
        // Simple weighted average
        combined_fraud_score = (ml_score * 0.4) + (rule_score * 0.3) + (velocity_score * 0.3)

        // Conditional computed field
        risk_category = when combined_fraud_score > 0.8 then "HIGH"
                        when combined_fraud_score > 0.5 then "MEDIUM"
                        else "LOW"

        // Boolean computed field
        requires_review = combined_fraud_score > 0.6 and risk_category != "LOW"
    }
}
```

**Generated Output**:
```java
public class FraudAnalysis implements Serializable {
    private BigDecimal mlScore;
    private BigDecimal ruleScore;
    private BigDecimal velocityScore;

    // Standard getters/setters...

    // =========================================================================
    // Computed Properties (auto-generated from DSL)
    // =========================================================================

    /**
     * Computed: (ml_score * 0.4) + (rule_score * 0.3) + (velocity_score * 0.3)
     */
    public BigDecimal getCombinedFraudScore() {
        if (mlScore == null || ruleScore == null || velocityScore == null) {
            return null;
        }
        return mlScore.multiply(new BigDecimal("0.4"))
            .add(ruleScore.multiply(new BigDecimal("0.3")))
            .add(velocityScore.multiply(new BigDecimal("0.3")));
    }

    /**
     * Computed: risk category based on combined_fraud_score
     */
    public String getRiskCategory() {
        BigDecimal score = getCombinedFraudScore();
        if (score == null) return null;
        if (score.compareTo(new BigDecimal("0.8")) > 0) return "HIGH";
        if (score.compareTo(new BigDecimal("0.5")) > 0) return "MEDIUM";
        return "LOW";
    }

    /**
     * Computed: requires_review flag
     */
    public boolean getRequiresReview() {
        BigDecimal score = getCombinedFraudScore();
        String category = getRiskCategory();
        return score != null
            && score.compareTo(new BigDecimal("0.6")) > 0
            && !"LOW".equals(category);
    }
}
```

---

### Solution 3: L1 State Context Generation

**Approach**: Enhance L1 state block to generate typed ProcessContext class.

**Current Grammar** (already exists):
```
state {
    local counter: counter
    local last_seen: map<string, timestamp>
}
```

**Enhanced Grammar**:
```antlr
stateDecl
    : LOCAL identifier COLON stateType (WITH OPERATIONS LBRACE operationList RBRACE)?
    ;

stateType
    : COUNTER | GAUGE | FLAG_SET | VALUE | MAP | LIST | SET
    ;

operationList
    : identifier (COMMA identifier)*
    ;
```

**DSL Syntax**:
```
process fraud_detection {
    state {
        // Flag set with has/add/remove operations
        local flags: flag_set with operations { has, add, remove, clear }

        // Single value with get/set
        local decision: value<string> with operations { get, set }

        // Map with get/put/contains
        local scores: map<string, decimal> with operations { get, put, contains }

        // Accumulator
        local total_amount: counter with operations { increment, get, reset }
    }
}
```

**Generated Output**:
```java
/**
 * Process context for fraud_detection
 * Auto-generated from L1 state declarations
 */
public class FraudDetectionContext implements Serializable {

    // Flink state handles (initialized in open())
    private transient MapState<String, Boolean> flagsState;
    private transient ValueState<String> decisionState;
    private transient MapState<String, BigDecimal> scoresState;
    private transient ValueState<Long> totalAmountState;

    // =========================================================================
    // Flag Operations
    // =========================================================================

    public boolean hasFlag(String flag) throws Exception {
        Boolean value = flagsState.get(flag);
        return value != null && value;
    }

    public void addFlag(String flag) throws Exception {
        flagsState.put(flag, true);
    }

    public void removeFlag(String flag) throws Exception {
        flagsState.remove(flag);
    }

    public void clearFlags() throws Exception {
        flagsState.clear();
    }

    // =========================================================================
    // Decision Operations
    // =========================================================================

    public String getDecision() throws Exception {
        return decisionState.value();
    }

    public void setDecision(String decision) throws Exception {
        decisionState.update(decision);
    }

    // =========================================================================
    // Scores Operations
    // =========================================================================

    public BigDecimal getScore(String key) throws Exception {
        return scoresState.get(key);
    }

    public void putScore(String key, BigDecimal value) throws Exception {
        scoresState.put(key, value);
    }

    public boolean containsScore(String key) throws Exception {
        return scoresState.contains(key);
    }

    // =========================================================================
    // Counter Operations
    // =========================================================================

    public void incrementTotalAmount(long delta) throws Exception {
        Long current = totalAmountState.value();
        totalAmountState.update((current == null ? 0L : current) + delta);
    }

    public long getTotalAmount() throws Exception {
        Long value = totalAmountState.value();
        return value == null ? 0L : value;
    }

    public void resetTotalAmount() throws Exception {
        totalAmountState.clear();
    }
}
```

---

### Solution 4: L4 Service Declarations

**Approach**: Add `services` block to RulesDSL for external dependency declaration.

**Grammar Addition**:
```antlr
servicesBlock
    : SERVICES LBRACE serviceDecl+ RBRACE
    ;

serviceDecl
    : identifier COLON serviceType serviceName DOT methodName
      LPAREN parameterList RPAREN ARROW returnType
      serviceOptions?
    ;

serviceType
    : SYNC | ASYNC | CACHED LPAREN duration RPAREN
    ;

serviceOptions
    : (TIMEOUT COLON duration)?
      (FALLBACK COLON literal)?
      (RETRY COLON INTEGER)?
    ;
```

**DSL Syntax**:
```
rules fraud_detection {
    services {
        // Async ML service call
        ml_fraud: async MLFraudService.predict(transaction: Transaction) -> decimal
            timeout: 500ms
            fallback: 0.0
            retry: 3

        // Cached database lookup
        bureau: cached(5m) BureauService.lookup(customer_id: string) -> BureauData
            timeout: 1s
            fallback: null

        // Sync reference data lookup
        occupation_median: sync ReferenceDataService.getMedianIncome(occupation: string) -> decimal
            fallback: 50000
    }

    procedural validate_income {
        // Services are now callable
        let bureau_data = call bureau(customer.id)
        let occupation_median = call occupation_median(customer.occupation)

        if bureau_data != null {
            // ... validation logic
        }
    }
}
```

**Generated Output**:
```java
public class FraudDetectionRules {

    // =========================================================================
    // Service Interfaces (user must provide implementations)
    // =========================================================================

    public interface MLFraudService {
        CompletableFuture<BigDecimal> predict(Transaction transaction);
    }

    public interface BureauService {
        BureauData lookup(String customerId);
    }

    public interface ReferenceDataService {
        BigDecimal getMedianIncome(String occupation);
    }

    // =========================================================================
    // Service Wrappers (with timeout, fallback, caching)
    // =========================================================================

    private final MLFraudService mlFraudService;
    private final BureauService bureauService;
    private final ReferenceDataService referenceDataService;

    // Cache for bureau lookups (5 minute TTL)
    private final Cache<String, BureauData> bureauCache =
        Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .build();

    public FraudDetectionRules(
            MLFraudService mlFraudService,
            BureauService bureauService,
            ReferenceDataService referenceDataService) {
        this.mlFraudService = mlFraudService;
        this.bureauService = bureauService;
        this.referenceDataService = referenceDataService;
    }

    /**
     * ML Fraud prediction with async handling, timeout, and fallback
     */
    protected BigDecimal callMlFraud(Transaction transaction) {
        try {
            return mlFraudService.predict(transaction)
                .orTimeout(500, TimeUnit.MILLISECONDS)
                .exceptionally(ex -> {
                    LOG.warn("ML fraud service failed, using fallback", ex);
                    return new BigDecimal("0.0");
                })
                .join();
        } catch (Exception e) {
            return new BigDecimal("0.0"); // fallback
        }
    }

    /**
     * Bureau lookup with caching and fallback
     */
    protected BureauData callBureau(String customerId) {
        return bureauCache.get(customerId, key -> {
            try {
                return bureauService.lookup(key);
            } catch (Exception e) {
                LOG.warn("Bureau service failed for {}", key, e);
                return null; // fallback
            }
        });
    }

    /**
     * Reference data lookup with fallback
     */
    protected BigDecimal callOccupationMedian(String occupation) {
        try {
            BigDecimal result = referenceDataService.getMedianIncome(occupation);
            return result != null ? result : new BigDecimal("50000"); // fallback
        } catch (Exception e) {
            return new BigDecimal("50000"); // fallback
        }
    }
}
```

---

### Solution 5: Action Method Generation

**Approach**: Generate action methods based on usage patterns with clear extension points.

**Current State**: Stubs generated with `throw UnsupportedOperationException`

**Enhanced Approach**: Categorize actions and generate appropriate implementations.

**DSL Syntax** (in L4 rules):
```
rules fraud_detection {
    actions {
        // Emit to side output
        add_risk_factor(name: string, score: integer) -> emit to risk_factors_output

        // Update state
        add_flag(flag: string) -> state flags.add(flag)
        add_review_reason(reason: string) -> state review_reasons.append(reason)

        // Log/audit
        log_decision(decision: string, reason: string) -> audit

        // External call
        notify_fraud_team(transaction_id: string) -> call NotificationService.alert
    }
}
```

**Generated Output**:
```java
// =========================================================================
// Action Methods (generated with implementations where possible)
// =========================================================================

/**
 * Action: add_risk_factor -> emit to risk_factors_output
 */
protected void addRiskFactor(String name, Integer score, Context ctx) {
    RiskFactor factor = new RiskFactor(name, score);
    ctx.output(RISK_FACTORS_OUTPUT_TAG, factor);
}

/**
 * Action: add_flag -> state flags.add
 */
protected void addFlag(String flag) throws Exception {
    context.addFlag(flag);
}

/**
 * Action: add_review_reason -> state review_reasons.append
 */
protected void addReviewReason(String reason) throws Exception {
    context.appendReviewReason(reason);
}

/**
 * Action: log_decision -> audit
 */
protected void logDecision(String decision, String reason) {
    AuditLog.log("DECISION", Map.of(
        "decision", decision,
        "reason", reason,
        "timestamp", Instant.now()
    ));
}

/**
 * Action: notify_fraud_team -> call NotificationService.alert
 * NOTE: Requires NotificationService injection
 */
protected void notifyFraudTeam(String transactionId) {
    notificationService.alert(transactionId);
}
```

---

## Implementation Phases

| Phase | Solution | Complexity | Value | Dependencies |
|-------|----------|------------|-------|--------------|
| **1** | L0 Runtime Library | LOW | HIGH | None |
| **2** | L2 Computed Fields | MEDIUM | HIGH | Grammar change |
| **3** | L1 State Context | MEDIUM | HIGH | Grammar enhancement |
| **4** | L4 Service Declarations | MEDIUM-HIGH | MEDIUM | Grammar addition |
| **5** | Action Method Generation | MEDIUM | MEDIUM | Phases 3, 4 |

---

## Architectural Boundary

### DSL Owns (Zero Java Coding)

- Data structures (POJOs with computed properties)
- Transformations (MapFunction implementations)
- Rules (ProcessFunction with full logic)
- Flow orchestration (Flink job wiring)
- State management (typed context with accessors)
- Service interfaces and wrappers
- Built-in functions (runtime library)

### User Provides (Dependency Injection)

- External service implementations (ML models, APIs)
- Custom business logic beyond DSL expressiveness
- Infrastructure configuration (L5)
- Database connection details

---

## Design Principle: Type Inference

### Core Principle

**L2 Schema is the single source of truth for types. All other layers INFER types.**

This reduces DSL verbosity, eliminates redundant declarations, and makes the DSL feel like business logic rather than programming.

### Type Declaration Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHERE TYPES ARE DECLARED vs INFERRED                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DECLARED (Required):                                                    │
│  ├─ L2 Schema field types         → Source of truth                     │
│  ├─ External service return types → Can't see inside external systems   │
│  └─ New output schema fields      → Creating new structure              │
│                                                                          │
│  INFERRED (No user declaration):                                         │
│  ├─ L4 given block fields         → Look up from schema                 │
│  ├─ Local variables (let)         → Infer from expression               │
│  ├─ Computed fields               → Infer from expression               │
│  ├─ Service call parameters       → Infer from schema field passed      │
│  ├─ Literals                      → Infer from format (123 → integer)   │
│  └─ Expressions                   → Infer from operand types            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Inference Rules

| Pattern | Inference | Example |
|---------|-----------|---------|
| Field path | Schema lookup | `txn.amount` → `decimal` |
| Integer literal | `integer` | `123` → `integer` |
| Decimal literal | `decimal` | `123.45` → `decimal` |
| String literal | `string` | `"hello"` → `string` |
| Boolean literal | `boolean` | `true` → `boolean` |
| List literal | `list<T>` | `[1,2,3]` → `list<integer>` |
| Arithmetic | Widest numeric | `int * decimal` → `decimal` |
| Comparison | `boolean` | `a > b` → `boolean` |
| Runtime function | Known return | `hour(ts)` → `integer` |
| Service call | Declared return | `call bureau(id)` → `BureauData` |

### DSL Syntax Comparison

**Before (verbose):**
```
rules fraud_check {
    given {
        amount: decimal
        category: string
    }

    procedural validate {
        var score: decimal = calculate_risk()
        ...
    }
}
```

**After (inferred):**
```
rules fraud_check {
    given { amount, category }    // Types from Transaction schema

    procedural validate {
        let score = calculate_risk()   // Type inferred
        ...
    }
}
```

### Implementation: Type Resolution Pipeline

```
Phase 1: Schema Registry (L6 Compilation)
├─ Parse all .schema files
├─ Build type map: { "Transaction.amount" → "BigDecimal", ... }
└─ Resolve nested types and schema references

Phase 2: Expression Type Inference
├─ For each L3/L4 expression:
│   ├─ Resolve field paths via schema registry
│   ├─ Apply inference rules for operators
│   └─ Propagate types through AST
└─ Cache inferred types for code generation

Phase 3: Code Generation
├─ Use inferred types for Java declarations
├─ Generate proper type widening where needed
└─ Emit compile-safe, type-correct code
```

### Benefits

1. **Reduced verbosity** - Less DSL code to write and maintain
2. **Eliminates mismatches** - Can't declare wrong type for known field
3. **Modern feel** - Aligns with TypeScript, Kotlin, Swift design
4. **Business focus** - DSL reads like business logic, not programming

---

## Design Principle: Java Records over POJOs

### Core Principle

**Generate Java Records instead of POJOs for all schema types.**

Records align with stream processing philosophy (immutable events), reduce generated code by ~80%, and leverage modern Java features.

### Comparison

| Aspect | POJO | Record |
|--------|------|--------|
| Lines per schema | ~80 | ~15 |
| Mutability | Mutable (setters) | Immutable |
| equals/hashCode | Manual, error-prone | Auto-generated, correct |
| Thread safety | Requires care | Automatic |
| Java version | 8+ | 16+ (17 LTS) |
| Boilerplate | High | Minimal |

### Generated Code Example

**DSL Input:**
```
schema Transaction pattern event_log {
    fields {
        transaction_id: string required
        amount: decimal
        customer_id: string
        timestamp: datetime
    }

    computed {
        amount_in_cents = amount * 100
    }
}
```

**Generated Record:**
```java
public record Transaction(
    String transactionId,
    BigDecimal amount,
    String customerId,
    Instant timestamp
) implements Serializable {

    // Compact constructor for validation
    public Transaction {
        Objects.requireNonNull(transactionId, "transactionId is required");
    }

    // Computed field
    public BigDecimal amountInCents() {
        return amount.multiply(new BigDecimal("100"));
    }

    // With-method for immutable updates
    public Transaction withAmount(BigDecimal newAmount) {
        return new Transaction(transactionId, newAmount, customerId, timestamp);
    }
}
```

### Why Records Align with Stream Processing

| Principle | Record Support |
|-----------|----------------|
| **Event immutability** | Language-enforced, not convention |
| **Functional transforms** | Create new instances naturally |
| **Thread safety** | No synchronization needed |
| **Debugging** | Events don't change mid-flight |
| **Correctness** | Compiler-enforced equality |

### Accessor Method Change

All generated code must use record accessor style:

```java
// POJO style (deprecated)
transaction.getAmount()

// Record style (new standard)
transaction.amount()
```

### Flink Compatibility

| Concern | Status | Notes |
|---------|--------|-------|
| Serialization | ✅ | Kryo works, POJO serializer improving |
| TypeInformation | ✅ | `TypeInformation.of(Record.class)` |
| KeySelector | ✅ | Use `record.field()` |
| State storage | ✅ | Works with ValueState, MapState |
| Jackson/JSON | ✅ | Full support since 2.12 |

### Requirements

- **Java 17+** as minimum version (LTS, widely adopted)
- Update all generators for record accessor pattern
- Generate `withField()` methods for common mutations
- Use compact constructor for `required` field validation

---

## Theoretical Foundation: CMCC & SBVR Alignment

### Overview

Nexflow's design aligns with two established business rules frameworks:

- **SBVR** (Semantics of Business Vocabulary and Business Rules) - OMG standard for human-readable rules
- **CMCC** (Conceptual Model Completeness Conjecture) - Theory that 5 primitives express all business truth

For complete analysis, see: [Nexflow-CMCC-SBVR-Alignment.md](./Nexflow-CMCC-SBVR-Alignment.md)

### The Core Insight

> "No grammar, no parser. Truth lives in structure." — CMCC

CMCC proposes that all computable business truth emerges from 5 primitives:

| Primitive | Meaning | Nexflow Mapping |
|-----------|---------|-----------------|
| **S** (Schema) | Entities & fields | L2 `fields { }` |
| **D** (Data) | Asserted records | L2 `entries { }` |
| **L** (Lookups) | Relationships | L2 `relationships { }` (proposed) |
| **A** (Aggregations) | Totals & counts | L1 aggregate, L4 |
| **F** (Formulas) | Derived facts | L2 `computed { }` (proposed) |

### Nexflow's Sweet Spot

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NEXFLOW ELIMINATES RUNTIME PARSING RISK                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Traditional: Rules parsed at RUNTIME → $180K outage at 2 AM            │
│  Nexflow: Rules compiled to STRUCTURE → Parser runs at BUILD time only  │
│                                                                          │
│  ┌──────────────────────┐   BUILD   ┌──────────────────────┐           │
│  │  DSL (like SBVR)     │   TIME    │  Java (like CMCC)    │           │
│  │  Human-readable      │ ────────► │  Structure IS truth  │           │
│  │  Declarative         │   ONCE    │  No runtime parsing  │           │
│  └──────────────────────┘           └──────────────────────┘           │
│                                                                          │
│  If the generated code compiles, the rule is correctly encoded.         │
│  There's nothing left to mis-parse at 2:14 AM.                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implications for This RFC

The CMCC alignment validates our design decisions:

1. **Computed Fields** = CMCC's Lambda Fields (F primitive)
   - Derived facts that materialize automatically
   - Structure IS the enforcement

2. **Type Inference** = Vocabulary-driven truth
   - Types flow from schema (single source)
   - No redundant declarations

3. **Java Records** = Immutable structure
   - Data is truth, not mutable state
   - Compiler enforces correctness

4. **Relationships Block** = CMCC's Lookups (L primitive)
   - Explicit entity relationships
   - Referential integrity by structure

### Recommended Addition: Relationships Block

To fully implement CMCC's L primitive, add to L2 SchemaDSL:

```
schema Rental {
    fields {
        vehicle_id: uuid required
        customer_id: uuid required
    }

    relationships {
        vehicle: Vehicle via vehicle_id required
        customer: Customer via customer_id required
    }
}
```

This generates navigation methods and enforces referential integrity at the model level.

---

## Open Questions

1. **Computed field dependencies**: Should computed fields be able to reference other computed fields? (creates ordering requirement)

2. **Service interface location**: Should service interfaces be generated per-rule or in a shared location?

3. **State context scope**: Should context be process-scoped or rule-scoped?

4. **Action categorization**: How do we distinguish between state-updating actions vs side-output actions vs external call actions?

5. **Fallback complexity**: Should fallback support expressions or just literals?

6. **Type inference errors**: How should we report when a field path can't be resolved to a schema type?

7. **Relationships vs foreign keys**: Should relationships be inferred from type references (e.g., `vehicle_id: Vehicle.id`) or declared explicitly?

8. **SBVR documentation generation**: Should we auto-generate RuleSpeak sentences from DSL for compliance documentation?

---

## Next Steps

- [ ] Review and refine this RFC
- [ ] Prioritize implementation phases
- [ ] Design grammar changes for L2 computed fields
- [ ] Prototype L0 runtime library generator
- [ ] Define service interface generation patterns

---

*This is a living document. Updates will be tracked with version history.*
