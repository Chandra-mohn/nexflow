# L3: Structured Data Manipulation Functions

> **Source**: Native Nexflow specification
> **Status**: Complete Specification
> **Context**: Format-agnostic structured data operations

---

## Overview

Structured data functions provide format-agnostic operations for manipulating complex, nested data structures. These functions abstract away the underlying serialization format (JSON, Avro, Protobuf, Parquet, etc.) and work uniformly across all supported formats.

**Design Principles**:
- **Format Agnostic**: Same function works for JSON, Avro, Protobuf, MessagePack, etc.
- **Path-Based Access**: Unified path syntax for nested field access
- **Type Safe**: Operations respect schema types when available
- **Null Safe**: Consistent null handling across all formats

**Supported Underlying Formats**:
- JSON (schema-less)
- Avro (schema-required)
- Protocol Buffers (schema-required)
- Parquet (columnar)
- MessagePack (binary JSON)
- CBOR (binary JSON)
- Thrift (schema-required)
- Custom (via codec extension)

---

## Path Expression Syntax

### Path Notation

Nexflow uses a unified path notation for accessing nested structures:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Path Expression Syntax                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Simple field        │ field_name                               │
│  Nested field        │ parent.child.grandchild                  │
│  Array index         │ items[0]                                 │
│  Array all           │ items[*]                                 │
│  Last element        │ items[-1]                                │
│  Slice               │ items[0:3]                               │
│  Filter              │ items[?(@.status == "active")]           │
│  Wildcard            │ *.name                                   │
│  Recursive           │ ..field_name                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Path Examples

```xform
// Given structure:
// {
//   "customer": {
//     "name": "John Doe",
//     "addresses": [
//       {"type": "home", "city": "NYC"},
//       {"type": "work", "city": "Boston"}
//     ],
//     "preferences": {
//       "notifications": {"email": true, "sms": false}
//     }
//   }
// }

// Simple nested access
customer_name = "customer.name"                    // "John Doe"

// Array index
first_address = "customer.addresses[0]"           // {"type":"home","city":"NYC"}
first_city = "customer.addresses[0].city"         // "NYC"

// Array all elements
all_cities = "customer.addresses[*].city"         // ["NYC", "Boston"]

// Filter expression
work_address = "customer.addresses[?(@.type == 'work')]"  // [{"type":"work"...}]

// Deep nested
email_pref = "customer.preferences.notifications.email"   // true

// Recursive descent (find all 'type' fields anywhere)
all_types = "..type"                              // ["home", "work"]
```

---

## Record/Object Functions

### Field Access

| Function | Signature | Description |
|----------|-----------|-------------|
| `field_get(record, path)` | `record, string → any` | Get field value by path |
| `field_get_or(record, path, default)` | `record, string, any → any` | Get with default |
| `field_exists(record, path)` | `record, string → boolean` | Check if path exists |
| `field_type(record, path)` | `record, string → string` | Get type at path |

#### Examples

```xform
// Get nested field
city = field_get(customer, "address.city")

// Get with default
phone = field_get_or(customer, "phone", "N/A")

// Check existence before access
has_email = field_exists(customer, "contact.email")
email = when has_email: field_get(customer, "contact.email")
        otherwise: null

// Type inspection
addr_type = field_type(customer, "address")  // "object" or "record"
```

### Field Modification

| Function | Signature | Description |
|----------|-----------|-------------|
| `field_set(record, path, value)` | `record, string, any → record` | Set field value |
| `field_remove(record, path)` | `record, string → record` | Remove field |
| `field_rename(record, old_path, new_path)` | `record, string, string → record` | Rename field |
| `field_move(record, from_path, to_path)` | `record, string, string → record` | Move field |

**Note**: All modification functions return a new record (immutable semantics).

#### Examples

