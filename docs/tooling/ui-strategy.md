# Nexflow User Interface Strategy

> **Category**: Tooling
> **Status**: Design Decision
> **Version**: 0.1.0
> **Last Updated**: 2025-11-28

---

## 1. Overview

This document defines the user interface strategy for authoring, visualizing, and managing Nexflow artifacts across all six layers. The core principle is **GUI for authoring convenience, text for storage and version control**.

### 1.1 Core Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FUNDAMENTAL PRINCIPLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              GUI ──────► Text Export ──────► Git                           │
│                                                                             │
│  • All artifacts stored as human-readable text files                       │
│  • GUI is authoring convenience, NOT source of truth                       │
│  • Text files are the canonical representation                             │
│  • Version control (Git) manages all changes                               │
│  • Bidirectional sync between GUI and text where applicable                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Summary Matrix

| Layer | Authoring UI | Visualization | Storage Format | Git-Controlled |
|-------|-------------|---------------|----------------|----------------|
| **L1** Process | Text IDE | DAG Viewer | `.proc` | Yes |
| **L2** Schema | ERD GUI + Table Editor | ERD + Table View | `.schema` | Yes |
| **L3** Transform | Text IDE | — | `.xform` | Yes |
| **L4** Rules | Text IDE + DT Wizard | Decision Table Preview | `.rules` | Yes |
| **L5** Infra | Canvas GUI | Topology View | `.infra` (YAML) | Yes |
| **L6** Pipeline | CLI | — | — | N/A |

---

## 2. Layer-by-Layer UI Specification

### 2.1 L1: Process Orchestration

**Primary Interface**: Text IDE with Visual DAG Viewer

#### Authoring: Text IDE
- Syntax highlighting for `.proc` files
- Autocomplete for keywords, schema references, transform references
- Inline validation and error highlighting
- Jump-to-definition for referenced schemas/transforms/rules

#### Visualization: DAG Viewer (Read-Only)
```
┌─────────────────────────────────────────────────────────────────┐
│                    DAG VISUALIZATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │ auth_events │ (Kafka Source)                                │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────┐     ┌─────────────┐                          │
│   │   enrich    │────▶│  customers  │ (MongoDB Lookup)         │
│   └──────┬──────┘     └─────────────┘                          │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────┐                                               │
│   │  transform  │ (normalize_amount)                            │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────┐                                               │
│   │    route    │ (fraud_detection_rules)                       │
│   └──────┬──────┘                                               │
│          │                                                      │
│    ┌─────┴─────┐                                                │
│    ▼           ▼                                                │
│ ┌──────┐  ┌──────┐                                              │
│ │approve│  │review│                                             │
│ └──────┘  └──────┘                                              │
│                                                                 │
│  Features:                                                      │
│  • Zoom/pan navigation                                          │
│  • Click node to highlight source code                          │
│  • Show parallelism hints                                       │
│  • Display window configurations                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Rationale
- Data engineers prefer text editing with IDE features
- DAG visualization aids understanding complex topologies
- Visual is read-only to prevent divergence from source
- Similar to: Airflow (Python + Web UI), dbt (YAML + lineage)

---

### 2.2 L2: Schema Registry

**Primary Interface**: ERD GUI + Table Editor (Dual-Mode)

#### Authoring: Dual-Mode Interface

**Mode 1: ERD GUI** (Relationships)
```
┌─────────────────────────────────────────────────────────────────┐
│                    ERD VIEW                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │   Customer   │                                              │
│   │ ──────────── │                                              │
│   │ customer_id  │◄─────────────────┐                          │
│   │ name         │                  │                          │
│   │ risk_tier    │                  │                          │
│   └──────────────┘                  │                          │
│          │                          │                          │
│          │ 1:N                      │ FK                       │
│          ▼                          │                          │
│   ┌──────────────┐           ┌──────────────┐                  │
│   │ Card Account │           │  Transaction │                  │
│   │ ──────────── │           │ ──────────── │                  │
│   │ account_id   │◄──────────│ account_id   │                  │
│   │ card_id      │           │ txn_id       │                  │
│   │ credit_limit │    1:N    │ amount       │                  │
│   │ customer_id ─┼───────────│ card_id      │                  │
│   └──────────────┘           └──────────────┘                  │
│                                                                 │
│  Actions:                                                       │
│  • Drag to create relationships                                 │
│  • Click entity to edit fields                                  │
│  • Right-click for context menu                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Mode 2: Table Editor** (Field Details)
```
┌─────────────────────────────────────────────────────────────────┐
│                    TABLE VIEW                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Entity: Customer    Mutation Pattern: [master_data ▼]         │
│  Version: 1.2                                                   │
│                                                                 │
│  ┌────────────────┬───────────┬─────────────┬─────────────────┐ │
│  │ Field          │ Type      │ Constraints │ Streaming       │ │
│  ├────────────────┼───────────┼─────────────┼─────────────────┤ │
│  │ customer_id    │ uuid      │ PK          │ key_field       │ │
│  │ name           │ string    │ len: 100    │ —               │ │
│  │ email          │ string    │ pattern:*@* │ —               │ │
│  │ risk_tier      │ enum      │ [H,M,L]     │ —               │ │
│  │ credit_limit   │ decimal   │ range: 0..∞ │ —               │ │
│  │ created_at     │ timestamp │ auto        │ time_field      │ │
│  │ updated_at     │ timestamp │ auto        │ watermark: 5s   │ │
│  └────────────────┴───────────┴─────────────┴─────────────────┘ │
│                                                                 │
│  [+ Add Field]  [+ Add Index]  [Validate]  [View History]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Rationale
- ERD shows "forest" (entity relationships, cardinality)
- Table shows "trees" (field details, constraints, types)
- Data governance users familiar with spreadsheet interfaces
- Both modes edit same underlying `.schema` file
- Similar to: Hasura Console, Prisma Studio, DBeaver

---

### 2.3 L3: Transform Catalog

**Primary Interface**: Text IDE Only

#### Authoring: Text IDE
```
┌─────────────────────────────────────────────────────────────────┐
│  currency_transforms.xform                                      │
├─────────────────────────────────────────────────────────────────┤
│  1│ transform normalize_amount                                  │
│  2│   description "Convert transaction amount to USD"           │
│  3│                                                             │
│  4│   input                                                     │
│  5│     amount: decimal                                         │
│  6│     currency: currency_code                                 │
│  7│   end                                                       │
│  8│                                                             │
│  9│   output                                                    │
│ 10│     amount_usd: decimal                                     │
│ 11│   end                                                       │
│ 12│                                                             │
│ 13│   implementation                                            │
│ 14│     rate = lookup(currency_rates, currency)                 │
│ 15│     amount_usd = amount * rate                              │
│ 16│   end                                                       │
│ 17│ end                                                         │
└─────────────────────────────────────────────────────────────────┘

