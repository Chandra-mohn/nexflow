# Nexflow: Architecture Decision Record

> **Document Version**: 1.0
> **Status**: Draft - Brainstorming Phase
> **Last Updated**: 2025-01-XX
> **Authors**: Chandra Mohn

---

## Executive Summary

Nexflow is a Domain-Specific Language framework for defining multi-stage Complex Event Processing (CEP) pipelines in the credit card domain. The architecture follows a **Railroad-First** philosophy where a core orchestration DSL defines universal processing semantics, while domain-specific components ("towns") plug into this infrastructure through well-defined contracts.

### Scale Requirements
- **Input Volume**: 1 billion records per processing window
- **Output Volume**: 20-22 billion records (20x+ fan-out)
- **Processing Window**: 2 hours
- **Record Size**: ~1 MB per record, ~5000 fields
- **Data Structure**: Nested JSON hierarchies
- **Concurrent Stages**: ~50 stages running continuously

### Technology Stack
- **Streaming**: Apache Kafka
- **Stream Processing**: Apache Flink
- **Batch Processing**: Apache Spark
- **Persistence**: MongoDB

---

## Part 1: Problem Domain Analysis

### 1.1 Processing Characteristics

#### Record Fan-Out Patterns
The 1B → 20B+ expansion occurs through:

| Pattern | Description | Example |
|---------|-------------|---------|
| **Normalization** | One record splits into multiple collection documents | Authorization → Account, Transaction, Merchant documents |
| **Ledger Explosion** | One transaction generates multiple ledger entries | Purchase → Debit, Credit, Fee, Interest entries |
| **Multi-Perspective** | Same event written to multiple contexts | Transaction → Risk view, Compliance view, Analytics view |

#### Event Types
- **MON (Monetary)**: Financial transactions affecting balances
- **NON-MON (Non-Monetary)**: Profile changes, address updates, preference modifications
- **Triggered**: NON-MON events that trigger MON transactions (e.g., address change triggers card reissue fee)

#### Data Characteristics
| Characteristic | Value | Implication |
|----------------|-------|-------------|
| Fields per record | ~5000 | Cannot define inline; must reference schemas |
| Record size | ~1 MB | Memory optimization critical |
| Structure | Nested JSON | Path-based field selection needed |
| Sparsity | Mixed | Some subtrees dense, others sparse |
| Schema stability | Controlled evolution | Version management required |

### 1.2 Processing Topology

- **Shape**: Directed Acyclic Graph (DAG), not linear
- **Stages**: ~50 concurrent processing stages
- **State Sharing**: Some stages share state (e.g., account balances)
- **Operation Mode**: Continuous (runs throughout the day)
- **Branches**: DAG includes fan-out (one source → many destinations) and fan-in (many sources → one destination)

---

## Part 2: Architectural Philosophy

### 2.1 The Railroad Metaphor

We adopt a **Railroad-First** development philosophy, analogous to US Western expansion where railroad infrastructure was built first, and towns developed around it with consistent interfaces.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAILROAD-FIRST PHILOSOPHY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  THE RAILROAD (Core DSL)                                        │
│  ════════════════════════                                       │
│  • Defines universal data flow semantics                        │
│  • Specifies stage contracts (how components connect)           │
│  • Establishes routing protocols                                │
│  • Provides error handling patterns                             │
│  • Ensures observability across all stages                      │
│                                                                 │
│  THE TOWNS (Domain Components)                                  │
│  ═════════════════════════════                                  │
│  • Plug into the railroad via standard contracts                │
│  • Define domain-specific logic (credit card rules)             │
│  • Can be built by different teams independently                │
│  • Interoperate because they follow railroad standards          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Why Railroad-First for This Domain

| Domain Characteristic | Why Railroad-First |
|----------------------|-------------------|
| Extreme scale (1B→22B) | Predictable data flow patterns, not ad-hoc connections |
| Complex DAG (50 stages) | Well-defined interchange format between stages |
| Multi-runtime (Kafka+Flink+Spark+MongoDB) | Abstraction layer unifying heterogeneous systems |
| Continuous operation | Reliable, debuggable, observable infrastructure |
| Regulated domain (credit cards) | Auditable, versioned, traceable transformations |

### 2.3 Key Architectural Insight

> **The DSL IS the railroad.**
>
> The core orchestration DSL defines the "tracks" — the universal protocol for how data flows, how stages connect, how errors propagate, how state is shared.
>
> The "towns" (schemas, transforms, rules, bindings) are **REFERENCED** by the DSL but not **DEFINED** by it.

---

## Part 3: Layered Architecture

### 3.1 Complete Layer Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Nexflow COMPLETE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ L1: PROCESS ORCHESTRATION DSL (The Railroad)                    │   │
│  │     • DAG topology definition                                   │   │
│  │     • Stage sequencing & routing                                │   │
│  │     • State sharing declarations                                │   │
│  │     • Error handling & checkpoints                              │   │
│  │     • References L2-L4 by name/URI                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │ references                               │
│          ┌───────────────────┼───────────────────┐                     │
│          ▼                   ▼                   ▼                     │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐            │
│  │ L2: SCHEMA    │   │ L3: TRANSFORM │   │ L4: BUSINESS  │            │
│  │    REGISTRY   │   │    CATALOG    │   │    RULES      │            │
│  │               │   │               │   │               │            │
│  │ • Field defs  │   │ • Field maps  │   │ • WHEN/THEN   │            │
│  │ • Hierarchies │   │ • Expressions │   │ • Decision    │            │
│  │ • Types       │   │ • Transform   │   │   tables      │            │
│  │ • Versions    │   │   blocks      │   │ • Formulas    │            │
│  │               │   │               │   │               │            │
│  │ [EXISTING:    │   │ [EXISTING:    │   │ [EXISTING:    │            │
│  │  To integrate]│   │  Excel-based  │   │  Business     │            │
│  │               │   │  attribute    │   │  Rules DSL]   │            │
│  │               │   │  mapping]     │   │               │            │
│  └───────────────┘   └───────────────┘   └───────────────┘            │
│          │                   │                   │                     │
│          └───────────────────┼───────────────────┘                     │
│                              ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ L4B: SERVICE DOMAIN DEFINITIONS                                 │   │
│  │      • Data persistence patterns                                │   │
│  │      • Functions/methods exposed as service operations          │   │
│  │      • [EXISTING: Service Domain DSL]                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│                              ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ L5: INFRASTRUCTURE BINDING                                      │   │
│  │     • Kafka topic mappings                                      │   │
│  │     • Flink job configurations                                  │   │
│  │     • Spark cluster assignments                                 │   │
│  │     • MongoDB collection bindings                               │   │
│  │     • Environment-specific (dev/staging/prod)                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ════════════════════════════════════════════════════════════════════  │
│                         COMPILATION TARGET                              │
│  ════════════════════════════════════════════════════════════════════  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ RUNTIME: Flink Jobs + Spark Jobs + Kafka Streams                │   │
│  │          (compiled, optimized, deployed)                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Existing Assets Integration