```xform
// Set nested field (creates intermediate objects if needed)
updated = field_set(customer, "address.zip", "10001")

// Remove field
without_ssn = field_remove(customer, "ssn")

// Rename field
renamed = field_rename(customer, "tel", "phone")

// Move field to different location
moved = field_move(customer, "legacy.email", "contact.email")
```

### Record Construction

| Function | Signature | Description |
|----------|-----------|-------------|
| `record_create(fields...)` | `(string, any)... → record` | Create new record |
| `record_merge(record1, record2)` | `record, record → record` | Merge records (right wins) |
| `record_merge_deep(record1, record2)` | `record, record → record` | Deep merge |
| `record_pick(record, paths...)` | `record, string... → record` | Pick specific fields |
| `record_omit(record, paths...)` | `record, string... → record` | Omit specific fields |
| `record_flatten(record, delimiter)` | `record, string → record` | Flatten nested to single level |
| `record_unflatten(record, delimiter)` | `record, string → record` | Unflatten to nested |

#### Examples

```xform
// Create record
new_record = record_create(
  "customer_id", "C123",
  "name", "John Doe",
  "status", "active"
)

// Merge records
base = record_create("a", 1, "b", 2)
overlay = record_create("b", 3, "c", 4)
merged = record_merge(base, overlay)  // {"a":1, "b":3, "c":4}

// Deep merge
config1 = record_create("db", record_create("host", "localhost", "port", 5432))
config2 = record_create("db", record_create("port", 5433))
deep_merged = record_merge_deep(config1, config2)
// {"db": {"host": "localhost", "port": 5433}}

// Pick specific fields
essential = record_pick(customer, "id", "name", "email")

// Omit sensitive fields
safe_record = record_omit(customer, "ssn", "password", "secret_key")

// Flatten
nested = {"a": {"b": {"c": 1}}}
flat = record_flatten(nested, ".")  // {"a.b.c": 1}

// Unflatten
unflat = record_unflatten(flat, ".")  // {"a": {"b": {"c": 1}}}
```

### Record Inspection

| Function | Signature | Description |
|----------|-----------|-------------|
| `record_keys(record)` | `record → list<string>` | Get all top-level keys |
| `record_keys_deep(record)` | `record → list<string>` | Get all keys (flattened paths) |
| `record_values(record)` | `record → list<any>` | Get all top-level values |
| `record_entries(record)` | `record → list<entry>` | Get key-value pairs |
| `record_size(record)` | `record → integer` | Count of top-level fields |
| `record_is_empty(record)` | `record → boolean` | Check if empty |

#### Examples

```xform
keys = record_keys(customer)  // ["id", "name", "address"]

all_paths = record_keys_deep(customer)  // ["id", "name", "address.city", "address.zip"]

count = record_size(customer)  // 3

is_empty = record_is_empty(record_create())  // true
```

---

## Array/List Functions

### Basic Array Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_get(array, index)` | `array, integer → any` | Get element at index |
| `array_get_or(array, index, default)` | `array, integer, any → any` | Get with default |
| `array_first(array)` | `array → any` | First element |
| `array_last(array)` | `array → any` | Last element |
| `array_length(array)` | `array → integer` | Array length |
| `array_is_empty(array)` | `array → boolean` | Check if empty |

#### Examples

```xform
items = [10, 20, 30, 40, 50]

first = array_first(items)  // 10
last = array_last(items)  // 50
third = array_get(items, 2)  // 30
safe = array_get_or(items, 10, 0)  // 0 (index out of bounds)
len = array_length(items)  // 5
```

### Array Modification

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_append(array, element)` | `array, any → array` | Add to end |
| `array_prepend(array, element)` | `array, any → array` | Add to beginning |
| `array_insert(array, index, element)` | `array, integer, any → array` | Insert at position |
| `array_remove(array, index)` | `array, integer → array` | Remove at index |
| `array_remove_value(array, value)` | `array, any → array` | Remove first occurrence |
| `array_remove_all(array, value)` | `array, any → array` | Remove all occurrences |
| `array_set(array, index, value)` | `array, integer, any → array` | Set element at index |
| `array_concat(array1, array2)` | `array, array → array` | Concatenate arrays |

#### Examples

```xform
items = [1, 2, 3]

