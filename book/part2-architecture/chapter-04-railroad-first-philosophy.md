# Chapter 4: Railroad-First Design Philosophy

> **Source**: Adapted from `docs/L1-Process-Orchestration-DSL.md`
> **Status**: Draft

---

## The Metaphor That Shapes Everything

Before we dive into syntax and semantics, we need to establish the mental model that guides every design decision in Nexflow. This isn't just an analogy—it's the architectural principle that determines what goes where and why.

**The railroad builds the towns, not the other way around.**

---

## Railroads and Towns

Imagine you're building a transcontinental railroad in the 1860s. You have two choices:

### Option A: Town-First
1. Survey where towns already exist
2. Connect them with track
3. Work around their layouts
4. Let each town dictate how the railroad serves them

### Option B: Railroad-First
1. Plan the optimal route for the railroad
2. Build stations at strategic points
3. Towns grow around the stations
4. The railroad's needs shape town development

History chose Option B. The Union Pacific didn't ask permission from non-existent towns—it laid track across the continent, and towns emerged at stations, water stops, and junctions.

**Nexflow takes the same approach to stream processing.**

---

## What This Means for DSL Design

### The Railroad (L1: Process Orchestration)

The `.proc` file is the railroad—the primary artifact that defines:
- Where data enters the system (stations)
- How it flows between processing stages (track)
- Where transformations and enrichments occur (junctions)
- Where data exits (terminal stations)

```
process authorization_enrichment          // The railroad line
  receive events from auth_events         // Entry station
  enrich using customers on card_id       // Junction with lookup
  transform using normalize_amount        // Processing yard
  route using fraud_rules                 // Switching yard
  emit to enriched_auths                  // Terminal station
end
```

The process definition is **primary**. It exists first. Everything else serves it.

### The Towns (L2, L3, L4)

The towns are the domain components that the railroad visits:
- **L2 Schemas** (`.schema`): Data structures at each station
- **L3 Transforms** (`.xform`): Processing capabilities at junctions
- **L4 Rules** (`.rules`): Routing logic at switching yards

These exist to serve the railroad, not the other way around.

```
// The railroad says: "I need a schema called auth_event_schema"
// The town provides it:

schema auth_event_schema                  // A town the railroad visits
  fields
    transaction_id: uuid
    card_id: string
    amount: decimal
  end
end
```

### The Track Configuration (L5: Infrastructure)

The `.infra` file is the physical track specification:
- Rail gauge (Kafka cluster configuration)
- Bridge capacity (parallelism settings)
- Station facilities (checkpoint storage)

```yaml
# production.infra - The physical track specifications
streams:
  auth_events:
    type: kafka
    topic: prod.auth.events.v3
    partitions: 128
```

---

## Why Railroad-First Matters

### 1. Clear Primary Artifact

In many stream processing systems, it's unclear what the "main" thing is:
- Is it the Kafka topics?
- Is it the Flink job?
- Is it the business rules?
- Is it the schema registry?

With railroad-first, the answer is unambiguous: **the `.proc` file is primary**.

Everything else is referenced by name from the process definition. If something isn't referenced by a process, it's not part of the active system.

### 2. Dependency Direction

Dependencies flow **from the railroad to the towns**, never the reverse:

```
.proc → references → .schema (by name)
.proc → references → .xform (by name)
.proc → references → .rules (by name)
.proc → bound by → .infra (at deployment)
```

A schema doesn't know which processes use it. A transform doesn't know when it's called. The process orchestrates; the components serve.

This creates a clean dependency graph:

```
                    ┌──────────┐
                    │  .proc   │
                    │ (L1)     │
                    └────┬─────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      ┌────────┐    ┌────────┐    ┌────────┐
      │.schema │    │ .xform │    │ .rules │
      │  (L2)  │    │  (L3)  │    │  (L4)  │
      └────────┘    └────────┘    └────────┘
```

### 3. Natural Team Boundaries

The railroad-towns split creates natural ownership boundaries:

| Component | Owner | Concern |
|-----------|-------|---------|
| Railroad (`.proc`) | Data Engineering | How data flows |
| Schemas (`.schema`) | Data Governance | What data looks like |
| Transforms (`.xform`) | Analytics Engineering | How data changes |
| Rules (`.rules`) | Business/Risk | What decisions are made |
| Infrastructure (`.infra`) | Platform | Where things run |

