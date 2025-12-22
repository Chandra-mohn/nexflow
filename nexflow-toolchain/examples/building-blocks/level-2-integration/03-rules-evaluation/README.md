# L12-03: Rules Evaluation (L1 + L4)

Stream processing with business rules decision tables.

## Layers Used
- **L1 ProcDSL**: Data flow orchestration
- **L4 RulesDSL**: Decision table evaluation

## Pattern
```
Kafka Source → Evaluate Decision Table → Route by Decision → Kafka Sinks
```

## Files
- `credit_rules.rules` - L4 decision table
- `rules_evaluation.proc` - L1 process with rules

## Key Concepts
- Rules evaluation: `evaluate using credit_decision_table`
- Decision-based routing
- Rules result access

## Build & Run
```bash
nexflow build examples/building-blocks/level-2-integration/03-rules-evaluation/
```
