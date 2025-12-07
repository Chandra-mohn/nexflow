# Nexflow File Organization Specification

> **Layer**: Cross-cutting
> **Status**: Draft
> **Version**: 0.1.0
> **Last Updated**: 2025-11-28

---

## 1. Overview

### 1.1 File Extensions by Layer

Nexflow uses **5 distinct file extensions**, one per specification layer:

| Extension | Layer | Purpose | Primary Owner |
|-----------|-------|---------|---------------|
| `.proc` | L1 | Process Orchestration | Data Engineering |
| `.schema` | L2 | Schema Registry | Data Governance |
| `.xform` | L3 | Transform Catalog | Data Engineering |
| `.rules` | L4 | Business Rules | Business/Risk Team |
| `.infra` | L5 | Infrastructure Binding | Platform/DevOps |

> **Note**: L6 (Compilation Pipeline) is not a DSL — it's the compiler that consumes L1-L5.

### 1.2 Design Rationale

**Team Ownership**: Different enterprise teams own different layers. Separate extensions enable:
- Access control by file type
- Targeted code review workflows
- Skill-appropriate tooling
- Audit and compliance tracking
- Independent deployment pipelines

**Railroad-Towns Metaphor**:
- `.proc` files are the **railroad** (orchestration)
- `.schema`, `.xform`, `.rules` files are the **towns** (domain components)
- `.infra` files are the **track configuration** (infrastructure bindings)

---

## 2. File Type Specifications

### 2.1 Process Files (`.proc`)

**Layer**: L1 - Process Orchestration
**Owner**: Data Engineering Team
**Purpose**: Define streaming/batch data processing pipelines

```
// authorization_enrichment.proc

process authorization_enrichment
  parallelism hint 128
  partition by card_id
  time by event_timestamp watermark delay 5 seconds

  receive events from auth_events
    schema auth_event_schema
    project transaction_id, card_id, amount, merchant_id, event_timestamp

  enrich using customers on card_id
    select customer_name, credit_limit, risk_tier

  transform using normalize_amount
  route using fraud_detection_rules

  emit to enriched_auths
end
```

**Characteristics**:
- References L2 schemas by name (`schema auth_event_schema`)
- References L3 transforms by name (`transform using normalize_amount`)
- References L4 rules by name (`route using fraud_detection_rules`)
- Contains orchestration logic only, no business rule details

---

### 2.2 Schema Files (`.schema`)

**Layer**: L2 - Schema Registry
**Owner**: Data Governance Team
**Purpose**: Define data structures, types, and mutation patterns

```
// auth_event.schema

schema auth_event_schema
  version 1.0
  mutation_pattern immutable_ledger

  fields
    transaction_id: uuid [primary_key]
    card_id: string [length: 16]
    amount: decimal [precision: 2]
    currency: currency_code
    merchant_id: string
    merchant_category: mcc_code
    event_timestamp: timestamp [watermark_field]
    location: string
  end

  streaming
    key_fields card_id
    time_field event_timestamp
    watermark_delay 5 seconds
  end
end
```

**Characteristics**:
- Defines field types and constraints
- Specifies mutation pattern (from 9 patterns)
- Contains streaming annotations (key fields, watermark hints)
- No business logic, pure data structure

---

### 2.3 Transform Files (`.xform`)

**Layer**: L3 - Transform Catalog
**Owner**: Data Engineering Team
**Purpose**: Define reusable data transformations and calculations

```
// currency_transforms.xform

transform normalize_amount
  description "Convert transaction amount to USD"

  input
    amount: decimal
    currency: currency_code
  end

  output
    amount_usd: decimal
  end

  implementation
    lookup exchange_rate from currency_rates on currency
    calculate amount_usd = amount * exchange_rate
  end
end

transform calculate_risk_score
  description "Compute transaction risk score"

  input
    amount: decimal
    merchant_category: mcc_code
    customer_risk_tier: string
  end

  output
    risk_score: integer [range: 0..100]
  end

  implementation
    // Transform logic
  end
end
```

