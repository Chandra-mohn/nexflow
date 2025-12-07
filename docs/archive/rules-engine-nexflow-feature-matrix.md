# Rules Engine → Nexflow Feature Matrix

> **Purpose**: Map existing rules_engine DSL features to Nexflow layers
> **Status**: Analysis Document
> **Version**: 0.1.0
> **Last Updated**: 2025-01-XX

---

## 1. Executive Summary

This document analyzes the existing **rules_engine** project (a high-performance rules code generator) and maps its features to the **Nexflow** layered architecture. The rules_engine focuses on **L4 Business Rules** - providing a production-ready DSL for conditional logic, actions, and Java code generation.

### Key Findings

| Category | rules_engine Features | Nexflow Mapping | Reusability |
|----------|----------------------|------------------|-------------|
| Rules DSL Grammar | ANTLR4 grammar, if-then-else, AND/OR/NOT | L4 Business Rules | **High** - Direct import |
| Code Generation | DSL → Java class compilation | L6 Compilation Pipeline | **High** - Reference architecture |
| Action Catalog | 20+ credit card actions | L4 Business Rules | **High** - Domain examples |
| Entity Schemas | JSON attribute definitions | L2 Schema Registry | **Medium** - Schema patterns |
| Function Registry | Math expressions, built-in functions | L3 Transform Catalog | **Medium** - Transform patterns |
| RuleContext | JSON data access patterns | L1 Runtime | **High** - Runtime pattern |
| Test Framework | Rule testing, scenario generation | L6 Compilation | **Medium** - Test infrastructure |

---

## 2. Reusability Summary

### Overall Assessment

```
┌────────────────────────────────────────────────────┐
│  rules_engine → Nexflow Reusability               │
├────────────────────────────────────────────────────┤
│                                                    │
│  Direct Import:     ~55%  ██████████████░░░░░░    │
│  Adapt/Reference:   ~30%  ████████░░░░░░░░░░░░    │
│  Not Applicable:    ~15%  ████░░░░░░░░░░░░░░░░    │
│                                                    │
│  TOTAL LEVERAGEABLE: ~85%                         │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Quantitative Breakdown

| Category | rules_engine Content | Reusability | Estimate |
|----------|---------------------|-------------|----------|
| **Rules DSL Grammar** | ANTLR4 parser, conditions, actions | ✅ Direct import | **95%** |
| **Code Generation** | DSL → Java, visitor patterns | ✅ Reference | **90%** |
| **Action Catalog** | 20 credit card actions | ✅ Domain examples | **100%** |
| **RuleContext Pattern** | JSON data access, reference passing | ✅ Direct import | **95%** |
| **Entity Schemas** | JSON attribute definitions | ⚠️ Adapt to L2 | **70%** |
| **Function Registry** | Math parser, built-in functions | ⚠️ Adapt to L3 | **60%** |
| **VS Code Extension** | Syntax highlighting, validation | ⚠️ Dev tooling | **50%** |
| **React UI** | Rules authoring interface | ❌ Not applicable | **0%** |

### Leverage Categories

| Leverage Level | Percentage | Components |
|----------------|------------|------------|
| **Direct Import** | ~55% | Rules DSL grammar, action patterns, RuleContext, code gen patterns |
| **Adapt/Reference** | ~30% | Entity schemas, function registry, test framework |
| **Not Applicable** | ~15% | React UI, Flask backend, stateless execution model |

### Value Assessment

The **~85% leverageable** content represents significant value:

1. **Rules DSL Grammar** (~40% of substance)
   - Production-tested ANTLR4 grammar
   - Complex boolean logic (AND/OR/parentheses)
   - Multi-step rules with if-then-elseif-else-endif
   - Nested attribute access (`applicant.creditScore`)
   - Maps perfectly to L4 Business Rules conditions

2. **Code Generation Pipeline**
   - Template-based Java code generation
   - AST visitor pattern implementation
   - Performance-optimized output (sub-millisecond execution)
   - Reference architecture for L6 Compilation Pipeline

3. **Action Catalog** (20 actions)
   - Credit card domain actions (approve, reject, flag, etc.)
   - Action registry pattern
   - Parameter validation patterns

The **~15% not applicable** is UI/authoring focused (React frontend, Flask CRUD API), which is out of scope for Nexflow.

---

## 3. Detailed Feature Matrix

### 3.1 Rules DSL Grammar

rules_engine has a production-tested ANTLR4 grammar for business rules.

| Feature | rules_engine Capability | Nexflow Layer | Reusability | Notes |
|---------|------------------------|----------------|-------------|-------|
| If-Then-Else | `if condition then action else action endif` | L4 Rules | ✅ **Direct** | Core conditional logic |
| Multi-Step Rules | Sequential condition evaluation | L4 Rules | ✅ **Direct** | `rule: step+` pattern |
| AND Logic | `condition and condition` | L4 Rules | ✅ **Direct** | Boolean conjunction |
| OR Logic | `condition or condition` | L4 Rules | ✅ **Direct** | Boolean disjunction |
| Parentheses | `(A and B) or (C and D)` | L4 Rules | ✅ **Direct** | Operator precedence |
| Comparison Operators | `=`, `!=`, `<`, `>`, `<=`, `>=` | L4 Rules | ✅ **Direct** | Standard comparisons |
| String Operators | `contains`, `starts_with`, `in` | L4 Rules | ✅ **Direct** | Text matching |
| Nested Attributes | `applicant.employment.status` | L4 Rules | ✅ **Direct** | Deep field access |
| Comments | `# comment` and `// comment` | L4 Rules | ✅ **Direct** | Documentation |