The risk analyst editing fraud rules doesn't need to understand the railroad—they just need to know their town will be visited when the railroad reaches it.

### 4. Independent Evolution

Towns can evolve independently as long as they honor their contract with the railroad:

```
// Version 1 of the transform
transform normalize_amount
  input: amount: decimal, currency: string
  output: amount_usd: decimal
end

// Version 2 - internal changes, same interface
transform normalize_amount
  input: amount: decimal, currency: string
  output: amount_usd: decimal
  // Internals completely rewritten
  // Railroad doesn't care
end
```

The railroad only knows: "I call `normalize_amount` with these inputs and get these outputs." How the town implements it is the town's business.

---

## The Anti-Pattern: Town-First Design

What happens when you let towns drive the architecture?

### Schema-First Anti-Pattern

```
// "Let's define all our schemas first, then figure out how to connect them"

schema auth_request { ... }
schema customer { ... }
schema merchant { ... }
schema enriched_auth { ... }
schema settlement { ... }

// Now... how do these connect?
// Who enriches what?
// When does settlement happen?
// ¯\_(ツ)_/¯
```

You end up with orphan schemas, unclear data flow, and no single source of truth for the pipeline.

### Rules-First Anti-Pattern

```
// "Let's define all our business rules first"

rule fraud_detection_v1 { ... }
rule fraud_detection_v2 { ... }
rule velocity_check { ... }
rule geographic_check { ... }

// When do these run?
// In what order?
// What data do they receive?
// ¯\_(ツ)_/¯
```

You end up with a rules library but no clear execution model.

### Infrastructure-First Anti-Pattern

```yaml
# "Let's set up Kafka topics first"

topics:
  - auth-events
  - enriched-auths
  - fraud-results
  - settlements

# Who produces to these?
# Who consumes?
# What's the schema?
# ¯\_(ツ)_/¯
```

You end up with infrastructure waiting for applications that may never materialize as designed.

---

## Railroad-First in Practice

### Starting a New Pipeline

With railroad-first, you start by asking: **What's the flow?**

```
// Step 1: Sketch the railroad
process authorization_enrichment
  receive events from auth_events        // I'll need this input
  enrich using customers on card_id      // I'll need this lookup
  transform using normalize_amount       // I'll need this transform
  route using fraud_rules                // I'll need these rules
  emit to enriched_auths                 // I'll need this output
end
```

Now you know exactly what towns you need to build:
- Schema for `auth_events`
- Lookup source `customers`
- Transform `normalize_amount`
- Rules `fraud_rules`
- Schema for `enriched_auths`

Each town has a clear purpose: **to serve this railroad**.

### Adding a New Feature

When adding features, you ask: **Where on the railroad?**

```
// "We need to add merchant risk scoring"

// Railroad-first: Add to the process
process authorization_enrichment
  receive events from auth_events
  enrich using customers on card_id
  enrich using merchants on merchant_id        // ← New stop
  transform using normalize_amount
  transform using calculate_merchant_risk      // ← New junction
  route using fraud_rules
  emit to enriched_auths
end

// Now build the towns to serve it:
// 1. Merchant lookup (L2)
// 2. Risk calculation transform (L3)
```

The railroad drives the feature; the towns serve it.

### Debugging a Problem

When something breaks, you ask: **Where on the railroad?**

```
// "Enriched auths are missing customer names"

// Follow the railroad:
process authorization_enrichment
  receive events from auth_events              // ✓ Events arriving?
  enrich using customers on card_id            // ← Suspect: lookup failing?
  ...
```

The railroad is the execution trace. Follow the track to find the broken town.

---

## Summary

Railroad-first design isn't just a metaphor—it's a structural principle:

1. **The process (`.proc`) is primary**: Everything exists to serve it
2. **Dependencies flow outward**: Railroad → Towns, never reverse
3. **Teams align to components**: Clear ownership boundaries
4. **Evolution is independent**: Towns change without railroad knowledge

This philosophy shapes every syntax decision, every file extension, and every team workflow in Nexflow.

In the next chapter, we'll see how this philosophy translates into the concrete syntax of L1 Process Orchestration.
