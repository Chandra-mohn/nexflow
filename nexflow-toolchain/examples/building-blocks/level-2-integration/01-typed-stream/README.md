# L12-01: Typed Stream (L1 + L2)

Schema-validated Kafka flow combining ProcDSL with SchemaDSL.

## Layers Used
- **L1 ProcDSL**: Data flow orchestration
- **L2 SchemaDSL**: Schema validation

## Pattern
```
Kafka Source → Schema Validation → Valid/Invalid Routing → Kafka Sinks
```

## Files
- `order.schema` - L2 schema definition with constraints
- `typed_stream.proc` - L1 process with schema validation

## Key Concepts
- Schema reference in process: `receive orders: Order from ...`
- Validation error routing
- Type-safe record access

## Build & Run
```bash
nexflow build examples/building-blocks/level-2-integration/01-typed-stream/
```
