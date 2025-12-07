# L5: Secret Management

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

L5 does NOT store secrets directly. Instead, it references external secret management systems. This ensures credentials are never committed to version control and can be rotated without code changes.

---

## Key Principles

1. **No Secrets in Code**: Never store actual credentials in `.infra` files
2. **Reference-Based**: Use `secret://` URIs to reference external secrets
3. **Provider Abstraction**: Support multiple secret providers
4. **Rotation Support**: Enable credential rotation without redeployment

---

## Supported Providers

| Provider | Use Case | Features |
|----------|----------|----------|
| **HashiCorp Vault** | Enterprise | Dynamic secrets, rotation, audit |
| **AWS Secrets Manager** | AWS native | Auto-rotation, IAM integration |
| **AWS Parameter Store** | Simple secrets | Cost-effective, hierarchical |
| **Kubernetes Secrets** | K8s native | Pod mounting, RBAC |
| **Azure Key Vault** | Azure native | HSM-backed, managed |
| **GCP Secret Manager** | GCP native | IAM, versioning |
| **Environment Variables** | Development | Simple, local testing |

---

## Secret Definition

### HashiCorp Vault

```yaml
secrets:
  # KV v2 secrets engine
  kafka_credentials:
    provider: vault
    path: secret/data/production/kafka
    keys:
      - username
      - password

    # Vault connection
    vault:
      address: ${VAULT_ADDR}
      namespace: credit-card  # Enterprise only

    # Authentication
    auth:
      method: kubernetes  # kubernetes, approle, token, aws
      role: flink-reader
      # For AppRole
      # role_id: ${VAULT_ROLE_ID}
      # secret_id: ${VAULT_SECRET_ID}

    # Caching
    cache:
      enabled: true
      ttl: 5m

    # Renewal
    renewal:
      enabled: true
      increment: 1h
```

### Dynamic Secrets (Vault)

```yaml
secrets:
  # Dynamic database credentials
  mongo_credentials:
    provider: vault
    path: database/creds/mongo-readonly
    type: dynamic

    vault:
      address: ${VAULT_ADDR}

    auth:
      method: kubernetes
      role: flink-reader

    # Lease management
    lease:
      renewal_enabled: true
      min_renewal_seconds: 60
      increment_seconds: 3600
```

### AWS Secrets Manager

```yaml
secrets:
  mongo_connection:
    provider: aws_secrets_manager
    secret_id: production/mongodb/connection
    region: us-east-1

    # Version (optional)
    version_stage: AWSCURRENT  # or version_id

    # Keys within JSON secret
    keys:
      - uri
      - username
      - password

    # Authentication
    auth:
      type: instance_profile  # instance_profile, static, assume_role
      # For assume_role
      # role_arn: arn:aws:iam::123456789:role/secret-reader

    # Caching
    cache:
      enabled: true
      ttl: 5m

    # Rotation
    rotation:
      auto_refresh: true
      refresh_interval: 1h
```

### AWS Parameter Store

```yaml
secrets:
  database_password:
    provider: aws_parameter_store
    name: /production/database/password
    region: us-east-1

    # Parameter type
    type: SecureString  # String, StringList, SecureString

    # Decryption
    with_decryption: true
    kms_key_id: ${KMS_KEY_ID}  # Optional custom KMS key

    auth:
      type: instance_profile
```

### Kubernetes Secrets

```yaml
secrets:
  redis_password:
    provider: kubernetes
    namespace: credit-card
    secret_name: redis-credentials
    key: password

    # Multiple keys from same secret
    # keys:
    #   - username
    #   - password

    # Service account (optional)
    service_account: flink-runner
```

### Azure Key Vault

```yaml
secrets:
  storage_connection:
    provider: azure_key_vault
    vault_url: https://my-vault.vault.azure.net
    secret_name: storage-connection-string

    # Version (optional)
    version: latest

    # Authentication
    auth:
      type: managed_identity  # managed_identity, service_principal, cli
      # For service_principal
      # tenant_id: ${AZURE_TENANT_ID}
      # client_id: ${AZURE_CLIENT_ID}
      # client_secret: ${AZURE_CLIENT_SECRET}
```

### GCP Secret Manager

```yaml
secrets:
  api_key:
    provider: gcp_secret_manager
    project: my-gcp-project
    secret: production-api-key

    # Version (optional)
    version: latest  # or specific version number

    # Authentication
    auth:
      type: workload_identity  # workload_identity, service_account
      # For service_account
      # key_file: /etc/gcp/service-account.json
```