**Grammar Example**:
```
rule creditCardApplication:
    if applicant.creditScore >= 750 and applicant.annualIncome > 60000 then instantApproval
    if applicant.creditScore >= 650 and applicant.employmentYears >= 2 then standardApproval
    if applicant.age < 18 or applicant.creditScore < 500 then rejectApplication
```

**Recommendation**: Import rules grammar patterns into L4-Business-Rules.md. This complements ccdsl's decision tables with procedural rule logic.

### 3.2 Code Generation Pipeline

rules_engine has a complete DSL → Java compilation pipeline.

| Feature | rules_engine Capability | Nexflow Layer | Reusability | Notes |
|---------|------------------------|----------------|-------------|-------|
| ANTLR Parse Tree | `RulesParser`, `RulesLexer` | L6 Compiler | ✅ **Reference** | Parser infrastructure |
| AST Visitor | `RuleDataExtractor` (listener pattern) | L6 Compiler | ✅ **Reference** | Tree walking |
| Template Code Gen | Python f-string templates | L6 Compiler | ⚠️ **Adapt** | Different target (Flink) |
| Java Class Output | `DirectJavaCodeGenerator` | L6 Compiler | ✅ **Reference** | Code gen patterns |
| Type-Safe Values | `compareValues` BiFunction | L6 Compiler | ✅ **Direct** | Runtime type handling |
| Hot ClassLoader | In-memory compilation (planned) | L6 Compiler | ⚠️ **Reference** | Dynamic loading |

**Generated Code Pattern**:
```java
public class CreditCheckRule implements Rule {
    @Override
    public RuleResult execute(RuleContext ctx) {
        if (compareValues.apply(ctx.getValue("applicant.creditScore"), 750) >= 0) {
            return RuleResult.action("instantApproval");
        }
        return RuleResult.noMatch();
    }
}
```

**Recommendation**: Use as reference architecture for L6 UDF generation. The visitor pattern and template approach align with Nexflow's compilation pipeline.

### 3.3 Action Catalog

rules_engine defines 20 credit card domain actions.

