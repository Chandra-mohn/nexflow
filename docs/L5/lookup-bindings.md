# L5: Lookup Bindings

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Lookup bindings map logical lookup names (used in L1 `enrich using` statements) to physical data stores. These are typically used for enrichment operations where streaming data is joined with reference data.

---

## Supported Data Stores

| Data Store | Use Case | Key Features |
|------------|----------|--------------|
| **MongoDB** | Document lookups | Flexible schema, rich queries |
| **Redis** | Fast key-value | Sub-millisecond latency, caching |
| **PostgreSQL** | Relational data | ACID, complex queries |
| **Cassandra** | Wide-column | High availability, linear scaling |
| **Elasticsearch** | Search lookups | Full-text search, aggregations |

---

## MongoDB Bindings

### Basic Configuration

```yaml
lookups:
  customers:
    type: mongodb
    uri: mongodb://mongo-cluster:27017
    database: credit_card
    collection: customers
```

### Complete Configuration

```yaml
lookups:
  customers:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers

    # Connection configuration
    connection:
      max_pool_size: 100
      min_pool_size: 10
      max_idle_time: 60s
      connect_timeout: 10s
      socket_timeout: 30s
      server_selection_timeout: 30s

    # Read configuration
    read:
      preference: secondaryPreferred  # primary, secondary, nearest
      concern: majority  # local, majority, linearizable
      max_staleness: 90s

    # Write configuration (if used for state)
    write:
      concern: majority
      journal: true
      wtimeout: 10s

    # Authentication
    auth:
      mechanism: SCRAM-SHA-256  # SCRAM-SHA-1, MONGODB-X509
      source: admin
      username: ${MONGO_USER}
      password: ${MONGO_PASSWORD}

    # TLS
    tls:
      enabled: true
      ca_file: /etc/ssl/mongo-ca.pem
      allow_invalid_certificates: false

    # Lookup optimization
    lookup:
      key_field: card_id
      projection:  # Only fetch needed fields
        - customer_name
        - credit_limit
        - risk_tier
      hint: idx_card_id  # Index hint

    # Caching
    cache:
      enabled: true
      ttl: 5m
      max_size: 100000
      eviction: lru
```

### MongoDB Property Reference

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `uri` | string | required | Connection string |
| `database` | string | required | Database name |
| `collection` | string | required | Collection name |
| `read.preference` | string | primary | Read preference |
| `connection.max_pool_size` | integer | 100 | Max connections |
| `cache.enabled` | boolean | false | Enable caching |
| `cache.ttl` | duration | 5m | Cache entry TTL |

---

## Redis Bindings

### Basic Configuration

```yaml
lookups:
  currency_rates:
    type: redis
    uri: redis://redis-cluster:6379
```

### Complete Configuration

```yaml
lookups:
  currency_rates:
    type: redis
    uri: ${REDIS_URI}
    database: 0

    # Cluster configuration
    cluster:
      enabled: true
      max_redirects: 5
      nodes:
        - redis-1:6379
        - redis-2:6379
        - redis-3:6379

    # Connection configuration
    connection:
      pool_size: 50
      min_idle: 10
      connect_timeout: 5s
      socket_timeout: 1s
      max_retries: 3

    # Sentinel configuration (if using Sentinel)
    sentinel:
      master_name: mymaster
      nodes:
        - sentinel-1:26379
        - sentinel-2:26379
        - sentinel-3:26379

    # Authentication
    auth:
      password: ${REDIS_PASSWORD}
      username: ${REDIS_USER}  # Redis 6+ ACL

    # TLS
    tls:
      enabled: true
      cert_file: /etc/ssl/redis-client.pem
      key_file: /etc/ssl/redis-client-key.pem
      ca_file: /etc/ssl/redis-ca.pem

    # Lookup configuration
    lookup:
      key_pattern: "customer:{card_id}"  # Key template
      type: hash  # string, hash, set, zset
      hash_field: data  # For hash type
      ttl_field: _ttl  # Field containing TTL

    # Serialization
    serialization:
      format: json  # json, msgpack, protobuf
      compression: none  # none, gzip, lz4
```

### Redis Key Patterns

```yaml
lookups:
  # Simple key lookup
  session_data:
    type: redis
    lookup:
      key_pattern: "session:{session_id}"
      type: string

  # Hash lookup (single field)
  customer_profile:
    type: redis
    lookup:
      key_pattern: "customer:{card_id}"
      type: hash
      # Fetches specific fields from hash

  # Hash lookup (all fields)
  merchant_info:
    type: redis
    lookup:
      key_pattern: "merchant:{merchant_id}"
      type: hash
      fetch_all: true

  # Sorted set (score-based)
  recent_transactions:
    type: redis
    lookup:
      key_pattern: "txn:{card_id}"
      type: zset
      range_type: score  # score, rank
      min_score: -inf
      max_score: +inf
      limit: 10
```

---

## PostgreSQL Bindings

### Basic Configuration

```yaml
lookups:
  merchant_categories:
    type: postgresql
    jdbc_url: jdbc:postgresql://postgres:5432/credit_card
    schema: reference
    table: merchant_categories
```

### Complete Configuration

