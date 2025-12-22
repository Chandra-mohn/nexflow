# L12-04: Schema Transform (L2 + L3)

Transform between two different schema types.

## Layers Used
- **L2 SchemaDSL**: Input and output schema definitions
- **L3 TransformDSL**: Field mappings between schemas

## Pattern
```
Input Schema → Transform Mapping → Output Schema
```

## Files
- `input_order.schema` - L2 input schema
- `output_summary.schema` - L2 output schema
- `order_to_summary.xform` - L3 transform between schemas

## Key Concepts
- Typed input/output schemas
- Field projection and renaming
- Nested field flattening
- Calculated output fields

## Build & Run
```bash
nexflow build examples/building-blocks/level-2-integration/04-schema-transform/
```
