# ProcDSL Advanced Patterns Analysis

## Purpose
This document analyzes advanced syntax patterns found in complex ProcDSL examples, evaluating each pattern's value for end-users writing process orchestration DSL code.

**Evaluation Criteria:**
- **User Value**: How much does this improve expressiveness for business/technical users?
- **Cognitive Load**: How easy is this to learn and remember?
- **Error Proneness**: How likely are users to make mistakes?
- **Ambiguity Risk**: Could this syntax confuse users or conflict with other patterns?

---

## Pattern 1: YAML-Style Indented Blocks

### Current Grammar (Supported)
```procdsl
transform using enrich_application
    lookups: { customer_data: customer_lookup.result, bureau_data: bureau.aggregated }
```

### Proposed Pattern (Not Yet Supported)
```procdsl
transform using enrich_application
    lookups:
        customer_data: customer_lookup.result
        bureau_data: enrichment_results.bureau_aggregated
        compliance_data: compliance_check.result
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Dramatically improves readability for complex configs |
| Cognitive Load | ⭐⭐ | Users must understand whitespace significance |
| Error Proneness | ⭐⭐ | Tab vs space issues, invisible errors |
| Ambiguity Risk | ⭐⭐⭐ | How does indentation end? What terminates the block? |

### Recommendation: **DEFER**

**Advantages:**
- Matches YAML mental model that many users know
- More readable for multi-field configurations
- Reduces visual noise from braces and commas

**Challenges:**
- ANTLR is not designed for whitespace-significant parsing
- Requires custom lexer modes or pre-processing
- "Invisible" bugs from wrong indentation are frustrating to debug
- Copy-paste from different editors can break code
- No clear block terminator makes nesting ambiguous

**Alternative**: Keep brace syntax but allow multi-line formatting:
```procdsl
lookups: {
    customer_data: customer_lookup.result,
    bureau_data: enrichment_results.bureau_aggregated
}
```

---

## Pattern 2: Function Calls in Expressions

### Examples
```procdsl
// Parameter initialization
params:
    calibration_config: lookup(calibration_configs, "production_v3")

// Field computation
set computed_hash = sha256(payload)

// Conditional with function
route when length(items) > 10
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Essential for any non-trivial data manipulation |
| Cognitive Load | ⭐⭐⭐⭐⭐ | Universal programming concept |
| Error Proneness | ⭐⭐⭐⭐ | Familiar syntax, clear error messages possible |
| Ambiguity Risk | ⭐⭐⭐⭐⭐ | Unambiguous - `name(args)` is universally understood |

### Recommendation: **IMPLEMENT** (High Priority)

**Advantages:**
- Absolutely essential for real-world data processing
- Users expect this in any expression-capable language
- Enables: `sha256()`, `now()`, `length()`, `lookup()`, `format()`, etc.
- No learning curve - every programmer knows function call syntax

**Challenges:**
- Need to define which functions are built-in vs user-defined
- Type checking becomes important (compile-time validation)
- Function resolution (where does `lookup` come from?)

**Implementation Complexity**: Low - grammar already has `functionCall`, just needs to be reachable from more expression contexts.

---

## Pattern 3: Duration Arithmetic

### Examples
```procdsl
// Deadline calculation
payload: { deadline: now() + 7 days }

// Timeout computation
schedule reminder after retry_count * 30 seconds

// Comparison with duration
route when age > 30 days
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Time-based logic is central to process orchestration |
| Cognitive Load | ⭐⭐⭐⭐⭐ | Natural language-like: "now + 7 days" |
| Error Proneness | ⭐⭐⭐⭐ | Clear semantics, hard to misuse |
| Ambiguity Risk | ⭐⭐⭐⭐ | Minor: is `7 days` the same as `7 * 1 day`? |

### Recommendation: **IMPLEMENT** (High Priority)

**Advantages:**
- Process orchestration is inherently time-sensitive
- Expresses business logic naturally: "escalate after 48 hours"
- Readable by non-programmers
- Common patterns: SLA calculation, retry delays, expiration times

**Challenges:**
- Type system needs duration-aware arithmetic
- What happens with `timestamp - timestamp`? (yields duration)
- Timezone handling complexity
- Should support: `5 minutes`, `2 hours`, `7 days`, `1 week`?

**Implementation Complexity**: Medium - extend expression grammar to allow duration operands in arithmetic.

---

## Pattern 4: Filter Clause in Receive

### Examples
```procdsl
receive pending_reviews
    from state_store "review_queue"
    filter status == "pending" and time_in_queue > sla_threshold

