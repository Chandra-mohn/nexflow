# Nexflow Stream Investigation Tools Specification

## Overview

Stream investigation tools for developers and support teams to inspect, decode, replay, and compare messages in Kafka streams with multi-format serialization support.

## Command Summary

| Command | Description | Priority |
|---------|-------------|----------|
| `nexflow peek` | Inspect live stream messages with filtering | P0 |
| `nexflow decode` | Convert binary formats to human-readable JSON | P0 |
| `nexflow replay` | Replay messages between topics | P1 |
| `nexflow diff` | Compare messages across topics/time ranges | P1 |

## Configuration

### Cluster Profiles (`nexflow.toml`)

```toml
[kafka.profiles.dev]
bootstrap_servers = "localhost:9092"
security_protocol = "PLAINTEXT"

[kafka.profiles.staging]
bootstrap_servers = "staging-kafka.internal:9092"
security_protocol = "SSL"
ssl_cafile = "/path/to/ca.pem"
ssl_certfile = "/path/to/client.pem"
ssl_keyfile = "/path/to/client-key.pem"

[kafka.profiles.prod]
bootstrap_servers = "prod-kafka.internal:9092"
security_protocol = "SSL"
ssl_cafile = "/path/to/prod-ca.pem"
ssl_certfile = "/path/to/prod-client.pem"
ssl_keyfile = "/path/to/prod-client-key.pem"
pii_mask = true  # Auto-mask PII fields

[kafka.schema_registry]
url = "http://localhost:8081"
# For offline mode, local schema files take precedence

[kafka.default_profile]
name = "dev"
```

### PII Masking Configuration

```toml
[kafka.pii]
# Fields to automatically mask in production data
masked_fields = [
    "ssn", "social_security_number",
    "credit_card", "card_number",
    "email", "phone", "address",
    "date_of_birth", "dob"
]
mask_pattern = "***MASKED***"
```

## Commands

### 1. `nexflow peek` - Stream Message Inspector

**Purpose**: Inspect live or historical messages from Kafka topics.

**Syntax**:
```bash
nexflow peek <topic> [OPTIONS]
```

**Options**:
| Option | Description | Default |
|--------|-------------|---------|
| `--profile, -p` | Kafka cluster profile | `dev` |
| `--limit, -n` | Number of messages | 10 |
| `--offset` | Start offset (`earliest`, `latest`, `<number>`) | `latest` |
| `--format, -f` | Output format (`json`, `table`, `raw`) | `json` |
| `--filter` | SQL-like filter expression | - |
| `--follow, -F` | Continuous streaming mode | false |
| `--partition` | Specific partition | all |
| `--timeout` | Connection timeout in seconds | 30 |
| `--unmask` | Disable PII masking (requires confirmation) | false |

**Examples**:
```bash
# Basic peek at latest 10 messages
nexflow peek orders-avro

# Filter by field value
nexflow peek orders-avro --filter "customer_id = 'C123'"

# Follow mode (like tail -f)
nexflow peek orders-avro --follow --filter "status = 'pending'"

# Use production profile
nexflow peek orders-avro --profile prod --limit 100

# Peek from specific offset
nexflow peek orders-avro --offset 1000 --limit 50

# Complex filter
nexflow peek orders-avro --filter "amount > 100 AND status IN ('pending', 'processing')"
```

**Output Formats**:

JSON (default):
```json
{
  "offset": 12345,
  "partition": 0,
  "timestamp": "2025-01-15T10:30:00Z",
  "key": "order-123",
  "value": {
    "order_id": "order-123",
    "customer_id": "C456",
    "amount": 99.99,
    "status": "pending"
  }
}
```

Table:
```
┌─────────┬───────────┬─────────────────────┬─────────────────────────────────────┐
│ Offset  │ Partition │ Timestamp           │ Key         │ Value (summary)       │
├─────────┼───────────┼─────────────────────┼─────────────┼───────────────────────┤
│ 12345   │ 0         │ 2025-01-15 10:30:00 │ order-123   │ {order_id: "order...  │
└─────────┴───────────┴─────────────────────┴─────────────┴───────────────────────┘
```

### 2. `nexflow decode` - Format Converter

**Purpose**: Decode binary-serialized messages to human-readable JSON.

**Syntax**:
```bash
nexflow decode <topic-or-file> [OPTIONS]
```

