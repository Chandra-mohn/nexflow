# L6: Compiler Error Catalog

> **Layer**: L6 - Compilation Pipeline
> **Status**: Specification
> **Version**: 1.0.0
> **Last Updated**: 2025-11-30

---

## 1. Overview

This document catalogs all error messages produced by the Nexflow compiler. Each error includes:

- **Error Code**: Unique identifier (e.g., `E001`)
- **Phase**: Compilation phase where error occurs
- **Message**: Error description
- **Help**: Suggested fixes
- **Example**: Code that triggers the error

---

## 2. Error Code Ranges

| Range | Phase | Description |
|-------|-------|-------------|
| E001-E099 | Lexer | Tokenization errors |
| E100-E199 | Parser | Syntax errors |
| E200-E299 | AST | Tree construction errors |
| E300-E399 | Semantic | Reference and type errors |
| E400-E499 | L2 Schema | Schema validation errors |
| E500-E599 | L3 Transform | Transform validation errors |
| E600-E699 | L4 Rules | Rule validation errors |
| E700-E799 | L5 Binding | Infrastructure binding errors |
| E800-E899 | IR | Graph construction errors |
| E900-E999 | CodeGen | Code generation errors |
| W001-W999 | Warnings | Non-fatal issues |

---

## 3. Lexer Errors (E001-E099)

### E001: Invalid Character

**Message**: `Unexpected character '{char}'`

**Help**: Check for unsupported Unicode characters or copy-paste artifacts.

**Example**:
```
process auth_enrichment
  parallelism 128®        // ← Invalid character
end
```

**Output**:
```
auth_enrichment.proc:2:17: error[E001]: Unexpected character '®'
   |
 2 |   parallelism 128®
   |                  ^
   |
   = help: Remove or replace the invalid character
```

---

### E002: Unterminated String

**Message**: `Unterminated string literal`

**Help**: Add the closing quote character.

**Example**:
```
schema auth_event_v1
  description "Authorization event
end
```

**Output**:
```
auth_enrichment.proc:2:15: error[E002]: Unterminated string literal
   |
 2 |   description "Authorization event
   |               ^
   |
   = help: Add a closing quote '"' before the end of line
```

---

### E003: Invalid Number

**Message**: `Invalid numeric literal '{value}'`

**Help**: Check number format (integers, decimals, durations).

**Example**:
```
process auth_enrichment
  parallelism 12.8       // ← Must be integer
end
```

---

### E004: Invalid Duration

**Message**: `Invalid duration format '{value}'`

**Help**: Use format like `30s`, `5m`, `1h`, `7d`.

**Example**:
```
process auth_enrichment
  checkpoint every 5 mins    // ← Should be '5m'
end
```

---

### E005: Reserved Word

**Message**: `'{word}' is a reserved keyword and cannot be used as identifier`

**Help**: Choose a different name.

**Example**:
```
process process              // ← 'process' is reserved
end
```

---

## 4. Parser Errors (E100-E199)

### E100: Unexpected Token

**Message**: `Unexpected token '{token}', expected {expected}`

**Help**: Check syntax against the grammar.

**Example**:
```
process auth_enrichment
  parallelism
end
```

**Output**:
```
auth_enrichment.proc:2:14: error[E100]: Unexpected token 'end', expected INTEGER
   |
 2 |   parallelism
   |              ^
 3 | end
   |
   = help: Provide a parallelism value, e.g., 'parallelism 128'
```

---

### E101: Missing 'end' Keyword

**Message**: `Missing 'end' keyword to close {construct}`

**Help**: Add `end` to close the block.

**Example**:
```
process auth_enrichment
  parallelism 128

process fraud_detection      // ← Missing 'end' for auth_enrichment
end
```

---

### E102: Missing Block

**Message**: `Missing required '{block}' block in {construct}`

**Help**: Add the required block.

**Example**:
```
process auth_enrichment
  parallelism 128
  // Missing 'receive' block
  emit to enriched_auths
end
```

**Output**:
```
auth_enrichment.proc:5:1: error[E102]: Missing required 'receive' block in process 'auth_enrichment'
   |
   = help: Add a receive block: 'receive events from <source>'
```

---

### E103: Invalid Block Order

**Message**: `'{block}' block must appear before '{other}' block`

**Help**: Reorder blocks according to grammar.

**Example**:
```
process auth_enrichment
  emit to enriched_auths     // ← emit before receive
  receive events from auth_events
end
```

---

### E104: Duplicate Block

**Message**: `Duplicate '{block}' block in {construct}`

**Help**: Remove the duplicate.

---

### E110: Decision Table Syntax Error

**Message**: `Invalid decision table syntax: {details}`

**Help**: Check table structure (pipes, columns, separators). All columns must be separated by `|`.

**Example**:
```
decision_table fraud_check
  decide:
    | score | amount | decision |
    |-------|--------|----------|
    | >= 700| > 1000   Approve  |  // ← Missing pipe between columns
```

---