// Modifications (all return new arrays)
with_4 = array_append(items, 4)  // [1, 2, 3, 4]
with_0 = array_prepend(items, 0)  // [0, 1, 2, 3]
with_insert = array_insert(items, 1, 99)  // [1, 99, 2, 3]
without_first = array_remove(items, 0)  // [2, 3]

// Concatenate
combined = array_concat([1, 2], [3, 4])  // [1, 2, 3, 4]
```

### Array Slicing

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_slice(array, start, end)` | `array, integer, integer → array` | Slice from start to end |
| `array_take(array, n)` | `array, integer → array` | Take first N elements |
| `array_take_last(array, n)` | `array, integer → array` | Take last N elements |
| `array_drop(array, n)` | `array, integer → array` | Drop first N elements |
| `array_drop_last(array, n)` | `array, integer → array` | Drop last N elements |

#### Examples

```xform
items = [1, 2, 3, 4, 5]

slice = array_slice(items, 1, 4)  // [2, 3, 4]
first_3 = array_take(items, 3)  // [1, 2, 3]
last_2 = array_take_last(items, 2)  // [4, 5]
skip_2 = array_drop(items, 2)  // [3, 4, 5]
```

### Array Transformation

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_map(array, expr)` | `array, expression → array` | Transform each element |
| `array_filter(array, predicate)` | `array, expression → array` | Filter by condition |
| `array_reduce(array, init, expr)` | `array, any, expression → any` | Reduce to single value |
| `array_flat_map(array, expr)` | `array, expression → array` | Map and flatten |
| `array_group_by(array, key_expr)` | `array, expression → map` | Group by key |
| `array_partition(array, predicate)` | `array, expression → tuple` | Split by condition |

#### Variable Binding

In transformation expressions:
- `it` or `$` refers to current element
- `idx` or `$index` refers to current index
- `acc` refers to accumulator (in reduce)

#### Examples

```xform
amounts = [100, 200, 150, 300]

// Map: double each
doubled = array_map(amounts, it * 2)  // [200, 400, 300, 600]

// Filter: keep > 150
large = array_filter(amounts, it > 150)  // [200, 300]

// Reduce: sum all
total = array_reduce(amounts, 0, acc + it)  // 750

// Complex objects
transactions = [
  {"id": 1, "amount": 100, "type": "debit"},
  {"id": 2, "amount": 200, "type": "credit"},
  {"id": 3, "amount": 150, "type": "debit"}
]

// Map to extract field
txn_amounts = array_map(transactions, it.amount)  // [100, 200, 150]

// Filter by condition
debits = array_filter(transactions, it.type == "debit")

// Group by type
by_type = array_group_by(transactions, it.type)
// {"debit": [...], "credit": [...]}

// Partition
partitioned = array_partition(amounts, it > 150)
// ([200, 300], [100, 150])  // (matching, non-matching)
```

### Array Searching

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_contains(array, value)` | `array, any → boolean` | Check if contains value |
| `array_index_of(array, value)` | `array, any → integer` | Find first index (-1 if not found) |
| `array_last_index_of(array, value)` | `array, any → integer` | Find last index |
| `array_find(array, predicate)` | `array, expression → any` | Find first matching |
| `array_find_index(array, predicate)` | `array, expression → integer` | Find index of first match |
| `array_any(array, predicate)` | `array, expression → boolean` | Any element matches |
| `array_all(array, predicate)` | `array, expression → boolean` | All elements match |
| `array_none(array, predicate)` | `array, expression → boolean` | No elements match |

#### Examples

