# Nexflow Simple End-to-End Example

A complete demonstration of the Nexflow DSL-to-Flink compilation pipeline, showcasing L1 (Flow), L5 (Infrastructure), and L6 (Master Compiler) layers.

## Overview

This example demonstrates a simple order processing pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEXFLOW E2E PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

  Producer (Python)              Flink Cluster               Consumer (Python)
  ┌──────────────┐              ┌─────────────────┐          ┌──────────────┐
  │ produce_     │    Kafka     │ OrderProcessing │   Kafka  │ consume_     │
  │ orders.py    │──────────────▶     Job         │──────────▶ orders.py    │
  │              │ orders.input │                 │  orders. │              │
  └──────────────┘              └────────┬────────┘ processed└──────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │ EnrichOrder     │
                                │ Function        │
                                │ ─────────────── │
                                │ + Calculate 8%  │
                                │   tax           │
                                │ + Add total     │
                                │ + Add timestamp │
                                └─────────────────┘
```

## Data Transformation

**Input (orders.input topic):**
```json
{
  "orderId": "ORD-00001",
  "customerId": "CUST001",
  "amount": 285.13,
  "status": "pending",
  "timestamp": 1734142893000
}
```

**Output (orders.processed topic):**
```json
{
  "orderId": "ORD-00001",
  "customerId": "CUST001",
  "amount": 285.13,
  "status": "pending",
  "timestamp": 1734142893000,
  "taxAmount": 22.81,
  "totalAmount": 307.94,
  "enrichedAt": "2025-12-14T03:01:33Z"
}
```

## Project Structure

```
simple-e2e/
├── nexflow.toml                    # Project configuration
├── README.md                       # This file
├── src/
│   ├── flow/
│   │   └── order_pipeline.proc     # L1 Flow DSL definition
│   └── infra/
│       └── local.infra             # L5 Infrastructure config
├── generated/                      # Generated Java code
│   ├── pom.xml                     # Maven build file
│   └── src/main/java/com/nexflow/examples/orders/
│       ├── flow/
│       │   └── OrderProcessingJob.java
│       ├── schema/
│       │   ├── Order.java          # Input record
│       │   └── EnrichedOrder.java  # Output record
│       └── transform/
│           └── EnrichOrderFunction.java
└── scripts/
    ├── produce_orders.py           # Test data producer
    └── consume_orders.py           # Output consumer
```

## Features Demonstrated

| Layer | Feature | Description |
|-------|---------|-------------|
| **L1 Flow** | Process definition | `receive`, `transform`, `emit` clauses |
| **L1 Flow** | Stream mode | Real-time streaming with watermarks |
| **L1 Flow** | Parallelism | `parallelism hint 2` for scaling |
| **L1 Flow** | Partitioning | `partition by customer_id` for key-based routing |
| **L5 Infra** | Kafka binding | Broker configuration for Docker environment |
| **L5 Infra** | Stream mapping | Logical names → physical Kafka topics |
| **L5 Infra** | Environment config | Local Docker vs production settings |
| **L6 Compiler** | Orchestration | Multi-phase compilation pipeline |
| **Code Gen** | Flink job | Full streaming job with Kafka connectors |
| **Code Gen** | Data Classes | Record-style classes with `with*()` methods |

## Prerequisites

- Docker and Docker Compose
- Java 11+ (Flink Docker image uses Java 11)
- Maven 3.x
- Python 3.8+ with `kafka-python` package

## Quick Start

### 1. Start Docker Infrastructure

```bash
cd ../../docker
docker compose up -d
```

Wait for services to be healthy:
```bash
docker compose ps
```

Expected services:
- `nexflow-kafka` (ports 9092 internal, 9093 external)
- `nexflow-flink-jobmanager` (port 8084 - Web UI)
- `nexflow-flink-taskmanager`
- `nexflow-zookeeper`
- `nexflow-kafka-ui` (port 8085 - Kafka message viewer)

### 2. Generate Code (if needed)

```bash
cd ../../
python3 -c "
from pathlib import Path
from backend.parser import parse as parse_dsl
from backend.generators.flow import FlowGenerator
from backend.generators.base import GeneratorConfig
from backend.parser.infra import InfraParser

example_dir = Path('examples/simple-e2e')
src_dir = example_dir / 'src'
output_dir = example_dir / 'generated'

# Parse L5 infrastructure
infra_config = InfraParser().parse_file(src_dir / 'infra/local.infra')

# Parse L1 flow
flow_content = (src_dir / 'flow/order_pipeline.proc').read_text()
flow_result = parse_dsl(flow_content, 'flow')

# Generate
config = GeneratorConfig(package_prefix='com.nexflow.examples.orders', output_dir=output_dir)
generator = FlowGenerator(config, infra_config=infra_config)
gen_result = generator.generate(flow_result.ast)

