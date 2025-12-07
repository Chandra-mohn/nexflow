# L2: Type System

> **Source**: Adapted from ccdsl/core/CORE_DSL_SPECIFICATION.md
> **Status**: Complete Specification

---

## Overview

The Nexflow type system provides:
- **Base types**: Fundamental data types
- **Constrained types**: Types with validation rules
- **Domain types**: Business-specific semantic types
- **Collection types**: Lists, sets, and maps
- **Type qualifiers**: Required, optional, unique, etc.

---

## Base Types

| Type | Description | Example Values | Storage |
|------|-------------|----------------|---------|
| `string` | Variable-length text | `"John Doe"`, `"ABC123"` | VARCHAR |
| `integer` | Whole numbers | `42`, `-100`, `0` | INT/BIGINT |
| `decimal` | Precise decimal numbers | `3.14159`, `1000.50` | DECIMAL |
| `boolean` | True/false values | `true`, `false` | BOOLEAN |
| `date` | Calendar dates (no time) | `2024-01-15` | DATE |
| `timestamp` | Date + time + timezone | `2024-01-15T10:30:00Z` | TIMESTAMP |
| `uuid` | Universally unique ID | `550e8400-e29b-...` | UUID |
| `bytes` | Binary data | Base64 encoded | BYTEA |

---

## Constrained Types

### Range Constraints

```schema
credit_score: integer [range: 300..850]
age: integer [range: 18..120]
percentage: decimal [range: 0..100]
temperature: decimal [range: -40..60]
```

**Semantics**: Value must be within inclusive range.

### Length Constraints

```schema
account_number: string [length: 16]           // Exact length
card_number: string [length: 16..19]          // Range
short_code: string [length: ..6]              // Max length
description: string [length: 10..]            // Min length
```

### Pattern Constraints (Regex)

```schema
email: string [pattern: "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"]
phone: string [pattern: "^\\+[1-9]\\d{1,14}$"]
postal_code: string [pattern: "^[0-9]{5}(-[0-9]{4})?$"]
```

### Enumeration Constraints

```schema
status: string [values: active, pending, closed]
tier: string [values: premier, preferred, standard]
currency: string [values: USD, EUR, GBP, JPY, CAD]
```

### Precision Constraints (Decimals)

```schema
amount: decimal [precision: 15, scale: 2]     // DECIMAL(15,2)
rate: decimal [precision: 7, scale: 4]        // DECIMAL(7,4)
```

---

## Domain Types

Domain types are semantic types that carry business meaning beyond their base type.

### Financial Types

```schema
// Money with currency
money: object
  amount: decimal [precision: 15, scale: 2]
  currency: currency_code
end

// Currency codes
currency_code: string [values: USD, EUR, GBP, JPY, CAD, AUD, CHF]

// Financial identifiers
account_number: string [length: 16, pattern: "^[0-9]+$"]
routing_number: string [length: 9, pattern: "^[0-9]+$"]
swift_code: string [length: 8..11, pattern: "^[A-Z]{6}[A-Z0-9]{2,5}$"]
```

### Card Types

```schema
card_number: string [length: 16..19, pattern: "^[0-9]+$"]
cvv: string [length: 3..4, pattern: "^[0-9]+$"]
expiry_month: integer [range: 1..12]
expiry_year: integer [range: 2020..2099]

card_brand: string [values: visa, mastercard, amex, discover]
card_type: string [values: credit, debit, prepaid]
```

### Merchant Types

```schema
// Merchant Category Code (ISO 18245)
mcc_code: string [length: 4, pattern: "^[0-9]+$"]

// Merchant identifiers
merchant_id: string [length: ..50]
terminal_id: string [length: ..20]
```

### Geographic Types

```schema
country_code: string [length: 2, pattern: "^[A-Z]{2}$"]     // ISO 3166-1 alpha-2
country_code_3: string [length: 3, pattern: "^[A-Z]{3}$"]   // ISO 3166-1 alpha-3
state_code: string [length: 2, pattern: "^[A-Z]{2}$"]
postal_code: string [pattern: "^[A-Z0-9 -]+$"]

latitude: decimal [range: -90..90]
longitude: decimal [range: -180..180]
```

### Contact Types

```schema
email: string [pattern: "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"]
phone: string [pattern: "^\\+[1-9]\\d{1,14}$"]  // E.164 format
url: string [pattern: "^https?://.*"]
```

