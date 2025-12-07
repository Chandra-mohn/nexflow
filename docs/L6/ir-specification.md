# L6: Intermediate Representation Specification

> **Layer**: L6 - Compilation Pipeline
> **Status**: Specification
> **Version**: 1.0.0
> **Last Updated**: 2025-11-30

---

## 1. Overview

### 1.1 Purpose

The Intermediate Representation (IR) is the unified, runtime-agnostic representation that bridges AST analysis and code generation. It captures:

- **Data flow** as directed edges between operators
- **Operators** as typed nodes with inputs/outputs
- **Execution semantics** (parallelism, time, state)
- **Optimization opportunities** for efficient code generation

### 1.2 Position in Compilation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Nexflow Compilation Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   L1-L4 Source Files                                                 │
│         │                                                            │
│         ▼                                                            │
│   ┌───────────────┐                                                  │
│   │ Lexer/Parser  │  (ANTLR4)                                       │
│   └───────┬───────┘                                                  │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                  │
│   │     AST       │  (Abstract Syntax Tree)                         │
│   └───────┬───────┘                                                  │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                  │
│   │   Semantic    │  Reference resolution, type checking            │
│   │   Analysis    │                                                  │
│   └───────┬───────┘                                                  │
│           │                                                          │
│           ▼                                                          │
│   ╔═══════════════╗                                                  │
│   ║      IR       ║  ◄── THIS DOCUMENT                              │
│   ║ (Unified DAG) ║                                                  │
│   ╚═══════╤═══════╝                                                  │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                  │
│   │  Optimization │  Passes applied to IR                           │
│   │    Passes     │                                                  │
│   └───────┬───────┘                                                  │
│           │                                                          │
│           ├──────────────┬───────────────┐                          │
│           ▼              ▼               ▼                          │
│   ┌───────────┐   ┌───────────┐   ┌───────────┐                    │
│   │ Flink Gen │   │ Spark Gen │   │ KStreams  │                    │
│   └───────────┘   └───────────┘   └───────────┘                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. IR Node Types

### 2.1 Node Hierarchy

```
IRNode (abstract)
├── SourceNode          # Data ingestion points
├── SinkNode            # Data emission points
├── OperatorNode        # Processing operations
│   ├── TransformNode   # L3 transforms
│   ├── RouteNode       # L4 routing decisions
│   ├── EnrichNode      # Lookup enrichment
│   ├── AggregateNode   # Windowed aggregations
│   ├── JoinNode        # Stream/stream joins
│   ├── CorrelateNode   # Await/hold patterns
│   └── FilterNode      # Predicate filtering
└── MetaNode            # Compilation metadata
```

### 2.2 SourceNode

Represents a data ingestion point from an external system.

```typescript
interface SourceNode {
  // Identity
  id: string;                    // Unique node identifier
  name: string;                  // Logical name from L1

  // Physical binding (from L5)
  binding: StreamBinding;
  physicalName: string;          // e.g., "kafka://broker:9092/topic"

  // Schema (from L2)
  schema: SchemaRef;             // Reference to L2 schema
  outputFields: Field[];         // Projected fields

  // Watermark configuration
  watermark?: {
    field: string;               // Timestamp field
    delay: Duration;             // Allowed lateness
    strategy: 'bounded' | 'monotonic' | 'idle';
  };

  // Execution config
  parallelism?: number;          // Source-specific parallelism

  // Metadata
  sourceLocation: SourceLocation; // .proc file location
}
```

**Example**:
```json
{
  "id": "src_auth_events",
  "name": "auth_events",
  "binding": {
    "type": "kafka",
    "topic": "prod.auth.events.v3",
    "brokers": "${KAFKA_BROKERS}"
  },
  "schema": { "ref": "auth_event_v1" },
  "outputFields": [
    { "name": "event_id", "type": "string" },
    { "name": "card_id", "type": "string" },
    { "name": "amount", "type": "decimal(15,2)" },
    { "name": "event_timestamp", "type": "timestamp" }
  ],
  "watermark": {
    "field": "event_timestamp",
    "delay": "30s",
    "strategy": "bounded"
  }
}
```