| Asset | Type | Integration Strategy |
|-------|------|---------------------|
| **Business Rules DSL** | Town DSL | Called by orchestration layer via `apply_rules: rules://rule-set-name` |
| **Excel Attribute Mappings** | Pseudo-DSL | Imported into Transform Catalog, versioned, referenced as transform blocks |
| **Service Domain Definitions** | Town DSL | Exposed as sink operations, referenced via `sink: service://operation-name` |

### 3.3 Layer Responsibilities

#### L1: Process Orchestration DSL (The Railroad)
**Owns:**
- Pipeline/DAG topology definitions
- Stage sequencing and dependencies
- Routing rules between stages
- State sharing declarations
- Error handling policies
- Checkpoint/recovery semantics
- Observability contracts

**References (does not own):**
- Schema definitions (by URI)
- Transform specifications (by catalog ID)
- Business rules (by rule set name)
- Infrastructure bindings (by logical name)

#### L2: Schema Registry
**Owns:**
- Field definitions and types
- Nested hierarchy structures
- Schema versions and evolution
- Field groups (reusable projections)
- Sparsity hints for optimization

**Sources:**
- Avro/JSON Schema definitions
- MongoDB collection schemas
- Generated from existing systems

#### L3: Transform Catalog
**Owns:**
- Field-level transforms (rename, coerce)
- Expression-level transforms (derivations)
- Block-level transforms (grouped operations)
- Parameterized transform templates
- Transform versioning

**Sources:**
- Reference database
- Excel imports (existing attribute mappings)
- Configuration files

#### L4: Business Rules Engine
**Owns:**
- WHEN/THEN conditional rules
- Decision tables
- Formula expressions
- Ledger explosion logic

**Note:** This is our **existing DSL** — the orchestration layer integrates with it.

#### L4B: Service Domain Definitions
**Owns:**
- Data persistence patterns
- Service operations (functions/methods)
- Domain entity definitions

**Note:** This is our **existing system** — exposed as sink targets for the orchestration layer.

#### L5: Infrastructure Binding
**Owns:**
- Logical-to-physical mappings
- Environment configurations
- Resource allocation hints
- Deployment topologies

---

## Part 4: Core Railroad Components

### 4.1 Record Envelope (The Rail Gauge)

Every piece of data flowing through the system has a universal structure:

```yaml
envelope:
  # Identity & Lineage
  correlation_id: string        # Unique ID for this record
  lineage_chain: string[]       # Parent record IDs (for fan-out tracking)

  # Metadata
  schema_ref: uri               # schema://schema-name-vX
  schema_version: semver        # e.g., "3.2.1"
  event_time: timestamp         # When the event occurred
  processing_time: timestamp    # When processed by this stage
  source_stage: string          # Which stage produced this

  # Routing
  target_stages: string[]       # Where this record should go next
  priority: enum                # HIGH, NORMAL, LOW
  partition_key: string         # For parallel processing

  # Payload
  data: object                  # The actual business data (conforms to schema_ref)

  # Observability
  trace_id: string              # Distributed tracing ID
  span_id: string               # Current span
```

### 4.2 Stage Contract (The Station Interface)

Every stage, regardless of implementation (Flink, Spark, custom), must conform to:

```yaml
stage_contract:
  # Declaration
  input:
    schemas: uri[]              # What schemas this stage consumes
    projection: projection_spec # Which fields are needed (optional)

  output:
    schemas: uri[]              # What schemas this stage produces
    routing: routing_spec       # How outputs are directed

  state:
    reads: state_ref[]          # Shared state this stage reads
    writes: state_ref[]         # Shared state this stage writes
    local: local_state_spec     # Stage-local state

  # Behavior
  error_handling:
    on_transform_error: policy  # dead_letter | skip | retry
    on_lookup_error: policy
    on_rule_error: policy

  checkpoint:
    interval: duration
    storage: uri

  # Observability
  metrics:
    - throughput
    - latency_p50
    - latency_p99
    - error_rate
  traces: enabled
  logs: structured
```

### 4.3 Routing Protocol (The Switching System)

```yaml
routing_protocol:
  # Named channels (not hardcoded topics)
  channels:
    - name: approved_authorizations
      type: stream
      # Physical binding resolved at deployment

  # Content-based routing
  rules:
    - condition: "risk_score < 0.7"
      target: approved_authorizations
    - condition: "risk_score >= 0.7 AND risk_score < 0.9"
      target: manual_review
    - default: declined

  # Fan-out semantics
  fan_out:
    type: broadcast | content_based | round_robin

  # Back-pressure
  back_pressure:
    strategy: block | drop_oldest | sample
    threshold: queue_depth | latency
```

### 4.4 Time Model (The Schedule System)

```yaml
time_model:
  # Time semantics
  event_time_field: "/envelope/event_time"
  processing_time: auto

  # Watermarks
  watermark:
    strategy: bounded_out_of_order
    max_delay: 5m

  # Late arrivals
  late_policy:
    allowed_lateness: 1h
    side_output: late_events

  # Windowing (when used)
  window:
    type: tumbling | sliding | session
    size: duration
    slide: duration           # for sliding only
    gap: duration             # for session only
```

### 4.5 Observability Contract (The Signal System)

```yaml
observability:
  metrics:
    namespace: "nexflow"
    labels:
      - pipeline
      - stage
      - schema_version
    standard:
      - records_in_total
      - records_out_total
      - records_error_total
      - processing_latency_seconds
      - state_size_bytes

  tracing:
    propagation: W3C_TRACE_CONTEXT
    sample_rate: 0.01           # 1% sampling

  logging:
    format: structured_json
    correlation: trace_id
    levels:
      normal: INFO
      error: ERROR
      debug: DEBUG              # enabled per-stage
```

---

## Part 5: Transform System

### 5.1 Transform Levels

#### Field-Level (Atomic)
```yaml
transform:
  type: rename
  id: T-0001
  source: /customer/name
  target: /account/holder_nm
```

#### Expression-Level (Derived)
```yaml
transform:
  type: derive
  id: T-0002
  expression: "credit_limit * utilization_rate"
  target: /calculated/current_balance
  inputs:
    - /account/credit_limit
    - /account/utilization_rate
```

#### Block-Level (Composite)
```yaml
transform_block:
  id: TB-2345
  name: account-normalization
  version: 3.2.1
  effective_date: 2024-01-15
  includes:
    - T-0001
    - T-0002
    - T-0003
    # ... through T-0050
```