**Options**:
| Option | Description | Default |
|--------|-------------|---------|
| `--from` | Source format (`avro`, `protobuf`, `confluent-avro`, `auto`) | `auto` |
| `--to` | Target format (`json`, `yaml`) | `json` |
| `--schema` | Schema file path (for offline mode) | - |
| `--registry` | Schema registry URL (overrides config) | from config |
| `--output, -o` | Output file path | stdout |
| `--pretty` | Pretty-print output | true |
| `--limit, -n` | Number of messages to decode | all |
| `--profile, -p` | Kafka cluster profile | `dev` |

**Examples**:
```bash
# Decode Avro topic to JSON (auto-detect schema from registry)
nexflow decode orders-avro --to json

# Decode with local schema file (offline mode)
nexflow decode orders-avro --schema ./schemas/order.avsc --to json

# Save to file
nexflow decode orders-avro --to json --output orders.json

# Decode Protobuf with local schema
nexflow decode events-proto --from protobuf --schema ./protos/event.proto

# Decode Confluent Avro from production
nexflow decode orders-avro --profile prod --registry https://prod-registry:8081

# Decode specific number of messages
nexflow decode orders-avro --limit 1000 --output sample.json
```

**Output**:
```json
[
  {
    "offset": 12345,
    "partition": 0,
    "timestamp": "2025-01-15T10:30:00Z",
    "key": "order-123",
    "value": {
      "order_id": "order-123",
      "customer_id": "C456",
      "items": [
        {"product_id": "P001", "quantity": 2}
      ]
    }
  }
]
```

### 3. `nexflow replay` - Message Replay

**Purpose**: Replay messages from one topic/time range to another topic.

**Syntax**:
```bash
nexflow replay <source-topic> <target-topic> [OPTIONS]
```

**Options**:
| Option | Description | Default |
|--------|-------------|---------|
| `--profile, -p` | Kafka cluster profile | `dev` |
| `--from-offset` | Start offset | `earliest` |
| `--to-offset` | End offset | `latest` |
| `--from-time` | Start timestamp (ISO format) | - |
| `--to-time` | End timestamp (ISO format) | - |
| `--filter` | SQL-like filter expression | - |
| `--transform` | Field transformation expression | - |
| `--dry-run` | Preview without sending | false |
| `--rate-limit` | Messages per second | unlimited |
| `--batch-size` | Batch size for sending | 100 |
| `--confirm` | Skip confirmation prompt | false |

**Examples**:
```bash
# Replay all messages from one topic to another
nexflow replay orders-prod orders-dev --profile dev

# Replay specific time range
nexflow replay orders-prod orders-dev \
  --from-time "2025-01-15T00:00:00Z" \
  --to-time "2025-01-15T12:00:00Z"

# Replay with filter
nexflow replay orders-prod orders-dev \
  --filter "customer_id = 'C123'" \
  --profile dev

# Preview what would be replayed
nexflow replay orders-prod orders-dev --dry-run --limit 10

# Rate-limited replay
nexflow replay orders-prod orders-dev --rate-limit 100

# Transform fields during replay
nexflow replay orders-prod orders-dev \
  --transform "customer_id = 'ANONYMIZED'"
```

**Output**:
```
Replay Configuration:
  Source: orders-prod (prod cluster)
  Target: orders-dev (dev cluster)
  Time Range: 2025-01-15T00:00:00Z to 2025-01-15T12:00:00Z
  Estimated Messages: ~15,234

Proceed? [y/N]: y

Progress: [████████████████████░░░░░] 80% (12,187/15,234)
  Rate: 523 msg/s | Elapsed: 00:23:15 | ETA: 00:05:50

✓ Replay complete: 15,234 messages sent
```

### 4. `nexflow diff` - Message Comparator

**Purpose**: Compare messages between topics, time ranges, or snapshots.

**Syntax**:
```bash
nexflow diff <source1> <source2> [OPTIONS]
```

**Options**:
| Option | Description | Default |
|--------|-------------|---------|
| `--profile, -p` | Kafka cluster profile | `dev` |
| `--key` | Field(s) to use as comparison key | message key |
| `--ignore` | Fields to ignore in comparison | - |
| `--output, -o` | Output file for diff report | stdout |
| `--format, -f` | Output format (`json`, `table`, `summary`) | `summary` |
| `--limit, -n` | Max messages to compare | 1000 |
| `--time-range` | Time range for comparison | - |

