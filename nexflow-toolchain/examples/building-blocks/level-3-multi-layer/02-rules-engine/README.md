# L124-02: Rules Engine (L1 + L2 + L4)

Stream processing with schema-driven business rules.

## Layers Used
- **L1 ProcDSL**: Flow orchestration with evaluate
- **L2 SchemaDSL**: Type definitions
- **L4 RulesDSL**: Business rule definitions

## Pattern
```
Typed Input → Rules Evaluation → Typed Decision Output
```

## Files
- `insurance_claim.schema` - L2 claim input schema
- `claim_decision.schema` - L2 decision output schema
- `claim_rules.rules` - L4 business rules
- `rules_engine.proc` - L1 flow with rule evaluation

## Key Concepts
- Schema-typed rule inputs
- Decision tables for business logic
- Rule-driven stream processing

## Build & Run
```bash
nexflow build examples/building-blocks/level-3-multi-layer/02-rules-engine/
```
