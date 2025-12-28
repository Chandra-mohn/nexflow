#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Stream Tools Roadmap

Future enhancements for Nexflow stream investigation and debugging tools.

**Status**: Planning / Not Yet Implemented
**Priority**: Post-MVP
**Last Updated**: 2025-12-28

---

## Current State (Implemented)

| Command | Purpose | Status |
|---------|---------|--------|
| `nexflow peek` | Inspect live/historical messages | ✅ Complete |
| `nexflow replay` | Replay messages between topics | ✅ Complete |
| `nexflow decode` | Decode binary messages to JSON/YAML | ✅ Complete |
| `nexflow diff` | Compare messages between topics | ✅ Complete |

---

## Proposed Tools

### 1. `nexflow search` - Full-Text Stream Search

**Purpose**: Search across multiple topics with regex patterns and field-based queries.

**Use Cases**:
- Find all messages containing a specific customer ID across order, payment, and shipping topics
- Search for error patterns in event streams
- Locate messages by partial field matches

**Proposed Interface**:
```bash
nexflow search "customer_id:C12345" --topics "orders-*,payments-*"
nexflow search --regex "error.*timeout" --topics events --from-time "2025-01-15"
nexflow search --field status --value "FAILED" --topics "*.dlq"
```

**Key Features**:
- Multi-topic wildcard search (`orders-*`, `*.dlq`)
- Field-path queries (`customer.address.city:NYC`)
- Regex pattern matching
- Time-bounded search
- Result aggregation and grouping
- Export results to JSON/CSV

**Technical Considerations**:
- Parallel topic consumption for performance
- Memory management for large result sets
- Index-based optimization (future)
- Integration with schema registry for field discovery

---

### 2. `nexflow export` - Bulk Data Export

**Purpose**: Export stream data to analytics-friendly formats for offline analysis.

**Use Cases**:
- Export historical data for data science analysis
- Create training datasets from production streams
- Archive compliance data to cold storage
- Feed data warehouses (Snowflake, BigQuery, Redshift)

**Proposed Interface**:
```bash
nexflow export orders-avro --format parquet --output ./exports/orders/
nexflow export orders-avro --format csv --from-time "2025-01-01" --to-time "2025-01-31"
nexflow export orders-avro --format jsonl --partition-by date --output s3://bucket/exports/
```

**Supported Formats**:
| Format | Use Case |
|--------|----------|
| Parquet | Analytics, data lakes (columnar, compressed) |
| CSV | Spreadsheet analysis, simple tools |
| JSON Lines | Log aggregation, streaming pipelines |
| Avro | Schema-preserved archives |

**Key Features**:
- Partitioned output (by date, hour, field value)
- Compression options (gzip, snappy, zstd)
- Cloud storage targets (S3, GCS, Azure Blob)
- Schema evolution handling
- Progress checkpointing for resumable exports
- PII masking during export

**Technical Considerations**:
- PyArrow for Parquet generation
- Chunked processing for memory efficiency
- Cloud SDK integration (boto3, google-cloud-storage)
- Parallel partition writing

---

### 3. `nexflow snapshot` - Point-in-Time Snapshots

**Purpose**: Create immutable snapshots of topic state for debugging and recovery.

**Use Cases**:
- Capture pre-deployment state for rollback
- Create reproducible test fixtures
- Preserve state before destructive operations
- Share debugging context with team members

**Proposed Interface**:
```bash
nexflow snapshot create orders-avro --name "pre-migration-v2"
nexflow snapshot list
nexflow snapshot inspect pre-migration-v2
nexflow snapshot delete pre-migration-v2 --confirm
```

**Snapshot Contents**:
```
snapshots/
├── pre-migration-v2/
│   ├── manifest.json       # Metadata, offsets, schema versions
│   ├── partition-0.avro    # Data files
│   ├── partition-1.avro
│   └── schema.avsc         # Schema at snapshot time
```

**Key Features**:
- Atomic snapshot creation
- Offset and schema version tracking
- Compression and encryption options
- Cloud storage support
- Snapshot comparison (`nexflow snapshot diff`)
- Metadata tagging and notes

**Technical Considerations**:
- Consistent offset capture across partitions
- Schema registry version pinning
- Storage backend abstraction
- Incremental snapshots (future)

---

### 4. `nexflow restore` - Snapshot Restoration

