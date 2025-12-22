# L12345-02: Fraud Detection (All Layers)

Real-time fraud detection system using all five DSL layers.

## Layers Used
- **L1 ProcDSL**: Stream processing with windowing
- **L2 SchemaDSL**: Transaction and alert schemas
- **L3 TransformDSL**: Feature extraction and enrichment
- **L4 RulesDSL**: Fraud detection rules and scoring
- **L5 ConfigDSL**: Environment-specific thresholds

## Architecture
```
Transactions → Feature Extraction → Rule Engine → Alert/Approve
                     │                    │
                     ▼                    ▼
              [Velocity Windows]    [ML Model Scores]
```

## Files
- `transaction.schema` - L2 transaction input
- `fraud_alert.schema` - L2 alert output
- `feature_extraction.xform` - L3 feature engineering
- `fraud_rules.rules` - L4 detection rules
- `dev.config` - L5 development thresholds
- `prod.config` - L5 production thresholds
- `fraud_detection.proc` - L1 main process

## Build & Run
```bash
nexflow build --config prod.config examples/building-blocks/level-4-full-stack/02-fraud-detection/
```
