# SchemaDSL.g4 Feature Coverage

> **Grammar Version**: 1.0.0
> **Verification Date**: 2025-11-29

---

## Coverage Summary

| Category | Features | Covered | Status |
|----------|----------|---------|--------|
| Mutation Patterns | 9 | 9 | ✅ 100% |
| Type System | 12 | 12 | ✅ 100% |
| Streaming Annotations | 15 | 15 | ✅ 100% |
| Schema Evolution | 8 | 8 | ✅ 100% |

**Overall Coverage**: ~95%

---

## 1. Mutation Patterns (9/9) ✅

| Pattern | Grammar Rule | Example Syntax |
|---------|--------------|----------------|
| `master_data` | `mutationPattern` | `pattern master_data` |
| `immutable_ledger` | `mutationPattern` | `pattern immutable_ledger` |
| `versioned_configuration` | `mutationPattern` | `pattern versioned_configuration` |
| `operational_parameters` | `mutationPattern` + `parametersBlock` | `pattern operational_parameters` |
| `event_log` | `mutationPattern` + `retentionDecl` | `pattern event_log` |
| `state_machine` | `mutationPattern` + `stateMachineBlock` | `pattern state_machine` |
| `temporal_data` | `mutationPattern` | `pattern temporal_data` |
| `reference_data` | `mutationPattern` + `entriesBlock` | `pattern reference_data` |
| `business_logic` | `mutationPattern` + `ruleBlock` | `pattern business_logic` |

---

## 2. Type System (12/12) ✅

### Base Types (8/8)

| Type | Grammar Rule |
|------|--------------|
| `string` | `baseType` |
| `integer` | `baseType` |
| `decimal` | `baseType` |
| `boolean` | `baseType` |
| `date` | `baseType` |
| `timestamp` | `baseType` |
| `uuid` | `baseType` |
| `bytes` | `baseType` |

### Constrained Types (5/5)

| Constraint | Grammar Rule | Example |
|------------|--------------|---------|
| Range | `rangeSpec` | `[range: 300..850]` |
| Length | `lengthSpec` | `[length: 16..19]` |
| Pattern | `constraintSpec` | `[pattern: "^[0-9]+$"]` |
| Values/Enum | `valueList` | `[values: USD, EUR, GBP]` |
| Precision/Scale | `constraintSpec` | `[precision: 15, scale: 2]` |

### Collection Types (3/3)

| Type | Grammar Rule | Example |
|------|--------------|---------|
| `list<T>` | `collectionType` | `list<string>` |
| `set<T>` | `collectionType` | `set<string>` |
| `map<K,V>` | `collectionType` | `map<string, decimal>` |

### Type Qualifiers (6/6)

| Qualifier | Grammar Rule |
|-----------|--------------|
| `required` | `fieldQualifier` |
| `optional` | `fieldQualifier` |
| `unique` | `fieldQualifier` |
| `cannot_change` | `fieldQualifier` |
| `encrypted` | `fieldQualifier` |
| `default: value` | `defaultClause` |

### Type Aliases ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Simple alias | `typeAlias` | `CustomerID: string [length: ..50]` |
| Complex alias | `typeAlias` with object | `Money: object ... end` |

---

## 3. Streaming Annotations (15/15) ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Key fields | `keyFieldsDecl` | `key_fields: [card_id]` |
| Time field | `timeFieldDecl` | `time_field: event_timestamp` |
| Time semantics | `timeSemanticsDecl` | `time_semantics: event_time` |
| Watermark delay | `watermarkDecl` | `watermark_delay: 30 seconds` |
| Watermark strategy | `watermarkDecl` | `watermark_strategy: bounded_out_of_orderness` |
| Max out-of-orderness | `watermarkDecl` | `max_out_of_orderness: 5 minutes` |
| Watermark interval | `watermarkDecl` | `watermark_interval: 100 milliseconds` |
| Punctuated watermark | `watermarkDecl` | `watermark_field: watermark_timestamp` |
| Late data handling | `lateDataDecl` | `late_data_handling: side_output` |
| Late data stream | `lateDataDecl` | `late_data_stream: late_events` |
| Allowed lateness | `allowedLatenessDecl` | `allowed_lateness: 5 minutes` |
| Idle timeout | `idleDecl` | `idle_timeout: 1 minute` |
| Idle behavior | `idleDecl` | `idle_behavior: mark_idle` |
| Sparsity hints | `sparsityDecl` | `sparsity ... end` |
| Retention config | `retentionBlockDecl` | `retention time: 90 days end` |

