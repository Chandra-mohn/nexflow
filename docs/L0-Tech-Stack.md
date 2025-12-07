# Nexflow Technology Stack Specification

> **Status**: Approved
> **Version**: 2.0
> **Last Updated**: 2025-12-04

---

## Overview

This document specifies the technology stack for Nexflow in two categories:

1. **Development Toolchain** - Technologies used to build the DSL parser, code generators, and IDE tooling
2. **Target Runtime** - Technologies for generated executable code

Design principles:
- Minimize dependencies in development toolchain
- Maximize compatibility with enterprise streaming/batch platforms
- Support both real-time and batch processing patterns

---

## Category 1: Development Toolchain

### Core Stack

| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| **Parser Generator** | ANTLR4 | 4.13+ | Grammar definition and parser generation |
| **Runtime Language** | Python | 3.11+ | Parser, AST, visitors, code generation |
| **ANTLR Runtime** | antlr4-python3-runtime | 4.13.2 | Python bindings for ANTLR |
| **Template Engine** | Python f-strings | native | Zero external dependencies |
| **Configuration** | PyYAML | 6.0+ | Workspace and DSL configuration |
| **IDE Extension** | VS Code + TypeScript | 5.0+ | Language support extension |
| **Syntax Highlighting** | TextMate Grammar | - | `.tmLanguage.json` definitions |
| **Language Protocol** | LSP (TypeScript) | - | Validation, completion, diagnostics |
| **Dev Query Tool** | DuckDB | 1.0+ | Query DSL definitions and metadata |

### Per-Layer Tooling

| Layer | Grammar | Parser Output | Code Generator |
|-------|---------|---------------|----------------|
| **L1** (Flow) | `ProcDSL.g4` | Flow AST | `flow_generator.py` |
| **L2** (Schema) | `SchemaDSL.g4` | Schema AST | `schema_generator.py` |
| **L3** (Mapping) | `MappingDSL.g4` | Mapping AST | `mapping_generator.py` |
| **L4** (Rules) | `RulesDSL.g4` | Decision AST | `rules_generator.py` |
| **L5** (Config) | YAML (native) | Config dict | `config_generator.py` |
| **L6** (Deploy) | YAML (native) | Deploy dict | `deploy_generator.py` |

### Development Environment

```
nexflow/
├── grammar/                    # ANTLR4 grammar files
│   ├── ProcDSL.g4
│   ├── SchemaDSL.g4
│   ├── MappingDSL.g4
│   └── RulesDSL.g4
├── backend/                    # Python toolchain
│   ├── parser/                 # ANTLR-generated + visitors
│   ├── ast/                    # Python dataclass AST nodes
│   ├── generators/             # Code generators (f-strings)
│   ├── validators/             # Semantic validation
│   ├── api/                    # Flask REST API
│   └── schema/                 # Schema handling
├── extension/                  # VS Code extension
│   ├── src/                    # TypeScript source
│   ├── syntaxes/               # TextMate grammars
│   └── package.json
├── rules/                      # DSL source files
│   ├── schemas/                # Entity definitions
│   ├── flows/                  # L1 flow definitions
│   ├── mappings/               # L3 transformations
│   └── decisions/              # L4 decision tables
└── generated/                  # Output directory
    ├── java/                   # Generated Java code
    ├── avro/                   # Generated Avro schemas
    └── deploy/                 # Generated K8s manifests
```

### Python Dependencies

```
# requirements.txt
antlr4-python3-runtime==4.13.2
Flask==2.3.3
Flask-CORS==4.0.0
PyYAML==6.0.1
python-dotenv==1.0.0
requests==2.31.0

# Development only
duckdb==1.0.0                   # DSL metadata queries
pytest==8.0.0
black==24.0.0
```

### DuckDB Usage (Development Only)

DuckDB is used exclusively in the development environment for querying DSL definitions and metadata:

```sql
-- Query schema definitions
FROM read_avro('schemas/*.avsc');

-- Analyze rule complexity
SELECT rule_name, condition_count, action_count
FROM read_avro('metadata/rules.avro')
WHERE complexity_score > 5;

-- Cross-reference entities
SELECT entity, COUNT(*) as usage_count
FROM read_avro('metadata/dependencies.avro')
GROUP BY entity;
```

**Note**: DuckDB is NOT used for business data queries. Production data flows through Kafka/Flink/Spark.

---

## Category 2: Target Runtime

### Primary Streaming Platform

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Stream Processing** | Apache Flink | 1.18+ | Primary streaming runtime |
| **Message Broker** | Apache Kafka | 3.6+ | Event streaming backbone |
| **Schema Registry** | Confluent Schema Registry | 7.5+ | Avro schema management |
| **Serialization** | Apache Avro | 1.11+ | Binary message format |
| **State Store** | MongoDB | 6.0+ | Lookup tables, enrichment data |
| **Flink State** | RocksDB | embedded | Stateful stream processing |

