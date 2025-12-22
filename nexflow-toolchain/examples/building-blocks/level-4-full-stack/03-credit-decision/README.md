# L12345-03: Credit Decision (All Layers)

Automated credit decisioning system using all five DSL layers.

## Layers Used
- **L1 ProcDSL**: Application flow with parallel enrichment
- **L2 SchemaDSL**: Application and decision schemas
- **L3 TransformDSL**: Credit score enrichment
- **L4 RulesDSL**: Underwriting rules
- **L5 ConfigDSL**: Risk thresholds by environment

## Architecture
```
Application → Enrich → Score → Underwrite → Decision
                │         │         │
                ▼         ▼         ▼
           [Bureau]   [Model]   [Rules]
```

## Files
- `application.schema` - L2 loan application
- `decision.schema` - L2 credit decision
- `credit_enrichment.xform` - L3 bureau data
- `underwriting_rules.rules` - L4 decision rules
- `dev.config` - L5 development config
- `prod.config` - L5 production config
- `credit_decision.proc` - L1 main process

## Build & Run
```bash
nexflow build --config prod.config examples/building-blocks/level-4-full-stack/03-credit-decision/
```
