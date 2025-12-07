# L3: Domain-Specific Functions

> **Source**: Native Nexflow specification
> **Status**: Complete Specification
> **Domain**: Credit Card Processing

---

## Overview

Domain-specific functions provide specialized operations for credit card processing workflows. These functions encapsulate industry-standard calculations, validation logic, and risk assessment patterns.

**Categories**:
- **Card Operations**: PAN validation, masking, network identification
- **Financial Calculations**: Interest, fees, payments, utilization
- **Risk Assessment**: Velocity, distance, scoring utilities
- **Compliance**: PCI-DSS helpers, regulatory calculations

---

## Card Operations

### PAN (Primary Account Number) Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `luhn_validate(pan)` | `string → boolean` | Validate card number using Luhn algorithm |
| `luhn_checksum(pan)` | `string → integer` | Calculate Luhn checksum digit |
| `mask_pan(pan)` | `string → string` | Mask PAN showing first 6 and last 4 |
| `mask_pan_custom(pan, show_first, show_last, mask_char)` | `string, integer, integer, string → string` | Custom PAN masking |
| `extract_bin(pan)` | `string → string` | Extract BIN/IIN (first 6-8 digits) |
| `extract_last_four(pan)` | `string → string` | Extract last 4 digits |
| `pan_length(pan)` | `string → integer` | Get PAN length (excluding spaces/dashes) |

#### Examples

```xform
// Validate card number
is_valid = luhn_validate("4532015112830366")  // true

// Mask for display
masked = mask_pan("4532015112830366")  // "453201******0366"

// Custom masking
custom_masked = mask_pan_custom("4532015112830366", 4, 4, "X")  // "4532XXXXXXXX0366"

// Extract components
bin = extract_bin("4532015112830366")  // "453201"
last_four = extract_last_four("4532015112830366")  // "0366"
```

### Card Network Identification

| Function | Signature | Description |
|----------|-----------|-------------|
| `identify_card_network(pan)` | `string → string` | Identify card network from BIN |
| `is_visa(pan)` | `string → boolean` | Check if Visa card |
| `is_mastercard(pan)` | `string → boolean` | Check if Mastercard |
| `is_amex(pan)` | `string → boolean` | Check if American Express |
| `is_discover(pan)` | `string → boolean` | Check if Discover |
| `is_diners(pan)` | `string → boolean` | Check if Diners Club |
| `is_jcb(pan)` | `string → boolean` | Check if JCB |
| `is_unionpay(pan)` | `string → boolean` | Check if UnionPay |

#### Network Identification Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                    Card Network BIN Ranges                       │
├─────────────────────────────────────────────────────────────────┤
│  Visa          │ 4xxx xxxx xxxx xxxx (13, 16, 19 digits)        │
│  Mastercard    │ 51-55xx, 2221-2720 (16 digits)                 │
│  Amex          │ 34xx, 37xx (15 digits)                         │
│  Discover      │ 6011, 644-649, 65xx (16-19 digits)             │
│  Diners Club   │ 300-305, 36, 38 (14-19 digits)                 │
│  JCB           │ 3528-3589 (16-19 digits)                       │
│  UnionPay      │ 62xx (16-19 digits)                            │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
network = identify_card_network("4532015112830366")  // "visa"

// Network-specific logic
fee_rate = when is_amex(card_number): 0.035
           when is_visa(card_number) or is_mastercard(card_number): 0.025
           otherwise: 0.030
```

### Card Expiration Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse_expiry(exp_string)` | `string → date` | Parse expiry (MM/YY or MMYY) |
| `is_expired(exp_date)` | `date → boolean` | Check if card expired |
| `is_expiring_soon(exp_date, days)` | `date, integer → boolean` | Expiring within N days |
| `months_until_expiry(exp_date)` | `date → integer` | Months until expiration |
| `format_expiry(exp_date)` | `date → string` | Format as MM/YY |

#### Examples

```xform
expiry = parse_expiry("12/25")  // 2025-12-31

expired = is_expired(expiry)  // false (assuming current date before Dec 2025)

expiring_soon = is_expiring_soon(expiry, 90)  // true if within 90 days

formatted = format_expiry(expiry)  // "12/25"
```

---

## Financial Calculations

