# L12345-04: Event Aggregator (All Layers)

Real-time event aggregation system using all five DSL layers.

## Layers Used
- **L1 ProcDSL**: Windowed aggregation and routing
- **L2 SchemaDSL**: Event and metrics schemas
- **L3 TransformDSL**: Event normalization
- **L4 RulesDSL**: Alerting rules
- **L5 ConfigDSL**: Aggregation windows and thresholds

## Architecture
```
Events → Normalize → Window → Aggregate → Alert Rules → Output
           │           │          │            │
           ▼           ▼          ▼            ▼
       [Schema]    [Tumble]   [Rollup]    [Thresholds]
```

## Files
- `event.schema` - L2 raw event schema
- `metrics.schema` - L2 aggregated metrics
- `event_normalizer.xform` - L3 event normalization
- `alert_rules.rules` - L4 alerting thresholds
- `dev.config` - L5 development windows
- `prod.config` - L5 production windows
- `event_aggregator.proc` - L1 main process

## Build & Run
```bash
nexflow build --config prod.config examples/building-blocks/level-4-full-stack/04-event-aggregator/
```