| Action Category | Actions | Nexflow Layer | Reusability | Notes |
|----------------|---------|----------------|-------------|-------|
| **Application Processing** | `rejectApplication`, `approveApplication`, `instantApproval`, `conditionalApproval`, `manualReview`, `requireManualReview` | L4 Rules | ✅ **Direct** | 6 actions |
| **Transaction Authorization** | `approveTransaction`, `blockTransaction`, `decline`, `temporaryBlock` | L4 Rules | ✅ **Direct** | 4 actions |
| **Risk Management** | `flagForReview`, `requireVerification`, `requirePhoneVerification`, `requireStepUpAuth`, `requireAdditionalAuth` | L4 Rules | ✅ **Direct** | 5 actions |
| **Communication** | `sendAlert`, `sendSMSVerification`, `sendRealTimeAlert` | L4 Rules | ✅ **Direct** | 3 actions |
| **Account Management** | `increaseCreditLimit`, `decreaseCreditLimit` | L4 Rules | ✅ **Direct** | 2 actions |

**Action Interface Pattern**:
```java
public interface Action {
    void execute(RuleContext context);
}

public class ActionRegistry {
    private Map<String, Action> actions = new HashMap<>();
    public void executeAction(String name, RuleContext context) { ... }
}
```

**Recommendation**: Import action catalog as L4 examples. The action registry pattern is useful for Nexflow's routing and emit semantics.

### 3.4 RuleContext Pattern

rules_engine has a production-tested data access pattern.

| Feature | rules_engine Capability | Nexflow Layer | Reusability | Notes |
|---------|------------------------|----------------|-------------|-------|
| JSON Data Access | `context.getValue("path.to.field")` | L1 Runtime | ✅ **Direct** | Dot notation paths |
| Reference Passing | Single object, no copying | L1 Runtime | ✅ **Direct** | Memory efficiency |
| Type Safety | Typed getters, null handling | L1 Runtime | ✅ **Direct** | Runtime safety |
| Path Resolution | Nested paths, array access | L1 Runtime | ✅ **Direct** | Deep field access |
| Thread Safety | Immutable reads, concurrent access | L1 Runtime | ✅ **Direct** | Streaming-safe |

**Context Pattern**:
```java
public class RuleContext {
    private JsonNode data;  // Single instance, reference passing

    public Object getValue(String path) { ... }  // "customer.creditScore"
    public JsonNode getData() { return data; }   // Full JSON access
}
```

**Recommendation**: Adopt RuleContext pattern for L1 runtime. This maps to Nexflow's enrichment lookups and transform inputs.

### 3.5 Entity Schemas

rules_engine defines entity schemas in JSON format.

| Feature | rules_engine Capability | Nexflow Layer | Reusability | Notes |
|---------|------------------------|----------------|-------------|-------|
| Entity Definitions | JSON schema files | L2 Schema | ⚠️ **Adapt** | Different format than ccdsl |
| Attribute Types | `string`, `number`, `datetime`, `boolean` | L2 Schema | ✅ **Direct** | Standard types |
| Required Fields | `required: true/false` | L2 Schema | ✅ **Direct** | Validation |
| Default Values | `default: value` | L2 Schema | ✅ **Direct** | Defaults |
| Schema Versioning | `schema_version: v2` | L2 Schema | ✅ **Direct** | Evolution support |

**Schema Example**:
```json
{
  "entity_name": "transaction",
  "schema_version": "v2",
  "attributes": [
    {"name": "amount", "type": "number", "required": true},
    {"name": "merchantCategory", "type": "string", "required": false}
  ]
}
```

**Recommendation**: Use as validation examples for L2 schema definitions. Align with ccdsl's entity format for consistency.

### 3.6 Function Registry

rules_engine has built-in functions for calculations.

| Feature | rules_engine Capability | Nexflow Layer | Reusability | Notes |
|---------|------------------------|----------------|-------------|-------|
| Math Expressions | `applicant.income * 0.3` | L3 Transform | ⚠️ **Adapt** | Calculation patterns |
| Expression Parser | Shunting Yard algorithm | L3 Transform | ⚠️ **Reference** | Math parsing |
| Function Validation | Parameter count, type checking | L3 Transform | ✅ **Direct** | Validation logic |
| Java Code Generation | Expression → Java calculation | L6 Compiler | ✅ **Reference** | Code gen patterns |