IDE Features:
• Syntax highlighting
• Autocomplete for builtin functions
• Type inference and checking
• Inline documentation
• Jump-to-definition for schemas
```

#### Rationale
- Transforms are code - GUIs add friction for engineers
- IDE features (autocomplete, refactor) are essential
- Version control and code review are critical
- No visualization needed - logic is linear
- Similar to: SQL editors, dbt models

---

### 2.4 L4: Business Rules

**Primary Interface**: Text IDE with Decision Table Wizard

#### Authoring: Text IDE with Embedded Decision Table Support
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  fraud_detection.rules                                          [Preview]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1│ // Procedural rule                                                    │
│   2│ rule velocity_check                                                   │
│   3│   if transaction.count_1h > customer.max_hourly                       │
│   4│      and transaction.amount_1h > customer.hourly_limit                │
│   5│   then temporaryBlock                                                 │
│   6│ end                                                                   │
│   7│                                                                        │
│   8│ // Decision table (inserted via wizard)                               │
│   9│ decision_table fraud_screening           ┌────────────────────────────┤
│  10│   hit_policy first_match                 │  DECISION TABLE PREVIEW    │
│  11│                                          │                            │
│  12│   conditions                             │  Hit Policy: First Match   │
│  13│     amount_usd: range                    │                            │
│  14│     merchant_category: in_set            │  ┌───────┬──────┬────────┐ │
│  15│   end                                    │  │Amount │ MCC  │ Route  │ │
│  16│                                          │  ├───────┼──────┼────────┤ │
│  17│   rules                                  │  │>10000 │  *   │ manual │ │
│  18│     | amount_usd | mcc    | route   |    │  │  *    │ 7995 │ block  │ │
│  19│     |------------|--------|---------|    │  │>1000  │  *   │ flag   │ │
│  20│     | > 10000    | *      | manual  |    │  │  *    │  *   │ approve│ │
│  21│     | *          | [7995] | block   |    │  └───────┴──────┴────────┘ │
│  22│     | > 1000     | *      | flag    |    │                            │
│  23│     | *          | *      | approve |    │  [Edit in Table View]      │
│  24│   end                                    │                            │
│  25│ end                                      └────────────────────────────┤
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Insert Decision Table]  [Insert Procedural Rule]  [Validate]  [Simulate] │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Decision Table Wizard
```
┌─────────────────────────────────────────────────────────────────┐
│               INSERT DECISION TABLE WIZARD                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Table Name: [fraud_screening          ]                        │
│  Hit Policy: [First Match ▼]                                    │
│                                                                 │
│  Conditions:                                                    │
│  ┌────────────────────┬─────────────┬─────────────────────────┐ │
│  │ Field              │ Type        │ Values                  │ │
│  ├────────────────────┼─────────────┼─────────────────────────┤ │
│  │ amount_usd         │ range       │ —                       │ │
│  │ merchant_category  │ in_set      │ —                       │ │
│  │ [+ Add Condition]  │             │                         │ │
│  └────────────────────┴─────────────┴─────────────────────────┘ │
│                                                                 │
│  Actions:                                                       │
│  ┌────────────────────┬─────────────┐                          │
│  │ Field              │ Type        │                          │
│  ├────────────────────┼─────────────┤                          │
│  │ route_to           │ assign      │                          │
│  │ [+ Add Action]     │             │                          │
│  └────────────────────┴─────────────┘                          │
│                                                                 │
│  Rules:                                                         │
│  ┌─────────┬──────────┬──────────┐                             │
│  │ amount  │ mcc      │ → route  │                             │
│  ├─────────┼──────────┼──────────┤                             │
│  │ > 10000 │ *        │ manual   │  [+ Add Row]               │
│  │ *       │ [7995]   │ block    │                             │
│  └─────────┴──────────┴──────────┘                             │
│                                                                 │
│  [Check Gaps]  [Check Overlaps]  [Cancel]  [Insert as Text]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Rationale
- Text-first approach keeps engineers and analysts in same tool
- Decision table wizard prevents syntax errors during creation
- Live preview panel shows tabular view without leaving editor
- Full expressiveness for complex procedural rules
- Simulation capability for testing before deployment
- Similar to: VS Code + custom extensions