#### Parameterized (Template)
```yaml
transform_template:
  id: T-TEMPLATE-001
  name: percentage_calc
  parameters:
    - field_a
    - field_b
    - result_field
  expression: "${field_a} / ${field_b} * 100"
  target: "${result_field}"

# Usage:
apply: T-TEMPLATE-001(credit_used, credit_limit, utilization_pct)
```

### 5.2 Transform Execution Semantics

**Supported modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Sequential** | T-001 → T-002 → T-003 (ordered) | When transforms depend on each other |
| **Parallel** | T-001, T-002, T-003 execute concurrently | Independent transforms for performance |
| **Dependency-Based** | Compiler determines order from declared dependencies | Complex transform graphs |

```yaml
transform_execution:
  mode: dependency_based
  transforms:
    - id: T-001
      depends_on: []
    - id: T-002
      depends_on: [T-001]      # Must run after T-001
    - id: T-003
      depends_on: []           # Can run parallel with T-001
```

### 5.3 Transform Sources

```yaml
transform_sources:
  reference_db:
    type: mongodb
    collection: transform_definitions
    sync: on_startup + watch

  excel_imports:
    type: excel
    path: /config/transforms/*.xlsx
    sync: daily_batch
    approval_required: true

  generated:
    type: schema_diff
    source_schema: v2
    target_schema: v3
    # Auto-generates renames for compatible changes
```

---

## Part 6: Schema Evolution & Versioning

### 6.1 Schema Evolution Strategy

| Change Type | Automation | Approval |
|-------------|------------|----------|
| **Compatible** (add optional field) | Auto-generate migration | Auto-approve |
| **Breaking** (remove field, type change) | Flag for review | Manual approval required |
| **Semantic** (meaning change) | Cannot auto-detect | Manual review required |

### 6.2 Version Coexistence

During schema transitions, support running v2 and v3 pipelines in parallel:

```yaml
pipeline: auth_processing
version_strategy:
  mode: parallel
  versions:
    - schema: auth-v2
      stages: [auth-v2-enrich, auth-v2-ledger]
      sunset_date: 2024-06-01
    - schema: auth-v3
      stages: [auth-v3-enrich, auth-v3-ledger]

  routing:
    # Route based on incoming schema version
    - condition: "schema_version.startsWith('2.')"
      pipeline: v2
    - condition: "schema_version.startsWith('3.')"
      pipeline: v3
```

### 6.3 Transform Versioning

```yaml
stage: enrichment
transform: catalog://auth-enrichment-T2345

# Version selection options:
version: 3.2.1                      # Explicit version (recommended for prod)
version: latest                     # Always newest (for dev/test)
version: effective(2024-03-15)      # Version active on specific date
version: compatible(3.x)            # Latest compatible with major version
```

---

## Part 7: Validation & Testing

### 7.1 Testing Levels

| Level | Scope | Automation |
|-------|-------|------------|
| **Unit Tests** | Individual transforms | Automated, CI/CD |
| **Contract Tests** | Schema compatibility | Automated, CI/CD |
| **Integration Tests** | Stage-to-stage flow | Automated, CI/CD |
| **Shadow Mode** | Full pipeline comparison | Production parallel run |

### 7.2 Unit Test Specification

```yaml
transform_test:
  transform: T-0002
  cases:
    - name: "normal calculation"
      input:
        credit_limit: 10000
        utilization_rate: 0.5
      expected:
        current_balance: 5000

    - name: "zero utilization"
      input:
        credit_limit: 10000
        utilization_rate: 0
      expected:
        current_balance: 0

    - name: "null handling"
      input:
        credit_limit: null
        utilization_rate: 0.5
      expected:
        current_balance: null
      # or: expected_error: "null_input"
```

### 7.3 Contract Tests

```yaml
contract_test:
  stage: enrichment

  input_contract:
    schema: auth-request-v3
    required_fields:
      - /account/id
      - /transaction/amount

  output_contract:
    schema: enriched-auth-v3
    guaranteed_fields:
      - /enriched/credit_score
      - /enriched/risk_tier
```

### 7.4 Shadow Mode

```yaml
shadow_deployment:
  production_pipeline: auth-processing-v2
  shadow_pipeline: auth-processing-v3

  comparison:
    sample_rate: 0.01          # Compare 1% of records
    fields_to_compare:
      - /output/risk_score
      - /output/decision
    tolerance:
      numeric: 0.001           # Allow small floating point differences

  alerts:
    divergence_threshold: 0.05  # Alert if >5% records differ
```

---

## Part 8: Stage Anatomy (Draft)

### 8.1 Complete Stage Definition

```yaml
stage: authorization_enrichment

  # ═══ IDENTITY ═══
  id: STG-AUTH-001
  version: 2.1.0
  owner: payments-team

  # ═══ INPUT ═══
  input:
    source: stream://auth-requests
    schema: schema://auth-request-v3
    project:
      include:
        - group://account_identity
        - group://transaction_core
      exclude:
        - /internal/**

  # ═══ PROCESSING ═══
  enrich:
    - lookup: mongo://customers
      on: account_id
      select: [credit_score, risk_tier, preferences/*]

  transform:
    - block: catalog://auth-enrichment-TB2345
    - inline:
        derive: "available_credit = credit_limit - current_balance"

  apply_rules: rules://fraud-detection-v2

  # ═══ OUTPUT ═══
  output:
    - route: approved
      condition: "risk_score < 0.7"
      sink: stream://approved-auths
      schema: schema://enriched-auth-v3

    - route: review
      condition: "risk_score >= 0.7 AND risk_score < 0.9"
      sink: stream://manual-review

    - route: declined
      condition: "risk_score >= 0.9"
      sink: stream://declined-auths

  # ═══ STATE ═══
  state:
    uses: [account_balances]      # Shared state reference
    local:
      - name: daily_counts
        type: counter
        key: account_id

  # ═══ ERROR HANDLING ═══
  on_error:
    transform_failure: dead_letter://transform-errors
    lookup_failure: skip_enrichment
    rule_failure: dead_letter://rule-errors

  # ═══ CHECKPOINTING ═══
  checkpoint:
    interval: 5m
    storage: state://checkpoints/auth-enrichment
```

---

## Part 9: Domain Separation

### 9.1 Terminology Boundaries

| Orchestration DSL (Generic) | Credit Card Domain Model |
|----------------------------|--------------------------|
| stage, pipeline, route | authorization, settlement |
| transform, enrich, split | cardholder, merchant |
| sink, source, checkpoint | dispute, chargeback |
| state, window, trigger | MON, NON-MON, ledger |
| envelope, schema, routing | account, transaction |

