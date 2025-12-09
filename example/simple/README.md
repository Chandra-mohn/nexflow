# Simple Use Case: Basic Transaction Validation

**Domain**: Credit Card Transaction Processing
**Complexity**: Simple (single stream, basic validation, straightforward rules)

## Business Scenario

A credit card processor needs to validate incoming transactions and approve or decline them based on simple business rules:
- Check if amount is within daily limit
- Verify merchant is not blacklisted
- Ensure card is not expired

## Pipeline Flow

```
card_transactions (Kafka)
    → validate_transaction (Transform)
    → approval_decision (Rules)
    → approved_transactions / declined_transactions (Kafka)
```

## Files

| File | Layer | Description |
|------|-------|-------------|
| `card_transaction.schema` | L2 | Transaction and card schemas |
| `validate_transaction.xform` | L3 | Basic validation transform |
| `approval_rules.rules` | L4 | Simple approval decision table |
| `transaction_processor.proc` | L1 | Process orchestration |

## Testing

Parse and generate:
```bash
# From nexflow-toolchain directory
python -m backend.cli parse example/simple/*.schema
python -m backend.cli parse example/simple/*.xform
python -m backend.cli parse example/simple/*.rules
python -m backend.cli parse example/simple/*.proc
python -m backend.cli generate example/simple/ --output target/simple/
```