---

### 2.5 L5: Infrastructure Binding

**Primary Interface**: Canvas GUI (Saves as YAML)

#### Authoring: Canvas-Based Visual Editor
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  production.infra                                            [Save as YAML] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SOURCES                          PROCESS                    SINKS        │
│   ────────                         ───────                    ─────        │
│                                                                             │
│   ┌──────────────┐                                     ┌──────────────┐    │
│   │    Kafka     │                                     │    Kafka     │    │
│   │ ──────────── │                                     │ ──────────── │    │
│   │ auth_events  │──────┐                       ┌─────▶│ enriched_out │    │
│   │              │      │                       │      │              │    │
│   │ brokers: 3   │      │                       │      │ partitions:  │    │
│   │ partitions:  │      │                       │      │   64         │    │
│   │   128        │      │                       │      └──────────────┘    │
│   └──────────────┘      │                       │                          │
│                         ▼                       │                          │
│   LOOKUPS        ┌─────────────────────────────────┐                       │
│   ───────        │   authorization_enrichment      │                       │
│                  │ ─────────────────────────────── │                       │
│   ┌──────────────┐│                                │                       │
│   │   MongoDB    ││  parallelism: 128              │                       │
│   │ ──────────── ││  memory: 4gb                   │                       │
│   │ customers    │├─▶ cpu: 2                       │                       │
│   │              ││                                │                       │
│   │ replica: 3   │└────────────────────────────────┘                       │
│   │ read_pref:   │      │                                                  │
│   │  secondary   │      │                          CHECKPOINTS             │
│   └──────────────┘      │                          ───────────             │
│                         │                          ┌──────────────┐        │
│   ┌──────────────┐      │                          │     S3       │        │
│   │    Redis     │      └─────────────────────────▶│ ──────────── │        │
│   │ ──────────── │                                 │ checkpoints/ │        │
│   │ fx_rates     │                                 │              │        │
│   │              │                                 │ bucket:      │        │
│   │ cluster: 3   │                                 │   prod-ckpt  │        │
│   └──────────────┘                                 └──────────────┘        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [+ Add Source]  [+ Add Lookup]  [+ Add Sink]  [+ Add Checkpoint]          │
│                                                                             │
│  Click node to edit properties │ Drag to connect │ [Validate] [Save]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Node Property Panel
```
┌─────────────────────────────────────────────────────────────────┐
│  EDIT: Kafka Source - auth_events                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Name:           [auth_events        ]                          │
│  Type:           Kafka                                          │
│                                                                 │
│  Connection:                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Brokers:      [${KAFKA_BROKERS}   ]  (env variable)     │   │
│  │ Topic:        [prod.auth.events.v3]                     │   │
│  │ Consumer Grp: [auth-enrichment    ]                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Performance:                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Partitions:   [128] ◄━━━━━━━━━━━━━━━━━━━━━►             │   │
│  │ Replication:  [3  ]                                     │   │
│  │ Retention:    [7 days ▼]                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Security:                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Auth Method:  [SASL_SSL ▼]                              │   │
│  │ Credentials:  [vault:kafka/prod/creds]                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Delete Node]                            [Cancel]  [Apply]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Generated YAML Output
```yaml
# production.infra
# Generated by Nexflow Canvas Editor
# Last modified: 2025-11-28T10:30:00Z