### Batch/Hybrid Platform (Cloudera)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Batch Processing** | Apache Spark | 3.5+ | Large batch jobs, complex reports |
| **Micro-batch Streaming** | Spark Structured Streaming | 3.5+ | Small reports, seconds latency |
| **Object Store** | Apache Ozone | CDP 7.1.4+ | Scalable storage replacing HDFS |
| **Table Format** | Apache Iceberg | 1.4+ | Unified batch+streaming lakehouse |
| **Platform** | Cloudera Data Platform | 7.1.4+ | Enterprise Hadoop distribution |

### Processing Pattern Selection

| Pattern | Technology | Use Case | Latency |
|---------|------------|----------|---------|
| **Real-time Streaming** | Flink DataStream | Transaction processing, fraud detection | Milliseconds |
| **Micro-batch Reports** | Spark Structured Streaming | Small operational reports | Seconds |
| **Batch Jobs** | Spark Batch | Large reports, daily extracts | Minutes-Hours |
| **Lakehouse** | Iceberg + Spark | Historical analysis, backfill | Variable |

### Generated Code Targets

| Layer | Primary Output | Secondary Output | Format |
|-------|---------------|------------------|--------|
| **L1 Flow** | Flink DataStream jobs | Spark Structured Streaming | Java 17 |
| **L2 Schema** | Avro schemas + POJOs | JSON Schema (dev) | `.avsc` + `.java` |
| **L3 Mapping** | Flink MapFunction | Spark UDFs | Java 17 |
| **L4 Rules** | Flink ProcessFunction | - | Java 17 |
| **L5 Config** | Flink/Kafka properties | Spark config | `.yaml` / `.properties` |
| **L6 Deploy** | K8s + Flink Operator | Docker Compose (dev) | `.yaml` |

---

## Layer-Specific Generation Details

### L1: Flow DSL → Streaming Jobs

**Flink Target (Primary)**:
```java
// Generated: TransactionProcessingPipeline.java
public class TransactionProcessingPipeline {
    public static void main(String[] args) {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Kafka source with Avro deserialization
        KafkaSource<Transaction> source = KafkaSource.<Transaction>builder()
            .setBootstrapServers(config.getKafkaBootstrap())
            .setTopics("transactions")
            .setValueOnlyDeserializer(new AvroDeserializationSchema<>(Transaction.class))
            .build();

        // Processing pipeline
        DataStream<Transaction> stream = env.fromSource(source, WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(5)), "kafka-source");

        // ... transformations, rules, sinks
    }
}
```

**Spark Target (Secondary)**:
```java
// Generated: DailyReportJob.java (batch)
SparkSession spark = SparkSession.builder().appName("DailyReport").getOrCreate();
Dataset<Row> transactions = spark.read().format("iceberg").load("lakehouse.transactions");
// ... batch transformations

// Generated: OperationalReportStream.java (micro-batch)
Dataset<Row> stream = spark.readStream().format("kafka").load();
// ... structured streaming transformations
```

### L2: Schema DSL → Avro + POJOs

**Avro Schema Output**:
```json
{
  "type": "record",
  "name": "Transaction",
  "namespace": "com.proc.schema",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "amount", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}},
    {"name": "timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}}
  ]
}
```

**Generated POJO**:
```java
// Generated: Transaction.java
@AvroGenerated
public class Transaction extends SpecificRecordBase {
    private String id;
    private BigDecimal amount;
    private Instant timestamp;
    // ... getters, setters, builder
}
```

### L3: Mapping DSL → Transformations

**Flink MapFunction**:
```java
// Generated: TransactionEnricher.java
public class TransactionEnricher extends RichMapFunction<Transaction, EnrichedTransaction> {
    private transient MongoClient mongoClient;

    @Override
    public void open(Configuration parameters) {
        mongoClient = MongoClients.create(config.getMongoUri());
    }

    @Override
    public EnrichedTransaction map(Transaction txn) {
        // Lookup from MongoDB
        Document merchant = lookupMerchant(txn.getMerchantId());
        // Apply mapping rules
        return EnrichedTransaction.builder()
            .transaction(txn)
            .merchantName(merchant.getString("name"))
            .riskTier(merchant.getString("risk_tier"))
            .build();
    }
}
```

### L4: Rules DSL → Decision Logic

**Flink ProcessFunction**:
```java
// Generated: FraudDetectionRules.java
public class FraudDetectionRules extends KeyedProcessFunction<String, EnrichedTransaction, RuleResult> {

    @Override
    public void processElement(EnrichedTransaction txn, Context ctx, Collector<RuleResult> out) {
        // Decision table: fraud_detection_rules
        // hit_policy: first_match

        if (txn.getAmountVsAverage() > 20 && txn.getLocationDistance() > 500) {
            out.collect(RuleResult.block(txn, "High amount + distance"));
            return;
        }
        if (txn.getAmountVsAverage() > 10 && txn.getLocationDistance() > 500
            && "HIGH".equals(txn.getMerchantRiskTier())) {
            out.collect(RuleResult.block(txn, "Amount + distance + high-risk merchant"));
            return;
        }
        // ... additional rules
        out.collect(RuleResult.approve(txn));
    }
}
```