### 2.3 SinkNode

Represents a data emission point to an external system.

```typescript
interface SinkNode {
  // Identity
  id: string;
  name: string;

  // Physical binding (from L5)
  binding: StreamBinding;
  physicalName: string;

  // Schema
  inputSchema: SchemaRef;

  // Fanout strategy (from L1 emit)
  fanout?: {
    strategy: 'broadcast' | 'partition' | 'round_robin';
    partitionKey?: string[];
  };

  // Write semantics
  deliveryGuarantee: 'at_least_once' | 'exactly_once';

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.4 TransformNode

Represents an L3 transform application.

```typescript
interface TransformNode {
  // Identity
  id: string;
  name: string;

  // Transform reference (from L3)
  transformRef: {
    name: string;
    version?: string;
  };

  // Type information
  inputSchema: SchemaRef;
  outputSchema: SchemaRef;

  // Purity (from L3)
  pure: boolean;

  // Caching (from L3)
  cache?: {
    enabled: boolean;
    ttl?: Duration;
    maxSize?: number;
  };

  // Generated UDF reference
  udfClassName?: string;

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.5 RouteNode

Represents an L4 routing decision.

```typescript
interface RouteNode {
  // Identity
  id: string;
  name: string;

  // Rule reference (from L4)
  ruleRef: {
    name: string;
    type: 'decision_table' | 'procedural_rule';
  };

  // Routing outcomes
  outcomes: {
    name: string;
    targetSinkId: string;
    probability?: number;  // For analytics
  }[];

  // Hit policy (from L4)
  hitPolicy: 'first_match' | 'single_hit' | 'multi_hit';

  // Generated UDF reference
  udfClassName?: string;

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.6 EnrichNode

Represents a lookup enrichment operation.

```typescript
interface EnrichNode {
  // Identity
  id: string;
  name: string;

  // Lookup binding (from L5)
  lookupRef: {
    name: string;
    binding: LookupBinding;
  };

  // Join specification
  joinType: 'inner' | 'left' | 'right';
  joinKeys: {
    streamField: string;
    lookupField: string;
  }[];

  // Field selection
  selectFields: string[];

  // Async lookup config
  async?: {
    capacity: number;
    timeout: Duration;
    ordered: boolean;
  };

  // Cache config (from L5)
  cache?: CacheConfig;

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.7 AggregateNode

Represents a windowed aggregation operation.

```typescript
interface AggregateNode {
  // Identity
  id: string;
  name: string;

  // Window specification (from L1)
  window: {
    type: 'tumbling' | 'sliding' | 'session';
    size: Duration;
    slide?: Duration;        // For sliding windows
    gap?: Duration;          // For session windows
  };

  // Grouping
  groupByFields: string[];

  // Aggregations (from L4)
  aggregations: {
    outputField: string;
    function: 'count' | 'sum' | 'avg' | 'min' | 'max' | 'first' | 'last';
    inputField?: string;
  }[];

  // Late data handling
  allowedLateness?: Duration;
  lateDataOutput?: string;   // Sink for late data

  // State management
  stateBackend?: string;     // Reference to L5 state config

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.8 JoinNode

Represents a stream-stream join operation.

```typescript
interface JoinNode {
  // Identity
  id: string;
  name: string;

  // Join specification
  joinType: 'inner' | 'left' | 'right' | 'full';

  // Join inputs
  leftInput: string;         // Node ID
  rightInput: string;        // Node ID

  // Join condition
  joinKeys: {
    leftField: string;
    rightField: string;
  }[];

  // Time bounds (for stream-stream joins)
  timeBounds?: {
    leftBefore: Duration;
    leftAfter: Duration;
    rightBefore: Duration;
    rightAfter: Duration;
  };