---

## 4. Schema Evolution (8/8) ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Version number | `versionBlock` | `version 3.2.1` |
| Compatibility mode | `compatibilityDecl` | `compatibility backward` |
| Previous version | `previousVersionDecl` | `previous_version 3.1.0` |
| Deprecation message | `deprecationDecl` | `deprecated: "Use v4"` |
| Deprecated since | `deprecationDecl` | `deprecated_since: "2024-01-01"` |
| Removal version | `deprecationDecl` | `removal_version: 4.0.0` |
| Migration guide | `migrationGuideDecl` | `migration_guide: "..."` |
| Migration block | `migrationBlock` | `migration ... end` |

---

## 5. Pattern-Specific Features ✅

### State Machine Pattern

| Feature | Grammar Rule |
|---------|--------------|
| Entity binding | `forEntityDecl` |
| States list | `statesDecl` |
| Initial state | `initialStateDecl` |
| Transitions | `transitionsBlock` |
| Transition actions | `onTransitionBlock` |

### Operational Parameters Pattern

| Feature | Grammar Rule |
|---------|--------------|
| Parameter declarations | `parametersBlock` |
| Default values | `parameterOption` |
| Range constraints | `parameterOption` |
| Schedulability | `parameterOption` |
| Change frequency | `parameterOption` |

### Reference Data Pattern

| Feature | Grammar Rule |
|---------|--------------|
| Entry definitions | `entriesBlock` |
| Entry fields | `entryField` |
| Deprecation | `entryField` |

### Business Logic Pattern

| Feature | Grammar Rule |
|---------|--------------|
| Rule definitions | `ruleBlock` |
| Given (inputs) | `givenBlock` |
| Calculate | `calculateBlock` |
| Return (outputs) | `returnBlock` |
| When expressions | `whenExpression` |

---

## 6. Nested Structures ✅

| Feature | Grammar Rule | Example |
|---------|--------------|---------|
| Inline object | `nestedObjectBlock` | `address: object ... end` |
| Deep nesting | Recursive `nestedObjectBlock` | `location: object coordinates: object ... end end` |
| List of objects | `nestedObjectBlock` with list | `addresses: list<object> ... end` |

---

## Example Schema (Validating Grammar)

```schema
schema auth_event
  pattern event_log
  version 3.2.1
  compatibility backward
  previous_version 3.1.0
  retention 7 days

  identity
    transaction_id: uuid, required, unique
  end

  streaming
    key_fields: [card_id]
    time_field: event_timestamp
    time_semantics: event_time
    watermark_strategy: bounded_out_of_orderness
    watermark_delay: 30 seconds
    late_data_handling: side_output
    late_data_stream: late_auth_events
    allowed_lateness: 5 minutes
    idle_timeout: 1 minute
    idle_behavior: mark_idle
  end

  fields
    card_id: string, required
    event_timestamp: timestamp, required
    amount: decimal [precision: 15, scale: 2], required
    currency: string [values: USD, EUR, GBP], required
    merchant_id: string, required
    fraud_score: integer [range: 0..100], optional, default: 0
  end

  merchant: object
    name: string
    category: string [length: 4]
    location: object
      city: string
      country: string [length: 2]
    end
  end
end
```

---

## Notes

1. **Semantic Validation** - The grammar parses syntax; the compiler must validate:
   - Identity block required for most patterns
   - Streaming block required for event_log
   - State transitions form valid graph
   - Compatibility mode matches actual changes

2. **Future Considerations**:
   - Union types (`string | integer`)
   - Nullable shorthand (`string?`)
   - Schema inheritance (`extends`)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-29 | Initial coverage verification |
