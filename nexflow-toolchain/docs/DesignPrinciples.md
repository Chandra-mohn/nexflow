#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Design Principles

## The Fundamental Problem

Modern stream processing systems suffer from a **semantic gap** - the chasm between what business stakeholders think and what engineers build. A credit analyst thinks in terms of "if the applicant's debt-to-income ratio exceeds 43%, decline the application." An engineer thinks in terms of Kafka consumers, Flink operators, serialization formats, and state backends.

This semantic gap creates:
- **Translation loss** - Business intent gets distorted through layers of technical interpretation
- **Maintenance burden** - When rules change, engineers must decode intent from implementation
- **Audit opacity** - Regulators can't trace from business policy to running code
- **Velocity friction** - Simple rule changes require full development cycles

Nexflow exists to **collapse this semantic gap** through domain-aligned language layers.

---

## Core Principles

### 1. Zero-Code Covenant

Users should never write Java code. All business logic is expressed in DSLs. The toolchain generates production-ready code from high-level specifications, eliminating the cognitive burden of infrastructure concerns.

### 2. Stream-Native Process Composition

Processes communicate exclusively through streams and business signals, never through direct invocation. This ensures:

- **Fault isolation** - Process failures don't cascade; message queues buffer during recovery
- **Independent scaling** - Each process scales based on its own load characteristics
- **Testability** - Processes can be tested in isolation with mock streams
- **Explicit topology** - Data flow is visible in the DSL, not hidden in call graphs

Processes declare what they consume and produce. The runtime orchestrates execution automatically based on data availability and business markers.

### 3. Layer Separation

Each DSL layer has a single responsibility:

- **Process layer** orchestrates data flow - it is the "railroad," NOT business logic
- **Schema layer** defines data contracts - structure and constraints
- **Transform layer** contains data derivation logic - pure functional mappings
- **Rules layer** expresses business policy - decision logic in domain terms

This separation ensures that:
- A business analyst can modify rules without touching flow orchestration
- A data architect can evolve schemas with backward compatibility
- A platform engineer can optimize parallelism without breaking business logic
- Each layer can be versioned, tested, and deployed independently

### 4. Infrastructure Abstraction

Logical names in DSL files are resolved to physical resources through bindings. Business logic never references specific servers, topics, or connection strings. This enables environment portability and infrastructure evolution without DSL changes.

### 5. Compile-Time Safety

All type mismatches and reference errors are caught at compile time. The system validates cross-layer dependencies, ensuring that referenced schemas, transforms, and rules exist and are compatible before any code is generated.

---

## Technology Philosophy

### The Immutable Event Spine

The event stream serves as an **immutable, ordered log of truth**. Every business event is captured with its exact timestamp, preserving causality. This enables:
- **Time travel** - Replay from any point to debug, audit, or recover
- **Decoupled evolution** - Producers and consumers evolve independently
- **Exactly-once semantics** - When combined with checkpointing

The event stream is the **nervous system** - every signal flows through it.

### The Stateful Processing Engine

The stream processor provides **continuous, stateful computation over unbounded streams**. It thinks in event-time, handles late data gracefully, and maintains consistent state across failures. Key capabilities:
- True separation of compute and storage
- Rich windowing semantics for temporal aggregations
- Savepoints for deployment without data loss
- Backpressure handling at scale

The processor is the **cognitive engine** - it reasons about events as they flow.

### The System of Record

The operational database serves as the **materialized view of current state**. Decisions are persisted asynchronously - the stream never blocks on persistence. This isn't the event log - it's where current truth lives for operational queries.

### The Analytical Memory

The data lake stores history for analysis. Columnar storage provides:
- Efficiency for analytical queries
- Schema evolution for changing business needs
- Time-partitioned storage for historical analysis

This is the **reporting layer** - where business intelligence, ML training, and compliance reporting draw from.

---

## The Async Persistence Model

Data flows through processing continuously, but persistence happens at **deliberate checkpoints** - semantic boundaries where state matters:

- **Ingestion** - Raw event lands (audit trail begins)
- **Decision** - Business outcome recorded (compliance checkpoint)
- **Emission** - Final state materialized (system of record updated)

Why async?
1. **Non-blocking flow** - The stream never waits for disk I/O
2. **Failure isolation** - Persistence failure doesn't halt processing
3. **Backpressure management** - Write pressure doesn't cascade upstream
4. **Eventual consistency** - Acceptable for operational stores; the event stream provides the true timeline

---

## The Multi-Layer DSL Philosophy

### Why Layers?

Each layer speaks a **different domain language** to a **different audience**:

| Layer | Audience | Language Style | Concern |
|-------|----------|----------------|---------|
| Rules | Business Analysts, Risk Officers | "when debt_ratio > 0.43 then decline" | Business policy |
| Transform | Data Engineers, Integration Specialists | "enriched.score = raw.score * factor" | Data derivation |
| Schema | Data Architects, API Designers | "field customer_id: string @pii" | Data contracts |
| Process | Platform Engineers, System Architects | "receive -> transform -> emit" | Flow orchestration |

### The Separation Principle

- **Process** doesn't know *what* data looks like - only *how* it flows
- **Schema** doesn't know *where* data goes - only *what shape* it has
- **Transform** doesn't know *why* decisions are made - only *how* data maps
- **Rules** doesn't know *how* execution happens - only *what* the business policy is

---

## Compilation Philosophy

Nexflow **compiles to native runtime code** rather than interpreting DSL at runtime. This is crucial:

1. **Type safety** - Errors caught at build time, not in production at 3 AM
2. **Performance** - No runtime parsing overhead; JIT can optimize fully
3. **Debuggability** - Generated code is readable, debuggable, traceable
4. **Portability** - Output is standard runtime code - no vendor lock-in

The DSL is for **humans**. The generated code is for **machines**. The AST is the **bridge** where validation, optimization, and cross-layer type checking occur.

---

## The Three-Date Model

For financial processing, Nexflow implements a three-date model:

- **Processing Date** - System time when record is processed
- **Business Date** - Logical business day from calendar context
- **EOD Markers** - Named conditions that signal phase transitions

This enables phase-based processing where different logic applies before and after business day boundaries - essential for settlement, reconciliation, and regulatory reporting.

---

## The Ultimate Goal

A business analyst should be able to read:

```
when applicant.debt_to_income > 0.43 then "decline"
when applicant.credit_score < 620 then "decline"
otherwise "approve"
```

...and know **exactly** what the running system does, without translation, without interpretation, without asking an engineer.

That's the promise of Nexflow: **executable business intent**.