### E111: Mismatched Columns

**Message**: `Row has {actual} columns, expected {expected}`

**Help**: Ensure all rows have the same number of columns.

---

## 5. Semantic Errors (E300-E399)

### E300: Undefined Reference

**Message**: `Undefined {kind} reference: '{name}'`

**Help**: Check spelling or define the referenced item.

**Example**:
```
process auth_enrichment
  receive events from auth_events
    schema auth_event_v2           // ← Schema not defined
end
```

**Output**:
```
auth_enrichment.proc:3:12: error[E300]: Undefined schema reference: 'auth_event_v2'
   |
 3 |     schema auth_event_v2
   |            ^^^^^^^^^^^^^
   |
   = help: Did you mean 'auth_event_v1'?
   = note: Available schemas: auth_event_v1, customer_v1, merchant_v1
```

---

### E301: Type Mismatch

**Message**: `Type mismatch: expected {expected}, found {actual}`

**Help**: Ensure types are compatible.

**Example**:
```
enrich using customer_lookup
  on card_id, account_type    // card_id is STRING, account_type is INTEGER
```

**Output**:
```
auth_enrichment.proc:5:7: error[E301]: Type mismatch in join key
   |
 5 |   on card_id, account_type
   |      ^^^^^^^  ^^^^^^^^^^^^
   |      STRING   INTEGER
   |
   = help: Join keys must have compatible types
```

---

### E302: Circular Dependency

**Message**: `Circular dependency detected: {cycle}`

**Help**: Remove the cycle by restructuring processes.

**Example**:
```
process A
  emit to B_input
end

process B
  emit to A_input     // Cycle: A → B → A
end
```

**Output**:
```
error[E302]: Circular dependency detected
   |
   = cycle: A → B → A
   = help: Break the cycle by introducing an intermediate process or buffer
```

---

### E303: Ambiguous Reference

**Message**: `Ambiguous reference: '{name}' matches multiple definitions`

**Help**: Use fully qualified name.

---

### E304: Duplicate Definition

**Message**: `Duplicate definition: '{name}' already defined at {location}`

**Help**: Rename one of the definitions.

---

### E310: Invalid Partition Key

**Message**: `Partition key '{field}' is not hashable`

**Help**: Use a hashable type (string, integer, etc.).

---

### E311: Invalid Time Field

**Message**: `Time field '{field}' must be a timestamp type`

**Help**: Use a timestamp field for event time processing.

---

### E312: Invalid Aggregation

**Message**: `Aggregation function '{func}' not valid for type '{type}'`

**Help**: Use numeric types for sum, avg, etc.

---

### E320: Missing Correlation Key

**Message**: `Correlation key '{field}' not found in stream '{stream}'`

**Help**: Ensure the field exists in both correlated streams.

---

### E321: Invalid Timeout

**Message**: `Timeout duration '{duration}' exceeds maximum of {max}`

**Help**: Use a shorter timeout or configure max timeout.

---

## 6. Schema Errors (E400-E499)

### E400: Schema Not Found

**Message**: `Schema '{name}' not found in schema registry`

**Help**: Define the schema or check the schema path.

---

### E401: Invalid Field Type

**Message**: `Invalid type '{type}' for field '{field}'`

**Help**: Use a supported type.

---

### E402: Field Not Found

**Message**: `Field '{field}' not found in schema '{schema}'`

**Help**: Check field name or update schema.

---

### E403: Schema Version Conflict

**Message**: `Schema version conflict: '{v1}' incompatible with '{v2}'`

**Help**: Use compatible schema versions.

---

### E410: Invalid Constraint

**Message**: `Invalid constraint for type '{type}': {constraint}`

**Help**: Check constraint syntax.

---

## 7. Transform Errors (E500-E599)

### E500: Transform Not Found

**Message**: `Transform '{name}' not found`

**Help**: Define the transform or check spelling.

---

### E501: Input Mismatch

**Message**: `Transform input type mismatch: expected {expected}, got {actual}`

**Help**: Ensure input matches transform signature.

---

### E502: Output Mismatch

**Message**: `Transform output type mismatch: expected {expected}, got {actual}`

**Help**: Update output schema or transform.

---

### E510: Impure Transform in Pure Context

**Message**: `Impure transform '{name}' cannot be used in pure context`

**Help**: Mark the containing context as impure or use a pure transform.

---

### E511: Invalid Expression

**Message**: `Invalid expression: {details}`

**Help**: Check expression syntax.

---

## 8. Rule Errors (E600-E699)

### E600: Rule Not Found

**Message**: `Rule set '{name}' not found`

**Help**: Define the rule set.

---

### E601: Hit Policy Violation

**Message**: `Hit policy '{policy}' violation: {details}`

**Help**: Ensure rules comply with hit policy.

---

### E602: Non-Exhaustive Rules

**Message**: `Rule set '{name}' is not exhaustive; missing coverage for: {cases}`

**Help**: Add wildcard row or cover all cases.

---