receive high_value_transactions
    from kafka "transactions"
    filter amount > 10000 or risk_score > 0.8
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Source-level filtering is critical for efficiency |
| Cognitive Load | ⭐⭐⭐⭐⭐ | SQL WHERE clause mental model |
| Error Proneness | ⭐⭐⭐⭐ | Boolean logic is well-understood |
| Ambiguity Risk | ⭐⭐⭐⭐⭐ | Very clear what `filter` means |

### Recommendation: **IMPLEMENT** (High Priority)

**Advantages:**
- Pushdown filtering to source for performance
- Reduces data volume early in pipeline
- Familiar SQL-like semantics
- Critical for high-volume streaming scenarios

**Challenges:**
- Not all sources support arbitrary filters (Kafka vs MongoDB vs Redis)
- Filter expression must be translatable to source query language
- Runtime vs compile-time filter evaluation

**Implementation Complexity**: Low - `filter expression` already exists in grammar, may need parsing context fixes.

---

## Pattern 5: Nested Conditional Logic (if/then/else)

### Examples
```procdsl
if time_in_queue > sla_minutes then
    emit_audit_event "sla_breached"
        payload: { application_id: app.id }
    emit to sla_breach_alerts
        to kafka "sla-breaches"
endif

if risk_score > 0.9 then
    transition to "high_risk_review"
elseif risk_score > 0.7 then
    transition to "standard_review"
else
    transition to "auto_approved"
endif
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐ | Conditional branching is fundamental |
| Cognitive Load | ⭐⭐⭐⭐ | BASIC-style if/then/endif is simple |
| Error Proneness | ⭐⭐⭐ | Nesting can get confusing, forgetting `endif` |
| Ambiguity Risk | ⭐⭐⭐ | Deep nesting reduces readability |

### Recommendation: **IMPLEMENT** (Medium Priority)

**Advantages:**
- Essential for conditional processing paths
- Imperative style familiar to most users
- Enables complex business logic expression

**Challenges:**
- Encourages imperative thinking vs declarative `route using`
- Deep nesting becomes unreadable
- Should we prefer `route when` for simple cases?
- `endif` terminator can be forgotten

**Design Question**: When to use `if/then/endif` vs `route when ... to`?
- **Suggestion**: `if/then` for side-effects (emit_audit, set)
- **Suggestion**: `route when` for flow routing decisions

**Implementation Complexity**: Medium - grammar has `ifStatement`, needs integration with emit/audit blocks.

---

## Pattern 6: Route on Field Path

### Current Grammar
```procdsl
route using simple_approval          // IDENTIFIER only
    approved to approved_flow
```

### Proposed Pattern
```procdsl
route using decision_result.decision  // Field path access
    "approved" to approved_flow
    "declined" to declined_flow
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Essential for routing on computed/nested values |
| Cognitive Load | ⭐⭐⭐⭐⭐ | Dot notation is universal |
| Error Proneness | ⭐⭐⭐⭐ | Clear field access semantics |
| Ambiguity Risk | ⭐⭐⭐⭐⭐ | No ambiguity |

### Recommendation: **IMPLEMENT** (High Priority)

**Advantages:**
- Currently `route using` only takes an identifier (rule name)
- But routing on a field value is extremely common
- `route using result.status` is natural and expected
- Enables: route based on any computed or nested field

**Challenges:**
- Disambiguate: is `result.status` a rule name or field path?
- **Solution**: If contains `.`, it's a field path; otherwise, it's a rule reference

**Implementation Complexity**: Low - change `IDENTIFIER` to `fieldPath` in route rule.

---

## Pattern 7: Object Literal Assignments

