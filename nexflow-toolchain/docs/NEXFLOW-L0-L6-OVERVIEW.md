#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow L0-L6 Layer Architecture

## Executive Summary

Nexflow is a multi-layer Domain-Specific Language (DSL) platform that transforms high-level business specifications into production-ready Apache Flink streaming applications. The architecture comprises seven distinct layers (L0-L6), each serving a specific purpose and user constituency.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NEXFLOW LAYER STACK                            │
├─────────────────────────────────────────────────────────────────────────┤
│  L6: Master Compiler        [Orchestration & Code Generation]           │
│  ↓ coordinates ↓                                                        │
│  L5: Infrastructure         [Environment Bindings]                      │
│  L4: Business Rules         [Decision Logic]                            │
│  L3: Transform Catalog      [Data Transformations]                      │
│  L2: Schema Registry        [Data Contracts]                            │
│  L1: Process Orchestration  [Pipeline Definition]                       │
│  ↓ depends on ↓                                                         │
│  L0: Runtime Library        [Generated Code Foundation]                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### L0: Runtime Library

#### Purpose
Provides the foundational runtime classes, utility functions, and base operators that all generated code depends upon. L0 is the "standard library" of Nexflow.

#### What It Provides
- **NexflowRuntime.java**: Core utility functions
  - Date/time functions: `now()`, `processingDate()`, `businessDate()`, `businessDateOffset()`
  - String operations: `concat()`, `trim()`, `uppercase()`, `substring()`
  - Math functions: `abs()`, `round()`, `ceil()`, `floor()`, `max()`, `min()`
  - Collection functions: `first()`, `last()`, `size()`, `isEmpty()`
- **VoltageRuntime.java**: PII encryption/decryption with Voltage FPE
- **Base operator classes**: Flink ProcessFunction implementations
- **State management utilities**: Keyed state accessors
- **Error handling patterns**: Retry logic, dead-letter handling

#### Users
| User Type | Usage |
|-----------|-------|
| **Generated Code** | All generated Java classes import and use L0 runtime |
| **Nexflow Developers** | Extend L0 when adding new built-in functions |
| **DevOps** | Configure L0 runtime properties at deployment |

#### Master Compiler Interaction
- L0 is **generated** by the Master Compiler, not parsed
- Emitted once per project as `NexflowRuntime.java`
- Must be generated **before** other layers that reference it
- Configurable via `nexflow.toml` for custom functions

---

### L1: Process Orchestration (ProcDSL)

#### Purpose
Defines the "railroad tracks" of data flow - how data enters the system, how it's processed, and where it goes. L1 is **pure orchestration** with no business logic.

#### What It Provides
- **Pipeline Definition**: Sources, sinks, routing topology
- **Execution Configuration**: Parallelism, partitioning, time semantics
- **State Management**: Checkpoints, state backends, TTL policies
- **Correlation**: Await/hold patterns for multi-event coordination
- **Error Handling**: Retry strategies, dead-letter queues
- **Business Date Context**: Three-date model with EOD markers
- **Phase-Based Processing**: Pre/post marker execution blocks

#### File Extension
`.proc`, `.flow`

#### Users
| User Type | Usage |
|-----------|-------|
| **Data Engineers** | Design pipeline topology and data flow |
| **Architects** | Define system integration points |
| **Platform Engineers** | Configure execution parameters |

#### Key Constructs
```
process, receive, emit, transform using, evaluate using, route,
window, join, merge, await, hold, parallel, branch,
business_date, processing_date, markers, phase, on error, checkpoint
```

#### EOD Markers (End-of-Day Processing)
L1 provides comprehensive support for phase-based financial processing:

```
process Settlement
    business_date from trading_calendar
    processing_date auto

    markers
        market_close: when after "16:00"
        trades_drained: when trades.drained
        eod_ready: when market_close and trades_drained
    end

    phase before eod_ready
        // Intraday processing
    end

    phase after eod_ready
        // Settlement processing
    end
end
```

**Marker Types**:
| Type | Syntax | Description |
|------|--------|-------------|
| Time-based | `when after "16:00"` | Fires at specified time |
| Data-drained | `when stream.drained` | Fires when stream has no pending data |
| Count-based | `when stream.count >= N` | Fires when threshold reached |
| Composite | `when marker1 and marker2` | Combines multiple conditions |

