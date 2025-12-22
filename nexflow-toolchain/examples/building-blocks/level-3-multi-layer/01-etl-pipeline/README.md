# L123-01: ETL Pipeline (L1 + L2 + L3)

Complete Extract-Transform-Load pipeline with type safety.

## Layers Used
- **L1 ProcDSL**: Flow orchestration
- **L2 SchemaDSL**: Input/output type definitions
- **L3 TransformDSL**: Data transformation logic

## Pattern
```
Typed Source → Transform → Typed Sink
```

## Files
- `raw_event.schema` - L2 input schema (raw data)
- `enriched_event.schema` - L2 output schema (cleaned/enriched)
- `event_transform.xform` - L3 transformation rules
- `etl_pipeline.proc` - L1 flow orchestration

## Key Concepts
- Schema validation at boundaries
- Complex transformations with lookups
- Type-safe end-to-end pipeline

## Build & Run
```bash
nexflow build examples/building-blocks/level-3-multi-layer/01-etl-pipeline/
```