### 9.2 Domain Model Location

Credit card terminology lives in:
- **Schema Registry**: Field names, types, hierarchies
- **Business Rules DSL**: Domain-specific conditions and actions
- **Service Domain Definitions**: Entity operations

The orchestration DSL remains **domain-agnostic**.

---

## Part 10: Flink Native Capability Assessment

This section documents Apache Flink's native support for Nexflow requirements, identifying what can be configured vs. what must be built. The goal is to **minimize custom code** by leveraging Flink's built-in capabilities.

### 10.1 Time Model (Section 4.4) - Flink Support

| Feature | Flink Support | DSL Work Required |
|---------|---------------|-------------------|
| **Event Time Extraction** | ✅ Native | Minimal mapping |
| **Watermark Strategies** | ✅ Native | Declarative config |
| **Late Data Handling** | ✅ Native | Declarative config |
| **Windowing (Tumbling/Sliding/Session)** | ✅ Native | Declarative config |
| **Idle Source Detection** | ✅ Native | Config option |

#### Flink Native Implementation

**Event Time & Watermarks (SQL DDL)**:
```sql
CREATE TABLE transactions (
  transaction_id STRING,
  amount DECIMAL(10,2),
  event_time TIMESTAMP(3),
  -- Declarative watermark with 5-second tolerance
  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (...);
```

**Windowing (SQL)**:
```sql
-- Tumbling window
SELECT TUMBLE_START(event_time, INTERVAL '10' MINUTE), COUNT(*)
FROM transactions
GROUP BY TUMBLE(event_time, INTERVAL '10' MINUTE);

-- Sliding window
SELECT HOP_START(event_time, INTERVAL '5' MINUTE, INTERVAL '10' MINUTE), SUM(amount)
FROM transactions
GROUP BY HOP(event_time, INTERVAL '5' MINUTE, INTERVAL '10' MINUTE);
```

**Late Data Handling (DataStream API)**:
```java
// Allowed lateness with side output for late events
OutputTag<Event> lateTag = new OutputTag<Event>("late") {};

SingleOutputStreamOperator<Event> result = stream
    .keyBy(...)
    .window(TumblingEventTimeWindows.of(Duration.ofMinutes(10)))
    .allowedLateness(Duration.ofHours(1))
    .sideOutputLateData(lateTag)
    .process(...);

DataStream<Event> lateStream = result.getSideOutput(lateTag);
```

#### DSL Implication

The DSL becomes a **thin declarative layer** that compiles to Flink SQL DDL:

```yaml
# DSL Declaration (what you write)
time_model:
  event_time: /transaction/timestamp
  watermark_delay: 5s
  allowed_lateness: 1h
  late_data: side_output://late-events
  idle_timeout: 10s

# Compiler generates Flink SQL DDL
```

### 10.2 Observability (Section 4.5) - Flink Support

| Feature | Flink Support | DSL Work Required |
|---------|---------------|-------------------|
| **Built-in Metrics** | ✅ Native (automatic) | None |
| **Metric Reporters** | ✅ Native (config) | Config only |
| **Custom Metrics** | ✅ Native (API) | Minimal code |
| **Distributed Tracing** | ⚠️ Partial (OTel) | Some integration |
| **Structured Logging** | ✅ Native (Log4j2) | Config only |

#### Built-in Metrics (Automatic)

Flink automatically collects:
- `numRecordsIn` / `numRecordsOut` (throughput)
- `numBytesIn` / `numBytesOut` (data volume)
- `currentInputWatermark` (time progress)
- `lastCheckpointDuration` (checkpoint health)
- `numLateRecordsDropped` (late data tracking)

#### Metric Reporters (Config Only)

```yaml
# flink-conf.yaml - generated by DSL compiler
metrics.reporter.prom.factory.class: org.apache.flink.metrics.prometheus.PrometheusReporterFactory
metrics.reporter.prom.port: 9249

metrics.reporter.datadog.factory.class: org.apache.flink.metrics.datadog.DatadogHttpReporterFactory
metrics.reporter.datadog.apikey: ${DATADOG_API_KEY}

metrics.reporter.otel.factory.class: org.apache.flink.metrics.otel.OpenTelemetryMetricReporterFactory
metrics.reporter.otel.exporter.endpoint: http://otel-collector:4317
metrics.reporter.otel.exporter.protocol: gRPC
```

**Supported reporters**: Prometheus, Datadog, StatsD, JMX, Slf4j, OpenTelemetry

#### DSL Implication

```yaml
# DSL Declaration
observability:
  metrics:
    reporters:
      - type: prometheus
        port: 9249
      - type: datadog
        api_key: ${DATADOG_API_KEY}
    custom:
      - name: records_enriched
        type: counter
      - name: enrichment_latency_ms
        type: histogram

  tracing:
    propagation: W3C_TRACE_CONTEXT
    sample_rate: 0.01

  logging:
    format: json
    correlation_field: trace_id

# Compiler generates flink-conf.yaml sections
```

### 10.3 Transform Execution (Section 5.2) - Flink Support

| Execution Mode | Flink Support | DSL Work Required |
|----------------|---------------|-------------------|
| **Sequential Transforms** | ✅ Native | Compilation |
| **Parallel Transforms** | ✅ Native (optimizer) | Compilation |
| **Dependency-Based** | ✅ Native (CTEs) | DAG analysis |
| **Expression Evaluation** | ✅ Native (SQL) | Code generation |
| **User-Defined Functions** | ✅ Native | Registration |

#### Flink Native Implementation

**Sequential (chained expressions)**:
```sql
SELECT func2(func1(col1)) AS derived FROM source
```

**Parallel (independent expressions)**:
```sql
-- Flink optimizer parallelizes independent columns
SELECT func1(a), func2(b), func3(c) FROM source
```

**Dependency-Based (CTEs)**:
```sql
WITH step1 AS (
  SELECT account_id, credit_limit * utilization_rate AS current_balance
  FROM accounts
),
step2 AS (
  SELECT account_id, current_balance, credit_limit - current_balance AS available_credit
  FROM step1 JOIN accounts USING (account_id)
)
SELECT * FROM step2
```

**User-Defined Functions**:
```sql
-- Register business rules as UDFs
CREATE FUNCTION calculate_risk AS 'com.company.rules.RiskCalculator';

SELECT account_id, calculate_risk(amount, merchant_category) AS risk_score
FROM transactions
```

#### DSL Implication

DSL compiler analyzes transform dependencies and generates optimized SQL:

```yaml
# DSL Declaration
transforms:
  execution: dependency_based
  steps:
    - id: T1
      derive: "credit_limit * utilization_rate"
      target: current_balance
    - id: T2
      depends_on: [T1]
      derive: "credit_limit - current_balance"
      target: available_credit
    - id: T3
      # No dependency - parallel with T1
      derive: "UPPER(customer_name)"
      target: normalized_name

# Compiler generates optimized Flink SQL with CTEs
```