#### Master Compiler Interaction
- **Compilation Order**: Last (Phase 5) - depends on all other layers
- **Input**: `.proc` files + resolved L2/L3/L4 references
- **Output**: Flink `DataStream` jobs, `ProcessFunction` implementations
- **L5 Integration**: Resolves `from kafka "topic"` → actual Kafka configuration
- **Import Resolution**: Processes files in topological order based on imports

---

### L2: Schema Registry (SchemaDSL)

#### Purpose
Defines data contracts - the structure, constraints, and evolution rules for all data entities. L2 ensures type safety across the entire pipeline.

#### What It Provides
- **Data Structures**: Field definitions with types and constraints
- **Mutation Patterns**: 9 patterns for different data behaviors
- **Streaming Metadata**: Key fields, time semantics, watermarks
- **Schema Evolution**: Versioning, compatibility modes, migration
- **PII Protection**: Voltage encryption profiles for sensitive fields
- **State Machines**: Entity lifecycle with state transitions
- **Computed Fields**: Derived values from other fields

#### File Extension
`.schema`

#### Users
| User Type | Usage |
|-----------|-------|
| **Data Architects** | Define canonical data models |
| **Domain Experts** | Specify business entity structures |
| **Data Governance** | Enforce data contracts and PII handling |
| **API Designers** | Define input/output contracts |

#### 9 Mutation Patterns
| Pattern | Description | Use Case |
|---------|-------------|----------|
| `master_data` | SCD Type 2 with history | Customer, Product catalogs |
| `immutable_ledger` | Append-only records | Financial transactions |
| `versioned_configuration` | Immutable versions | Feature flags, settings |
| `operational_parameters` | Hot-reloadable | Rate limits, thresholds |
| `event_log` | Append-only events | Event sourcing |
| `state_machine` | Entity state tracking | Order status, workflows |
| `temporal_data` | Effective-dated | Pricing, contracts |
| `reference_data` | Lookup tables | Country codes, currencies |
| `business_logic` | Compiled rules | Validation rules |

#### Master Compiler Interaction
- **Compilation Order**: Second (Phase 2) - after L5, before L3/L4
- **Input**: `.schema` files
- **Output**: Java Records, Builder classes, Migration helpers
- **Generated Artifacts**:
  - `{SchemaName}.java` - Immutable Java Record
  - `{SchemaName}Builder.java` - Builder pattern implementation
  - `{SchemaName}Migration.java` - Version migration utilities
- **PII Processing**: Generates Voltage encrypt/decrypt calls for `pii.*` fields

---

### L3: Transform Catalog (TransformDSL)

#### Purpose
Defines reusable, composable data transformations. L3 contains the **pure functional logic** that converts data from one form to another.

#### What It Provides
- **Field Transforms**: Single-field operations
- **Expression Transforms**: Multi-field calculations
- **Block Transforms**: Large-scale mappings (50+ fields)
- **Transform Composition**: Sequential, parallel, conditional
- **Input/Output Validation**: Pre/post-condition checks
- **Stateful Transforms**: Access to keyed state
- **Lookup Integration**: External data enrichment

#### File Extension
`.xform`, `.transform`

#### Users
| User Type | Usage |
|-----------|-------|
| **Business Analysts** | Define field mappings and calculations |
| **Data Engineers** | Create reusable transformation logic |
| **Domain Experts** | Specify business calculations |
| **QA Engineers** | Define validation rules |

#### Key Constructs
```
transform, transform_block, input, output, apply, mappings,
validate_input, validate_output, compose, when/otherwise,
lookup, state, params, pure, cache
```

#### Master Compiler Interaction
- **Compilation Order**: Third (Phase 3) - after L2
- **Input**: `.xform` files + L2 schema references
- **Output**: Transform function classes
- **Generated Artifacts**:
  - `{TransformName}Transform.java` - Transform implementation
  - `{TransformName}Expressions.java` - Expression evaluators
- **Type Checking**: Validates input/output types against L2 schemas

---

### L4: Business Rules (RulesDSL)