```yaml
lookups:
  merchant_categories:
    type: postgresql
    jdbc_url: ${POSTGRES_URL}

    # Table configuration
    schema: reference
    table: merchant_categories

    # Connection pool
    pool:
      size: 20
      min_idle: 5
      max_lifetime: 30m
      idle_timeout: 10m
      connection_timeout: 30s

    # Query configuration
    query:
      # Custom lookup query (optional)
      sql: |
        SELECT mcc_code, category_name, risk_level, is_high_risk
        FROM reference.merchant_categories
        WHERE mcc_code = ?
      # Or use auto-generated query
      key_column: mcc_code
      select_columns:
        - mcc_code
        - category_name
        - risk_level
        - is_high_risk

    # Read configuration
    read:
      fetch_size: 1000
      read_only: true
      isolation_level: READ_COMMITTED

    # Authentication
    auth:
      username: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

    # SSL
    ssl:
      mode: verify-full  # disable, allow, prefer, require, verify-ca, verify-full
      root_cert: /etc/ssl/postgres-ca.pem
      client_cert: /etc/ssl/postgres-client.pem
      client_key: /etc/ssl/postgres-client-key.pem

    # Caching
    cache:
      enabled: true
      ttl: 1h  # Reference data changes infrequently
      max_size: 50000
      refresh_strategy: lazy  # lazy, eager
```

### PostgreSQL Query Patterns

```yaml
lookups:
  # Simple key lookup
  card_accounts:
    type: postgresql
    query:
      key_column: card_id
      select_columns: [account_status, credit_limit, open_date]

  # Composite key lookup
  card_account_history:
    type: postgresql
    query:
      key_columns: [card_id, effective_date]
      sql: |
        SELECT * FROM card_accounts
        WHERE card_id = ? AND effective_date <= ?
        ORDER BY effective_date DESC
        LIMIT 1

  # Range lookup
  exchange_rates:
    type: postgresql
    query:
      sql: |
        SELECT rate FROM exchange_rates
        WHERE from_currency = ? AND to_currency = ?
        AND effective_date <= ?
        ORDER BY effective_date DESC
        LIMIT 1
```

---

## Cassandra Bindings

### Complete Configuration

```yaml
lookups:
  transaction_history:
    type: cassandra
    contact_points:
      - cassandra-1:9042
      - cassandra-2:9042
      - cassandra-3:9042
    datacenter: us-east-1
    keyspace: credit_card

    # Table configuration
    table: transaction_history

    # Query configuration
    query:
      partition_key: card_id
      clustering_keys: [transaction_date, transaction_id]
      select_columns:
        - amount
        - merchant_id
        - status
      limit: 100

    # Connection configuration
    connection:
      pool_size: 8
      max_requests_per_connection: 1024

    # Load balancing
    load_balancing:
      policy: token_aware  # round_robin, token_aware, dc_aware
      local_datacenter: us-east-1
      shuffle_replicas: true

    # Authentication
    auth:
      username: ${CASSANDRA_USER}
      password: ${CASSANDRA_PASSWORD}

    # Consistency
    consistency:
      read: LOCAL_QUORUM  # ONE, LOCAL_ONE, LOCAL_QUORUM, QUORUM, ALL
      serial: LOCAL_SERIAL
```

---

## Elasticsearch Bindings

### Complete Configuration

```yaml
lookups:
  merchant_search:
    type: elasticsearch
    hosts:
      - https://es-node-1:9200
      - https://es-node-2:9200
    index: merchants

    # Query configuration
    query:
      type: term  # term, match, bool
      field: merchant_id
      # Or custom query
      template: |
        {
          "query": {
            "bool": {
              "must": [
                { "term": { "merchant_id": "{{merchant_id}}" }},
                { "term": { "is_active": true }}
              ]
            }
          },
          "_source": ["name", "category", "risk_score"]
        }

    # Connection configuration
    connection:
      connect_timeout: 5s
      socket_timeout: 30s
      max_retry_timeout: 60s

    # Authentication
    auth:
      type: api_key  # basic, api_key, bearer
      api_key: ${ES_API_KEY}

    # SSL
    ssl:
      enabled: true
      ca_path: /etc/ssl/es-ca.pem
      verify_hostname: true
```

---

## Caching Strategy

### Cache Configuration

```yaml
lookups:
  customers:
    type: mongodb
    cache:
      enabled: true
      ttl: 5m
      max_size: 100000
      eviction: lru  # lru, lfu, fifo

      # Cache warming
      warm_on_start: true
      warm_query: |
        { "is_active": true }
      warm_limit: 50000

      # Cache refresh
      refresh:
        strategy: write_through  # write_through, write_behind, refresh_ahead
        async: true

      # Cache metrics
      metrics:
        enabled: true
        report_interval: 60s
```

### Cache Levels

| Level | Scope | Use Case |
|-------|-------|----------|
| **L1** | Per-task | Hot data, sub-ms access |
| **L2** | Per-job | Shared across tasks |
| **External** | Distributed | Shared across jobs (Redis) |

```yaml
lookups:
  customers:
    type: mongodb
    cache:
      l1:
        enabled: true
        max_size: 10000
        ttl: 1m
      l2:
        enabled: true
        max_size: 100000
        ttl: 5m
```

---

## Async Lookup

For high-throughput scenarios, configure async lookups:

```yaml
lookups:
  customers:
    type: mongodb
    async:
      enabled: true
      capacity: 1000  # Max outstanding requests
      timeout: 30s
      ordered: false  # Allow reordering for throughput
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [stream-bindings.md](./stream-bindings.md) - Stream configurations
- [state-checkpoints.md](./state-checkpoints.md) - State and checkpoints
