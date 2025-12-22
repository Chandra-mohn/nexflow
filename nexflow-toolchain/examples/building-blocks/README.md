# Nexflow DSL Building Blocks
#### Author: Chandra Mohn

A progressive collection of samples demonstrating Nexflow DSL patterns from simple to complex.

## Learning Path

```
Level 1: Unit Blocks          → Single DSL layer, atomic patterns
Level 2: Two-Layer Integration → Combining 2 DSL layers
Level 3: Multi-Layer Patterns  → 3+ layers working together
Level 4: Full-Stack Examples   → Complete applications (L1-L5)
```

## DSL Layer Overview

| Layer | Name | Purpose | File Extension |
|-------|------|---------|----------------|
| **L1** | ProcDSL | Data flow orchestration | `.proc` |
| **L2** | SchemaDSL | Data structure definitions | `.schema` |
| **L3** | TransformDSL | Field mappings & transforms | `.xform` |
| **L4** | RulesDSL | Business rules & decisions | `.rules` |
| **L5** | ConfigDSL | Environment configuration | `.config` |

---

## Level 1: Unit Blocks (18 samples)

Single-layer samples demonstrating core concepts of each DSL.

### L1 ProcDSL - Data Flow (8 samples)

| Sample | Description | Key Concepts |
|--------|-------------|--------------|
| [01-passthrough](level-1-unit/l1-procdsl/01-passthrough.proc) | Kafka → Kafka identity | `receive`, `send` |
| [02-filter](level-1-unit/l1-procdsl/02-filter.proc) | Conditional filtering | `where` clause |
| [03-split](level-1-unit/l1-procdsl/03-split.proc) | Route to multiple outputs | `route`, `when` |
| [04-join](level-1-unit/l1-procdsl/04-join.proc) | Combine two streams | `join`, `on` |
| [05-union](level-1-unit/l1-procdsl/05-union.proc) | Merge multiple streams | `union` |
| [06-window-aggregate](level-1-unit/l1-procdsl/06-window-aggregate.proc) | Tumbling window | `window`, `aggregate` |
| [07-keyed-aggregate](level-1-unit/l1-procdsl/07-keyed-aggregate.proc) | Group by aggregation | `group by`, `aggregate` |
| [08-dead-letter](level-1-unit/l1-procdsl/08-dead-letter.proc) | Error routing | `on_error`, `send to` |

### L2 SchemaDSL - Data Structures (4 samples)

| Sample | Description | Key Concepts |
|--------|-------------|--------------|
| [01-flat-record](level-1-unit/l2-schemadsl/01-flat-record.schema) | Simple fields | `record`, field types |
| [02-nested-record](level-1-unit/l2-schemadsl/02-nested-record.schema) | Nested objects | Nested records |
| [03-collection-fields](level-1-unit/l2-schemadsl/03-collection-fields.schema) | Lists and arrays | `list of` |
| [04-constrained-types](level-1-unit/l2-schemadsl/04-constrained-types.schema) | Validation rules | `range`, `length`, `pattern` |

### L3 TransformDSL - Field Mappings (4 samples)

| Sample | Description | Key Concepts |
|--------|-------------|--------------|
| [01-field-mapping](level-1-unit/l3-transformdsl/01-field-mapping.xform) | Direct field copy | `mappings`, `->` |
| [02-calculated-fields](level-1-unit/l3-transformdsl/02-calculated-fields.xform) | Expressions | Arithmetic, functions |
| [03-conditional-mapping](level-1-unit/l3-transformdsl/03-conditional-mapping.xform) | When/otherwise | `when`, `otherwise` |
| [04-lookup-enrichment](level-1-unit/l3-transformdsl/04-lookup-enrichment.xform) | External lookup | `lookups`, `lookup()` |

### L4 RulesDSL - Business Rules (4 samples)