### E603: Overlapping Rules

**Message**: `Rules {rule1} and {rule2} overlap without explicit priority`

**Help**: Add priority column or make rules mutually exclusive.

---

### E610: Invalid Condition

**Message**: `Invalid condition syntax: {details}`

**Help**: Check condition format.

---

### E611: Invalid Action

**Message**: `Invalid action '{action}': {reason}`

**Help**: Check action syntax and target.

---

### E620: Undefined Outcome

**Message**: `Undefined route outcome: '{outcome}'`

**Help**: Define the outcome in the rule set declaration.

---

## 9. Binding Errors (E700-E799)

### E700: Missing Binding

**Message**: `No L5 binding found for logical name '{name}'`

**Help**: Add binding in .infra file.

**Example**:
```
receive events from customer_events    // No L5 binding for 'customer_events'
```

**Output**:
```
auth_enrichment.proc:2:22: error[E700]: No L5 binding found for logical name 'customer_events'
   |
 2 |   receive events from customer_events
   |                      ^^^^^^^^^^^^^^^^
   |
   = help: Add binding in production.infra:

     streams:
       customer_events:
         type: kafka
         topic: prod.customer.events.v1
         brokers: ${KAFKA_BROKERS}
```

---

### E701: Invalid Binding Type

**Message**: `Binding type '{type}' not supported for '{usage}'`

**Help**: Use appropriate binding type.

---

### E702: Missing Required Property

**Message**: `Missing required property '{prop}' in binding '{name}'`

**Help**: Add the required property.

---

### E703: Invalid Property Value

**Message**: `Invalid value '{value}' for property '{prop}'`

**Help**: Check property format.

---

### E710: Environment Variable Not Found

**Message**: `Environment variable '{var}' not found and no default provided`

**Help**: Set the variable or provide default.

---

### E711: Secret Reference Invalid

**Message**: `Invalid secret reference: '{ref}'`

**Help**: Check secret reference format.

---

### E720: Incompatible Binding

**Message**: `Binding '{name}' incompatible with usage as {usage}`

**Help**: Use correct direction (source/sink).

---

## 10. IR Errors (E800-E899)

### E800: Invalid Graph Structure

**Message**: `Invalid IR graph structure: {details}`

**Help**: Internal compiler error - report bug.

---

### E801: Orphan Node

**Message**: `Node '{id}' is not connected to any source or sink`

**Help**: Connect the node or remove it.

---

### E802: Invalid Edge

**Message**: `Invalid edge from '{source}' to '{target}': {reason}`

**Help**: Check edge connectivity.

---

## 11. Code Generation Errors (E900-E999)

### E900: Unsupported Feature

**Message**: `Feature '{feature}' not supported for target '{target}'`

**Help**: Use a different feature or target.

---

### E901: UDF Generation Failed

**Message**: `Failed to generate UDF for '{name}': {reason}`

**Help**: Simplify the rule or transform.

---

### E910: Target Not Available

**Message**: `Code generation target '{target}' not available`

**Help**: Install target generator or use supported target.

---

## 12. Warnings (W001-W999)

### W001: Unused Import

**Message**: `Unused schema import: '{name}'`

**Help**: Remove unused import.

---

### W002: Deprecated Feature

**Message**: `Feature '{feature}' is deprecated, use '{replacement}' instead`

**Help**: Update to new syntax.

---

### W010: Low Parallelism

**Message**: `Parallelism {value} may be too low for input volume`

**Help**: Consider increasing parallelism.

---

### W011: High State TTL

**Message**: `State TTL of {duration} may cause memory issues`

**Help**: Consider reducing TTL.

---

### W020: Potential Overlap

**Message**: `Rules may have overlapping conditions; consider adding priority`

**Help**: Add explicit priority column.

---

### W021: Missing Default Case

**Message**: `No default/wildcard case in decision table`

**Help**: Add wildcard row for exhaustiveness.

---

### W030: Unused Variable

**Message**: `Variable '{name}' defined but never used`

**Help**: Remove unused variable.

---

## 13. Error Output Format

### Standard Format

```
{file}:{line}:{column}: {severity}[{code}]: {message}
   |
 {line} | {source_line}
   |     {underline}
   |
   = help: {help_text}
   = note: {additional_info}
```

### JSON Format (for tooling)

```json
{
  "errors": [
    {
      "code": "E300",
      "severity": "error",
      "message": "Undefined schema reference: 'auth_event_v2'",
      "file": "auth_enrichment.proc",
      "line": 3,
      "column": 12,
      "endLine": 3,
      "endColumn": 25,
      "help": "Did you mean 'auth_event_v1'?",
      "notes": ["Available schemas: auth_event_v1, customer_v1"]
    }
  ],
  "warnings": [],
  "summary": {
    "errorCount": 1,
    "warningCount": 0
  }
}
```

---

## 14. Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no errors) |
| 1 | Compilation failed (errors) |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Permission denied |
| 5 | Internal error |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-30 | - | Initial catalog |