#### Purpose
Encapsulates business decision logic in declarative, auditable formats. L4 separates complex business rules from orchestration code.

#### What It Provides
- **Decision Tables**: Matrix-based multi-condition logic
- **Procedural Rules**: If-then-elseif-else chains
- **Hit Policies**: first_match, single_hit, multi_hit, collect_all
- **External Services**: Async lookups with fallbacks
- **Action Declarations**: Typed action methods with targets
- **Post-Calculations**: Derived values from rule results
- **EOD Marker Conditions**: Phase-aware rules using `marker X fired` and `between markers`

#### File Extension
`.rules`

#### Users
| User Type | Usage |
|-----------|-------|
| **Business Analysts** | Define decision tables without code |
| **Compliance Officers** | Audit and verify business logic |
| **Risk Managers** | Specify risk assessment criteria |
| **Product Owners** | Maintain business rules independently |

#### Key Constructs
```
decision_table, rule, given, decide, return, execute,
hit_policy, when/then/otherwise, in, matches, lookup,
services, actions, post_calculate, aggregate,
marker X fired, marker X pending, between X and Y
```

#### EOD Marker Conditions in Rules
L4 rules can reference L1 marker states:

```
decision_table phase_routing
    decide:
        | marker eod_1 fired | amount   | action      |
        |====================|==========|=============|
        | true               | > $10000 | hold        |
        | false              | *        | process_now |

        | between eod_1 and eod_2 | routing     |
        |=========================|=============|
        | true                    | batch_queue |
        | false                   | realtime    |
end
```

#### Master Compiler Interaction
- **Compilation Order**: Fourth (Phase 4) - after L3
- **Input**: `.rules` files + L2 schema references
- **Output**: Rule engine classes
- **Generated Artifacts**:
  - `{TableName}Rules.java` - Decision table implementation
  - `{TableName}Engine.java` - Rule evaluation engine
  - `{RuleName}Rule.java` - Procedural rule implementation
- **Optimization**: Generates efficient condition evaluation order

---

### L5: Infrastructure Binding

#### Purpose
Maps logical names used in DSL files to physical infrastructure resources. L5 provides environment-specific configuration without changing business logic.

#### What It Provides
- **Stream Bindings**: Kafka topics, consumer groups, serializers
- **Persistence Bindings**: MongoDB connections, databases, collections
- **Resource Configuration**: Parallelism hints, memory settings
- **Environment Profiles**: dev, staging, production configurations
- **Secrets Management**: Credential references (not values)

#### File Extension
`.infra`

#### Users
| User Type | Usage |
|-----------|-------|
| **DevOps Engineers** | Define environment configurations |
| **Platform Engineers** | Manage infrastructure mappings |
| **SRE Teams** | Configure resource limits and monitoring |
| **Security Teams** | Manage credential references |

#### Key Constructs
```
environment, streams, persistence, resources,
kafka (topic, bootstrap_servers, consumer_group),
mongodb (uri, database, collection),
parallelism, memory, checkpoints
```

#### Example
```
environment production

streams
    orders-input:
        type kafka
        topic "prod.orders.incoming"
        bootstrap_servers "${KAFKA_BROKERS}"
        consumer_group "order-processor-prod"

    orders-output:
        type kafka
        topic "prod.orders.processed"
end

persistence
    order-db:
        type mongodb
        uri "${MONGODB_URI}"
        database "orders"
        collection "processed_orders"
end
```

#### Master Compiler Interaction
- **Compilation Order**: First (Phase 1) - before all DSL layers
- **Input**: `.infra` files (selected by environment)
- **Output**: `BindingResolver` instance (not files)
- **Environment Selection Logic**:
  1. Explicit `--infra` flag
  2. `{environment}.infra` matching environment parameter
  3. `default.infra`
  4. `local.infra` or `dev.infra`
  5. First `.infra` file found
- **L1 Integration**: Passes bindings to FlowGenerator for infrastructure-aware code

---

### L6: Master Compiler

#### Purpose
Orchestrates the entire compilation pipeline, managing layer dependencies, import resolution, and code generation coordination.