**Purpose**: Restore messages from snapshots to topics.

**Use Cases**:
- Restore test environment to known state
- Recover from data corruption
- Replay historical scenarios for debugging
- Populate new environments

**Proposed Interface**:
```bash
nexflow restore pre-migration-v2 --to orders-dev
nexflow restore pre-migration-v2 --to orders-dev --filter "status = 'PENDING'"
nexflow restore pre-migration-v2 --to orders-dev --transform "customer_id = 'ANONYMIZED'"
nexflow restore pre-migration-v2 --to orders-dev --dry-run
```

**Key Features**:
- Target topic validation
- Optional filtering during restore
- Field transformation (anonymization)
- Dry-run preview
- Rate limiting
- Progress tracking and resumability

**Technical Considerations**:
- Schema compatibility validation
- Idempotent restore (offset-based deduplication)
- Transaction support for exactly-once
- Rollback capability

---

### 5. `nexflow stats` - Topic Statistics

**Purpose**: Real-time and historical statistics for stream monitoring.

**Use Cases**:
- Monitor message throughput and lag
- Track schema version distribution
- Identify partition imbalances
- Capacity planning

**Proposed Interface**:
```bash
nexflow stats orders-avro
nexflow stats orders-avro --watch --interval 5s
nexflow stats orders-avro --histogram message_size
nexflow stats --all-topics --profile prod
```

**Statistics Provided**:
```
Topic: orders-avro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Partitions:     12
Total Messages: 1,234,567
Message Rate:   ~450 msg/s (last 5 min)

Partition Distribution:
  P0: 102,345 (8.3%)  ████████░░
  P1: 108,234 (8.8%)  █████████░
  ...

Schema Versions:
  v3 (current): 89.2%
  v2:           10.5%
  v1:            0.3%

Message Size:
  Min:  124 bytes
  Avg:  2.3 KB
  Max:  45.2 KB
  P99:  8.1 KB

Consumer Groups:
  order-processor: lag 0, 3 members
  analytics:       lag 12,345, 1 member
```

**Key Features**:
- Real-time watch mode
- Historical trends (requires metrics store)
- Consumer group lag monitoring
- Schema version tracking
- Message size distribution
- Partition balance analysis
- Alert thresholds

**Technical Considerations**:
- Kafka AdminClient for metadata
- Consumer group offset APIs
- Schema registry version queries
- Optional Prometheus/metrics integration

---

### 6. `nexflow trace` - Message Flow Tracing

**Purpose**: Trace message flow by correlation ID across multiple topics.

**Use Cases**:
- Debug end-to-end order processing flow
- Trace failed transactions across services
- Visualize event sourcing chains
- Support team investigation

**Proposed Interface**:
```bash
nexflow trace --correlation-id "ORD-12345" --topics "orders,payments,shipping,notifications"
nexflow trace --key "customer:C789" --topics "*.events"
nexflow trace --correlation-id "ORD-12345" --output trace-report.html
```

**Trace Output**:
```
Trace: ORD-12345
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Timeline:
──────────────────────────────────────────────────
10:15:23.456  orders-received     OrderCreated
     │        {"order_id": "ORD-12345", "amount": 99.99}
     │
10:15:23.512  payments-requested  PaymentInitiated
     │        {"order_id": "ORD-12345", "payment_id": "PAY-001"}
     │
10:15:24.001  payments-completed  PaymentConfirmed
     │        {"payment_id": "PAY-001", "status": "SUCCESS"}
     │
10:15:24.234  shipping-requested  ShipmentCreated
     │        {"order_id": "ORD-12345", "tracking": "TRK-999"}
     │
10:15:25.100  notifications-sent  EmailSent
              {"order_id": "ORD-12345", "template": "order_confirmed"}

Total Duration: 1.644 seconds
Hops: 5 topics
```

**Key Features**:
- Multi-topic correlation
- Timeline visualization
- Latency analysis between hops
- Gap detection (missing expected events)
- HTML/JSON report export
- Configurable correlation field paths

**Technical Considerations**:
- Parallel topic scanning
- Configurable correlation field extraction
- Time-window bounding for efficiency
- Caching for repeated traces

---

### 7. `nexflow dlq` - Dead Letter Queue Management

**Purpose**: Inspect, analyze, and reprocess messages from dead letter queues.