for f in gen_result.files:
    path = output_dir / f.path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f.content)
    print(f'Generated: {f.path}')
"
```

### 3. Build Java Project

```bash
cd examples/simple-e2e/generated
mvn clean package -DskipTests
```

### 4. Deploy to Flink

```bash
# Copy JAR to Flink
docker cp target/order-processing-1.0.0.jar nexflow-flink-jobmanager:/opt/flink/job/

# Submit job
docker exec nexflow-flink-jobmanager flink run -d /opt/flink/job/order-processing-1.0.0.jar
```

### 5. Send Test Data

```bash
cd ..
pip install kafka-python
python3 scripts/produce_orders.py localhost:9093 10
```

### 6. View Processed Output

```bash
python3 scripts/consume_orders.py localhost:9093 orders.processed
```

Or use the Kafka UI at http://localhost:8085

## DSL Files Explained

### L1 Flow DSL (`src/flow/order_pipeline.proc`)

```
process order_processing
    parallelism hint 2              # Scale to 2 parallel instances
    partition by customer_id        # Route by customer for ordering
    time by timestamp               # Event time processing
        watermark delay 5 seconds   # Handle late arrivals
    mode stream                     # Continuous streaming mode

    receive orders from input_orders    # Kafka source
        schema Order

    transform using enrich_order        # Apply transformation

    emit to processed_orders            # Kafka sink
        schema EnrichedOrder
end
```

### L5 Infrastructure Config (`src/infra/local.infra`)

```yaml
version: "1.0"
environment: local

kafka:
  brokers: localhost:9093           # External port for local access
  security_protocol: PLAINTEXT

streams:
  input_orders:                     # Logical name in L1
    topic: orders.input             # Physical Kafka topic
    parallelism: 2
    consumer_group: order-processing
    start_offset: earliest

  processed_orders:                 # Logical name in L1
    topic: orders.processed         # Physical Kafka topic
    parallelism: 2

resources:
  job_parallelism: 2
  task_slots: 2
  checkpoint_interval: 30s
  state_backend: rocksdb
```

## Generated Code Highlights

### Data Classes (Record-Style)

Nexflow generates data classes with record-style accessors (`field()` instead of `getField()`):

```java
public class Order implements Serializable {
    // Record-style accessors
    public String orderId() { return orderId; }
    public Double amount() { return amount; }

    // With methods for immutable-style updates
    public Order withAmount(Double amount) {
        return new Order(orderId, customerId, amount, status, timestamp);
    }
}
```

**Note:** The Nexflow generator produces true Java Records when targeting Java 16+.
This example uses Java 11 classes (for Flink Docker compatibility) with record-style API:
- **Record-style accessors** - `order.amount()` instead of `order.getAmount()`
- **With methods** - immutable update pattern
- **Factory methods** - `EnrichedOrder.fromOrder(order)`

### Flink Job Structure

```java
public class OrderProcessingJob {
    // Docker internal hostname for inter-container communication
    private static final String KAFKA_BOOTSTRAP_SERVERS =
        System.getenv().getOrDefault("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092");

    public void buildPipeline(StreamExecutionEnvironment env) {
        // Source: Kafka consumer with JSON deserialization
        KafkaSource<Order> source = KafkaSource.<Order>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setTopics("orders.input")
            .setValueOnlyDeserializer(new JsonDeserializationSchema<>(Order.class))
            .build();

        // Transform: Order → EnrichedOrder
        DataStream<EnrichedOrder> enriched = env
            .fromSource(source, WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofMillis(5000)), "input")
            .map(new EnrichOrderFunction());

        // Sink: Kafka producer with JSON serialization
        enriched.sinkTo(KafkaSink.<EnrichedOrder>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setRecordSerializer(...)
            .build());
    }
}
```

## Docker Networking Note

When running inside Docker containers, Flink uses Docker internal hostnames:
- **Internal**: `kafka:9092` (container-to-container)
- **External**: `localhost:9093` (host machine access)

The L5 infrastructure config should specify the appropriate broker address based on deployment context.

## Monitoring

- **Flink UI**: http://localhost:8084 - Job status, metrics, logs
- **Kafka UI**: http://localhost:8085 - Topics, messages, consumer groups

## Cleanup

```bash
# Stop Flink job
docker exec nexflow-flink-jobmanager flink cancel <JOB_ID>

# Stop all containers
cd ../../docker
docker compose down

# Remove volumes (clears Kafka data)
docker compose down -v
```

## Next Steps

This example demonstrates core L1/L5/L6 functionality. Future enhancements:

- **L2 Schema**: Auto-generate records from `.schema` DSL files
- **L3 Transform**: Generate transformation logic from `.xform` DSL files
- **L4 Rules**: Add decision logic from `.rules` DSL files
- **MongoDB Sink**: Persist results using L5 persistence config
