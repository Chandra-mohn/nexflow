# Complex Use Case: Real-Time Credit Decisioning Platform

**Domain**: Credit Card Application and Real-Time Credit Limit Management
**Complexity**: Complex (multi-source enrichment, ML ensemble, state machines, event sourcing)

## Business Scenario

A financial institution needs a comprehensive credit decisioning platform with:
- Real-time credit application processing
- Multi-bureau credit data enrichment
- ML ensemble scoring with multiple models
- Regulatory compliance checks (KYC/AML)
- Dynamic credit limit management based on behavior
- Event-sourced audit trail for compliance
- Multi-stage approval workflows with human-in-the-loop
- Cross-channel consistency (web, mobile, branch, partner API)

## Pipeline Architecture

```
                                    ┌─────────────────┐
                                    │  Credit Bureau  │
                                    │   (Experian)    │
                                    └────────┬────────┘
                                             │
┌──────────────┐    ┌──────────────┐   ┌─────▼─────┐    ┌──────────────┐
│ Applications │───▶│   Validate   │──▶│  Enrich   │───▶│   ML Score   │
│   (Kafka)    │    │   & Parse    │   │  Multi-   │    │   Ensemble   │
└──────────────┘    └──────────────┘   │  Source   │    └──────┬───────┘
                                       └─────┬─────┘           │
                                             │          ┌──────▼───────┐
                                    ┌────────▼────────┐ │   Decision   │
                                    │  Credit Bureau  │ │    Engine    │
                                    │   (TransUnion)  │ └──────┬───────┘
                                    └─────────────────┘        │
                                                        ┌──────▼───────┐
                    ┌───────────────────────────────────│    Route     │
                    │               │                   └──────────────┘
                    ▼               ▼                          │
            ┌───────────┐   ┌───────────┐              ┌──────▼───────┐
            │ Auto      │   │  Manual   │              │   Declined   │
            │ Approved  │   │  Review   │              │              │
            └─────┬─────┘   └─────┬─────┘              └──────┬───────┘
                  │               │                           │
                  ▼               ▼                           ▼
            ┌───────────────────────────────────────────────────────┐
            │              Event Store (Audit Trail)                 │
            └───────────────────────────────────────────────────────┘
```

## Files

| File | Layer | Description |
|------|-------|-------------|
| `credit_schemas.schema` | L2 | Application, bureau, decision, audit schemas |
| `credit_transforms.xform` | L3 | Bureau enrichment, score normalization, feature engineering |
| `credit_rules.rules` | L4 | Decisioning tables, compliance rules, limit calculations |
| `credit_decisioning.proc` | L1 | Multi-stage credit decisioning pipeline |

## Key Features Demonstrated

### L1 (Process Orchestration)
- Multi-source async enrichment with fan-out/fan-in
- State machine for application lifecycle
- Human-in-the-loop approval workflow
- Event sourcing pattern for audit compliance
- Cross-process coordination
- Dynamic parallelism based on load
- Circuit breakers for external services
- Saga pattern for distributed transactions

### L2 (Schema Definition)
- Complex nested objects with deep hierarchies
- Polymorphic schemas for different application types
- Schema versioning and evolution
- Audit event schemas with full lineage
- Reference data with TTL management

### L3 (Transform Definition)
- Multi-step feature engineering pipelines
- Score normalization across multiple bureaus
- Async external service integration
- Idempotent transformation patterns
- Complex aggregation with multiple time windows

### L4 (Rules Definition)
- Multi-dimensional decision tables
- Regulatory compliance rule sets
- Dynamic limit calculation formulas
- Exception handling procedures
- Override approval workflows

## Testing

```bash
# Generate all artifacts
python -m backend.cli generate example/complex/ --output target/complex/

# Validate schemas
python -m backend.cli validate example/complex/credit_schemas.schema

# Run compliance checks
python -m backend.cli compliance-check example/complex/ --regulation pci-dss
```

## Compliance Notes

This use case demonstrates patterns for:
- PCI-DSS compliance (card data handling)
- SOX compliance (audit trails)
- GDPR compliance (data minimization, right to explanation)
- Fair lending regulations (adverse action notices)