### Examples
```procdsl
set approval_details = {
    decision: "approved",
    approved_amount: pricing.final_amount,
    conditions: applied_conditions,
    expires_at: now() + 30 days
}

emit to notifications
    payload: {
        type: "approval",
        recipient: applicant.email,
        data: approval_details
    }
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐⭐⭐ | Constructing structured data is fundamental |
| Cognitive Load | ⭐⭐⭐⭐⭐ | JSON-like syntax is universally known |
| Error Proneness | ⭐⭐⭐⭐ | Matching braces can be tricky |
| Ambiguity Risk | ⭐⭐⭐⭐⭐ | Very clear syntax |

### Recommendation: **IMPLEMENT** (High Priority)

**Advantages:**
- Essential for constructing output payloads
- Enables inline data construction without separate transforms
- JSON familiarity means zero learning curve
- Composable with field references and function calls

**Challenges:**
- Schema validation at compile time
- Nested objects can get complex
- Mixing static and dynamic values

**Implementation Complexity**: Low - `objectLiteral` already exists, needs to be allowed in `set` and `expression` contexts.

---

## Pattern 8: Logging Syntax Consistency

### Current Variations
```procdsl
log_error("Transaction processing failed")   // Function-call style
log_error "Transaction processing failed"    // Keyword style
log_warning "Enrichment timeout"             // Keyword style
```

### Analysis

| Dimension | Rating | Notes |
|-----------|--------|-------|
| User Value | ⭐⭐⭐ | Logging is important but syntax is bikeshedding |
| Cognitive Load | ⭐⭐ | Inconsistency is confusing |
| Error Proneness | ⭐⭐ | Users will mix styles and get errors |
| Ambiguity Risk | ⭐⭐ | Two syntaxes for same thing is bad |

### Recommendation: **STANDARDIZE** (Low Priority)

**Advantages of function-call style `log_error("msg")`:**
- Consistent with other function calls
- Can extend with structured logging: `log_error("msg", { context: value })`
- Familiar programming pattern

**Advantages of keyword style `log_error "msg"`:**
- More DSL-like, less "programming"
- Slightly more readable for simple cases
- Consistent with `emit to`, `route to` patterns

**Recommendation**: Pick ONE. Suggest **keyword style** to match DSL philosophy:
```procdsl
log_error "message"
log_warning "message"
log_info "message"
```

---

## Summary: Priority Matrix

| Pattern | User Value | Implementation | Recommendation |
|---------|-----------|----------------|----------------|
| Function Calls in Expressions | ⭐⭐⭐⭐⭐ | Low | **IMPLEMENT NOW** |
| Duration Arithmetic | ⭐⭐⭐⭐⭐ | Medium | **IMPLEMENT NOW** |
| Filter in Receive | ⭐⭐⭐⭐⭐ | Low | **IMPLEMENT NOW** |
| Route on Field Path | ⭐⭐⭐⭐⭐ | Low | **IMPLEMENT NOW** |
| Object Literal Assignments | ⭐⭐⭐⭐⭐ | Low | **IMPLEMENT NOW** |
| Nested if/then/else | ⭐⭐⭐⭐ | Medium | **IMPLEMENT NEXT** |
| Logging Consistency | ⭐⭐⭐ | Low | **STANDARDIZE** |
| YAML-Style Indentation | ⭐⭐⭐⭐⭐ | High | **DEFER** |

---

## Decision Framework

### Implement If:
1. **High user value** - enables common use cases
2. **Low cognitive load** - familiar patterns
3. **Low ambiguity** - single clear interpretation
4. **Reasonable implementation** - doesn't require architectural changes

### Defer If:
1. **High implementation complexity** - whitespace-sensitive parsing
2. **Alternative exists** - brace syntax works well enough
3. **Marginal value** - nice-to-have vs must-have
4. **High ambiguity risk** - could confuse users

---

## Appendix: User Persona Considerations

### Business Analyst
- Prefers natural language patterns
- Values: readable durations (`7 days`), clear routing (`route when`)
- Struggles with: nested braces, complex expressions

### Technical Architect
- Prefers explicit, precise syntax
- Values: function calls, type safety, clear scoping
- Struggles with: implicit behavior, magic indentation

### Developer (Integration)
- Prefers familiar programming patterns
- Values: JSON-like objects, function syntax, filter expressions
- Struggles with: DSL-specific idioms that differ from host language

**Conclusion**: The recommended patterns (function calls, duration arithmetic, object literals, filter, route on field path) serve all three personas well. YAML-style indentation primarily benefits Business Analysts but creates pain for the other two personas.