| Sample | Description | Key Concepts |
|--------|-------------|--------------|
| [01-simple-decision-table](level-1-unit/l4-rulesdsl/01-simple-decision-table.rules) | Basic decision | `decision_table`, `decide` |
| [02-multi-column-table](level-1-unit/l4-rulesdsl/02-multi-column-table.rules) | Multiple conditions | Multi-column conditions |
| [03-procedural-rule](level-1-unit/l4-rulesdsl/03-procedural-rule.rules) | If-then-else | `rule`, `if`, `then` |
| [04-collection-rule](level-1-unit/l4-rulesdsl/04-collection-rule.rules) | List predicates | `any`, `all`, `sum` |

### L5 ConfigDSL - Environment Config (2 samples)

| Sample | Description | Key Concepts |
|--------|-------------|--------------|
| [01-dev-environment](level-1-unit/l5-configdsl/01-dev-environment.config) | Development settings | `environment`, `kafka` |
| [02-prod-environment](level-1-unit/l5-configdsl/02-prod-environment.config) | Production settings | HA, security, scaling |

---

## Level 2: Two-Layer Integration (6 samples)

Combining two DSL layers to build more complete patterns.

| Sample | Layers | Description |
|--------|--------|-------------|
| [01-typed-stream](level-2-integration/01-typed-stream/) | L1+L2 | Schema-validated Kafka flow |
| [02-transform-pipeline](level-2-integration/02-transform-pipeline/) | L1+L3 | Stream with field transformations |
| [03-rules-evaluation](level-2-integration/03-rules-evaluation/) | L1+L4 | Stream with decision table routing |
| [04-schema-transform](level-2-integration/04-schema-transform/) | L2+L3 | Input→Output schema mapping |
| [05-configurable-job](level-2-integration/05-configurable-job/) | L1+L5 | Process with environment config |
| [06-typed-rules](level-2-integration/06-typed-rules/) | L2+L4 | Schema-driven decision table |

---

## Level 3: Multi-Layer Patterns (4 samples)

Three or more layers working together for complete data pipelines.

| Sample | Layers | Description |
|--------|--------|-------------|
| [01-etl-pipeline](level-3-multi-layer/01-etl-pipeline/) | L1+L2+L3 | Extract → Validate → Transform → Load |
| [02-rules-engine](level-3-multi-layer/02-rules-engine/) | L1+L2+L4 | Validate → Decide → Route |
| [03-enrich-and-decide](level-3-multi-layer/03-enrich-and-decide/) | L1+L3+L4 | Enrich → Rules → Output |
| [04-full-logic-layer](level-3-multi-layer/04-full-logic-layer/) | L2+L3+L4 | Schema + Transform + Rules |

---

## Level 4: Full-Stack Examples (4 samples)

Complete applications using all five DSL layers.

| Sample | Description | Domain |
|--------|-------------|--------|
| [01-order-processing](level-4-full-stack/01-order-processing/) | Order validation & routing | E-commerce |
| [02-fraud-detection](level-4-full-stack/02-fraud-detection/) | Real-time fraud scoring | Financial |
| [03-credit-decision](level-4-full-stack/03-credit-decision/) | Loan application evaluation | Banking |
| [04-event-aggregator](level-4-full-stack/04-event-aggregator/) | Multi-source consolidation | Analytics |

---

## Quick Start

### Build a Sample
```bash
# Build a single sample
nexflow build examples/building-blocks/level-1-unit/l1-procdsl/01-passthrough.proc

# Build with specific config
nexflow build examples/building-blocks/level-2-integration/01-typed-stream/ \
  --config examples/building-blocks/level-1-unit/l5-configdsl/01-dev-environment.config
```

### Run Generated Code
```bash
# Navigate to generated output
cd generated/01-passthrough/

# Run with Maven
mvn compile exec:java
```

---

## Pattern Index

| Use Case | Samples |
|----------|---------|
| **Simple Routing** | L1-01, L1-02, L1-03 |
| **Stream Joining** | L1-04, L1-05 |
| **Aggregation** | L1-06, L1-07 |
| **Error Handling** | L1-08 |
| **Data Validation** | L2-04, L12-01 |
| **Field Transformation** | L3-01, L3-02, L12-02 |
| **Business Decisions** | L4-01, L4-02, L12-03 |
| **Complete Pipelines** | Level 3 & 4 |

---

*Nexflow DSL Building Blocks v1.0.0*