```xform
numbers = [1, 2, 3, 4, 5]

has_3 = array_contains(numbers, 3)  // true
idx = array_index_of(numbers, 3)  // 2

// Find first even
first_even = array_find(numbers, it % 2 == 0)  // 2

// Check conditions
any_large = array_any(numbers, it > 4)  // true
all_positive = array_all(numbers, it > 0)  // true
none_negative = array_none(numbers, it < 0)  // true
```

### Array Ordering

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_sort(array)` | `array → array` | Sort ascending |
| `array_sort_desc(array)` | `array → array` | Sort descending |
| `array_sort_by(array, key_expr)` | `array, expression → array` | Sort by key |
| `array_sort_by_desc(array, key_expr)` | `array, expression → array` | Sort by key descending |
| `array_reverse(array)` | `array → array` | Reverse order |
| `array_shuffle(array)` | `array → array` | Random shuffle |

#### Examples

```xform
numbers = [3, 1, 4, 1, 5]

sorted = array_sort(numbers)  // [1, 1, 3, 4, 5]
sorted_desc = array_sort_desc(numbers)  // [5, 4, 3, 1, 1]
reversed = array_reverse(numbers)  // [5, 1, 4, 1, 3]

// Sort objects by field
transactions = [
  {"id": "A", "amount": 300},
  {"id": "B", "amount": 100},
  {"id": "C", "amount": 200}
]

by_amount = array_sort_by(transactions, it.amount)
// [{"id":"B","amount":100}, {"id":"C","amount":200}, {"id":"A","amount":300}]
```

### Array Set Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `array_distinct(array)` | `array → array` | Remove duplicates |
| `array_distinct_by(array, key_expr)` | `array, expression → array` | Distinct by key |
| `array_union(array1, array2)` | `array, array → array` | Set union |
| `array_intersect(array1, array2)` | `array, array → array` | Set intersection |
| `array_difference(array1, array2)` | `array, array → array` | Set difference |
| `array_symmetric_diff(array1, array2)` | `array, array → array` | Symmetric difference |

#### Examples

```xform
a = [1, 2, 2, 3, 3, 3]
b = [3, 4, 5]

unique = array_distinct(a)  // [1, 2, 3]
union = array_union(a, b)  // [1, 2, 3, 4, 5]
common = array_intersect(a, b)  // [3]
diff = array_difference(a, b)  // [1, 2]
sym_diff = array_symmetric_diff(a, b)  // [1, 2, 4, 5]
```

---

## Map/Dictionary Functions

### Map Access

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_get(map, key)` | `map, any → any` | Get value by key |
| `map_get_or(map, key, default)` | `map, any, any → any` | Get with default |
| `map_contains_key(map, key)` | `map, any → boolean` | Check key exists |
| `map_contains_value(map, value)` | `map, any → boolean` | Check value exists |

#### Examples

```xform
rates = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73}

usd_rate = map_get(rates, "USD")  // 1.0
cad_rate = map_get_or(rates, "CAD", 1.25)  // 1.25 (default)
has_eur = map_contains_key(rates, "EUR")  // true
```

### Map Modification

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_put(map, key, value)` | `map, any, any → map` | Add/update entry |
| `map_put_all(map, other_map)` | `map, map → map` | Add all entries |
| `map_remove(map, key)` | `map, any → map` | Remove entry |
| `map_remove_all(map, keys)` | `map, list → map` | Remove multiple |

#### Examples

```xform
rates = {"USD": 1.0, "EUR": 0.85}

// Add CAD
with_cad = map_put(rates, "CAD", 1.35)

// Merge maps
more_rates = {"GBP": 0.73, "JPY": 110.0}
all_rates = map_put_all(rates, more_rates)

// Remove
without_eur = map_remove(rates, "EUR")
```

### Map Inspection

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_keys(map)` | `map → list<any>` | Get all keys |
| `map_values(map)` | `map → list<any>` | Get all values |
| `map_entries(map)` | `map → list<entry>` | Get key-value pairs |
| `map_size(map)` | `map → integer` | Count of entries |
| `map_is_empty(map)` | `map → boolean` | Check if empty |

