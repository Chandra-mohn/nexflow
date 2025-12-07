# L2: Schema Evolution

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Schema evolution defines how schemas can change over time while maintaining compatibility with existing data and consumers. Nexflow supports:

- **Versioning**: Semantic version management
- **Compatibility modes**: Backward, forward, full, none
- **Migration patterns**: Safe upgrade paths
- **Breaking change detection**: Compile-time validation

---

## Versioning

### Semantic Versioning

Schemas use semantic versioning (MAJOR.MINOR.PATCH):

```schema
schema customer
  version 2.3.1

  // MAJOR: Breaking changes
  // MINOR: New features, backward compatible
  // PATCH: Bug fixes, documentation
end
```

### Version Declaration

```schema
schema auth_event
  version 3.2.0
  compatibility backward
  previous_version 3.1.0

  // Schema definition...
end
```

### Version Chain

```
auth_event v1.0.0 (initial)
    ↓
auth_event v1.1.0 (added optional field)
    ↓
auth_event v2.0.0 (BREAKING: renamed field)
    ↓
auth_event v2.1.0 (added optional field)
    ↓
auth_event v3.0.0 (BREAKING: changed type)
```

---

## Compatibility Modes

### Backward Compatible

New schema can read data written by old schema.

**Safe operations**:
- Add optional fields (with defaults)
- Remove fields (old readers ignore)
- Widen numeric types (int → long)

**Example**:
```schema
// v1.0.0
schema customer_v1
  fields
    customer_id: string
    name: string
  end
end

// v1.1.0 - Backward compatible
schema customer_v1_1
  version 1.1.0
  compatibility backward
  previous_version 1.0.0

  fields
    customer_id: string
    name: string
    email: string, optional          // NEW: optional field
    phone: string, optional          // NEW: optional field
  end
end
```

### Forward Compatible

Old schema can read data written by new schema.

**Safe operations**:
- Remove optional fields
- Add fields (old readers ignore)
- Narrow numeric types (long → int) with validation

**Example**:
```schema
// v2.0.0 - Forward compatible from v1.1.0
schema customer_v2
  version 2.0.0
  compatibility forward
  previous_version 1.1.0

  fields
    customer_id: string
    name: string
    // email: removed (old readers ignore)
    contact_method: string           // NEW: old readers ignore
  end
end
```

### Full Compatible

Both backward and forward compatible. Most restrictive.

**Safe operations**:
- Add optional fields with defaults
- Remove optional fields

**Example**:
```schema
schema transaction
  version 3.1.0
  compatibility full
  previous_version 3.0.0

  fields
    // All existing fields unchanged
    transaction_id: uuid
    amount: decimal
    // Only safe additions
    notes: string, optional, default: ""
  end
end
```

### None (Breaking)

No compatibility guaranteed. Use for major version bumps.

```schema
schema customer
  version 3.0.0
  compatibility none
  previous_version 2.5.0

  // Breaking changes allowed
  fields
    id: uuid                         // BREAKING: renamed from customer_id
    full_name: string                // BREAKING: renamed from name
    email: string, required          // BREAKING: now required
  end
end
```

---

## Compatible Changes

### Always Safe

| Change | Backward | Forward | Full |
|--------|----------|---------|------|
| Add optional field with default | ✓ | ✓ | ✓ |
| Add documentation | ✓ | ✓ | ✓ |
| Add alias for field | ✓ | ✓ | ✓ |

### Backward Compatible Only

| Change | Backward | Forward | Full |
|--------|----------|---------|------|
| Add required field with default | ✓ | ✗ | ✗ |
| Remove optional field | ✓ | ✗ | ✗ |
| Widen numeric type (int→long) | ✓ | ✗ | ✗ |
| Add enum value | ✓ | ✗ | ✗ |

### Forward Compatible Only

| Change | Backward | Forward | Full |
|--------|----------|---------|------|
| Remove optional field | ✗ | ✓ | ✗ |
| Narrow numeric type (long→int) | ✗ | ✓* | ✗ |
| Remove enum value | ✗ | ✓ | ✗ |

*With validation that values fit

### Breaking Changes

| Change | Backward | Forward | Full |
|--------|----------|---------|------|
| Rename field | ✗ | ✗ | ✗ |
| Change field type | ✗ | ✗ | ✗ |
| Remove required field | ✗ | ✗ | ✗ |
| Add required field (no default) | ✗ | ✗ | ✗ |
| Change field optionality | ✗ | ✗ | ✗ |

---

## Migration Patterns

### Field Rename

Use deprecation + new field:

```schema
// v2.0.0 - Safe rename
schema customer
  version 2.0.0
  compatibility backward

  fields
    customer_id: string

    // Deprecated field (still works)
    name: string, deprecated: "Use full_name instead"

    // New field
    full_name: string, optional
  end

  migration
    // Copy old to new if new is null
    full_name = coalesce(full_name, name)
  end
end

// v3.0.0 - Complete migration
schema customer
  version 3.0.0
  compatibility none  // Breaking

  fields
    customer_id: string
    full_name: string, required  // name removed
  end
end
```

### Type Change

Add new field, migrate, remove old:

```schema
// v1: amount as string
schema transaction_v1
  fields
    amount: string  // "100.50"
  end
end

// v2: add decimal field
schema transaction_v2
  version 2.0.0
  compatibility backward

  fields
    amount: string, deprecated: "Use amount_decimal"
    amount_decimal: decimal, optional
  end

  migration
    amount_decimal = parse_decimal(amount)
  end
end

// v3: switch to decimal
schema transaction_v3
  version 3.0.0
  compatibility none

  fields
    amount: decimal, required
  end
end
```

### Field Splitting

```schema
// v1: combined field
schema customer_v1
  fields
    address: string  // "123 Main St, City, ST 12345"
  end
end

// v2: add structured fields
schema customer_v2
  version 2.0.0
  compatibility backward

  fields
    address: string, deprecated: "Use structured address"
    street: string, optional
    city: string, optional
    state: string, optional
    postal_code: string, optional
  end

  migration
    // Parse old format into new fields
    (street, city, state, postal_code) = parse_address(address)
  end
end
```

---

## Deprecation

### Field Deprecation

```schema
schema customer
  fields
    // Active fields
    customer_id: string
    email: string

    // Deprecated fields
    phone: string, deprecated: "Use contact.phone instead"
    fax: string, deprecated: "Fax no longer supported", removal: "4.0.0"
  end
end
```

### Schema Deprecation

```schema
schema old_transaction
  version 2.5.0
  deprecated: "Use transaction schema instead"
  deprecated_since: "2024-01-01"
  removal_version: "3.0.0"
  migration_guide: "docs/migration/old-transaction-to-transaction.md"
end
```

---

## Schema Registry Integration

### Registration

```bash
# Register new schema version
nexflow schema register auth_event.schema

# Check compatibility before registration
nexflow schema check auth_event.schema

# List schema versions
nexflow schema list auth_event
```

### Compatibility Check

```bash
$ nexflow schema check auth_event.schema

Checking auth_event v3.2.0 against v3.1.0...

Compatibility mode: backward

Changes detected:
  + Added field: fraud_score (optional, default: 0)
  + Added field: risk_factors (optional, default: [])

Result: COMPATIBLE ✓

Changes are backward compatible with v3.1.0
```

### Breaking Change Detection

```bash
$ nexflow schema check auth_event.schema

Checking auth_event v4.0.0 against v3.2.0...

Compatibility mode: backward

BREAKING CHANGES DETECTED:
  ✗ Renamed field: transaction_id → txn_id
  ✗ Changed type: amount (string → decimal)
  ✗ Removed required field: legacy_code

Result: INCOMPATIBLE ✗

To proceed with breaking changes:
  1. Set compatibility: none
  2. Update version to MAJOR bump (4.0.0)
  3. Create migration guide
```

---

## Best Practices

### 1. Always Start with Compatibility Mode

```schema
schema new_schema
  version 1.0.0
  compatibility backward  // Default to backward
end
```

### 2. Use Defaults for New Fields

```schema
// Good
new_field: string, optional, default: ""

// Bad - forces MAJOR version bump
new_field: string, required
```

### 3. Deprecate Before Removing

```schema
// Version N: deprecate
field: string, deprecated: "Will be removed in N+2"

// Version N+1: still present but deprecated
field: string, deprecated: "Will be removed in N+2"

// Version N+2: remove (MAJOR bump)
// field removed
```

### 4. Document Migration Paths

```schema
schema customer
  version 3.0.0
  compatibility none
  previous_version 2.5.0

  migration_guide: """
    Breaking changes in v3.0.0:

    1. `name` renamed to `full_name`
       - Update all queries: WHERE name → WHERE full_name
       - Migration: full_name = name

    2. `address` split into structured fields
       - See parse_address() function for migration
  """
end
```

### 5. Version Schemas in Source Control

```
schemas/
├── auth_event/
│   ├── v1.0.0.schema
│   ├── v2.0.0.schema
│   ├── v3.0.0.schema
│   └── current.schema → v3.0.0.schema
```

---

## Related Documents

- [mutation-patterns.md](./mutation-patterns.md) - Data patterns
- [type-system.md](./type-system.md) - Type definitions
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - L2 overview
