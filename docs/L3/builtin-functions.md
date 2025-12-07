# L3: Builtin Functions

> **Source**: Adapted from rules_engine + Native Nexflow
> **Status**: Complete Specification

---

## Overview

Builtin functions provide the standard library for Nexflow transforms.

### Core Categories (This Document)

- **Math Functions**: Numeric calculations
- **String Functions**: Text manipulation
- **Date/Time Functions**: Temporal operations
- **Type Conversion Functions**: Type casting
- **Collection Functions**: List/array operations
- **Null Handling Functions**: Null-safe operations
- **Conditional Functions**: Control flow
- **UUID Functions**: Identifier generation

### Extended Function Libraries

| Document | Categories | Description |
|----------|------------|-------------|
| [domain-functions.md](./domain-functions.md) | Card Operations, Financial Calculations, Risk Assessment, Compliance | Credit card domain-specific functions |
| [window-functions.md](./window-functions.md) | Window Aggregates, Running Calculations, Window Navigation | Streaming CEP functions for stateful computations |
| [structured-data-functions.md](./structured-data-functions.md) | Record Operations, Array Operations, Map Operations, Path Queries | Format-agnostic structured data manipulation |

```
┌─────────────────────────────────────────────────────────────────┐
│                    L3 Function Library Architecture              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              builtin-functions.md (Core)                 │    │
│  │  Math │ String │ DateTime │ TypeConv │ Collection │ Null │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│          ┌───────────────────┼───────────────────┐               │
│          ▼                   ▼                   ▼               │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐      │
│  │ domain-       │   │ window-       │   │ structured-   │      │
│  │ functions.md  │   │ functions.md  │   │ data-         │      │
│  │               │   │               │   │ functions.md  │      │
│  │ • Card Ops    │   │ • Aggregates  │   │ • Records     │      │
│  │ • Financial   │   │ • Running     │   │ • Arrays      │      │
│  │ • Risk        │   │ • Navigation  │   │ • Maps        │      │
│  │ • Compliance  │   │ • Windowing   │   │ • Path Query  │      │
│  └───────────────┘   └───────────────┘   └───────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Math Functions

### Basic Arithmetic

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `abs(n)` | `decimal → decimal` | Absolute value | `abs(-5)` → `5` |
| `round(n, d)` | `decimal, integer → decimal` | Round to d decimals | `round(3.14159, 2)` → `3.14` |
| `floor(n)` | `decimal → integer` | Round down | `floor(3.7)` → `3` |
| `ceil(n)` | `decimal → integer` | Round up | `ceil(3.2)` → `4` |
| `truncate(n, d)` | `decimal, integer → decimal` | Truncate to d decimals | `truncate(3.999, 2)` → `3.99` |

### Comparison

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `min(a, b, ...)` | `decimal... → decimal` | Minimum value | `min(5, 3, 8)` → `3` |
| `max(a, b, ...)` | `decimal... → decimal` | Maximum value | `max(5, 3, 8)` → `8` |
| `clamp(v, lo, hi)` | `decimal, decimal, decimal → decimal` | Clamp to range | `clamp(15, 0, 10)` → `10` |

### Advanced Math

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `power(b, e)` | `decimal, decimal → decimal` | Exponentiation | `power(2, 3)` → `8` |
| `sqrt(n)` | `decimal → decimal` | Square root | `sqrt(16)` → `4` |
| `log(n)` | `decimal → decimal` | Natural logarithm | `log(2.718)` → `1` |
| `log10(n)` | `decimal → decimal` | Base-10 logarithm | `log10(100)` → `2` |
| `mod(a, b)` | `integer, integer → integer` | Modulo | `mod(17, 5)` → `2` |

### Percentage

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `percent(part, whole)` | `decimal, decimal → decimal` | Calculate percentage | `percent(25, 100)` → `25.0` |
| `percent_of(pct, value)` | `decimal, decimal → decimal` | Apply percentage | `percent_of(10, 200)` → `20` |
| `percent_change(old, new)` | `decimal, decimal → decimal` | Percent change | `percent_change(100, 120)` → `20` |

### Financial

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `compound_interest(p, r, n, t)` | `decimal, decimal, integer, integer → decimal` | Compound interest | `compound_interest(1000, 0.05, 12, 1)` |
| `simple_interest(p, r, t)` | `decimal, decimal, decimal → decimal` | Simple interest | `simple_interest(1000, 0.05, 1)` → `50` |
| `annualize(rate, periods)` | `decimal, integer → decimal` | Annualize rate | `annualize(0.01, 12)` |

---

## String Functions

### Basic Operations

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `length(s)` | `string → integer` | String length | `length("hello")` → `5` |
| `concat(s1, s2, ...)` | `string... → string` | Concatenate | `concat("a", "b")` → `"ab"` |
| `substring(s, start, len)` | `string, integer, integer → string` | Extract substring | `substring("hello", 0, 3)` → `"hel"` |
| `left(s, n)` | `string, integer → string` | Left n characters | `left("hello", 2)` → `"he"` |
| `right(s, n)` | `string, integer → string` | Right n characters | `right("hello", 2)` → `"lo"` |

### Case Conversion

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `upper(s)` | `string → string` | Uppercase | `upper("hello")` → `"HELLO"` |
| `lower(s)` | `string → string` | Lowercase | `lower("HELLO")` → `"hello"` |
| `title_case(s)` | `string → string` | Title Case | `title_case("john doe")` → `"John Doe"` |
| `capitalize(s)` | `string → string` | First char upper | `capitalize("hello")` → `"Hello"` |

### Trimming

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `trim(s)` | `string → string` | Remove whitespace | `trim("  hi  ")` → `"hi"` |
| `trim_left(s)` | `string → string` | Left trim | `trim_left("  hi")` → `"hi"` |
| `trim_right(s)` | `string → string` | Right trim | `trim_right("hi  ")` → `"hi"` |

### Search and Replace

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `contains(s, sub)` | `string, string → boolean` | Contains substring | `contains("hello", "ell")` → `true` |
| `starts_with(s, pre)` | `string, string → boolean` | Starts with prefix | `starts_with("hello", "he")` → `true` |
| `ends_with(s, suf)` | `string, string → boolean` | Ends with suffix | `ends_with("hello", "lo")` → `true` |
| `index_of(s, sub)` | `string, string → integer` | Find position (-1 if not found) | `index_of("hello", "l")` → `2` |
| `replace(s, old, new)` | `string, string, string → string` | Replace all | `replace("hello", "l", "L")` → `"heLLo"` |
| `replace_first(s, old, new)` | `string, string, string → string` | Replace first | `replace_first("hello", "l", "L")` → `"heLlo"` |

### Pattern Matching

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `matches(s, pattern)` | `string, string → boolean` | Regex match | `matches("abc123", "^[a-z]+[0-9]+$")` → `true` |
| `regex_replace(s, pat, repl)` | `string, string, string → string` | Regex replace | `regex_replace("abc123", "[0-9]", "X")` → `"abcXXX"` |
| `regex_extract(s, pat, grp)` | `string, string, integer → string` | Extract group | `regex_extract("abc123", "([a-z]+)", 1)` → `"abc"` |

### Splitting and Joining

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `split(s, delim)` | `string, string → list<string>` | Split by delimiter | `split("a,b,c", ",")` → `["a","b","c"]` |
| `join(list, delim)` | `list<string>, string → string` | Join with delimiter | `join(["a","b"], ",")` → `"a,b"` |

### Padding

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `pad_left(s, len, ch)` | `string, integer, string → string` | Left pad | `pad_left("42", 5, "0")` → `"00042"` |
| `pad_right(s, len, ch)` | `string, integer, string → string` | Right pad | `pad_right("hi", 5, " ")` → `"hi   "` |

---

## Date/Time Functions

### Current Time

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `now()` | `→ timestamp` | Current timestamp | `now()` → `2024-01-15T10:30:00Z` |
| `today()` | `→ date` | Current date | `today()` → `2024-01-15` |
| `current_year()` | `→ integer` | Current year | `current_year()` → `2024` |
| `current_month()` | `→ integer` | Current month | `current_month()` → `1` |

### Extraction

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `year(d)` | `date/timestamp → integer` | Extract year | `year("2024-06-15")` → `2024` |
| `month(d)` | `date/timestamp → integer` | Extract month | `month("2024-06-15")` → `6` |
| `day(d)` | `date/timestamp → integer` | Extract day | `day("2024-06-15")` → `15` |
| `hour(t)` | `timestamp → integer` | Extract hour | `hour("2024-01-15T14:30:00")` → `14` |
| `minute(t)` | `timestamp → integer` | Extract minute | `minute("2024-01-15T14:30:00")` → `30` |
| `second(t)` | `timestamp → integer` | Extract second | `second("2024-01-15T14:30:45")` → `45` |
| `day_of_week(d)` | `date → integer` | Day of week (1=Mon) | `day_of_week("2024-01-15")` → `1` |
| `day_of_year(d)` | `date → integer` | Day of year | `day_of_year("2024-02-01")` → `32` |

### Arithmetic

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `add_days(d, n)` | `date, integer → date` | Add days | `add_days("2024-01-15", 5)` → `"2024-01-20"` |
| `add_months(d, n)` | `date, integer → date` | Add months | `add_months("2024-01-15", 2)` → `"2024-03-15"` |
| `add_years(d, n)` | `date, integer → date` | Add years | `add_years("2024-01-15", 1)` → `"2025-01-15"` |
| `add_hours(t, n)` | `timestamp, integer → timestamp` | Add hours | `add_hours(now(), 2)` |
| `add_minutes(t, n)` | `timestamp, integer → timestamp` | Add minutes | `add_minutes(now(), 30)` |

### Difference

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `date_diff(d1, d2, unit)` | `date, date, string → integer` | Difference in units | `date_diff("2024-01-15", "2024-01-10", "days")` → `5` |
| `days_between(d1, d2)` | `date, date → integer` | Days between | `days_between("2024-01-15", "2024-01-10")` → `5` |
| `months_between(d1, d2)` | `date, date → integer` | Months between | `months_between("2024-06-15", "2024-01-15")` → `5` |
| `years_between(d1, d2)` | `date, date → integer` | Years between | `years_between("2024-01-15", "2020-01-15")` → `4` |

### Formatting

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `format_date(d, fmt)` | `date, string → string` | Format date | `format_date("2024-01-15", "MM/DD/YYYY")` → `"01/15/2024"` |
| `format_timestamp(t, fmt)` | `timestamp, string → string` | Format timestamp | `format_timestamp(now(), "YYYY-MM-DD HH:mm")` |

**Format Patterns**:
- `YYYY` - 4-digit year
- `YY` - 2-digit year
- `MM` - 2-digit month
- `DD` - 2-digit day
- `HH` - 2-digit hour (24h)
- `hh` - 2-digit hour (12h)
- `mm` - 2-digit minute
- `ss` - 2-digit second
- `SSS` - milliseconds

### Parsing

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `parse_date(s, fmt)` | `string, string → date` | Parse date | `parse_date("01/15/2024", "MM/DD/YYYY")` |
| `parse_timestamp(s, fmt)` | `string, string → timestamp` | Parse timestamp | `parse_timestamp("2024-01-15 14:30", "YYYY-MM-DD HH:mm")` |

### Comparison

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `is_before(d1, d2)` | `date, date → boolean` | d1 before d2 | `is_before("2024-01-10", "2024-01-15")` → `true` |
| `is_after(d1, d2)` | `date, date → boolean` | d1 after d2 | `is_after("2024-01-15", "2024-01-10")` → `true` |
| `is_same_day(d1, d2)` | `date, date → boolean` | Same day | `is_same_day("2024-01-15", "2024-01-15")` → `true` |

### Truncation

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `start_of_day(t)` | `timestamp → timestamp` | Midnight | `start_of_day(now())` → `2024-01-15T00:00:00Z` |
| `end_of_day(t)` | `timestamp → timestamp` | End of day | `end_of_day(now())` → `2024-01-15T23:59:59Z` |
| `start_of_month(d)` | `date → date` | First of month | `start_of_month("2024-01-15")` → `"2024-01-01"` |
| `end_of_month(d)` | `date → date` | Last of month | `end_of_month("2024-01-15")` → `"2024-01-31"` |

---

## Type Conversion Functions

### Numeric Conversions

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `to_integer(v)` | `any → integer` | Convert to integer | `to_integer("42")` → `42` |
| `to_decimal(v)` | `any → decimal` | Convert to decimal | `to_decimal("3.14")` → `3.14` |
| `to_string(v)` | `any → string` | Convert to string | `to_string(42)` → `"42"` |
| `to_boolean(v)` | `any → boolean` | Convert to boolean | `to_boolean("true")` → `true` |

### Safe Parsing

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `parse_int(s)` | `string → integer, nullable` | Safe parse int | `parse_int("abc")` → `null` |
| `parse_decimal(s)` | `string → decimal, nullable` | Safe parse decimal | `parse_decimal("3.14")` → `3.14` |
| `parse_boolean(s)` | `string → boolean, nullable` | Safe parse boolean | `parse_boolean("yes")` → `true` |

### Type Checking

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `is_number(v)` | `any → boolean` | Check if numeric | `is_number("42")` → `false` |
| `is_string(v)` | `any → boolean` | Check if string | `is_string("hello")` → `true` |
| `is_date(v)` | `any → boolean` | Check if valid date | `is_date("2024-01-15")` → `true` |
| `type_of(v)` | `any → string` | Get type name | `type_of(42)` → `"integer"` |

---

## Collection Functions

### List Operations

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `size(list)` | `list<any> → integer` | List size | `size([1,2,3])` → `3` |
| `first(list)` | `list<any> → any` | First element | `first([1,2,3])` → `1` |
| `last(list)` | `list<any> → any` | Last element | `last([1,2,3])` → `3` |
| `get(list, idx)` | `list<any>, integer → any` | Get by index | `get([1,2,3], 1)` → `2` |
| `contains(list, val)` | `list<any>, any → boolean` | Contains value | `contains([1,2,3], 2)` → `true` |

### Aggregation

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `sum(list)` | `list<decimal> → decimal` | Sum of values | `sum([1,2,3])` → `6` |
| `avg(list)` | `list<decimal> → decimal` | Average | `avg([1,2,3])` → `2` |
| `min_of(list)` | `list<decimal> → decimal` | Minimum | `min_of([1,2,3])` → `1` |
| `max_of(list)` | `list<decimal> → decimal` | Maximum | `max_of([1,2,3])` → `3` |
| `count(list)` | `list<any> → integer` | Count elements | `count([1,2,3])` → `3` |
| `count_where(list, cond)` | `list<any>, condition → integer` | Count matching | `count_where(items, amount > 100)` |

### Transformation

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `map(list, expr)` | `list<any>, expression → list<any>` | Transform each | `map(amounts, it * 2)` |
| `filter(list, cond)` | `list<any>, condition → list<any>` | Filter by condition | `filter(items, amount > 100)` |
| `sort(list)` | `list<any> → list<any>` | Sort ascending | `sort([3,1,2])` → `[1,2,3]` |
| `sort_desc(list)` | `list<any> → list<any>` | Sort descending | `sort_desc([3,1,2])` → `[3,2,1]` |
| `distinct(list)` | `list<any> → list<any>` | Remove duplicates | `distinct([1,2,2,3])` → `[1,2,3]` |
| `flatten(list)` | `list<list<any>> → list<any>` | Flatten nested | `flatten([[1,2],[3]])` → `[1,2,3]` |

---

## Null Handling Functions

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `is_null(v)` | `any → boolean` | Check if null | `is_null(null)` → `true` |
| `is_not_null(v)` | `any → boolean` | Check if not null | `is_not_null(42)` → `true` |
| `coalesce(v1, v2, ...)` | `any... → any` | First non-null | `coalesce(null, null, 42)` → `42` |
| `null_if(v, cmp)` | `any, any → any` | Null if equal | `null_if(0, 0)` → `null` |
| `if_null(v, default)` | `any, any → any` | Default if null | `if_null(null, 0)` → `0` |
| `empty_to_null(s)` | `string → string` | Empty string to null | `empty_to_null("")` → `null` |
| `null_to_empty(s)` | `string → string` | Null to empty string | `null_to_empty(null)` → `""` |

---

## Conditional Functions

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `if(cond, then, else)` | `boolean, any, any → any` | Conditional | `if(x > 0, "positive", "non-positive")` |
| `case_when(...)` | `(cond, val)... → any` | Multiple conditions | See example below |
| `switch(v, ...)` | `any, (match, val)... → any` | Value matching | See example below |

### Case-When Example

```xform
tier = case_when(
  credit_score >= 800, "excellent",
  credit_score >= 700, "good",
  credit_score >= 600, "fair",
  true, "poor"
)
```

### Switch Example

```xform
description = switch(status,
  "A", "Active",
  "P", "Pending",
  "C", "Closed",
  "Unknown"  // default
)
```

---

## UUID Functions

| Function | Signature | Description | Example |
|----------|-----------|-------------|---------|
| `uuid()` | `→ uuid` | Generate UUID | `uuid()` → `"550e8400-..."` |
| `uuid_from_string(s)` | `string → uuid` | Parse UUID | `uuid_from_string("550e8400-...")` |
| `uuid_to_string(u)` | `uuid → string` | UUID to string | `uuid_to_string(id)` |

---

## Related Documents

### Core Documentation
- [expression-patterns.md](./expression-patterns.md) - Using functions in expressions
- [transform-syntax.md](./transform-syntax.md) - Transform declaration
- [validation-patterns.md](./validation-patterns.md) - Validation functions

### Extended Function Libraries
- [domain-functions.md](./domain-functions.md) - Credit card domain-specific functions
- [window-functions.md](./window-functions.md) - Streaming window and aggregate functions
- [structured-data-functions.md](./structured-data-functions.md) - Format-agnostic data manipulation