  // Output schema
  outputSchema: SchemaRef;

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.9 CorrelateNode

Represents an await/hold correlation pattern.

```typescript
interface CorrelateNode {
  // Identity
  id: string;
  name: string;

  // Correlation type (from L1)
  correlationType: 'await' | 'hold';

  // Primary and secondary streams
  primaryStream: string;     // Node ID
  secondaryStream: string;   // Node ID

  // Correlation key
  correlationKeys: {
    primaryField: string;
    secondaryField: string;
  }[];

  // Timeout handling
  timeout: {
    duration: Duration;
    action: {
      type: 'emit' | 'discard' | 'route';
      target?: string;       // Sink for timeout
    };
  };

  // State management
  stateBackend?: string;

  // Metadata
  sourceLocation: SourceLocation;
}
```

### 2.10 FilterNode

Represents a predicate filter operation.

```typescript
interface FilterNode {
  // Identity
  id: string;
  name: string;

  // Filter predicate
  predicate: Expression;     // Boolean expression tree

  // Schema passthrough
  inputSchema: SchemaRef;
  outputSchema: SchemaRef;   // Same as input

  // Metadata
  sourceLocation: SourceLocation;
}
```

---

## 3. IR Edges

### 3.1 Edge Specification

```typescript
interface IREdge {
  // Identity
  id: string;

  // Source and target
  sourceNodeId: string;
  sourcePort: string;        // 'output' or named port
  targetNodeId: string;
  targetPort: string;        // 'input' or named port

  // Partitioning
  partitioning: {
    strategy: 'forward' | 'hash' | 'broadcast' | 'rebalance';
    keyFields?: string[];    // For hash partitioning
  };

  // Schema on edge
  schema: SchemaRef;

  // Data characteristics (for optimization)
  characteristics?: {
    estimatedThroughput?: number;  // records/sec
    avgRecordSize?: number;        // bytes
    isOrdered?: boolean;
  };
}
```

### 3.2 Partitioning Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `forward` | No shuffle, same parallelism | Sequential operators |
| `hash` | Hash by key fields | Joins, group-by |
| `broadcast` | Send to all partitions | Small dimension tables |
| `rebalance` | Round-robin distribution | Load balancing |

---

## 4. IR Graph

### 4.1 Graph Structure

```typescript
interface IRGraph {
  // Identity
  processName: string;
  version: string;

  // Graph contents
  nodes: Map<string, IRNode>;
  edges: Map<string, IREdge>;

  // Entry and exit points
  sources: string[];         // Source node IDs
  sinks: string[];           // Sink node IDs

  // Execution configuration (from L1)
  execution: {
    parallelism: number;
    maxParallelism?: number;
    executionMode: 'streaming' | 'batch' | 'micro_batch';

    time?: {
      characteristic: 'event_time' | 'processing_time';
      watermarkInterval?: Duration;
    };

    checkpointing?: {
      interval: Duration;
      mode: 'exactly_once' | 'at_least_once';
    };
  };

  // State configuration (from L1 + L5)
  state?: {
    backend: string;         // L5 state backend reference
    ttl?: Duration;
  };

  // Resilience (from L1)
  resilience?: {
    restartStrategy: string;
    maxRestarts?: number;
    restartDelay?: Duration;
  };

  // Metadata
  compiledAt: Timestamp;
  compilerVersion: string;
  sourceFiles: SourceFile[];
}
```

### 4.2 Example IR Graph

```json
{
  "processName": "authorization_enrichment",
  "version": "1.0.0",
  "nodes": {
    "src_auth_events": {
      "type": "SourceNode",
      "name": "auth_events",
      "binding": { "type": "kafka", "topic": "prod.auth.events.v3" },
      "schema": { "ref": "auth_event_v1" }
    },
    "enrich_customer": {
      "type": "EnrichNode",
      "name": "customer_lookup",
      "lookupRef": { "name": "customers" },
      "joinType": "left",
      "joinKeys": [{ "streamField": "card_id", "lookupField": "card_id" }]
    },
    "route_fraud": {
      "type": "RouteNode",
      "name": "fraud_detection",
      "ruleRef": { "name": "fraud_detection_v2", "type": "decision_table" },
      "outcomes": [
        { "name": "approved", "targetSinkId": "sink_approved" },
        { "name": "declined", "targetSinkId": "sink_declined" },
        { "name": "review", "targetSinkId": "sink_review" }
      ],
      "hitPolicy": "first_match"
    },
    "sink_approved": {
      "type": "SinkNode",
      "name": "approved_auths",
      "binding": { "type": "kafka", "topic": "prod.auth.approved.v3" }
    },
    "sink_declined": {
      "type": "SinkNode",
      "name": "declined_auths",
      "binding": { "type": "kafka", "topic": "prod.auth.declined.v3" }
    },
    "sink_review": {
      "type": "SinkNode",
      "name": "review_auths",
      "binding": { "type": "kafka", "topic": "prod.auth.review.v3" }
    }
  },
  "edges": {
    "e1": {
      "sourceNodeId": "src_auth_events",
      "targetNodeId": "enrich_customer",
      "partitioning": { "strategy": "hash", "keyFields": ["card_id"] }
    },
    "e2": {
      "sourceNodeId": "enrich_customer",
      "targetNodeId": "route_fraud",
      "partitioning": { "strategy": "forward" }
    },
    "e3_approved": {
      "sourceNodeId": "route_fraud",
      "sourcePort": "approved",
      "targetNodeId": "sink_approved",
      "partitioning": { "strategy": "forward" }
    }
  },
  "sources": ["src_auth_events"],
  "sinks": ["sink_approved", "sink_declined", "sink_review"],
  "execution": {
    "parallelism": 128,
    "executionMode": "streaming",
    "time": {
      "characteristic": "event_time",
      "watermarkInterval": "1s"
    }
  }
}
```

---

## 5. Type System

### 5.1 Base Types

| Type | Description | IR Representation |
|------|-------------|-------------------|
| `string` | Text | `{ "type": "string" }` |
| `integer` | 64-bit signed int | `{ "type": "integer" }` |
| `decimal` | Arbitrary precision | `{ "type": "decimal", "precision": 15, "scale": 2 }` |
| `boolean` | True/false | `{ "type": "boolean" }` |
| `timestamp` | Date + time | `{ "type": "timestamp", "precision": 3 }` |
| `date` | Date only | `{ "type": "date" }` |
| `bytes` | Binary data | `{ "type": "bytes" }` |

### 5.2 Complex Types

| Type | Description | IR Representation |
|------|-------------|-------------------|
| `array<T>` | List | `{ "type": "array", "elementType": T }` |
| `map<K,V>` | Dictionary | `{ "type": "map", "keyType": K, "valueType": V }` |
| `row` | Structured | `{ "type": "row", "fields": [...] }` |

### 5.3 Field Specification

```typescript
interface Field {
  name: string;
  type: TypeSpec;
  nullable: boolean;
  metadata?: {
    description?: string;
    source?: string;          // Which L2 schema
    derived?: boolean;        // Computed field
  };
}
```

---

## 6. Expression Trees

### 6.1 Expression Node Types

```typescript
type Expression =
  | LiteralExpr
  | FieldRefExpr
  | BinaryExpr
  | UnaryExpr
  | FunctionCallExpr
  | CaseExpr
  | CastExpr
  | IsNullExpr;

interface LiteralExpr {
  type: 'literal';
  value: any;
  dataType: TypeSpec;
}

interface FieldRefExpr {
  type: 'field_ref';
  fieldPath: string[];      // ["customer", "address", "city"]
}

interface BinaryExpr {
  type: 'binary';
  operator: '+' | '-' | '*' | '/' | '=' | '!=' | '<' | '>' | 'AND' | 'OR';
  left: Expression;
  right: Expression;
}

interface FunctionCallExpr {
  type: 'function_call';
  functionName: string;
  arguments: Expression[];
}

interface CaseExpr {
  type: 'case';
  branches: { condition: Expression; result: Expression }[];
  default?: Expression;
}
```

---

## 7. Optimization Passes

### 7.1 Pass Interface

```typescript
interface OptimizationPass {
  name: string;
  priority: number;          // Lower = earlier
  apply(graph: IRGraph): IRGraph;
  isApplicable(graph: IRGraph): boolean;
}
```

### 7.2 Standard Passes

| Pass | Priority | Description |
|------|----------|-------------|
| Predicate Pushdown | 10 | Move filters closer to sources |
| Projection Pushdown | 20 | Remove unused fields early |
| Operator Fusion | 30 | Combine sequential operators |
| Partition Alignment | 40 | Optimize shuffle operations |
| Dead Code Elimination | 50 | Remove unreachable nodes |
| Common Subexpression | 60 | Reuse repeated calculations |

### 7.3 Predicate Pushdown Example

**Before**:
```
SourceNode → TransformNode → FilterNode(amount > 1000)
```

**After**:
```
SourceNode(filter: amount > 1000) → TransformNode
```

### 7.4 Operator Fusion Example

**Before**:
```
TransformNode(normalize_amount) → TransformNode(calculate_fee) → TransformNode(format_output)
```

**After**:
```
FusedTransformNode([normalize_amount, calculate_fee, format_output])
```

---

## 8. Serialization Format

### 8.1 JSON Schema

The IR is serialized as JSON for portability and debugging. A JSON Schema is provided for validation.

### 8.2 Binary Format (Optional)

For large graphs, a binary format (Protocol Buffers or FlatBuffers) may be used for efficiency.

### 8.3 Debug Format

Human-readable text format for debugging:

```
PROCESS: authorization_enrichment
PARALLELISM: 128
MODE: streaming

SOURCES:
  [src_auth_events] Kafka<prod.auth.events.v3> → schema:auth_event_v1

OPERATORS:
  [enrich_customer] EnrichLookup(customers) ON card_id
    ← src_auth_events (hash: card_id)

  [route_fraud] Route(fraud_detection_v2)
    ← enrich_customer (forward)
    → approved: sink_approved
    → declined: sink_declined
    → review: sink_review

SINKS:
  [sink_approved] Kafka<prod.auth.approved.v3>
  [sink_declined] Kafka<prod.auth.declined.v3>
  [sink_review] Kafka<prod.auth.review.v3>
```

---

## 9. Validation Rules

### 9.1 Structural Validation

| Rule | Description |
|------|-------------|
| Acyclic graph | No cycles in the DAG |
| Connected sources | All sources reach at least one sink |
| Connected sinks | All sinks reachable from at least one source |
| Valid edges | All edge references exist |

### 9.2 Type Validation

| Rule | Description |
|------|-------------|
| Schema compatibility | Edge schemas match connected nodes |
| Join key types | Join keys have compatible types |
| Aggregation types | Aggregation functions valid for field types |

### 9.3 Semantic Validation

| Rule | Description |
|------|-------------|
| Watermark field exists | Watermark field present in source schema |
| Partition key exists | Partition keys present in schema |
| Correlation keys match | Correlation keys exist in both streams |

---

## 10. Code Generation Interface

### 10.1 Generator Interface

```typescript
interface CodeGenerator {
  targetRuntime: string;     // 'flink', 'spark', 'kafka-streams'

  generateDDL(graph: IRGraph): string[];
  generateDML(graph: IRGraph): string[];
  generateUDFs(graph: IRGraph): CompiledUDF[];
  generateConfig(graph: IRGraph): RuntimeConfig;

  validate(graph: IRGraph): ValidationResult;
}
```

### 10.2 Target-Specific Extensions

Each target runtime may extend IR nodes with target-specific properties:

```typescript
interface FlinkSourceNode extends SourceNode {
  flinkConnector: string;
  flinkFormat: string;
  flinkProperties: Map<string, string>;
}
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-30 | - | Initial specification |