### Environment Variables (Development)

```yaml
secrets:
  local_password:
    provider: env
    variable: DATABASE_PASSWORD

    # Default value (for optional secrets)
    default: development_password
```

---

## Secret Usage

### In Stream Bindings

```yaml
streams:
  auth_events:
    type: kafka
    properties:
      sasl.username: secret://kafka_credentials/username
      sasl.password: secret://kafka_credentials/password
```

### In Lookup Bindings

```yaml
lookups:
  customers:
    type: mongodb
    uri: secret://mongo_connection/uri
```

### In Checkpoint Storage

```yaml
checkpoints:
  s3_checkpoints:
    type: s3
    auth:
      access_key: secret://s3_credentials/access_key
      secret_key: secret://s3_credentials/secret_key
```

### Full URI Reference

```yaml
lookups:
  database:
    type: postgresql
    jdbc_url: secret://postgres_credentials/jdbc_url

# The secret contains the full connection string:
# jdbc:postgresql://host:5432/db?user=xxx&password=yyy
```

---

## Secret URI Format

```
secret://<secret_name>/<key>
secret://<secret_name>         # Returns entire secret value
secret://<secret_name>/<key>?version=<version>
```

### Examples

```yaml
# Single key from secret
password: secret://kafka_credentials/password

# Entire secret value
connection_string: secret://mongo_connection

# Specific version
api_key: secret://api_key?version=2

# With default fallback
optional_key: secret://optional_secret/key?default=default_value
```

---

## Secret Groups

Group related secrets for easier management:

```yaml
secrets:
  _groups:
    kafka:
      provider: vault
      path: secret/data/production/kafka
      vault:
        address: ${VAULT_ADDR}
      auth:
        method: kubernetes
        role: flink-reader

  # Reference group
  kafka_username:
    _group: kafka
    key: username

  kafka_password:
    _group: kafka
    key: password
```

---

## Rotation Support

### Automatic Rotation Detection

```yaml
secrets:
  database_credentials:
    provider: aws_secrets_manager
    secret_id: production/database

    rotation:
      # Detect rotation via version change
      auto_refresh: true
      refresh_interval: 5m

      # Callback on rotation
      on_rotation:
        action: reconnect  # reconnect, restart, alert
        grace_period: 30s
```

### Dual-Secret Pattern

For zero-downtime rotation:

```yaml
secrets:
  database_primary:
    provider: vault
    path: secret/data/database/primary

  database_secondary:
    provider: vault
    path: secret/data/database/secondary

lookups:
  database:
    type: postgresql
    # Try primary, fallback to secondary during rotation
    auth:
      primary: secret://database_primary
      secondary: secret://database_secondary
      fallback_enabled: true
```

---

## Security Best Practices

### Principle of Least Privilege

```yaml
secrets:
  kafka_credentials:
    provider: vault
    auth:
      method: kubernetes
      role: flink-kafka-reader  # Minimal permissions
```

### Secret Isolation

```yaml
# Separate secrets per environment
secrets:
  # Production
  prod_database:
    provider: vault
    path: secret/data/production/database

  # Staging (in staging.infra)
  staging_database:
    provider: vault
    path: secret/data/staging/database
```

### Audit Logging

```yaml
secrets:
  _config:
    audit:
      enabled: true
      log_access: true
      log_destination: security-audit-logs
```

---

## Error Handling

### Missing Secrets

```yaml
secrets:
  optional_api_key:
    provider: vault
    path: secret/data/optional/api-key

    # Behavior if secret not found
    on_missing:
      action: default  # fail, default, warn
      default_value: ""

  required_password:
    provider: vault
    path: secret/data/required/password

    on_missing:
      action: fail
      message: "Required secret not found: database password"
```

### Provider Unavailable

```yaml
secrets:
  database_password:
    provider: vault

    # Retry configuration
    retry:
      attempts: 3
      backoff: exponential
      initial_delay: 1s
      max_delay: 30s

    # Fallback provider
    fallback:
      provider: env
      variable: DB_PASSWORD
```

---

## Development Configuration

```yaml
# development.infra
secrets:
  # Use environment variables for local development
  _config:
    default_provider: env

  kafka_credentials:
    provider: env
    variables:
      username: KAFKA_USERNAME
      password: KAFKA_PASSWORD

  mongo_connection:
    provider: env
    variable: MONGO_URI
    default: mongodb://localhost:27017/credit_card
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [deployment-targets.md](./deployment-targets.md) - Deployment configuration