environment: production
version: 1.0

streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    brokers: ${KAFKA_BROKERS}
    consumer_group: auth-enrichment
    partitions: 128
    replication: 3
    retention: 7d
    security:
      method: SASL_SSL
      credentials: vault:kafka/prod/creds

  enriched_out:
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
    replica_set: rs0
    read_preference: secondaryPreferred

  fx_rates:
    type: redis
    uri: ${REDIS_URI}
    cluster_mode: true
    nodes: 3

checkpoints:
  auth_checkpoints:
    type: s3
    bucket: prod-ckpt
    prefix: auth/enrichment/

resources:
  authorization_enrichment:
    parallelism: 128
    task_memory: 4gb
    task_cpu: 2
```

#### Rationale
- Visual topology shows infrastructure relationships clearly
- Drag-and-drop faster than writing YAML from scratch
- Property panels prevent typos and invalid configurations
- Environment variables and secrets handled via dropdowns
- **But**: YAML output remains editable for quick fixes
- Similar to: CloudFormation Designer, Lens (Kubernetes)

---

### 2.6 L6: Compilation Pipeline

**Primary Interface**: CLI Only

#### CLI Commands
```bash
# Validate all artifacts
procdsl validate ./

# Validate specific layer
procdsl validate --layer schema ./schemas/
procdsl validate --layer rules ./rules/

# Compile process with dependencies
procdsl compile ./processes/authorization/enrichment.proc \
  --schemas ./schemas/ \
  --transforms ./transforms/ \
  --rules ./rules/ \
  --infra ./infra/production.infra \
  --output ./generated/

# Dry-run compilation (validate without generating)
procdsl compile --dry-run ./processes/

# Deploy to target runtime
procdsl deploy --target kubernetes --cluster prod-east

# Generate dependency graph
procdsl deps ./processes/authorization/enrichment.proc --format dot

# Run rule simulation
procdsl simulate ./rules/fraud_detection.rules \
  --input ./test/sample_transactions.json

# Export schema as various formats
procdsl export ./schemas/customer.schema --format avro
procdsl export ./schemas/customer.schema --format protobuf
```

#### Rationale
- Runs in CI/CD pipelines (Jenkins, GitHub Actions)
- Scriptable and automatable
- No human interaction needed for production builds
- Structured output (JSON, exit codes) for tooling integration

---

## 3. Bidirectional Sync Requirements

For layers with GUI authoring (L2, L4 wizard, L5), bidirectional synchronization between GUI and text is critical.

### 3.1 Round-Trip Integrity

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROUND-TRIP REQUIREMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Text File ◄──────────────────────────► GUI Editor             │
│       │           (bidirectional)            │                  │
│       │                                      │                  │
│       ▼                                      ▼                  │
│  git commit                           visual editing            │
│  git diff                             drag-and-drop             │
│  git merge                            property panels           │
│       │                                      │                  │
│       └─────────► MUST STAY IN SYNC ◄────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Requirements

| Requirement | Description |
|-------------|-------------|
| **Lossless Round-Trip** | GUI → Text → GUI produces identical result |
| **Comment Preservation** | Manual comments in text preserved through GUI edits |
| **Formatting Stability** | Consistent formatting for clean diffs |
| **Conflict Resolution** | Text-based merge conflicts resolvable by humans |
| **Validation Parity** | Same validation rules in GUI and CLI |

### 3.3 Implementation Strategy

```
Option A: GUI as Parser + Serializer
────────────────────────────────────
Load:    .infra file → Parse → Internal Model → Render GUI
Save:    GUI State → Internal Model → Serialize → .infra file

Option B: GUI Generates AST Patches
────────────────────────────────────
Load:    .infra file → AST → GUI binds to AST nodes
Edit:    GUI modifies AST in place
Save:    AST → Pretty Print → .infra file (preserves structure)