**Use Cases**:
- Investigate processing failures
- Retry failed messages after bug fixes
- Generate failure reports for SRE
- Identify systemic failure patterns

**Proposed Interface**:
```bash
nexflow dlq list --profile prod
nexflow dlq inspect orders.dlq --limit 100
nexflow dlq analyze orders.dlq --group-by error_type
nexflow dlq retry orders.dlq --filter "error_type = 'TIMEOUT'" --to orders-retry
nexflow dlq purge orders.dlq --older-than 30d --confirm
```

**DLQ Analysis Output**:
```
DLQ Analysis: orders.dlq
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Messages: 1,234
Time Range:     2025-01-15 to 2025-01-28

Error Distribution:
  VALIDATION_ERROR:    456 (37.0%)  ████████████░░░░░░░░
  TIMEOUT:             312 (25.3%)  ████████░░░░░░░░░░░░
  SCHEMA_MISMATCH:     234 (19.0%)  ██████░░░░░░░░░░░░░░
  DOWNSTREAM_FAILURE:  232 (18.8%)  ██████░░░░░░░░░░░░░░

Failure Trends (last 7 days):
  Mon: ████░░░░░░  45
  Tue: ██░░░░░░░░  23
  Wed: ███████░░░  78
  Thu: █████████░  92
  Fri: ████████████ 120  ← spike
  Sat: ██░░░░░░░░  18
  Sun: █░░░░░░░░░  12

Top Failing Records:
  customer:C456 - 23 failures (VALIDATION_ERROR)
  customer:C789 - 18 failures (TIMEOUT)
```

**Key Features**:
- DLQ discovery (convention-based: `*.dlq`, `*-dlq`)
- Error categorization and grouping
- Trend analysis
- Selective retry with filtering
- Transformation before retry
- Purge with safety confirmations
- Report generation

**Technical Considerations**:
- Error metadata extraction (headers, wrapper fields)
- Original topic detection for retry routing
- Idempotent retry (deduplication)
- Audit logging for compliance

---

## Implementation Priority Matrix

| Tool | User Value | Complexity | Dependencies | Priority |
|------|------------|------------|--------------|----------|
| `stats` | High | Low | Kafka AdminClient | P1 |
| `search` | High | Medium | Multi-topic consumer | P1 |
| `dlq` | High | Medium | Error metadata parsing | P1 |
| `trace` | High | Medium | Correlation extraction | P2 |
| `export` | Medium | Medium | PyArrow, cloud SDKs | P2 |
| `snapshot` | Medium | High | Storage abstraction | P3 |
| `restore` | Medium | High | Schema validation | P3 |

---

## Common Infrastructure Requirements

### Shared Components

1. **Multi-Topic Consumer**
   - Parallel consumption across topics
   - Wildcard topic resolution
   - Unified message iteration

2. **Storage Abstraction**
   - Local filesystem
   - S3/GCS/Azure Blob
   - Compression handlers

3. **Progress Tracking**
   - Resumable operations
   - Checkpoint persistence
   - Progress reporting

4. **Output Formatters**
   - JSON, YAML, Table, CSV
   - HTML reports
   - Prometheus metrics

### Configuration Extensions

```toml
# nexflow.toml additions

[stream.search]
default_topics = ["orders-*", "events-*"]
max_results = 10000

[stream.export]
default_format = "parquet"
compression = "snappy"
partition_by = "date"

[stream.snapshots]
storage = "local"  # or "s3", "gcs"
path = "./snapshots"

[stream.dlq]
patterns = ["*.dlq", "*-dlq", "*-dead-letter"]
retention_days = 30
```

---

## Future Considerations

### Integration Points

- **Grafana/Prometheus**: Export metrics for dashboards
- **Slack/PagerDuty**: Alert on DLQ spikes
- **Jupyter Notebooks**: Export API for data science
- **VS Code Extension**: Inline stream preview

### Advanced Features

- **Time Travel**: Query topic state at specific timestamp
- **Schema Diff**: Compare schema versions with migration suggestions
- **Lineage Tracking**: Data lineage across transformations
- **Cost Analysis**: Estimate storage/compute costs by topic

---

## References

- [Current Stream Tools Implementation](../BACKEND-USAGE.md)
- [Kafka Configuration](../specs/SERIALIZATION-CONFIG.md)
- [Data Flow Architecture](../DATA-FLOW-ARCHITECTURE.md)