### Interest Calculations

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_daily_interest(principal, apr)` | `decimal, decimal → decimal` | Daily interest amount |
| `calculate_monthly_interest(principal, apr)` | `decimal, decimal → decimal` | Monthly interest amount |
| `calculate_interest_for_period(principal, apr, days)` | `decimal, decimal, integer → decimal` | Interest for N days |
| `calculate_apr_from_daily(daily_rate)` | `decimal → decimal` | Convert daily rate to APR |
| `calculate_daily_from_apr(apr)` | `decimal → decimal` | Convert APR to daily rate |
| `calculate_effective_apr(nominal_apr, compounds_per_year)` | `decimal, integer → decimal` | Effective annual rate |

#### Interest Calculation Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                    Interest Calculation Methods                  │
├─────────────────────────────────────────────────────────────────┤
│  Daily Rate        │ APR / 365                                  │
│  Monthly Rate      │ APR / 12                                   │
│  Daily Interest    │ Balance × (APR / 365)                      │
│  Monthly Interest  │ Balance × (APR / 12)                       │
│  Period Interest   │ Balance × (APR / 365) × Days               │
│  Effective APR     │ (1 + APR/n)^n - 1                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
// Daily interest on $1000 at 18% APR
daily_interest = calculate_daily_interest(1000.00, 0.18)  // 0.49 (approx)

// Interest for billing period (30 days)
period_interest = calculate_interest_for_period(1500.00, 0.18, 30)  // 22.19

// Effective APR with monthly compounding
effective = calculate_effective_apr(0.18, 12)  // 0.1956 (19.56%)
```

### Fee Calculations

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_late_fee(balance, days_overdue, fee_schedule)` | `decimal, integer, fee_schedule → decimal` | Late payment fee |
| `calculate_overlimit_fee(balance, credit_limit, fee_amount)` | `decimal, decimal, decimal → decimal` | Over-limit fee |
| `calculate_cash_advance_fee(amount, pct_fee, min_fee, max_fee)` | `decimal, decimal, decimal, decimal → decimal` | Cash advance fee |
| `calculate_foreign_transaction_fee(amount, fee_pct)` | `decimal, decimal → decimal` | Foreign transaction fee |
| `calculate_balance_transfer_fee(amount, pct_fee, min_fee)` | `decimal, decimal, decimal → decimal` | Balance transfer fee |
| `calculate_annual_fee(fee_amount, months_active)` | `decimal, integer → decimal` | Prorated annual fee |

#### Fee Schedule Type

```xform
// Fee schedule definition (typically from L2 schema or L5 config)
type fee_schedule = object
  base_fee: decimal
  tiered_fees: list<object>
    min_days: integer
    max_days: integer
    fee: decimal
  end
  max_fee: decimal
  first_offense_waiver: boolean
end
```

#### Examples

```xform
// Late fee with tiered schedule
late_fee = calculate_late_fee(
  balance: 2500.00,
  days_overdue: 15,
  fee_schedule: late_fee_schedule
)  // Returns fee based on schedule

// Cash advance fee: 5% with $10 min, $50 max
cash_fee = calculate_cash_advance_fee(200.00, 0.05, 10.00, 50.00)  // 10.00

// Foreign transaction fee: 3%
fx_fee = calculate_foreign_transaction_fee(150.00, 0.03)  // 4.50
```

### Payment Calculations

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_minimum_payment(balance, min_pct, min_amount, interest, fees)` | `decimal, decimal, decimal, decimal, decimal → decimal` | Minimum payment due |
| `calculate_payoff_months(balance, apr, monthly_payment)` | `decimal, decimal, decimal → integer` | Months to pay off balance |
| `calculate_payoff_interest(balance, apr, monthly_payment)` | `decimal, decimal, decimal → decimal` | Total interest if paying minimum |
| `calculate_statement_balance(previous, payments, purchases, interest, fees)` | `decimal, decimal, decimal, decimal, decimal → decimal` | Statement balance |
| `apply_payment_allocation(payment, balances, allocation_method)` | `decimal, balance_set, string → balance_set` | Allocate payment to balances |

#### Payment Allocation Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                    Payment Allocation Methods                    │
├─────────────────────────────────────────────────────────────────┤
│  highest_apr_first  │ Pay highest APR balances first (default)  │
│  lowest_balance     │ Pay smallest balances first               │
│  proportional       │ Distribute proportionally across balances │
│  fifo               │ Pay oldest balances first                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
// Minimum payment: greater of 2% of balance or $25, plus interest and fees
min_payment = calculate_minimum_payment(
  balance: 3500.00,
  min_pct: 0.02,
  min_amount: 25.00,
  interest: 52.50,
  fees: 0.00
)  // 122.50 (70.00 principal + 52.50 interest)