### 10.4 Checkpointing & Recovery - Flink Support

| Feature | Flink Support | DSL Work Required |
|---------|---------------|-------------------|
| **State Backend** | ✅ Native (RocksDB/HashMap) | Config only |
| **Checkpoint Storage** | ✅ Native (S3/HDFS/local) | Config only |
| **Savepoints** | ✅ Native | Config only |
| **Recovery from Checkpoint** | ✅ Native | Config only |

#### Flink Native Implementation

```yaml
# flink-conf.yaml
state.backend.type: rocksdb
execution.checkpointing.storage: filesystem
execution.checkpointing.dir: s3://bucket/checkpoints

# Enable checkpointing
execution.checkpointing.interval: 5min
execution.checkpointing.externalized-checkpoint-retention: RETAIN_ON_CANCELLATION
```

### 10.5 Summary: Build vs. Configure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BUILD vs CONFIGURE MATRIX                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CAPABILITY              BUILD    CONFIG    FLINK NATIVE                │
│  ════════════════════════════════════════════════════════════════════   │
│                                                                         │
│  TIME MODEL                                                             │
│  Event time extraction      □         ■       ✅ SQL WATERMARK          │
│  Watermark strategy         □         ■       ✅ SQL WATERMARK          │
│  Late data handling         □         ■       ✅ allowedLateness        │
│  Late data side output      □         ■       ✅ sideOutputLateData     │
│  Windowing                  □         ■       ✅ SQL TUMBLE/HOP         │
│  Idle detection             □         ■       ✅ withIdleness           │
│                                                                         │
│  OBSERVABILITY                                                          │
│  Built-in metrics           □         □       ✅ Automatic              │
│  Metric reporters           □         ■       ✅ flink-conf.yaml        │
│  Custom metrics             ◐         □       ✅ Metric API             │
│  Distributed tracing        ◐         ◐       ⚠️ Partial (OTel)        │
│  Structured logging         □         ■       ✅ Log4j2 JSON            │
│                                                                         │
│  TRANSFORM EXECUTION                                                    │
│  Sequential transforms      □         □       ✅ SQL chaining           │
│  Parallel transforms        □         □       ✅ Optimizer              │
│  Dependency ordering        ◐         □       ✅ CTE / subqueries       │
│  Expression evaluation      □         □       ✅ SQL expressions        │
│  UDF registration           ◐         ■       ✅ CREATE FUNCTION        │
│                                                                         │
│  CHECKPOINTING                                                          │
│  State backend              □         ■       ✅ RocksDB/HashMap        │
│  Checkpoint storage         □         ■       ✅ S3/HDFS/local          │
│  Recovery                   □         ■       ✅ Native                 │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  Legend: ■ = Config only   □ = Zero work   ◐ = Minimal code/compile     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.6 Revised Compilation Strategy

Given Flink's comprehensive native support, the DSL compiler primarily generates:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 DSL COMPILATION ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DSL (YAML)                                                             │
│      │                                                                  │
│      ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ DSL COMPILER                                                    │   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ SQL          │  │ Config       │  │ UDF          │          │   │
│  │  │ Generator    │  │ Generator    │  │ Generator    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │         │                 │                 │                   │   │
│  └─────────┼─────────────────┼─────────────────┼───────────────────┘   │
│            │                 │                 │                        │
│            ▼                 ▼                 ▼                        │
│     ┌────────────┐   ┌────────────┐   ┌────────────┐                   │
│     │ Flink SQL  │   │ flink-conf │   │ Java UDFs  │                   │
│     │ DDL + DML  │   │ .yaml      │   │ (from biz  │                   │
│     │            │   │            │   │  rules DSL)│                   │
│     └────────────┘   └────────────┘   └────────────┘                   │
│            │                 │                 │                        │
│            └─────────────────┼─────────────────┘                        │
│                              ▼                                          │
│                    ┌─────────────────┐                                  │
│                    │ FLINK RUNTIME   │                                  │
│                    │ (native code    │                                  │
│                    │  + UDFs only)   │                                  │
│                    └─────────────────┘                                  │
│                                                                         │
│  Result: 90%+ of runtime is native Flink                               │
│          DSL generates SQL + config, not custom operators              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.7 What Must Be Built (Minimal)

| Component | Reason | Effort |
|-----------|--------|--------|
| **DSL Compiler** | Translate DSL → Flink SQL + config | Core work |
| **UDF Framework** | Host business rules as callable functions | Integration |
| **Envelope Handling** | Standardize record wrapper with trace_id | Small |
| **Trace Propagation** | Pass W3C headers through Kafka headers | Small |

### 10.8 Key Recommendations

1. **Prefer Flink SQL over DataStream API** - More declarative, better optimized
2. **Use SQL DDL for schemas** - Native watermark, type handling
3. **Compile business rules to UDFs** - Register via CREATE FUNCTION
4. **Configure, don't code** - Metrics, checkpointing, state backend all config-based
5. **Leverage Flink optimizer** - It handles parallelism automatically

---

## Part 11: Infrastructure Anatomy (The Railroad Components)

This section maps each technology in our stack to the railroad metaphor, defining their roles, responsibilities, and how they interconnect as the "tracks" of our processing infrastructure.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    RAILROAD INFRASTRUCTURE OVERVIEW                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                              ┌─────────────┐                                    │
│                              │   KAFKA     │                                    │
│                              │  (Tracks)   │                                    │
│                              └──────┬──────┘                                    │
│                                     │                                           │
│              ┌──────────────────────┼──────────────────────┐                   │
│              │                      │                      │                   │
│              ▼                      ▼                      ▼                   │
│     ┌─────────────┐        ┌─────────────┐        ┌─────────────┐             │
│     │   FLINK     │        │   SPARK     │        │  MONGODB    │             │
│     │ (Switching  │        │   (Freight  │        │  (Stations/ │             │
│     │   System)   │        │    Yards)   │        │   Depots)   │             │
│     └─────────────┘        └─────────────┘        └─────────────┘             │
│                                                                                 │
│  Legend:                                                                        │
│  • Kafka   = The tracks (data transport layer)                                 │
│  • Flink   = The switching system (real-time routing & processing)             │
│  • Spark   = The freight yards (batch processing & heavy transformations)      │
│  • MongoDB = The stations/depots (persistent storage & state)                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 11.1 Apache Kafka - The Tracks