**Characteristics**:
- Typed input/output signatures
- Reusable across multiple processes
- May reference L2 schemas for type validation
- Contains calculation logic, not routing logic

---

### 2.4 Rules Files (`.rules`)

**Layer**: L4 - Business Rules
**Owner**: Business/Risk Team
**Purpose**: Define business logic, routing decisions, and compliance rules

```
// fraud_detection.rules

// Decision Table Style
decision_table fraud_screening
  hit_policy first_match

  conditions
    amount_usd: range
    merchant_category: in_set
    customer_risk_tier: equals
  end

  actions
    route_to: assign
    flag_reason: assign
  end

  rules
    | amount_usd  | merchant_category     | customer_risk_tier | route_to     | flag_reason       |
    |-------------|----------------------|-------------------|--------------|-------------------|
    | > 10000     | *                    | *                 | manual_review| high_value        |
    | *           | ["7995","5933"]      | *                 | block        | high_risk_mcc     |
    | > 1000      | *                    | "high"            | flag_review  | risk_tier_amount  |
    | *           | *                    | *                 | approve      | null              |
  end
end

// Procedural Rule Style
rule velocity_check
  if transaction.count_1h > customer.max_hourly_transactions
     and transaction.amount_1h > customer.hourly_spending_limit
  then temporaryBlock

  if transaction.count_24h > 50
     or transaction.amount_24h > customer.daily_limit * 2
  then flagForReview
end
```

**Characteristics**:
- Two styles: decision tables and procedural rules
- Business-readable syntax
- No infrastructure concerns
- Auditable for compliance

---

### 2.5 Infrastructure Files (`.infra`)

**Layer**: L5 - Infrastructure Binding
**Owner**: Platform/DevOps Team
**Purpose**: Map logical names to physical resources

```yaml
# production.infra (YAML-based for tooling compatibility)

environment: production
version: 1.0

streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}
    partitions: 128
    replication: 3

  enriched_auths:
    type: kafka
    topic: prod.auth.enriched.v3
    brokers: ${KAFKA_BROKERS}
    partitions: 64

lookups:
  customers:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers
    read_preference: secondaryPreferred

  currency_rates:
    type: redis
    uri: ${REDIS_URI}
    key_pattern: "fx:rate:{currency}"

checkpoints:
  auth_checkpoints:
    type: s3
    bucket: company-checkpoints
    prefix: auth/enrichment/

resources:
  authorization_enrichment:
    parallelism: 128
    task_memory: 4gb
    task_cpu: 2
```

**Characteristics**:
- YAML format (standard for infrastructure)
- Environment-specific (dev, staging, prod)
- Contains secrets references (not actual secrets)
- Resource sizing hints

---

## 3. Directory Structure

### 3.1 Recommended Project Layout

```
credit-card-processing/
├── processes/                    # L1: .proc files
│   ├── authorization/
│   │   ├── enrichment.proc
│   │   ├── routing.proc
│   │   └── settlement.proc
│   └── fraud/
│       ├── detection.proc
│       └── investigation.proc
│
├── schemas/                      # L2: .schema files
│   ├── events/
│   │   ├── auth_event.schema
│   │   ├── settlement_event.schema
│   │   └── fraud_alert.schema
│   └── entities/
│       ├── customer.schema
│       ├── card_account.schema
│       └── merchant.schema
│
├── transforms/                   # L3: .xform files
│   ├── currency/
│   │   └── currency_transforms.xform
│   ├── risk/
│   │   └── risk_scoring.xform
│   └── validation/
│       └── field_validation.xform
│
├── rules/                        # L4: .rules files
│   ├── fraud/
│   │   ├── fraud_detection.rules
│   │   └── velocity_limits.rules
│   ├── authorization/
│   │   ├── approval_rules.rules
│   │   └── decline_rules.rules
│   └── compliance/
│       └── regulatory_checks.rules
│
├── infra/                        # L5: .infra files
│   ├── development.infra
│   ├── staging.infra
│   └── production.infra
│
└── compiled/                     # L6: Generated output
    ├── flink-sql/
    ├── udfs/
    └── deployment/
```