// Payoff calculation
months = calculate_payoff_months(5000.00, 0.18, 150.00)  // 44 months
total_interest = calculate_payoff_interest(5000.00, 0.18, 150.00)  // ~1600.00
```

### Credit Utilization

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_utilization(balance, credit_limit)` | `decimal, decimal → decimal` | Utilization percentage (0-100) |
| `calculate_available_credit(credit_limit, balance, pending)` | `decimal, decimal, decimal → decimal` | Available credit |
| `is_overlimit(balance, credit_limit)` | `decimal, decimal → boolean` | Check if over limit |
| `utilization_tier(utilization_pct)` | `decimal → string` | Utilization risk tier |
| `recommended_utilization_target(credit_limit)` | `decimal → decimal` | Target balance for good utilization |

#### Utilization Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│                    Utilization Risk Tiers                        │
├─────────────────────────────────────────────────────────────────┤
│  0-10%     │ excellent  │ Optimal for credit score              │
│  10-30%    │ good       │ Healthy utilization                   │
│  30-50%    │ fair       │ Moderate risk signal                  │
│  50-75%    │ high       │ Elevated risk indicator               │
│  75-100%   │ critical   │ Near or at limit                      │
│  >100%     │ overlimit  │ Over credit limit                     │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
utilization = calculate_utilization(2500.00, 10000.00)  // 25.0

available = calculate_available_credit(10000.00, 2500.00, 150.00)  // 7350.00

tier = utilization_tier(utilization)  // "good"

target = recommended_utilization_target(10000.00)  // 3000.00 (30%)
```

---

## Risk Assessment Functions

### Velocity Analysis

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_velocity_score(count, window_hours, threshold)` | `integer, integer, integer → decimal` | Velocity risk score (0-100) |
| `is_velocity_breach(count, window_hours, threshold)` | `integer, integer, integer → boolean` | Check if threshold exceeded |
| `velocity_percentile(count, avg_count, stddev)` | `integer, decimal, decimal → decimal` | Percentile vs. normal behavior |
| `burst_detection_score(recent_count, historical_avg)` | `integer, decimal → decimal` | Burst pattern detection |

#### Examples

```xform
// Velocity score: 5 transactions in 1 hour, threshold of 3
velocity = calculate_velocity_score(5, 1, 3)  // 66.67

// Check breach
is_breach = is_velocity_breach(5, 1, 3)  // true

// Burst detection: 8 txns in last hour vs avg of 2
burst_score = burst_detection_score(8, 2.0)  // High score indicating anomaly
```

### Geographic Risk

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_distance_km(lat1, lon1, lat2, lon2)` | `decimal, decimal, decimal, decimal → decimal` | Haversine distance |
| `calculate_distance_miles(lat1, lon1, lat2, lon2)` | `decimal, decimal, decimal, decimal → decimal` | Distance in miles |
| `is_impossible_travel(distance_km, time_hours)` | `decimal, decimal → boolean` | Impossible travel detection |
| `travel_velocity_kmh(distance_km, time_hours)` | `decimal, decimal → decimal` | Required travel speed |
| `is_high_risk_country(country_code, high_risk_list)` | `string, list<string> → boolean` | Check high-risk country |
| `country_risk_score(country_code, risk_config)` | `string, risk_config → decimal` | Country risk score |

#### Geographic Risk Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                    Impossible Travel Detection                   │
├─────────────────────────────────────────────────────────────────┤
│  Travel Speed > 1000 km/h  │ Impossible (faster than commercial │
│                            │ aircraft typical ground speed)     │
│  Travel Speed > 500 km/h   │ Highly suspicious                  │
│  Travel Speed > 200 km/h   │ Suspicious (fast car/train)        │
│  Travel Speed < 200 km/h   │ Possible                           │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
// Distance between New York and Los Angeles
distance = calculate_distance_km(40.7128, -74.0060, 34.0522, -118.2437)  // ~3935 km

// Impossible travel check: 3935 km in 2 hours
impossible = is_impossible_travel(3935.0, 2.0)  // true (requires 1967 km/h)

// Travel velocity
velocity = travel_velocity_kmh(3935.0, 2.0)  // 1967.5 km/h

// Country risk
is_risky = is_high_risk_country("NG", ["NG", "RU", "CN", "UA"])  // true
```