Recommended: Option B (preserves formatting and comments)
```

---

## 4. Tooling Architecture

### 4.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TOOLING ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        IDE PLUGIN (VS Code)                          │   │
│  │                                                                      │   │
│  │  • Syntax highlighting: .proc, .schema, .xform, .rules, .infra      │   │
│  │  • Language Server Protocol (LSP) for autocomplete/validation       │   │
│  │  • Integrated DAG preview panel (L1)                                │   │
│  │  • Decision table preview panel (L4)                                │   │
│  │  • Jump-to-definition across layers                                 │   │
│  │  • Inline error diagnostics                                         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     WEB APPLICATION                                  │   │
│  │                                                                      │   │
│  │  • L2 Schema Editor: ERD GUI + Table Editor                         │   │
│  │  • L4 Decision Table Wizard: Visual table construction              │   │
│  │  • L5 Canvas Editor: Infrastructure topology designer               │   │
│  │  • DAG Visualization: Process flow viewer                           │   │
│  │  • Rule Simulator: Test rules with sample data                      │   │
│  │  • Deployment Dashboard: Monitor compiled artifacts                 │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          CLI (procdsl)                               │   │
│  │                                                                      │   │
│  │  • procdsl validate     Validate artifacts                          │   │
│  │  • procdsl compile      Compile to runtime code                     │   │
│  │  • procdsl deploy       Deploy to target cluster                    │   │
│  │  • procdsl test         Run rule simulations                        │   │
│  │  • procdsl export       Export schemas to Avro/Protobuf             │   │
│  │  • procdsl deps         Generate dependency graph                   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Shared Components

All tools share common components:

| Component | Purpose |
|-----------|---------|
| **Parser Library** | ANTLR4-based parsers for all file formats |
| **Validation Engine** | Cross-layer validation rules |
| **AST Library** | Abstract syntax tree manipulation |
| **Serializer** | Format-preserving text output |
| **Schema Store** | Cache for cross-reference resolution |

---

## 5. User Workflow Examples

### 5.1 Data Engineer: Create New Process

```
1. Open VS Code with Nexflow extension
2. Create new file: authorization_enrichment.proc
3. Use autocomplete to scaffold process structure
4. Reference schemas, transforms, rules by name (autocomplete suggests)
5. Preview DAG in side panel to verify topology
6. Save → Git commit → PR review
```

### 5.2 Data Governance: Define Schema

```
1. Open Nexflow Web App → Schema Editor
2. Switch to ERD view → Drag new entity onto canvas
3. Double-click entity → Switch to Table view
4. Add fields with types and constraints
5. Define relationships to other entities
6. Save → Exports to .schema file → Git commit
```

### 5.3 Business Analyst: Create Fraud Rules

```
1. Open VS Code with Nexflow extension
2. Create new file: fraud_screening.rules
3. Click "Insert Decision Table" → Opens wizard
4. Define conditions and actions in form
5. Fill in rule rows in spreadsheet-like interface
6. Click "Insert" → Generates text in editor
7. Preview panel shows formatted table
8. Save → Git commit → PR review
```

### 5.4 Platform Engineer: Configure Infrastructure

```
1. Open Nexflow Web App → Infrastructure Canvas
2. Drag Kafka source onto canvas → Configure properties
3. Drag MongoDB lookup → Configure connection
4. Connect components to process node
5. Set resource allocation (parallelism, memory)
6. Click "Save" → Generates production.infra (YAML)
7. Review YAML in text editor for fine-tuning
8. Git commit → GitOps deploys
```

---

## 6. Open Questions

| Question | Options | Notes |
|----------|---------|-------|
| Web framework for GUI? | React / Vue / Svelte | TBD based on team expertise |
| Canvas library for L5? | React Flow / JointJS / Cytoscape | Need evaluation |
| ERD library for L2? | Mermaid / GoJS / Custom | Need evaluation |
| IDE plugin target? | VS Code only / Multi-IDE | Start VS Code, expand later |
| Hosting model? | Self-hosted / SaaS / Both | Enterprise requirement |

---

## 7. Implementation Priority

| Priority | Component | Rationale |
|----------|-----------|-----------|
| **P0** | CLI (validate, compile) | Enables CI/CD pipeline |
| **P0** | VS Code syntax highlighting | Minimum viable editing |
| **P1** | L5 Canvas Editor | Most complex authoring, highest friction |
| **P1** | L4 Decision Table Wizard | Business user enablement |
| **P2** | L2 ERD + Table Editor | Governance workflow |
| **P2** | DAG Visualization | Debugging and documentation |
| **P3** | LSP (autocomplete, validation) | Developer experience |
| **P3** | Rule Simulator | Testing capability |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2025-11-28 | - | Initial UI strategy document |