**Examples**:
```bash
# Compare two topics
nexflow diff orders-v1 orders-v2 --key order_id

# Compare same topic between time ranges
nexflow diff orders-avro orders-avro \
  --time-range "2025-01-14" "2025-01-15" \
  --key order_id

# Ignore timestamp fields in comparison
nexflow diff orders-dev orders-staging \
  --key order_id \
  --ignore updated_at,created_at

# Generate JSON diff report
nexflow diff orders-dev orders-prod \
  --key order_id \
  --output diff-report.json \
  --format json
```

**Output (Summary)**:
```
Diff Report: orders-v1 vs orders-v2
═══════════════════════════════════════════════════

Messages analyzed: 1,000 vs 1,023
  ✓ Matching: 980 (96.1%)
  ✗ Different: 15 (1.5%)
  + Only in orders-v2: 23 (2.3%)
  - Only in orders-v1: 5 (0.5%)

Field-level differences:
  • status: 10 changes
  • amount: 3 changes
  • metadata.version: 2 changes

Sample Differences:
┌────────────┬─────────────────────┬─────────────────────┐
│ Key        │ orders-v1           │ orders-v2           │
├────────────┼─────────────────────┼─────────────────────┤
│ order-123  │ status: "pending"   │ status: "confirmed" │
│ order-456  │ amount: 99.99       │ amount: 109.99      │
└────────────┴─────────────────────┴─────────────────────┘
```

## Filter Expression Syntax

SQL-like filter expressions for `--filter` option:

### Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `status = 'pending'` |
| `!=` / `<>` | Not equals | `status != 'cancelled'` |
| `>`, `<`, `>=`, `<=` | Comparison | `amount > 100` |
| `IN` | In list | `status IN ('pending', 'processing')` |
| `NOT IN` | Not in list | `status NOT IN ('cancelled')` |
| `LIKE` | Pattern match | `order_id LIKE 'ORD-%'` |
| `IS NULL` | Null check | `metadata IS NULL` |
| `IS NOT NULL` | Not null | `customer_id IS NOT NULL` |
| `AND` | Logical AND | `status = 'pending' AND amount > 100` |
| `OR` | Logical OR | `status = 'pending' OR status = 'processing'` |
| `NOT` | Logical NOT | `NOT status = 'cancelled'` |

### Field Access
- Simple: `status`, `amount`
- Nested: `metadata.version`, `customer.address.city`
- Array: `items[0].product_id`

### Examples
```bash
# Simple equality
--filter "status = 'pending'"

# Numeric comparison
--filter "amount >= 100.00"

# Combined conditions
--filter "status = 'pending' AND amount > 50 AND customer_id IS NOT NULL"

# Pattern matching
--filter "order_id LIKE 'ORD-2025%'"

# Nested field access
--filter "customer.tier = 'premium'"

# In list
--filter "status IN ('pending', 'processing', 'confirmed')"
```

## VS Code Integration

The stream tools integrate with the Nexflow VS Code extension through:

### Stream Explorer Panel
- Tree view of configured Kafka clusters and topics
- Quick access to peek, decode, and diff operations
- Topic metadata display (partitions, offsets, message count)

### Message Viewer
- Rich JSON viewer with syntax highlighting
- Field-level PII masking indicators
- Schema information display
- Copy/export functionality

### Replay Wizard
- Guided workflow for replay operations
- Visual time range selection
- Filter builder with autocomplete
- Progress tracking

### Diff Viewer
- Side-by-side comparison view
- Highlighted differences
- Filter by change type (added/removed/modified)
- Export to various formats

## Error Handling

### Common Errors
| Error | Cause | Resolution |
|-------|-------|------------|
| `ConnectionError` | Cannot connect to Kafka | Check profile, network, SSL certs |
| `SchemaNotFound` | Schema not in registry | Use `--schema` for local file |
| `AuthenticationFailed` | Invalid credentials | Check SSL/SASL configuration |
| `TopicNotFound` | Topic doesn't exist | Verify topic name |
| `OffsetOutOfRange` | Invalid offset | Use valid offset or `earliest`/`latest` |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Connection error |
| 4 | Authentication error |
| 5 | Schema error |

## Dependencies

### Python Packages
- `confluent-kafka` - Kafka client with Avro support
- `fastavro` - Avro serialization
- `protobuf` - Protobuf support
- `rich` - Terminal formatting
- `click` - CLI framework (already used)

### Optional
- `grpcio` - For schema registry gRPC
- `httpx` - Async HTTP for schema registry