Kafka serves as the **data transport layer** — the tracks upon which all data moves between processing stages.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           KAFKA AS THE TRACKS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  RAILROAD ANALOGY              KAFKA COMPONENT                                  │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│  Rail Lines                    Topics                                           │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Named pathways for data     • Logical channels for event streams            │
│  • Multiple parallel tracks    • Partitions enable parallelism                 │
│  • Dedicated routes            • Topic-per-stage or topic-per-domain           │
│                                                                                 │
│  Rail Gauge (standard width)   Record Format / Schema                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Universal compatibility     • Avro/JSON schema with registry                │
│  • Any train fits any track    • Any stage can consume standard envelope       │
│                                                                                 │
│  Track Switches                Consumer Groups                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Route trains to stations    • Route messages to processing stages           │
│  • Load balancing at junctions • Partition assignment for parallelism          │
│                                                                                 │
│  Train Cars                    Partitions                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Ordered sequence            • Ordered within partition                      │
│  • Batch transport             • Batch consumption for throughput              │
│                                                                                 │
│  Track Signals                 Offsets                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Track position              • Consumer position in stream                   │
│  • Prevent collisions          • Enable replay and exactly-once                │
│                                                                                 │
│  Maintenance Logs              Retention & Compaction                           │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Historical track records    • Time-based or size-based retention            │
│  • Audit trail                 • Log compaction for stateful topics            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Kafka Role in Nexflow

| DSL Concept | Kafka Implementation |
|-------------|---------------------|
| `stream://channel-name` | Kafka topic |
| `partition_key` in envelope | Kafka message key |
| Stage-to-stage routing | Topic-based pub/sub |
| Fan-out (broadcast) | Multiple consumer groups on same topic |
| Dead letter queue | Dedicated DLQ topic per stage |
| Replay/recovery | Consumer offset reset |

#### Kafka Configuration Pattern

```yaml
# DSL Declaration
channels:
  auth_requests:
    type: stream
    partitions: 128          # Scale for 1B records
    replication: 3
    retention: 7d

  enriched_auths:
    type: stream
    partitions: 128
    compaction: false

  account_state:
    type: changelog          # Compacted topic for state
    compaction: true
    retention: infinite

# Compiler generates topic configurations
```

#### Key Kafka Features for Nexflow

| Feature | Railroad Role | Nexflow Usage |
|---------|---------------|----------------|
| **Partitioning** | Parallel tracks | Scale to 1B records via partition-level parallelism |
| **Consumer Groups** | Route assignment | Each stage is a consumer group |
| **Exactly-Once** | Cargo integrity | Transactional producers + consumers |
| **Compaction** | State snapshots | Changelog topics for shared state |
| **Headers** | Cargo manifest | Trace IDs, schema version, routing hints |

---

### 11.2 Apache Flink - The Switching System

Flink serves as the **real-time switching and processing system** — making routing decisions, transforming data in motion, and managing state.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       FLINK AS THE SWITCHING SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  RAILROAD ANALOGY              FLINK COMPONENT                                  │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│  Switch Tower                  JobManager                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Central coordination        • Job scheduling and orchestration              │
│  • Route planning              • Checkpoint coordination                       │
│  • Failure detection           • Failure recovery management                   │
│                                                                                 │
│  Track Switches                Operators                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Route trains in real-time   • Filter, map, join, aggregate                  │
│  • Split/merge tracks          • Fan-out and fan-in operations                 │
│  • Conditional routing         • Content-based routing                         │
│                                                                                 │
│  Switch Operators              TaskManagers                                     │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Execute switching           • Execute operator logic                        │
│  • Local track sections        • Manage local state                            │
│  • Parallel workers            • Parallelism slots                             │
│                                                                                 │
│  Signal System                 Watermarks                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Time synchronization        • Event time progress tracking                  │
│  • Safe passage timing         • Window trigger decisions                      │
│                                                                                 │
│  Switch State Board            State Backend (RocksDB)                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Current switch positions    • Keyed state for aggregations                  │
│  • Train locations             • Window contents                               │
│  • Quick reference             • Fast local state access                       │
│                                                                                 │
│  Emergency Brakes              Checkpoints                                      │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Recovery points             • Consistent snapshots                          │
│  • Resume from safe state      • Exactly-once recovery                         │
│                                                                                 │
│  Dispatch Schedule             Event Time Processing                            │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Time-based operations       • Windowed aggregations                         │
│  • Scheduled actions           • Time-based triggers                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Flink Role in Nexflow

| DSL Concept | Flink Implementation |
|-------------|---------------------|
| `stage` definition | Flink SQL job or DataStream program |
| `transform` | SQL expressions or UDFs |
| `route` with condition | CASE expressions or ProcessFunction |
| `state.uses` | Keyed state with RocksDB backend |
| `checkpoint` | Flink checkpointing to S3/HDFS |
| `time_model` | Watermark strategies |
| `apply_rules` | UDF calls to business rules |

#### Flink Job Pattern

```yaml
# DSL Declaration
stage: authorization_enrichment
  transform:
    - block: catalog://auth-enrichment-TB2345
  output:
    - route: approved
      condition: "risk_score < 0.7"
      sink: stream://approved-auths
    - route: declined
      condition: "risk_score >= 0.7"
      sink: stream://declined-auths

# Compiler generates Flink SQL:
# INSERT INTO approved_auths
# SELECT * FROM enriched WHERE risk_score < 0.7;
#
# INSERT INTO declined_auths
# SELECT * FROM enriched WHERE risk_score >= 0.7;
```

#### Key Flink Features for Nexflow

| Feature | Railroad Role | Nexflow Usage |
|---------|---------------|----------------|
| **SQL/Table API** | Standard switching rules | Declarative transformations |
| **Keyed State** | Per-track state | Account balances, counters |
| **Windowing** | Scheduled batches | Time-based aggregations |
| **Side Outputs** | Alternate routes | Late data, error handling |
| **Checkpoints** | Recovery points | Exactly-once processing |
| **Savepoints** | Planned stops | Version upgrades, migrations |

---

### 11.3 Apache Spark - The Freight Yards