### Map Transformation

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_map_values(map, expr)` | `map, expression → map` | Transform values |
| `map_map_keys(map, expr)` | `map, expression → map` | Transform keys |
| `map_filter(map, predicate)` | `map, expression → map` | Filter entries |
| `map_invert(map)` | `map → map` | Swap keys and values |

#### Variable Binding

In map transformations:
- `key` or `$key` refers to current key
- `value` or `$value` refers to current value

#### Examples

```xform
prices = {"apple": 1.5, "banana": 0.75, "cherry": 3.0}

// Double all prices
doubled = map_map_values(prices, value * 2)
// {"apple": 3.0, "banana": 1.5, "cherry": 6.0}

// Uppercase keys
upper_keys = map_map_keys(prices, upper(key))
// {"APPLE": 1.5, "BANANA": 0.75, "CHERRY": 3.0}

// Filter expensive items
expensive = map_filter(prices, value > 1.0)
// {"apple": 1.5, "cherry": 3.0}

// Invert (useful for lookups)
lookup = {"A": "Active", "I": "Inactive", "P": "Pending"}
inverted = map_invert(lookup)
// {"Active": "A", "Inactive": "I", "Pending": "P"}
```

### Map Construction

| Function | Signature | Description |
|----------|-----------|-------------|
| `map_create(entries...)` | `(any, any)... → map` | Create from key-value pairs |
| `map_from_entries(entries)` | `list<entry> → map` | Create from entry list |
| `map_from_arrays(keys, values)` | `list, list → map` | Create from parallel arrays |
| `array_to_map(array, key_expr, value_expr)` | `array, expr, expr → map` | Convert array to map |

#### Examples

```xform
// Create from pairs
rates = map_create("USD", 1.0, "EUR", 0.85, "GBP", 0.73)

// From parallel arrays
keys = ["a", "b", "c"]
values = [1, 2, 3]
from_arrays = map_from_arrays(keys, values)  // {"a":1, "b":2, "c":3}

// Array of objects to map
users = [
  {"id": "U1", "name": "Alice"},
  {"id": "U2", "name": "Bob"}
]
user_map = array_to_map(users, it.id, it.name)
// {"U1": "Alice", "U2": "Bob"}
```

---

## Nested Structure Operations

### Deep Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `deep_get(data, path)` | `any, string → any` | Get value at path |
| `deep_set(data, path, value)` | `any, string, any → any` | Set value at path |
| `deep_remove(data, path)` | `any, string → any` | Remove at path |
| `deep_merge(data1, data2)` | `any, any → any` | Deep merge structures |
| `deep_equals(data1, data2)` | `any, any → boolean` | Deep equality check |
| `deep_copy(data)` | `any → any` | Deep copy |

#### Examples

```xform
data = {
  "customer": {
    "profile": {
      "preferences": {
        "notifications": true
      }
    }
  }
}

// Deep get
pref = deep_get(data, "customer.profile.preferences.notifications")  // true

// Deep set (creates path if needed)
updated = deep_set(data, "customer.profile.preferences.theme", "dark")

// Deep merge
overlay = {"customer": {"profile": {"name": "John"}}}
merged = deep_merge(data, overlay)
// Merges while preserving existing nested values
```

### Path Query Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `query(data, path_expr)` | `any, string → list<any>` | Query with path expression |
| `query_first(data, path_expr)` | `any, string → any` | First matching result |
| `query_paths(data, path_expr)` | `any, string → list<string>` | Get matching paths |

#### Examples

```xform
orders = {
  "items": [
    {"product": "A", "qty": 2, "price": 10},
    {"product": "B", "qty": 1, "price": 25},
    {"product": "C", "qty": 3, "price": 5}
  ]
}

// Query all prices
prices = query(orders, "items[*].price")  // [10, 25, 5]

// Query with filter
expensive = query(orders, "items[?(@.price > 10)]")
// [{"product":"B", "qty":1, "price":25}]

