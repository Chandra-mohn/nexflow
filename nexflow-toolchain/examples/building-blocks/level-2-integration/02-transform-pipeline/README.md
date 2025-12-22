# L12-02: Transform Pipeline (L1 + L3)

Stream processing with field transformations.

## Layers Used
- **L1 ProcDSL**: Data flow orchestration
- **L3 TransformDSL**: Field mappings and calculations

## Pattern
```
Kafka Source → Transform (map/calculate) → Kafka Sink
```

## Files
- `order_transform.xform` - L3 transform definition
- `transform_pipeline.proc` - L1 process using transform

## Key Concepts
- Transform reference: `transform using order_enricher`
- Calculated fields
- Field mapping and projection

## Build & Run
```bash
nexflow build examples/building-blocks/level-2-integration/02-transform-pipeline/
```
