# L134-03: Enrich and Decide (L1 + L3 + L4)

Transform/enrich data then apply business rules.

## Layers Used
- **L1 ProcDSL**: Flow orchestration
- **L3 TransformDSL**: Data enrichment
- **L4 RulesDSL**: Decision logic

## Pattern
```
Raw Input → Enrich/Transform → Business Rules → Decision Output
```

## Files
- `enrich_transaction.xform` - L3 enrichment logic
- `transaction_rules.rules` - L4 decision rules
- `enrich_decide.proc` - L1 flow orchestration

## Key Concepts
- Enrichment before rule evaluation
- Lookups feeding into decisions
- Combined transformation and rules

## Build & Run
```bash
nexflow build examples/building-blocks/level-3-multi-layer/03-enrich-and-decide/
```