### L5: Config DSL → Runtime Configuration

```yaml
# Generated: flink-conf.yaml
execution.checkpointing.interval: 60000
execution.checkpointing.mode: EXACTLY_ONCE
state.backend: rocksdb
state.checkpoints.dir: s3://proc-checkpoints/fraud-detection

# Generated: kafka.properties
bootstrap.servers: kafka-cluster:9092
schema.registry.url: http://schema-registry:8081
```

### L6: Deploy DSL → Kubernetes Manifests

```yaml
# Generated: flink-deployment.yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: fraud-detection-pipeline
spec:
  image: nexflow/fraud-detection:1.0.0
  flinkVersion: v1_18
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "2"
  jobManager:
    resource:
      memory: "2048m"
      cpu: 1
  taskManager:
    resource:
      memory: "4096m"
      cpu: 2
    replicas: 3
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT TOOLCHAIN                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   ANTLR4     │    │   Python     │    │   VS Code    │     │
│   │   Grammar    │───▶│   Parser +   │◀───│  Extension   │     │
│   │   (.g4)      │    │   Generator  │    │  (TypeScript)│     │
│   └──────────────┘    └──────────────┘    └──────────────┘     │
│                              │                    │              │
│                              │              ┌─────▼─────┐       │
│                              │              │  DuckDB   │       │
│                              │              │ (dev only)│       │
│                              ▼              └───────────┘       │
│                       ┌──────────────┐                          │
│                       │  Generated   │                          │
│                       │    Code      │                          │
│                       └──────────────┘                          │
│                                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TARGET RUNTIME                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  STREAMING (Primary)                     │   │
│   │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ │   │
│   │  │  Kafka  │──▶│  Flink  │──▶│ MongoDB │   │  Avro   │ │   │
│   │  │         │   │         │   │ (state) │   │ Registry│ │   │
│   │  └─────────┘   └─────────┘   └─────────┘   └─────────┘ │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  BATCH/HYBRID (Cloudera)                 │   │
│   │  ┌─────────┐   ┌─────────┐   ┌─────────┐               │   │
│   │  │  Spark  │──▶│ Iceberg │──▶│  Ozone  │               │   │
│   │  │ Batch/  │   │ Tables  │   │ (o3fs)  │               │   │
│   │  │ Stream  │   │         │   │         │               │   │
│   │  └─────────┘   └─────────┘   └─────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DEPLOYMENT                                 │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │ Kubernetes  │   │    Flink    │   │  Prometheus │          │
│   │   Cluster   │   │  Operator   │   │  + Grafana  │          │
│   └─────────────┘   └─────────────┘   └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Version Compatibility Matrix

### Development Toolchain

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Python | 3.10 | 3.11+ | dataclasses, type hints |
| ANTLR4 | 4.13 | 4.13.2 | Python runtime |
| Node.js | 18 | 20 LTS | VS Code extension |
| TypeScript | 5.0 | 5.3 | Extension development |
| DuckDB | 0.10 | 1.0+ | Avro extension support |

### Target Runtime

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Java | 11 | 17 LTS | Generated code target |
| Apache Flink | 1.17 | 1.18 | Primary streaming |
| Apache Kafka | 3.5 | 3.6 | Message broker |
| Apache Spark | 3.4 | 3.5 | Batch + micro-batch |
| Apache Iceberg | 1.3 | 1.4 | Table format |
| MongoDB | 5.0 | 6.0+ | State store |
| Kubernetes | 1.26 | 1.28 | Container orchestration |
| Flink Operator | 1.5 | 1.6 | K8s deployment |

---

## Technology Rationale

### Why Python for Toolchain?
- Consistent with existing rules-dsl project
- Excellent ANTLR4 support via `antlr4-python3-runtime`
- f-strings provide clean, dependency-free templating
- Rapid development and iteration
- No Java in development toolchain (per requirement)

### Why Avro for Schemas?
- Native Kafka/Confluent integration
- Schema evolution with compatibility guarantees
- Compact binary serialization
- DuckDB support for development queries
- Industry standard for streaming data

### Why Flink as Primary Runtime?
- True event-at-a-time streaming (millisecond latency)
- Exactly-once semantics
- Sophisticated state management
- Native Kubernetes operator
- Strong Kafka/Avro integration

### Why Spark for Batch/Reports?
- Industry standard for large-scale batch
- Structured Streaming for micro-batch use cases
- Iceberg integration for lakehouse patterns
- Cloudera platform compatibility
- Familiar to enterprise data teams

### Why MongoDB for State?
- Flexible document model for lookup tables
- Strong consistency options
- Flink Async I/O support
- Good operational tooling
- Handles varied entity schemas

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-04 | Initial draft with Java toolchain |
| 2.0 | 2025-12-04 | Revised to Python toolchain, added Cloudera/Spark/Iceberg, clarified DuckDB scope |