#### What It Provides
- **Pipeline Orchestration**: Coordinates L0-L5 in correct order
- **Import Resolution**: Topological ordering of files
- **Binding Validation**: Ensures L5 references exist
- **Cross-Layer Type Checking**: Validates schema references
- **Code Generation**: Delegates to layer-specific generators
- **Error Aggregation**: Collects errors from all phases

#### Users
| User Type | Usage |
|-----------|-------|
| **Build Systems** | CI/CD integration via CLI |
| **Developers** | Local compilation via `nexflow build` |
| **IDE Extensions** | Real-time validation |
| **Test Frameworks** | Compilation verification |

#### Compilation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    L6 MASTER COMPILER PIPELINE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: L5 Infrastructure                                         │
│  ├── Find .infra file for environment                              │
│  ├── Parse infrastructure bindings                                  │
│  └── Create BindingResolver                                         │
│                                                                     │
│  Phase 2: L2 Schema                                                 │
│  ├── Discover all .schema files                                    │
│  ├── Resolve imports → topological order                           │
│  ├── Parse each schema definition                                   │
│  └── Generate: Records, Builders, Migrations                       │
│                                                                     │
│  Phase 3: L3 Transform                                              │
│  ├── Discover all .xform files                                     │
│  ├── Resolve imports → topological order                           │
│  ├── Parse transform definitions                                    │
│  ├── Validate against L2 schemas                                   │
│  └── Generate: Transform functions, Expressions                     │
│                                                                     │
│  Phase 4: L4 Rules                                                  │
│  ├── Discover all .rules files                                     │
│  ├── Resolve imports → topological order                           │
│  ├── Parse rule definitions                                         │
│  ├── Validate against L2 schemas                                   │
│  └── Generate: Rule engines, Decision tables                        │
│                                                                     │
│  Phase 5: L1 Flow                                                   │
│  ├── Discover all .proc files                                      │
│  ├── Resolve imports → topological order                           │
│  ├── Parse process definitions                                      │
│  ├── Resolve L5 infrastructure bindings                            │
│  ├── Validate L2/L3/L4 references                                  │
│  └── Generate: Flink jobs, Operators, Sources, Sinks               │
│                                                                     │
│  Final: L0 Runtime                                                  │
│  └── Generate: NexflowRuntime.java                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Key Methods
```python
class MasterCompiler:
    def compile() -> CompilationResult
        # Execute full pipeline

    def validate_bindings() -> List[str]
        # Check all L5 references resolve

    def _compile_layer(phase, files) -> LayerResult
        # Compile single layer with topological ordering

    def _resolve_infra_file() -> Optional[Path]
        # Find appropriate .infra for environment
```

---

## End-of-Day (EOD) Marker System

EOD markers are a cross-layer feature enabling phase-based processing for financial services workflows.

### Three-Date Model

Nexflow implements a three-date model essential for financial processing:

| Date Concept | Source | Usage |
|--------------|--------|-------|
| **Processing Date** | System clock | When record is processed by the system |
| **Business Date** | Calendar service | Logical business day (may differ from processing date) |
| **EOD Markers** | L1 process definition | Named conditions triggering phase transitions |

### Cross-Layer EOD Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EOD MARKER CROSS-LAYER FLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  L1 (ProcDSL) - DEFINES MARKERS                                         │
│  ├── business_date from trading_calendar                               │
│  ├── processing_date auto                                              │
│  ├── markers                                                           │
│  │   ├── market_close: when after "16:00"                             │
│  │   ├── trades_drained: when trades.drained                          │
│  │   └── eod_ready: when market_close and trades_drained              │
│  └── phase before/after eod_ready                                      │
│                                                                         │
│  L4 (RulesDSL) - CONSUMES MARKER STATE                                  │
│  ├── marker eod_1 fired       (boolean condition)                      │
│  ├── marker eod_1 pending     (boolean condition)                      │
│  └── between eod_1 and eod_2  (time window condition)                  │
│                                                                         │
│  L0 (Runtime) - PROVIDES DATE FUNCTIONS                                 │
│  ├── processingDate(context)                                           │
│  ├── businessDate(context)                                             │
│  └── businessDateOffset(context, days)                                 │
│                                                                         │
│  Generated Code - IMPLEMENTS MARKER STATE MACHINE                       │
│  ├── MarkerStateManager (tracks fired/pending)                         │
│  ├── PhaseRouter (routes to before/after logic)                        │
│  └── MarkerConditionEvaluator (for L4 rule conditions)                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Marker Types Summary

