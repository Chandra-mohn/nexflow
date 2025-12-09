# Medium Use Case: Fraud Detection Pipeline

**Domain**: Credit Card Fraud Detection
**Complexity**: Medium (enrichment, windowing, multi-stage rules)

## Business Scenario

A credit card company needs real-time fraud detection with:
- Customer profile enrichment from database
- Velocity calculations (transactions per hour/day)
- ML model score integration
- Multi-stage fraud decision logic
- Alert generation for suspicious activity

## Pipeline Flow

```
transactions (Kafka)
    → enrich with customer_profile (MongoDB)
    → calculate_velocity (Window: 1 hour tumbling)
    → fraud_scoring (Transform + ML model)
    → fraud_decision (Rules)
    → alerts / approved / blocked (Kafka)
```

## Files

| File | Layer | Description |
|------|-------|-------------|
| `fraud_schemas.schema` | L2 | Transaction, customer, alert schemas |
| `fraud_transforms.xform` | L3 | Enrichment and scoring transforms |
| `fraud_rules.rules` | L4 | Fraud detection decision tables |
| `fraud_detector.proc` | L1 | Fraud detection pipeline |

## Key Features Demonstrated

- **L1**: Enrichment, windowing, routing, state management
- **L2**: Nested objects, streaming config, state machine
- **L3**: Multi-field transforms, validation, error handling
- **L4**: Decision tables with hit policies, procedural rules

## Testing

```bash
python -m backend.cli generate example/medium/ --output target/medium/
```