// First match
first_expensive = query_first(orders, "items[?(@.price > 10)]")
// {"product":"B", "qty":1, "price":25}
```

### Structure Transformation

| Function | Signature | Description |
|----------|-----------|-------------|
| `transform(data, mapping)` | `any, transform_spec → any` | Apply transformation mapping |
| `project(data, projection)` | `any, projection_spec → any` | Project to new structure |
| `reshape(data, shape)` | `any, shape_spec → any` | Reshape structure |

#### Transform Specification

```xform
// Mapping specification
transform_spec = {
  "target_field": "source.path",
  "another": "other.path",
  "computed": expr("source.a + source.b")
}

// Apply transformation
source = {"user": {"name": "John", "age": 30}, "score": 85}
result = transform(source, {
  "full_name": "user.name",
  "user_age": "user.age",
  "rating": expr("score / 10")
})
// {"full_name": "John", "user_age": 30, "rating": 8.5}
```

---

## Schema-Aware Operations

### Schema Validation

| Function | Signature | Description |
|----------|-----------|-------------|
| `validate_schema(data, schema_ref)` | `any, schema → validation_result` | Validate against schema |
| `is_valid(data, schema_ref)` | `any, schema → boolean` | Check validity |
| `coerce_to_schema(data, schema_ref)` | `any, schema → any` | Coerce types to match schema |

#### Examples

```xform
// Validate against L2 schema
result = validate_schema(event, transaction_schema)
// Returns: {valid: true/false, errors: [...]}

// Simple check
if is_valid(event, transaction_schema):
  process(event)
else:
  route_to_dlq(event)

// Type coercion
raw = {"amount": "123.45", "count": "5"}
typed = coerce_to_schema(raw, expected_schema)
// {"amount": 123.45, "count": 5}
```

### Schema Introspection

| Function | Signature | Description |
|----------|-----------|-------------|
| `schema_fields(schema_ref)` | `schema → list<field_info>` | Get field definitions |
| `schema_field_type(schema_ref, path)` | `schema, string → string` | Get field type |
| `schema_required_fields(schema_ref)` | `schema → list<string>` | Get required fields |

---

## Format Conversion

### Serialization Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `to_json(data)` | `any → string` | Serialize to JSON string |
| `from_json(json_string)` | `string → any` | Parse JSON string |
| `to_json_pretty(data)` | `any → string` | Serialize to formatted JSON |

**Note**: These are format-specific helpers. The core structured data functions work with in-memory representations regardless of serialization format.

### Binary Format Hints

For Avro, Protobuf, etc., the serialization is handled at the L5 infrastructure layer. Within transforms, you work with the deserialized in-memory representation:

```xform
// These work identically whether source is JSON, Avro, or Protobuf
customer_name = field_get(event, "customer.name")
updated = field_set(event, "processed", true)
```

---

## Performance Considerations

### Efficient Patterns

```xform
// GOOD: Single deep access
value = deep_get(data, "a.b.c.d.e")

// AVOID: Multiple navigations to same parent
// BAD:
a = field_get(data, "customer.profile.name")
b = field_get(data, "customer.profile.email")
c = field_get(data, "customer.profile.phone")

// BETTER: Extract parent once
profile = field_get(data, "customer.profile")
a = field_get(profile, "name")
b = field_get(profile, "email")
c = field_get(profile, "phone")
```

### Immutability Note

All modification functions return new structures. The original is unchanged:

```xform
original = {"a": 1}
modified = field_set(original, "b", 2)
// original is still {"a": 1}
// modified is {"a": 1, "b": 2}
```

This enables safe parallel processing and caching.

---

## Related Documents

- [builtin-functions.md](./builtin-functions.md) - Core function library
- [transform-syntax.md](./transform-syntax.md) - Transform syntax
- [../L2/type-system.md](../L2/type-system.md) - Type system and schemas
- [../L2-Schema-Registry.md](../L2-Schema-Registry.md) - Schema definitions