| Marker Type | L1 Syntax | Use Case |
|-------------|-----------|----------|
| **Time-based** | `when after "16:00"` | Market close, batch windows |
| **Data-drained** | `when stream.drained` | All data received |
| **Count-based** | `when stream.count >= N` | Threshold triggers |
| **Composite** | `when m1 and m2` | Multi-condition EOD |

### Phase Processing

```
┌─────────────────────────────────────────┐
│           MARKER TIMELINE               │
├─────────────────────────────────────────┤
│                                         │
│  ───────────────┬───────────────────    │
│                 │                       │
│   BEFORE phase  │  AFTER phase          │
│   (intraday)    │  (settlement)         │
│                 │                       │
│                 ▼                       │
│           marker fires                  │
│                                         │
└─────────────────────────────────────────┘
```

---

## Cross-Layer Relationships

### Dependency Graph

```
L1 (Flow) ──imports──► L2 (Schema)
    │                      ▲
    │                      │
    ├──references──► L3 (Transform) ──imports──► L2
    │
    ├──references──► L4 (Rules) ──imports──► L2
    │
    └──bindings──► L5 (Infrastructure)

All Generated Code ──depends──► L0 (Runtime)

L6 (Master Compiler) ──orchestrates──► All Layers
```

### Import System (v0.7.0+)

Files can import definitions from other DSL files:

```
// In order_processing.proc
import ./schemas/order.schema
import ./transforms/enrichment.xform
import ./rules/validation.rules
```

The Master Compiler:
1. Scans all files for import statements
2. Builds dependency graph
3. Detects circular dependencies (error)
4. Produces topological order
5. Processes files in dependency order

---

## User Persona Summary

| Layer | Primary Users | Secondary Users |
|-------|---------------|-----------------|
| **L0** | Generated Code | Nexflow Developers, DevOps |
| **L1** | Data Engineers | Architects, Platform Engineers |
| **L2** | Data Architects | Domain Experts, Data Governance |
| **L3** | Business Analysts | Data Engineers, QA Engineers |
| **L4** | Business Analysts | Compliance, Risk Managers |
| **L5** | DevOps Engineers | Platform Engineers, SRE |
| **L6** | Build Systems | Developers, IDE Extensions |

---

## Generated Output Structure

```
generated/
└── flink/
    └── src/main/java/com/example/
        ├── runtime/
        │   └── NexflowRuntime.java          # L0
        ├── flow/
        │   ├── OrderProcessingJob.java       # L1
        │   ├── OrderReceiveFunction.java     # L1
        │   └── OrderEmitFunction.java        # L1
        ├── schema/
        │   ├── Order.java                    # L2
        │   ├── OrderBuilder.java             # L2
        │   └── OrderMigration.java           # L2
        ├── transform/
        │   ├── EnrichOrderTransform.java     # L3
        │   └── EnrichOrderExpressions.java   # L3
        └── rules/
            ├── ValidationRules.java          # L4
            └── ValidationEngine.java         # L4
```

---

## Design Principles

### Zero-Code Covenant
Users never write Java code. All business logic is expressed in DSLs.

### Layer Isolation
Each layer has a single responsibility:
- L1 = Flow (not logic)
- L2 = Structure (not behavior)
- L3 = Transformation (not orchestration)
- L4 = Decisions (not persistence)
- L5 = Configuration (not logic)

### Infrastructure Abstraction
Logical names in DSL files are resolved to physical resources via L5.

### Compile-Time Safety
All type mismatches and reference errors are caught during compilation.

### Environment Portability
Same DSL files deploy to dev/staging/prod by swapping L5 bindings.

---

## Version Compatibility

| Component | Current Version | Notes |
|-----------|-----------------|-------|
| ProcDSL (L1) | 0.7.0 | Imports, processing_date |
| SchemaDSL (L2) | 1.0.0 | Full feature set |
| TransformDSL (L3) | 1.0.0 | Full feature set |
| RulesDSL (L4) | 1.1.0 | Collection operations |
| Master Compiler (L6) | 1.0.0 | Full pipeline |