**Expression Example**:
```
# Rules DSL
if applicant.totalDebt > applicant.annualIncome * 0.4 then requireManualReview

# Generated Java
if (((Number)ctx.getValue("applicant.totalDebt")).doubleValue() >
    ((Number)ctx.getValue("applicant.annualIncome")).doubleValue() * 0.4) { ... }
```

**Recommendation**: Reference for L3 transform calculations. Consider function registry pattern for L3 Transform Catalog.

---

## 4. Integration Recommendations

### 4.1 Immediate Imports (High Reusability)

These components can be imported directly into Nexflow:

| Component | Source | Target | Action |
|-----------|--------|--------|--------|
| Rules Grammar Patterns | `COMPLEX_RULES_SAMPLES.md` | L4-Business-Rules.md | Import if-then-else patterns |
| Action Catalog | `ACTIONS_CATALOG.md` | L4-Business-Rules.md | Import as domain examples |
| RuleContext Pattern | `DATA_STRUCTURE.md` | L1-Runtime-Semantics.md | Adopt data access pattern |
| Code Gen Architecture | `CURRENT_STATE_SUMMARY.md` | L6-Compilation-Pipeline.md | Reference for UDF generation |

### 4.2 Adaptations Required (Medium Reusability)

| Component | Adaptation Needed | Target Layer |
|-----------|-------------------|--------------|
| Entity Schemas | Align with ccdsl entity format | L2 Schema Registry |
| Function Registry | Map to L3 transform signatures | L3 Transform Catalog |
| Test Framework | Adapt for streaming scenarios | L6 Compilation |
| Expression Parser | Integrate with Flink SQL generation | L6 Compilation |

### 4.3 Not Applicable (Low Reusability)

| Component | Reason | Notes |
|-----------|--------|-------|
| React UI | Out of scope | Rules authoring frontend |
| Flask Backend | Different architecture | CRUD API, not streaming |
| Stateless Execution | Nexflow is stateful/streaming | Different execution model |
| VS Code Extension | Dev tooling, not DSL | Could revisit later |

---

## 5. Complementary Relationship: ccdsl + rules_engine

The two existing DSL projects complement each other for L4 Business Rules:

| Aspect | ccdsl | rules_engine | Combined Value |
|--------|-------|--------------|----------------|
| **Rule Style** | Decision tables (matrix) | Procedural (if-then-else) | Both paradigms |
| **Condition Types** | Declarative conditions | Boolean expressions | Complete condition coverage |
| **Action Types** | assign, calculate, lookup, call, emit | Domain-specific actions | Rich action vocabulary |
| **Code Generation** | Multi-target (Java, SQL, Python) | Java-focused, optimized | Production patterns |
| **Exhaustiveness** | Gap/overlap detection | Sequential fallthrough | Different validation |
| **Domain Examples** | Entity definitions, mutation patterns | Action catalog, schemas | Comprehensive examples |

### Unified L4 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    L4: Business Rules Layer                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    │
│  │   Decision Tables       │    │   Procedural Rules      │    │
│  │   (from ccdsl)          │    │   (from rules_engine)   │    │
│  │                         │    │                         │    │
│  │ • Matrix-based logic    │    │ • If-then-else logic    │    │
│  │ • Exhaustiveness check  │    │ • AND/OR/parentheses    │    │
│  │ • Hit policies          │    │ • Multi-step rules      │    │
│  │ • Condition types       │    │ • Nested attributes     │    │
│  │ • Action types          │    │ • Action registry       │    │
│  └─────────────────────────┘    └─────────────────────────┘    │
│                    │                         │                  │
│                    └────────────┬────────────┘                  │
│                                 ▼                               │
│                    ┌─────────────────────────┐                  │
│                    │   Unified L4 Compiler   │                  │
│                    │                         │                  │
│                    │ • Decision table → UDF  │                  │
│                    │ • Procedural rule → UDF │                  │
│                    │ • Action execution      │                  │
│                    └─────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Gap Analysis

### 6.1 Features in rules_engine NOT in Nexflow

