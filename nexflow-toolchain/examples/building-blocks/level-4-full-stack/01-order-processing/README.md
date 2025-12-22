# L12345-01: Order Processing (All Layers)

Complete order processing system using all five DSL layers.

## Layers Used
- **L1 ProcDSL**: Flow orchestration with routing and error handling
- **L2 SchemaDSL**: Order and fulfillment type definitions
- **L3 TransformDSL**: Order enrichment and calculations
- **L4 RulesDSL**: Pricing, shipping, and validation rules
- **L5 ConfigDSL**: Environment-specific configuration

## Architecture
```
                    ┌─────────────┐
                    │  L5 Config  │
                    └──────┬──────┘
                           │
┌──────────┐    ┌──────────▼──────────┐    ┌──────────┐
│ L2 Input │───▶│     L1 Process      │───▶│ L2 Output│
│  Schema  │    │  ┌────────────────┐ │    │  Schema  │
└──────────┘    │  │ L3 Transform   │ │    └──────────┘
                │  │ L4 Rules       │ │
                │  └────────────────┘ │
                └─────────────────────┘
```

## Files
- `order.schema` - L2 order input schema
- `fulfillment.schema` - L2 fulfillment output schema
- `order_enrichment.xform` - L3 transformations
- `order_business_rules.rules` - L4 business rules
- `dev.config` - L5 development config
- `prod.config` - L5 production config
- `order_processing.proc` - L1 main process

## Build & Run
```bash
# Development
nexflow build --config dev.config examples/building-blocks/level-4-full-stack/01-order-processing/

# Production
nexflow build --config prod.config examples/building-blocks/level-4-full-stack/01-order-processing/
```