### 3.2 Team Repository Model (Alternative)

For large organizations, separate repositories per layer:

```
org/nexflow-processes      # Data Engineering owns
org/nexflow-schemas        # Data Governance owns
org/nexflow-transforms     # Data Engineering owns
org/nexflow-rules          # Business/Risk owns
org/nexflow-infra          # Platform owns
```

---

## 4. Team Ownership Matrix

### 4.1 RACI by File Type

| Activity | `.proc` | `.schema` | `.xform` | `.rules` | `.infra` |
|----------|---------|-----------|----------|----------|----------|
| **Create** | Data Eng | Data Gov | Data Eng | Business | Platform |
| **Modify** | Data Eng | Data Gov | Data Eng | Business | Platform |
| **Review** | Data Eng + Arch | Data Gov + Arch | Data Eng | Business + Risk | Platform + Security |
| **Approve** | Tech Lead | Data Steward | Tech Lead | Business Owner | Platform Lead |
| **Deploy** | Data Eng | Automated | Automated | Automated | Platform |

### 4.2 Access Control Recommendations

| Team | `.proc` | `.schema` | `.xform` | `.rules` | `.infra` |
|------|---------|-----------|----------|----------|----------|
| Data Engineering | Read/Write | Read | Read/Write | Read | Read |
| Data Governance | Read | Read/Write | Read | Read | None |
| Business Analysts | None | Read | None | Read/Write | None |
| Risk/Compliance | None | Read | None | Read/Write | None |
| Platform/DevOps | Read | Read | Read | Read | Read/Write |
| Security | Read | Read | Read | Read | Read/Audit |

---

## 5. Tooling Requirements

### 5.1 IDE Support (Future)

Each file type should have:
- Syntax highlighting
- Auto-completion for keywords
- Reference validation (e.g., `.proc` referencing `.schema`)
- Error diagnostics

### 5.2 CLI Commands

```bash
# Validate all files
procdsl validate ./

# Validate specific layer
procdsl validate --layer schema ./schemas/

# Compile process with all dependencies
procdsl compile ./processes/authorization/enrichment.proc \
  --schemas ./schemas/ \
  --transforms ./transforms/ \
  --rules ./rules/ \
  --infra ./infra/production.infra

# Generate dependency graph
procdsl deps ./processes/authorization/enrichment.proc
```

### 5.3 CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Nexflow Validation

on:
  pull_request:
    paths:
      - 'processes/**/*.proc'
      - 'schemas/**/*.schema'
      - 'transforms/**/*.xform'
      - 'rules/**/*.rules'
      - 'infra/**/*.infra'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate Schemas
        if: contains(github.event.pull_request.changed_files, '.schema')
        run: procdsl validate --layer schema ./schemas/

      - name: Validate Rules
        if: contains(github.event.pull_request.changed_files, '.rules')
        run: procdsl validate --layer rules ./rules/

      - name: Full Compilation Test
        run: procdsl compile --dry-run ./processes/
```

---

## 6. Cross-Reference Resolution

### 6.1 Reference Syntax

```
// In .proc files:
schema <schema_name>           // References L2
transform using <xform_name>   // References L3
route using <rules_name>       // References L4

// Resolved at compile time by L6 compiler
```

### 6.2 Resolution Order

1. **Local directory** (same folder as .proc file)
2. **Layer-specific directory** (`./schemas/`, `./transforms/`, `./rules/`)
3. **Configured search paths** (from compiler config)
4. **Error** if not found

### 6.3 Versioning

```
// Explicit version reference
schema auth_event_schema@1.2

// Latest version (default)
schema auth_event_schema
```

---

## 7. Migration from Single-File

If starting with a monolithic design, split by:

1. Extract schema definitions → `.schema` files
2. Extract transform logic → `.xform` files
3. Extract business rules → `.rules` files
4. Extract infra config → `.infra` files
5. Keep orchestration → `.proc` files

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-11-28 | - | Initial specification |