| Feature | rules_engine Has | Nexflow Status | Recommendation |
|---------|------------------|-----------------|----------------|
| VS Code Extension | ✅ Syntax highlighting | ❌ Not defined | Consider for dev tooling |
| React Rules Editor | ✅ Visual authoring | ❌ Not applicable | Out of scope |
| Hot Class Loading | ✅ Planned | ⚠️ Reference for L6 | Consider for runtime |
| Performance Metrics | ✅ Sub-ms execution | ⚠️ Reference | Align with L1 runtime targets |

### 6.2 Features in Nexflow NOT in rules_engine

| Feature | Nexflow Has | rules_engine Status | Notes |
|---------|--------------|---------------------|-------|
| Streaming Orchestration | ✅ | ❌ | rules_engine is stateless |
| Event-Time Processing | ✅ | ❌ | No time semantics |
| Correlation Patterns | ✅ | ❌ | No await/hold |
| Checkpointing | ✅ | ❌ | No state persistence |
| Window Operations | ✅ | ❌ | No windowing |
| Decision Tables | ⚠️ (via ccdsl) | ❌ | Different rule paradigm |

---

## 7. Layer-by-Layer Import Plan

### 7.1 L1 Runtime Semantics

**Import from rules_engine**:
```yaml
rule_context_pattern:
  source: DATA_STRUCTURE.md
  action: Adopt JSON data access pattern for enrichment/transform inputs

reference_passing:
  source: DATA_STRUCTURE.md § "Memory Management"
  action: Apply same efficiency pattern for streaming context
```

### 7.2 L2 Schema Registry

**Import from rules_engine**:
```yaml
entity_schema_format:
  source: rules-dsl/rules/schemas/*.json
  action: Align with ccdsl entity format, use as validation examples
```

### 7.3 L3 Transform Catalog

**Reference from rules_engine**:
```yaml
expression_parser:
  source: function_registry.py § MathExpressionParser
  action: Reference for calculation transforms

function_validation:
  source: function_registry.py § FunctionSignature
  action: Adopt validation pattern for transform signatures
```

### 7.4 L4 Business Rules

**Import from rules_engine**:
```yaml
procedural_rules:
  source: COMPLEX_RULES_SAMPLES.md + SAMPLE_RULES.md
  action: Import if-then-else patterns as alternative to decision tables

action_catalog:
  source: ACTIONS_CATALOG.md
  action: Import 20 credit card actions as domain examples

boolean_logic:
  source: Grammar patterns
  action: Document AND/OR/parentheses support
```

### 7.5 L6 Compilation Pipeline

**Reference from rules_engine**:
```yaml
code_generation:
  source: template_code_generator.py + DirectJavaCodeGenerator.java
  action: Reference architecture for UDF generation

visitor_pattern:
  source: RuleDataExtractor class
  action: Apply AST visitor pattern for L4 rule compilation
```

---

## 8. Combined Reusability: ccdsl + rules_engine

### Total Assets Available

| Asset Type | ccdsl | rules_engine | Combined |
|------------|-------|--------------|----------|
| Data Patterns | 9 mutation patterns | - | 9 |
| Entity Definitions | 4 entities | 4 schemas | 8 examples |
| Decision Tables | Complete spec | - | 1 spec |
| Procedural Rules | - | Complete grammar | 1 grammar |
| Actions | 5 action types | 20 domain actions | Complete system |
| Code Generation | Multi-target | Java-optimized | Comprehensive |
| Type System | Full type system | Basic types | Full coverage |

### Overall Import Value

```
┌────────────────────────────────────────────────────────────────┐
│  Combined Reusability: ccdsl + rules_engine                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  L2 Schema Registry:    ~80% from ccdsl + rules_engine        │
│  L3 Transform Catalog:  ~50% reference from both              │
│  L4 Business Rules:     ~90% from both (complementary)        │
│  L6 Compilation:        ~70% reference from both              │
│                                                                │
│  OVERALL Nexflow ACCELERATION: ~75%                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-01-XX | - | Initial feature matrix |
