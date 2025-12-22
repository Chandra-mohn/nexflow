# L234-04: Full Logic Layer (L2 + L3 + L4)

Complete business logic layer without flow orchestration.

## Layers Used
- **L2 SchemaDSL**: Type definitions
- **L3 TransformDSL**: Data transformations
- **L4 RulesDSL**: Business rules

## Pattern
```
Input Schema → Transform → Rules → Output Schema
```

## Files
- `order_input.schema` - L2 input schema
- `order_output.schema` - L2 output schema
- `order_transform.xform` - L3 field mappings
- `order_rules.rules` - L4 business logic

## Key Concepts
- Reusable logic layer independent of flow
- Schema-to-schema transformations with rules
- Can be embedded in any L1 flow

## Build & Run
```bash
nexflow build examples/building-blocks/level-3-multi-layer/04-full-logic-layer/
```
