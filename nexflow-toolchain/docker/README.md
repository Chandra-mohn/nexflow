# Nexflow Docker Development Environment

Complete development environment for the Nexflow stream processing platform.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEXFLOW DATA ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────┘

                         ┌─────────────┐
                         │   Sources   │
                         └──────┬──────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                            KAFKA                                 │
│        (Topics: transactions, enriched-transactions, alerts)     │
└──────────┬────────────────────────────────────────┬─────────────┘
           │                                        │
           ▼                                        ▼
┌──────────────────────┐                 ┌──────────────────────┐
│   FLINK (Streaming)  │                 │    SPARK (Batch)     │
│   - Transformations  │                 │   - OLTP → OLAP      │
│   - Rules engine     │                 │   - Large extracts   │
│   - CEP patterns     │                 │   - Reporting prep   │
└──────────┬───────────┘                 └──────────┬───────────┘
           │                                        │
           ▼                                ┌───────┴───────┐
┌──────────────────────┐                   ▼               ▼
│   KAFKA CONNECT      │           ┌────────────┐  ┌────────────┐
│   (MongoDB Sink)     │           │ RAW        │  │ OLAP       │
└──────────┬───────────┘           │ Parquet    │  │ Parquet    │
           │                       │ (Archive)  │  │ (Reports)  │
           ▼                       └────────────┘  └────────────┘
┌──────────────────────┐                   │               │
│      MONGODB         │                   └───────┬───────┘
│   (Real-time DB)     │                           ▼
└──────────────────────┘                 ┌──────────────────┐
                                         │ Local Filesystem │
                                         │ (Docker Volume)  │
                                         │                  │
                                         │ Prod: TBD        │
                                         │ (S3/Ozone/HDFS)  │
                                         └──────────────────┘
```

## Key Design Decisions

| Data Flow | Method | Rationale |
|-----------|--------|-----------|
| Kafka → MongoDB | Kafka Connect (declarative) | No custom code, exactly-once semantics |
| Kafka → Parquet | Spark batch processing | OLTP→OLAP transforms, large extracts (10TB+) |
| Parquet Storage (Dev) | Local filesystem | Simple, no additional infrastructure |
| Parquet Storage (Prod) | TBD (S3/Ozone/HDFS) | Depends on deployment environment |
| Spark → MongoDB | **NOT ALLOWED** | Separation of concerns |

### Parquet Output Use Cases
- **Reporting**: Large-scale analytics and business intelligence
- **Data Extracts**: Up to 10TB for downstream systems
- **Future Mainframe Integration**: Ready for COBOL/EBCDIC export (out of scope for now)

## Services

| Service | Port | Description |
|---------|------|-------------|
| Kafka | 9092 (internal), 9093 (external) | Message broker |
| Zookeeper | 2181 | Kafka coordination |
| Schema Registry | 8081 | Avro/JSON schema management |
| Kafka Connect | 8083 | Data integration platform |
| Kafka UI | 8085 | Web interface for Kafka |
| MongoDB | 27017 | Real-time database |
| Flink JobManager | 8084 | Stream processing (Web UI) |
| Flink TaskManager | - | Stream processing workers |
| Spark Master | 8080 (Web), 7077 (RPC) | Batch processing master |
| Spark Worker | - | Batch processing workers |

## Quick Start

```bash
# Start everything
./scripts/start.sh

# Start only what you need
./scripts/start.sh kafka      # Kafka stack only
./scripts/start.sh streaming  # Kafka + Flink
./scripts/start.sh batch      # Kafka + Spark
./scripts/start.sh mongodb    # Kafka + MongoDB + Connect

# Check status
./scripts/status.sh

# Create topics
./scripts/create-topics.sh

# Deploy Kafka Connect connectors
./scripts/deploy-connector.sh

# Stop (preserve data)
./scripts/stop.sh

# Stop and remove all data
./scripts/stop.sh clean
```

## Resource Requirements

| Configuration | RAM | CPU | Disk |
|---------------|-----|-----|------|
| Kafka only | 4GB | 2 cores | 5GB |
| Streaming (Kafka+Flink) | 8GB | 4 cores | 10GB |
| Batch (Kafka+Spark) | 8GB | 4 cores | 10GB |
| Full environment | 12GB+ | 6+ cores | 20GB |

## MongoDB Collections

The MongoDB init script creates three collections matching L2 Schema DSL definitions:

- **transactions** - Raw transaction events from Kafka
- **enriched_transactions** - Processed transactions with risk scoring
- **alerts** - Fraud alerts and notifications

## Kafka Connect Connectors

### MongoDB Sink

Syncs data from Kafka topics to MongoDB collections:

```bash
# Deploy the connector
./scripts/deploy-connector.sh mongodb-sink-transactions

# Check connector status
curl http://localhost:8083/connectors/mongodb-sink-transactions/status
```

Topics mapped:
- `transactions` → `transactions` collection
- `enriched-transactions` → `enriched_transactions` collection
- `alerts` → `alerts` collection

## Development Workflows

### Testing Stream Processing (Flink)

```bash
# Start streaming stack
./scripts/start.sh streaming

# Submit Flink job
docker exec nexflow-flink-jobmanager flink run /path/to/job.jar

# Monitor at http://localhost:8084
```

### Testing Batch Processing (Spark)

```bash
# Start batch stack
./scripts/start.sh batch

# Submit Spark job
docker exec nexflow-spark-master spark-submit \
    --master spark://spark-master:7077 \
    /path/to/job.py

# Monitor at http://localhost:8080
# Output goes to parquet-output volume
```

### Accessing Parquet Output

```bash
# Copy parquet files from container
docker cp nexflow-spark-worker:/opt/bitnami/spark/output ./local-output

# Or mount a local directory by editing docker-compose.yml
```

## Troubleshooting

### Kafka Connect not starting

The MongoDB connector plugin is installed on first start. Wait for the installation to complete (check logs):

```bash
docker-compose logs -f kafka-connect
```

### Services unhealthy

Check individual service logs:

```bash
docker-compose logs kafka
docker-compose logs mongodb
docker-compose logs flink-jobmanager
```

### Reset everything

```bash
./scripts/stop.sh clean
./scripts/start.sh
```

## Credentials

| Service | Username | Password |
|---------|----------|----------|
| MongoDB (admin) | nexflow | nexflow_dev |
| MongoDB (app) | nexflow_app | nexflow_app_dev |

**Note**: These are development credentials. Use proper secrets management in production.