### Merchant Risk

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_high_risk_mcc(mcc_code, high_risk_list)` | `string, list<string> → boolean` | Check high-risk MCC |
| `mcc_risk_score(mcc_code, risk_config)` | `string, mcc_config → decimal` | MCC risk score |
| `mcc_category(mcc_code)` | `string → string` | Get MCC category name |
| `is_gambling_mcc(mcc_code)` | `string → boolean` | Check if gambling MCC |
| `is_cash_equivalent_mcc(mcc_code)` | `string → boolean` | Check if cash-like MCC |
| `is_high_chargeback_mcc(mcc_code)` | `string → boolean` | High chargeback category |

#### High-Risk MCC Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    High-Risk MCC Codes                           │
├─────────────────────────────────────────────────────────────────┤
│  Gambling/Gaming     │ 7995, 7800, 7801, 7802                   │
│  Cash Equivalent     │ 6051, 6211, 6540 (quasi-cash)            │
│  High Chargeback     │ 5967 (telemarketing), 5966 (outbound)    │
│  Money Transfer      │ 4829, 6012                               │
│  Crypto              │ 6051 (when crypto merchant)              │
│  Adult               │ 5967 (adult content)                     │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
// Check high-risk MCC
is_risky_mcc = is_high_risk_mcc("7995", high_risk_mcc_list)  // true (gambling)

// MCC category
category = mcc_category("5411")  // "Grocery Stores, Supermarkets"

// Specific checks
is_gambling = is_gambling_mcc("7995")  // true
is_cash_equiv = is_cash_equivalent_mcc("6051")  // true
```

### Behavioral Risk

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_odd_hours(timestamp, start_hour, end_hour, timezone)` | `timestamp, integer, integer, string → boolean` | Odd hours check |
| `is_weekend(timestamp, timezone)` | `timestamp, string → boolean` | Weekend transaction |
| `is_holiday(date, holiday_list)` | `date, list<date> → boolean` | Holiday transaction |
| `dormancy_days(last_activity_date)` | `date → integer` | Days since last activity |
| `is_dormant_account(last_activity_date, threshold_days)` | `date, integer → boolean` | Account dormancy check |
| `pattern_deviation_score(value, avg, stddev)` | `decimal, decimal, decimal → decimal` | Z-score deviation |

#### Examples

```xform
// Odd hours: 2 AM - 5 AM local time
is_odd = is_odd_hours(transaction_timestamp, 2, 5, "America/New_York")

// Weekend check
is_wknd = is_weekend(transaction_timestamp, "America/New_York")

// Dormancy
dormant_days = dormancy_days(last_activity)  // e.g., 45
is_dormant = is_dormant_account(last_activity, 30)  // true if >30 days

// Deviation from normal (z-score)
deviation = pattern_deviation_score(2500.00, 150.00, 75.00)  // 31.33 (extreme)
```

---

## Composite Risk Scoring

### Risk Score Calculation

| Function | Signature | Description |
|----------|-----------|-------------|
| `weighted_risk_score(scores, weights)` | `list<decimal>, list<decimal> → decimal` | Weighted average score |
| `normalize_score(raw_score, min, max)` | `decimal, decimal, decimal → decimal` | Normalize to 0-100 |
| `risk_level_from_score(score, thresholds)` | `decimal, threshold_config → string` | Score to risk level |
| `combine_risk_factors(factors)` | `list<risk_factor> → risk_summary` | Combine multiple factors |

#### Risk Level Thresholds

```xform
// Standard threshold configuration
type threshold_config = object
  low_max: decimal      // e.g., 30
  medium_max: decimal   // e.g., 60
  high_max: decimal     // e.g., 80
  // > high_max = critical
end
```

#### Examples

```xform
// Weighted risk score
component_scores = [25.0, 60.0, 40.0, 15.0]  // velocity, amount, geo, behavioral
component_weights = [0.25, 0.30, 0.25, 0.20]
overall = weighted_risk_score(component_scores, component_weights)  // 36.75

// Risk level
level = risk_level_from_score(36.75, thresholds)  // "medium"

// Normalize raw score
normalized = normalize_score(750.0, 0.0, 1000.0)  // 75.0
```

---

## Currency and Amount Functions

### Currency Validation

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_valid_currency_code(code)` | `string → boolean` | Validate ISO 4217 code |
| `currency_decimal_places(code)` | `string → integer` | Decimal places for currency |
| `is_zero_decimal_currency(code)` | `string → boolean` | Check if zero-decimal (JPY, etc.) |
| `format_currency(amount, code)` | `decimal, string → string` | Format with symbol |
| `currency_symbol(code)` | `string → string` | Get currency symbol |