Spark serves as the **batch processing and heavy transformation center** — handling large-scale data movements, complex analytics, and bulk operations.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        SPARK AS THE FREIGHT YARDS                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  RAILROAD ANALOGY              SPARK COMPONENT                                  │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│  Freight Yard Master           Driver                                           │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Plans car sorting           • Job planning and DAG creation                 │
│  • Coordinates movements       • Task scheduling                               │
│  • Optimizes operations        • Query optimization (Catalyst)                 │
│                                                                                 │
│  Sorting Tracks                Executors                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Parallel sorting lanes      • Parallel task execution                       │
│  • Heavy lifting               • Data processing                               │
│  • Bulk operations             • Shuffle operations                            │
│                                                                                 │
│  Classification Yard           Shuffle                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Sort cars by destination    • Redistribute data by key                      │
│  • Group related cargo         • Prepare for aggregations                      │
│  • Major reorganization        • Wide transformations                          │
│                                                                                 │
│  Cargo Manifest                DataFrame / Dataset                              │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Structured cargo list       • Structured data with schema                   │
│  • Type information            • Type safety                                   │
│  • Processing instructions     • Transformation lineage                        │
│                                                                                 │
│  Warehouse Storage             Caching / Persist                                │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Temporary cargo storage     • In-memory caching                             │
│  • Reuse for multiple routes   • Reuse across actions                          │
│                                                                                 │
│  Bulk Loading Docks            Batch Sources/Sinks                              │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Load entire trainloads      • Read/write entire datasets                    │
│  • Efficient bulk transfer     • Optimized I/O (Parquet, ORC)                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Spark Role in Nexflow

| DSL Concept | Spark Implementation |
|-------------|---------------------|
| Batch `stage` | Spark SQL job |
| Historical reprocessing | Batch read from Kafka/storage |
| Complex aggregations | DataFrame operations |
| ML-based scoring | Spark MLlib models |
| Data lake writes | Delta Lake / Parquet output |
| Schema migration | Batch transformation jobs |

#### Spark Use Cases in Nexflow

```yaml
# DSL Declaration for Batch Stage
stage: daily_reconciliation
  type: batch                    # Triggers Spark instead of Flink
  schedule: "0 2 * * *"          # Daily at 2 AM

  input:
    source: lake://transactions/dt={{ ds }}
    schema: schema://transaction-v3

  transform:
    - block: catalog://reconciliation-TB5678
    - aggregate:
        group_by: [account_id, transaction_date]
        compute:
          daily_total: sum(amount)
          transaction_count: count(*)

  output:
    sink: lake://daily_summaries/dt={{ ds }}
    format: parquet
    partition_by: [transaction_date]

# Compiler generates Spark SQL job
```

#### Key Spark Features for Nexflow

| Feature | Railroad Role | Nexflow Usage |
|---------|---------------|----------------|
| **Spark SQL** | Cargo sorting rules | Batch transformations |
| **Catalyst Optimizer** | Route optimization | Query planning |
| **Adaptive Query Execution** | Dynamic rerouting | Runtime optimization |
| **Delta Lake** | Cargo tracking | ACID transactions on data lake |
| **Structured Streaming** | Micro-batch freight | Near-real-time batch processing |
| **MLlib** | Specialized cargo handling | Risk scoring, fraud detection |

#### Flink vs. Spark Decision Matrix

| Characteristic | Use Flink | Use Spark |
|----------------|-----------|-----------|
| Latency requirement | < 1 second | Minutes acceptable |
| Processing model | Continuous stream | Batch or micro-batch |
| State management | Per-record state | Aggregate state |
| Data volume timing | Continuous inflow | Periodic bulk |
| Complexity | Event-by-event logic | Set-based operations |
| Recovery granularity | Record-level | Batch-level |

---

### 11.4 MongoDB - The Stations and Depots

MongoDB serves as the **persistent storage layer** — stations where data is loaded/unloaded, and depots where state is maintained.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      MONGODB AS STATIONS AND DEPOTS                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  RAILROAD ANALOGY              MONGODB COMPONENT                                │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│  Train Station                 Collection                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Passenger boarding point    • Document storage                              │
│  • Cargo loading/unloading     • Read/write operations                         │
│  • Named destination           • Named entity storage                          │
│                                                                                 │
│  Station Platform              Document                                         │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Individual train stop       • Single record                                 │
│  • Flexible capacity           • Flexible schema (nested JSON)                 │
│  • Quick access                • Direct document access by _id                 │
│                                                                                 │
│  Depot Warehouse               Database                                         │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Long-term storage           • Persistent data storage                       │
│  • Organized by type           • Collections grouped logically                 │
│  • Inventory management        • Index management                              │
│                                                                                 │
│  Station Index Board           Indexes                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Quick lookup                • Fast query paths                              │
│  • Arrival/departure times     • Compound indexes for common queries           │
│  • Platform assignments        • Unique indexes for keys                       │
│                                                                                 │
│  Cargo Manifest System         Schema Validation                                │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Cargo type verification     • Document validation rules                     │
│  • Loading requirements        • Required fields, types                        │
│                                                                                 │
│  Multi-Station Network         Replica Set                                      │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Redundant stations          • High availability                             │
│  • Failover routing            • Automatic failover                            │
│  • Read distribution           • Read preference options                       │
│                                                                                 │
│  Regional Distribution         Sharding                                         │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Geographic distribution     • Horizontal scaling                            │
│  • Load balancing              • Shard key distribution                        │
│  • Parallel operations         • Parallel queries across shards                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### MongoDB Role in Nexflow

| DSL Concept | MongoDB Implementation |
|-------------|------------------------|
| `sink: mongo://collection` | Collection write |
| `lookup: mongo://collection` | Collection read/join |
| `state.uses` (persistent) | State collection |
| Reference data | Lookup collections |
| Service Domain entities | Domain collections |
| Audit trail | Audit collection with TTL |

#### MongoDB Collection Patterns

```yaml
# DSL Declaration
sinks:
  accounts:
    type: mongo
    collection: accounts
    database: credit_card
    write_concern: majority
    indexes:
      - fields: [account_id]
        unique: true
      - fields: [customer_id, status]

  transactions:
    type: mongo
    collection: transactions
    database: credit_card
    sharding:
      key: account_id
      strategy: hashed
    indexes:
      - fields: [account_id, transaction_date]
      - fields: [merchant_id]

  account_state:
    type: mongo
    collection: account_state
    database: state
    # Used by Flink for state externalization
    indexes:
      - fields: [account_id]
        unique: true

# Compiler generates collection setup scripts
```

#### Key MongoDB Features for Nexflow

| Feature | Railroad Role | Nexflow Usage |
|---------|---------------|----------------|
| **Flexible Schema** | Variable cargo | Nested JSON records (5000 fields) |
| **Sharding** | Distributed depots | Scale to billions of documents |
| **Aggregation Pipeline** | In-depot processing | Complex lookups, enrichments |
| **Change Streams** | Departure notifications | CDC for event sourcing |
| **TTL Indexes** | Auto-cleanup | Expire old audit records |
| **Transactions** | Cargo integrity | Multi-document ACID |

---

### 11.5 Infrastructure Integration Patterns

