# L12-05: Configurable Job (L1 + L5)

Process with environment-specific configuration.

## Layers Used
- **L1 ProcDSL**: Data flow orchestration
- **L5 ConfigDSL**: Environment configuration

## Pattern
```
Configuration → Process Definition → Environment-Specific Deployment
```

## Files
- `dev.config` - L5 development config
- `prod.config` - L5 production config
- `configurable_job.proc` - L1 process

## Key Concepts
- Environment-specific settings
- Config variable references
- Deployment profiles

## Build & Run
```bash
# Development
nexflow build --config dev.config configurable_job.proc

# Production
nexflow build --config prod.config configurable_job.proc
```
