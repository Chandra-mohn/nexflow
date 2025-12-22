# L12-06: Typed Rules (L2 + L4)

Schema-driven decision tables with typed inputs/outputs.

## Layers Used
- **L2 SchemaDSL**: Input/output type definitions
- **L4 RulesDSL**: Decision table with schema types

## Pattern
```
Input Schema → Decision Table → Output Schema
```

## Files
- `application.schema` - L2 input schema
- `decision_result.schema` - L2 output schema
- `typed_decision.rules` - L4 rules with schema types

## Key Concepts
- Schema-typed decision table inputs
- Typed return values
- Validation at rules boundary

## Build & Run
```bash
nexflow build examples/building-blocks/level-2-integration/06-typed-rules/
```