### Time Types

```schema
// Duration with units
duration: object
  value: integer
  unit: string [values: seconds, minutes, hours, days, weeks, months, years]
end

// Time of day
time_of_day: string [pattern: "^[0-2][0-9]:[0-5][0-9](:[0-5][0-9])?$"]

// Timezone
timezone: string [pattern: "^[A-Z][a-z]+/[A-Z][a-z_]+$"]  // e.g., America/New_York
```

---

## Collection Types

### List Type

Ordered collection allowing duplicates:

```schema
tags: list<string>
amounts: list<decimal>
addresses: list<address>  // List of complex objects
```

### Set Type

Unordered collection without duplicates:

```schema
categories: set<string>
permissions: set<permission_type>
```

### Map Type

Key-value associations:

```schema
attributes: map<string, string>
balances: map<currency_code, decimal>
metadata: map<string, any>
```

---

## Type Qualifiers

### Required vs Optional

```schema
fields
  customer_id: string, required      // Cannot be null
  email: string, required
  phone: string, optional            // Can be null (default)
  middle_name: string                // Optional by default
end
```

### Unique

```schema
identity
  account_id: string, unique, required
  email: string, unique
end
```

### Cannot Change (Immutable)

```schema
fields
  created_at: timestamp, required, cannot_change
  account_number: string, required, unique, cannot_change
  ssn: string, cannot_change, encrypted
end
```

### Encrypted

```schema
fields
  ssn: string, encrypted
  card_number: string, encrypted
  password: string, encrypted
end
```

### Default Values

```schema
fields
  status: string, default: "pending"
  created_at: timestamp, default: now()
  retry_count: integer, default: 0
  is_active: boolean, default: true
end
```

---

## Nested Types (Objects)

### Inline Object Definition

```schema
schema customer
  fields
    customer_id: string, required
    name: string, required
  end

  address: object
    street: string
    city: string
    state: state_code
    postal_code: postal_code
    country: country_code, default: "US"
  end

  preferences: object
    notification_email: boolean, default: true
    notification_sms: boolean, default: false
    language: string, default: "en"
  end
end
```

### Deep Nesting

```schema
schema transaction
  fields
    transaction_id: uuid, required
    amount: decimal, required
  end

  merchant: object
    merchant_id: string, required
    name: string
    location: object
      city: string
      state: state_code
      country: country_code
      coordinates: object
        latitude: latitude
        longitude: longitude
      end
    end
  end
end
```

### Array of Objects

```schema
schema customer
  addresses: list<object>
    type: string [values: home, work, billing, shipping]
    street: string
    city: string
    state: state_code
    postal_code: postal_code
    is_primary: boolean, default: false
  end
end
```

---

## Type Aliases

Define reusable type aliases:

```schema
types
  // Simple alias
  CustomerID: string [length: ..50]
  AccountNumber: string [length: 16, pattern: "^[0-9]+$"]

  // Complex alias
  Money: object
    amount: decimal [precision: 15, scale: 2]
    currency: currency_code
  end

  // Constrained alias
  CreditScore: integer [range: 300..850]
  Percentage: decimal [range: 0..100, precision: 5, scale: 2]
end

schema transaction
  fields
    transaction_id: uuid
    amount: Money                    // Using type alias
    customer_id: CustomerID          // Using type alias
  end
end
```

---

## Type Validation

### Compile-Time Validation

The compiler validates:
- Type compatibility in assignments
- Constraint satisfaction
- Required fields present
- Enum values valid

```schema
// Compiler validates:
credit_score: integer [range: 300..850]
// ERROR if assigned: credit_score = 900

status: string [values: active, pending]
// ERROR if assigned: status = "invalid"
```

### Runtime Validation

Generated code validates:
- Null checks for required fields
- Range validation
- Pattern matching
- Referential integrity

---

## Type Coercion Rules

| From | To | Allowed |
|------|-----|---------|
| `integer` | `decimal` | Yes (automatic) |
| `decimal` | `integer` | No (explicit cast required) |
| `string` | `integer` | No (parse function required) |
| `timestamp` | `date` | Yes (truncates time) |
| `date` | `timestamp` | Yes (midnight assumed) |

---

## Related Documents

- [mutation-patterns.md](./mutation-patterns.md) - Data patterns
- [streaming-annotations.md](./streaming-annotations.md) - Streaming metadata
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - L2 overview