#### Zero-Decimal Currencies

```
┌─────────────────────────────────────────────────────────────────┐
│                    Zero-Decimal Currencies                       │
├─────────────────────────────────────────────────────────────────┤
│  JPY (Japanese Yen)        │ No decimal places                  │
│  KRW (Korean Won)          │ No decimal places                  │
│  VND (Vietnamese Dong)     │ No decimal places                  │
│  CLP (Chilean Peso)        │ No decimal places                  │
│  ISK (Icelandic Krona)     │ No decimal places                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
is_valid = is_valid_currency_code("USD")  // true
is_valid = is_valid_currency_code("XXX")  // false

decimals = currency_decimal_places("USD")  // 2
decimals = currency_decimal_places("JPY")  // 0

formatted = format_currency(1234.56, "USD")  // "$1,234.56"
formatted = format_currency(1234, "JPY")  // "¥1,234"
```

### Amount Validation

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_valid_amount(amount, currency)` | `decimal, string → boolean` | Validate amount for currency |
| `round_to_currency(amount, currency)` | `decimal, string → decimal` | Round to currency precision |
| `amount_in_minor_units(amount, currency)` | `decimal, string → integer` | Convert to minor units (cents) |
| `amount_from_minor_units(units, currency)` | `integer, string → decimal` | Convert from minor units |

#### Examples

```xform
// Validate (USD should have max 2 decimal places)
is_valid = is_valid_amount(123.456, "USD")  // false
is_valid = is_valid_amount(123.45, "USD")  // true

// Round to currency precision
rounded = round_to_currency(123.456, "USD")  // 123.46
rounded = round_to_currency(123.6, "JPY")  // 124

// Minor units
cents = amount_in_minor_units(123.45, "USD")  // 12345
yen = amount_in_minor_units(1234, "JPY")  // 1234

amount = amount_from_minor_units(12345, "USD")  // 123.45
```

---

## Compliance Functions

### PCI-DSS Helpers

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_pci_compliant_log(message)` | `string → boolean` | Check if safe to log (no PAN) |
| `sanitize_for_logging(data)` | `any → any` | Remove sensitive data for logging |
| `hash_pan(pan, salt)` | `string, string → string` | One-way hash of PAN |
| `tokenize_pan(pan, format)` | `string, string → string` | Format-preserving tokenization |

### Regulatory Calculations

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_regulation_e_liability(amount, days_to_report)` | `decimal, integer → decimal` | Reg E consumer liability |
| `is_within_dispute_window(transaction_date, dispute_type)` | `date, string → boolean` | Check dispute eligibility |
| `calculate_chargeback_deadline(transaction_date, network)` | `date, string → date` | Chargeback filing deadline |

#### Regulation E Liability Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                    Regulation E Liability                        │
├─────────────────────────────────────────────────────────────────┤
│  Reported within 2 days    │ Max $50 liability                  │
│  Reported within 60 days   │ Max $500 liability                 │
│  Reported after 60 days    │ Unlimited liability                │
└─────────────────────────────────────────────────────────────────┘
```

#### Examples

```xform
// Consumer liability calculation
liability = calculate_regulation_e_liability(5000.00, 5)  // 50.00 (reported within 2 days)
liability = calculate_regulation_e_liability(5000.00, 45)  // 500.00 (within 60 days)

// Dispute window check
can_dispute = is_within_dispute_window(transaction_date, "fraud")  // depends on date

// Chargeback deadline
deadline = calculate_chargeback_deadline(transaction_date, "visa")  // transaction_date + 120 days
```

---

## Function Purity

All domain functions are categorized by purity:

| Category | Purity | Notes |
|----------|--------|-------|
| Card Operations | Pure | Deterministic string operations |
| Financial Calculations | Pure | Deterministic math |
| Risk Assessment | Pure | Deterministic scoring |
| Currency Functions | Pure | Static reference data |
| Compliance Functions | Mixed | Some require external lookups |

**Pure functions** can be:
- Cached aggressively
- Executed in parallel
- Used in windowed aggregations

**Impure functions** must be:
- Marked with `pure: false` in transforms
- Called with appropriate caching configuration

---

## Related Documents

- [builtin-functions.md](./builtin-functions.md) - Core function library
- [transform-syntax.md](./transform-syntax.md) - Using functions in transforms
- [../L4/decision-tables.md](../L4/decision-tables.md) - Using functions in decision tables
- [../L4/procedural-rules.md](../L4/procedural-rules.md) - Using functions in rules