How the four technologies work together as an integrated railroad system:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    INTEGRATED RAILROAD OPERATIONS                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  PATTERN 1: REAL-TIME STREAMING (Primary Path)                                  │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│    Kafka          Flink           Kafka           MongoDB                       │
│    (Inbound)  →   (Switch)    →   (Outbound)  →   (Station)                    │
│                                                                                 │
│    auth_events → enrichment   → approved_auths → accounts                       │
│                   stage          declined_auths   transactions                  │
│                     │                              ledger_entries               │
│                     ▼                                                           │
│                  MongoDB                                                        │
│                  (Lookup)                                                       │
│                  customers                                                      │
│                                                                                 │
│  ───────────────────────────────────────────────────────────────────────────   │
│                                                                                 │
│  PATTERN 2: BATCH REPROCESSING (Freight Yard)                                   │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│    Data Lake      Spark          Data Lake        MongoDB                       │
│    (Source)   →   (Freight)  →   (Processed)  →   (Station)                    │
│                                                                                 │
│    raw_events → reconciliation → summaries     → daily_balances                 │
│    (Parquet)     batch job       (Parquet)       (bulk upsert)                 │
│                                                                                 │
│  ───────────────────────────────────────────────────────────────────────────   │
│                                                                                 │
│  PATTERN 3: HYBRID (Lambda-style)                                               │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│                        ┌──── Flink (real-time) ────┐                           │
│    Kafka ─────────────►│                           │──────► MongoDB             │
│    (events)            └──── Spark (batch) ────────┘       (merged view)        │
│                                                                                 │
│    Real-time: Low-latency approximate results                                  │
│    Batch: High-accuracy reconciled results                                     │
│    Merge: Best of both worlds                                                  │
│                                                                                 │
│  ───────────────────────────────────────────────────────────────────────────   │
│                                                                                 │
│  PATTERN 4: STATE EXTERNALIZATION                                               │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│    Flink                  Kafka                   MongoDB                       │
│    (Processing)   ←──►    (Changelog)    ←──►     (State Store)                │
│                                                                                 │
│    Flink keyed state backed by Kafka changelog topic                           │
│    MongoDB as queryable state store for external access                        │
│    Enables: State queries, debugging, analytics on live state                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 11.6 Infrastructure Mapping Summary

| Railroad Concept | Kafka | Flink | Spark | MongoDB |
|------------------|-------|-------|-------|---------|
| **Primary Role** | Tracks | Switching | Freight Yards | Stations |
| **Data Model** | Streams | Streams/Tables | DataFrames | Documents |
| **Latency** | ms | ms-sec | sec-min | ms |
| **State** | Topics | Keyed State | Cached DFs | Collections |
| **Scaling** | Partitions | Parallelism | Executors | Sharding |
| **Recovery** | Offsets | Checkpoints | Lineage | Replica Sets |
| **Query** | Consumer API | SQL/DataStream | SQL/DataFrame | MQL/Aggregation |

### 11.7 DSL Abstraction Layer

The DSL abstracts these infrastructure details behind logical references:

```yaml
# Logical References (DSL)          Physical Mapping (Infrastructure)
# ═══════════════════════════════════════════════════════════════════

stream://auth-events            →   Kafka topic: auth_events
stream://approved-auths         →   Kafka topic: approved_auths

mongo://customers               →   MongoDB: credit_card.customers
mongo://transactions            →   MongoDB: credit_card.transactions

lake://daily-summaries          →   S3: s3://datalake/daily_summaries/

state://account-balances        →   Flink RocksDB + Kafka changelog

catalog://transform-T2345       →   MongoDB: config.transforms

rules://fraud-detection-v2      →   UDF: com.company.rules.FraudDetectionV2
```

This abstraction enables:
- **Environment portability**: Same DSL works in dev/staging/prod
- **Technology evolution**: Swap implementations without DSL changes
- **Team independence**: Stage developers don't need infrastructure expertise

---

## Part 12: Open Design Questions

### 12.1 Deferred Decisions

| Topic | Status | Notes |
|-------|--------|-------|
| Field Projection Grammar | Deferred | Options proposed, awaiting selection |
| DSL Syntax (YAML vs custom) | Open | To be explored |
| Compilation Strategy | Open | How DSL compiles to Flink/Spark |
| IDE/Tooling | Open | Developer experience considerations |

### 12.2 Field Projection Options (For Future Discussion)

**Option 1: JSONPath-Style**
```yaml
project:
  - /account/profile/name
  - /account/profile/address/*
  - /transaction/**
```

**Option 2: Named Field Groups**
```yaml
project:
  - group://account_identity
  - group://transaction_core
```

**Option 3: Computed from Transform**
```yaml
transform: catalog://auth-enrichment-T2345
# Compiler infers required fields
```

**Option 4: Hybrid** 
```yaml
project:
  include:
    - group://account_identity
    - /transaction/**
  exclude:
    - /transaction/internal/*
```

---

## Part 13: Development Phases

### Phase 1: Core Railroad (Foundation)
- [ ] Record envelope specification
- [ ] Stage contract definition
- [ ] Routing protocol semantics
- [ ] Error handling patterns
- [ ] Checkpoint/recovery model
- [ ] Core DSL grammar

### Phase 2: Reference Architecture
- [ ] Compilation to Flink
- [ ] Compilation to Spark
- [ ] Kafka integration patterns
- [ ] MongoDB integration patterns
- [ ] State store abstractions

### Phase 3: Existing Asset Integration
- [ ] Business Rules DSL bridge
- [ ] Excel attribute mapping import
- [ ] Service Domain bridge

### Phase 4: Tooling
- [ ] DSL parser/validator
- [ ] Compiler implementation
- [ ] Schema registry integration
- [ ] Transform catalog integration
- [ ] IDE support / developer experience

### Phase 5: Operational Readiness
- [ ] Monitoring dashboards
- [ ] Alerting rules
- [ ] Deployment automation
- [ ] Shadow mode infrastructure
- [ ] Performance benchmarking (1B→22B validation)

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **CEP** | Complex Event Processing |
| **DAG** | Directed Acyclic Graph |
| **DSL** | Domain-Specific Language |
| **Envelope** | Universal wrapper structure for all records |
| **Fan-out** | One input record producing multiple output records |
| **MON** | Monetary transaction (affects balances) |
| **NON-MON** | Non-monetary event (profile/preference changes) |
| **Railroad** | Core DSL infrastructure (the tracks) |
| **Stage** | Processing unit in the DAG |
| **Town** | Domain-specific component (schemas, rules, transforms) |
| **Transform Block** | Grouped transforms applied as a unit |

## Appendix B: Reference Links

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-XX | Chandra Mohn | Initial brainstorming capture |
| 1.1 | 2025-01-XX | Chandra Mohn | Added Flink Native Capability Assessment (Part 10) |
| 1.2 | 2025-01-XX | Chandra Mohn | Added Infrastructure Anatomy - Railroad Components (Part 11) |

