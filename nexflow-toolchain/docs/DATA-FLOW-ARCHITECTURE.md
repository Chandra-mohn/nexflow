#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Data Flow Architecture

Complete end-to-end data flow from DSL definition through runtime execution.

---

## Overview

Nexflow transforms declarative DSL definitions into production-ready Apache Flink streaming applications. This document traces data flow through all six layers (L0-L5) across four phases: Design, Build, Deploy, and Runtime.

---

## Layer Summary

| Layer | File Type | Purpose | Output |
|-------|-----------|---------|--------|
| **L0** | `.java`, `.kt` | Hand-coded components (custom functions, utilities) | Compiled classes (referenced by L1-L4) |
| **L1** | `.proc` | Process orchestration | `*Job.java` - Flink DAG |
| **L2** | `.schema` | Data structure definitions | `*.java` - Records, Builders |
| **L3** | `.xform` | Field mappings & transformations | `*Transform.java` - MapFunctions |
| **L4** | `.rules` | Business decision logic | `*Rules.java` - Rule engines |
| **L5** | `.toml` | Infrastructure configuration | Runtime config injection |
| **External** | N/A | Infrastructure (Kafka, DBs, Schema Registry) | N/A - runtime dependencies |

---

## L0: Hand-Coded Components

L0 represents **developer-written code** that extends or customizes the generated pipeline. These components are referenced by DSL layers (L1-L4) and compiled alongside generated code.

### L0 Component Types

| Component Type | Used By | Purpose | Example |
|----------------|---------|---------|---------|
| **Custom Functions** | L3 Transform | Complex business logic not expressible in DSL | `GeoDistanceCalculator.java` |
| **Lookup Services** | L1 Process | External data enrichment | `CustomerLookupService.java` |
| **Custom Serializers** | L2 Schema | Special serialization formats | `EncryptedAvroSerializer.java` |
| **Validation Logic** | L1 Process | Complex validation rules | `FraudDetectionValidator.java` |
| **Aggregators** | L1 Process | Custom aggregation functions | `WeightedAverageAggregator.java` |
| **State Handlers** | L1 Process | Custom state management | `SessionStateHandler.java` |
| **Connectors** | L1 Process | Custom source/sink connectors | `RedisLookupConnector.java` |

### L0 Project Structure

```
project/
+-- src/
|   +-- main/
|   |   +-- java/com/company/
|   |       +-- functions/              # L0 - Custom functions
|   |       |   +-- GeoDistanceCalculator.java
|   |       |   +-- RiskScoreComputer.java
|   |       +-- services/               # L0 - Lookup services
|   |       |   +-- CustomerLookupService.java
|   |       |   +-- InventoryService.java
|   |       +-- validators/             # L0 - Custom validators
|   |       |   +-- FraudDetectionValidator.java
|   |       +-- serializers/            # L0 - Custom serializers
|   |           +-- EncryptedAvroSerializer.java
|   +-- dsl/
|       +-- flow/                       # L1 - .proc files
|       +-- schema/                     # L2 - .schema files
|       +-- transform/                  # L3 - .xform files
|       +-- rules/                      # L4 - .rules files
+-- generated/                          # Generated code (L1-L4 output)
```

### Referencing L0 from DSL Layers

**From L1 (Process):**
```
process OrderProcessor {
    receive Order from kafka "orders"

    // Reference L0 custom validator
    validate using com.company.validators.FraudDetectionValidator

    // Reference L0 lookup service
    enrich from com.company.services.CustomerLookupService
        on customer_id

    emit to "enriched-orders"
}
```

**From L3 (Transform):**
```
transform OrderEnrichment {
    input Order
    output EnrichedOrder

    mapping
        order_id -> order_id
        // Reference L0 custom function
        com.company.functions.GeoDistanceCalculator.calculate(lat, lon) -> distance
        com.company.functions.RiskScoreComputer.compute(amount, customer) -> risk_score
    end
}
```

### L0 Integration in Build Pipeline

```
+-------------------------------------------------------------------------+
|                        Build Pipeline with L0                           |
+-------------------------------------------------------------------------+
|                                                                         |
|  +-----------------+                                                    |
|  |  L0 Components  |  (Developer-written Java/Kotlin)                   |
|  |  src/main/java/ |                                                    |
|  +--------+--------+                                                    |
|           |                                                             |
|           |  +---------------------------------------------+            |
|           |  |  DSL Files (L1-L4)                          |            |
|           |  |  +-------+ +-------+ +-------+ +-------+    |            |
|           |  |  |.proc  | |.schema| |.xform | |.rules |    |            |
|           |  |  +---+---+ +---+---+ +---+---+ +---+---+    |            |
|           |  +------+--------+--------+--------+------+    |            |
|           |         |        |        |        |                        |
|           |         +--------+--------+--------+                        |
|           |                      |                                      |
|           |                      v                                      |
|           |            +-----------------+                              |
|           |            |  nexflow build  |                              |
|           |            |  (Generates L1-L4 Java)                        |
|           |            +--------+--------+                              |
|           |                     |                                       |
|           |                     v                                       |
|           |            +-----------------+                              |
|           |            |  generated/     |                              |
|           |            |  (L1-L4 Java)   |                              |
|           |            +--------+--------+                              |
|           |                     |                                       |
|           +---------------------+                                       |
|                                 |                                       |
|                                 v                                       |
|                       +-----------------+                               |
|                       |   mvn compile   |                               |
|                       |  (Compiles ALL) |                               |
|                       +--------+--------+                               |
|                                |                                        |
|                                v                                        |
|                       +-----------------+                               |
|                       |    app.jar      |                               |
|                       |  L0 + L1-L4     |                               |
|                       +-----------------+                               |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## End-to-End Flow Diagram

```
+-------------------------------------------------------------------------------------------------------------+
|                                    DESIGN TIME (Developer)                                                  |
+-------------------------------------------------------------------------------------------------------------+
|                                                                                                             |
|   L0 Hand-Coded            L2 SchemaDSL         L3 TransformDSL      L4 RulesDSL        L1 ProcDSL          |
|   ------------             -------------        ---------------      --------------     -----------         |
|   *.java / *.kt            order.schema         enrich.xform         credit.rules      process.proc         |
|   +-----------+            +-----------+        +-----------+        +-----------+     +-----------+        |
|   | Custom    |            | schema    |        | transform |        | rules     |     | process   |        |
|   | Functions |<-----------|  Order {  |        |  Enrich { |        |  Credit { |     |  Main {   |        |
|   | Services  |  imports   |   id      |        |   map ... |        |   decide  |     |   receive |        |
|   | Validators|            |   amount  |        |   filter  |        |   when... |     |   xform   |        |
|   | Connectors|            | }         |        | }         |        | }         |     |   emit    |        |
|   +-----------+            +-----------+        +-----------+        +-----------+     | }         |        |
|         |                        |                    |                    |           +-----------+        |
|         |                        |                    |                    |                 |              |
|         |                        +--------------------+--------------------+-----------------+              |
|         |                                             |                                                     |
|         |                                             v                                                     |
|         |                                   +-----------------+                                             |
|         |                                   |  nexflow build  |                                             |
|         |                                   |  (Generates L1-L4 Java)                                       |
|         |                                   +--------+--------+                                             |
|         |                                            |                                                      |
|         +--------------------------------------------+  (combined at mvn compile)                           |
|                                                      |                                                      |
+------------------------------------------------------+------------------------------------------------------+
                                               |
                                               v
+-------------------------------------------------------------------------------------------------------------+
|                                    BUILD TIME (Compiler)                                                    |
+-------------------------------------------------------------------------------------------------------------+
|                                                                                                             |
|   Generated Java Code                                                                                       |
|   -------------------                                                                                       |
|                                                                                                             |
|   +-----------------+   +-----------------+   +-----------------+   +-----------------+                     |
|   | Order.java      |   | EnrichXform.java|   | CreditRules.java|   | MainJob.java    |                     |
|   | (Record)        |   | (MapFunction)   |   | (RuleEngine)    |   | (Flink Job)     |                     |
|   |                 |   |                 |   |                 |   |                 |                     |
|   | + orderId()     |   | + apply()       |   | + evaluate()    |   | + main()        |                     |
|   | + amount()      |   | + filter()      |   | + decide()      |   | + buildPipeline |                     |
|   | + status()      |   |                 |   |                 |   |                 |                     |
|   +-----------------+   +-----------------+   +-----------------+   +-----------------+                     |
|          |                      |                     |                      |                              |
|          +----------------------+---------------------+----------------------+                              |
|                                              |                                                              |
|                                    +---------+---------+                                                    |
|                                    |     pom.xml       |                                                    |
|                                    |   + flink-kafka   |                                                    |
|                                    |   + flink-avro    |                                                    |
|                                    +---------+---------+                                                    |
|                                              |                                                              |
|                                      mvn package                                                            |
|                                              |                                                              |
|                                              v                                                              |
|                                    +-----------------+                                                      |
|                                    |  app.jar        |                                                      |
|                                    |  (Fat JAR)      |                                                      |
|                                    +--------+--------+                                                      |
|                                              |                                                              |
+----------------------------------------------+--------------------------------------------------------------+
                                               |
                                               v
+-------------------------------------------------------------------------------------------------------------+
|                              DEPLOY TIME (L5 Infrastructure)                                                |
+-------------------------------------------------------------------------------------------------------------+
|                                                                                                             |
|   L5 InfraDSL (nexflow.toml + environment configs)                                                          |
|   ------------------------------------------------                                                          |
|                                                                                                             |
|   +-------------------------------------------------------------------------------------+                   |
|   |  [kafka]                          [serialization]           [targets.flink]         |                   |
|   |  bootstrap = "kafka:9092"         registry.url = "..."      parallelism = 4         |                   |
|   |                                   default_format = avro     checkpoint = 60s        |                   |
|   +-------------------------------------------------------------------------------------+                   |
|                                              |                                                              |
|                                    flink run app.jar                                                        |
|                                              |                                                              |
+----------------------------------------------+--------------------------------------------------------------+
                                               |
                                               v
+-------------------------------------------------------------------------------------------------------------+
|                                    RUNTIME (Flink Cluster)                                                  |
+-------------------------------------------------------------------------------------------------------------+
|                                                                                                             |
|   External Systems (Infrastructure)                                                                         |
|   ---------------------------------                                                                         |
|                                                                                                             |
|   +--------------+          +-------------------------------------------+         +--------------+          |
|   |   Kafka      |          |              Flink Job                    |         |   Kafka      |          |
|   |   Source     |          |   +---------------------------------+     |         |   Sink       |          |
|   |   Topic      |          |   |                                 |     |         |   Topic      |          |
|   |              |          |   |  +-------+    +-------+    +-------+  |         |              |          |
|   | orders-input |--------->|   |  |Deser- |--->|Trans- |--->|Rules  |  |-------->| orders-out   |          |
|   |              |   Avro   |   |  |ialize |    |form   |    |Engine |  |  Avro   |              |          |
|   |              |   wire   |   |  |(L2)   |    |(L3)   |    |(L4)   |  |  wire   |              |          |
|   |              |  format  |   |  +-------+    +-------+    +-------+  | format  |              |          |
|   |              |          |   |                                 |     |         |              |          |
|   +--------------+          |   +---------------------------------+     |         +--------------+          |
|          |                  |                    |                      |                |                  |
|          |                  |              State Store                  |                |                  |
|          |                  |           (checkpointing)                 |                |                  |
|          |                  +-------------------------------------------+                |                  |
|          |                                       |                                       |                  |
|          v                                       v                                       v                  |
|   +--------------+                     +--------------+                        +--------------+             |
|   |   Schema     |                     |   Metrics    |                        |   Database   |             |
|   |   Registry   |<--------------------|   (Flink UI) |                        |   (MongoDB)  |             |
|   |              |   schema lookup     |              |                        |              |             |
|   |  order-value |   on deserialize    |  throughput  |                        |   persist    |             |
|   |  (Avro)      |                     |  latency     |                        |   results    |             |
|   +--------------+                     +--------------+                        +--------------+             |
|                                                                                                             |
+-------------------------------------------------------------------------------------------------------------+
```

---

## Phase 1: Design Time

### DSL Files and Their Relationships

```
                    +-------------------------------------+
                    |         L1 ProcDSL (.proc)          |
                    |    "The Orchestrator"               |
                    |                                     |
                    |  - Defines the processing pipeline  |
                    |  - References schemas, transforms   |
                    |  - Specifies sources and sinks      |
                    +----------------+--------------------+
                                     |
                                     | imports
                    +----------------+----------------+
                    |                |                |
                    v                v                v
        +---------------+  +---------------+  +---------------+
        | L2 SchemaDSL  |  | L3 TransformDSL|  | L4 RulesDSL  |
        |   (.schema)   |  |   (.xform)    |  |   (.rules)    |
        |               |  |               |  |               |
        | Data shapes   |  | Field maps    |  | Decision      |
        | Constraints   |  | Filters       |  | tables        |
        | PII markers   |  | Computations  |  | Conditions    |
        +---------------+  +---------------+  +---------------+
```

### Example: Order Processing System

**L2 Schema (order.schema)**
```
schema Order {
    identity
        order_id: string required
    end

    fields
        customer_id: string required
        amount: decimal(10,2) required
        currency: string = "USD"
        status: string = "pending"
        created_at: timestamp
    end

    serialization
        format confluent_avro
        compatibility BACKWARD
    end
}
```

**L3 Transform (enrich.xform)**
```
transform OrderEnrichment {
    input Order
    output EnrichedOrder

    mapping
        order_id -> order_id
        customer_id -> customer_id
        amount -> amount
        currency -> currency
        status -> status
        created_at -> created_at

        // Computed fields
        amount * 0.1 -> tax_amount
        amount + tax_amount -> total_amount
        uppercase(currency) -> currency_code
    end
}
```

**L4 Rules (credit.rules)**
```
rules CreditDecision {
    input EnrichedOrder
    output CreditResult

    decision_table
        hit_policy first

        | total_amount | customer_tier | -> decision    |
        |--------------|---------------|----------------|
        | < 100        | *             | AUTO_APPROVE   |
        | < 1000       | "gold"        | AUTO_APPROVE   |
        | < 1000       | "silver"      | REVIEW         |
        | < 1000       | *             | DECLINE        |
        | >= 1000      | "gold"        | REVIEW         |
        | >= 1000      | *             | DECLINE        |
    end
}
```

**L1 Process (order_processor.proc)**
```
process OrderProcessor {
    receive Order from kafka "orders-input"
        format confluent_avro
        consumer_group "order-processors"

    transform using OrderEnrichment

    evaluate using CreditDecision

    route by decision
        when "AUTO_APPROVE" -> emit to "approved-orders"
        when "REVIEW" -> emit to "review-queue"
        when "DECLINE" -> emit to "declined-orders"
    end
}
```

---

## Phase 2: Build Time

### Compilation Pipeline

```
+-------------------------------------------------------------------------+
|                        Master Compiler                                  |
+-------------------------------------------------------------------------+
|                                                                         |
|  Phase 1: Parse All DSL Files                                           |
|  ----------------------------                                           |
|  +---------+  +---------+  +---------+  +---------+                     |
|  | .schema |  | .xform  |  | .rules  |  | .proc   |                     |
|  | Parser  |  | Parser  |  | Parser  |  | Parser  |                     |
|  +----+----+  +----+----+  +----+----+  +----+----+                     |
|       |            |            |            |                          |
|       v            v            v            v                          |
|  +---------+  +---------+  +---------+  +---------+                     |
|  | Schema  |  |Transform|  | Rules   |  | Process |                     |
|  |  AST    |  |  AST    |  |  AST    |  |  AST    |                     |
|  +----+----+  +----+----+  +----+----+  +----+----+                     |
|       |            |            |            |                          |
|       +------------+------------+------------+                          |
|                           |                                             |
|  Phase 2: Resolve Imports & Validate                                    |
|  -----------------------------------                                    |
|                           |                                             |
|                           v                                             |
|                  +-----------------+                                    |
|                  | Import Resolver |                                    |
|                  |  + Validator    |                                    |
|                  +--------+--------+                                    |
|                           |                                             |
|  Phase 3: Generate Code (Dependency Order)                              |
|  -----------------------------------------                              |
|                           |                                             |
|       +-------------------+-------------------+                         |
|       |                   |                   |                         |
|       v                   v                   v                         |
|  +---------+        +---------+        +---------+                      |
|  |   L2    |        |   L3    |        |   L4    |                      |
|  |Generator|------->|Generator|------->|Generator|                      |
|  |(Schema) | refs   |(Xform)  | refs   |(Rules)  |                      |
|  +----+----+        +----+----+        +----+----+                      |
|       |                  |                  |                           |
|       |                  |                  |                           |
|       +------------------+------------------+                           |
|                          |                                              |
|                          v                                              |
|                    +---------+                                          |
|                    |   L1    |                                          |
|                    |Generator|  (Wires everything together)             |
|                    | (Proc)  |                                          |
|                    +----+----+                                          |
|                         |                                               |
|  Phase 4: Output                                                        |
|  ---------------                                                        |
|                         |                                               |
|                         v                                               |
|  +------------------------------------------------------------------+   |
|  | generated/                                                       |   |
|  | +-- src/main/java/com/nexflow/                                   |   |
|  | |   +-- schema/                                                  |   |
|  | |   |   +-- Order.java              (L2 Record)                  |   |
|  | |   |   +-- OrderBuilder.java       (L2 Builder)                 |   |
|  | |   |   +-- EnrichedOrder.java      (L2 Record)                  |   |
|  | |   |   +-- CreditResult.java       (L2 Record)                  |   |
|  | |   +-- transform/                                               |   |
|  | |   |   +-- OrderEnrichment.java    (L3 MapFunction)             |   |
|  | |   +-- rules/                                                   |   |
|  | |   |   +-- CreditDecision.java     (L4 RuleEngine)              |   |
|  | |   +-- flow/                                                    |   |
|  | |       +-- OrderProcessorJob.java  (L1 Flink Job)               |   |
|  | +-- pom.xml                                                      |   |
|  +------------------------------------------------------------------+   |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Generated Code Structure

**Order.java (L2 - Schema)**
```java
package com.nexflow.schema;

import java.math.BigDecimal;
import java.time.Instant;

public record Order(
    String orderId,
    String customerId,
    BigDecimal amount,
    String currency,
    String status,
    Instant createdAt
) {
    // Avro schema embedded for serialization
    public static org.apache.avro.Schema getClassSchema() { ... }
}
```

**OrderEnrichment.java (L3 - Transform)**
```java
package com.nexflow.transform;

import org.apache.flink.api.common.functions.MapFunction;
import com.nexflow.schema.Order;
import com.nexflow.schema.EnrichedOrder;

public class OrderEnrichment implements MapFunction<Order, EnrichedOrder> {
    @Override
    public EnrichedOrder apply(Order input) {
        BigDecimal taxAmount = input.amount().multiply(new BigDecimal("0.1"));
        BigDecimal totalAmount = input.amount().add(taxAmount);

        return new EnrichedOrder(
            input.orderId(),
            input.customerId(),
            input.amount(),
            input.currency(),
            input.status(),
            input.createdAt(),
            taxAmount,
            totalAmount,
            input.currency().toUpperCase()
        );
    }
}
```

**CreditDecision.java (L4 - Rules)**
```java
package com.nexflow.rules;

import com.nexflow.schema.EnrichedOrder;
import com.nexflow.schema.CreditResult;

public class CreditDecision {
    public CreditResult evaluate(EnrichedOrder input) {
        BigDecimal total = input.totalAmount();
        String tier = input.customerTier();

        // Decision table logic (hit_policy: first)
        if (total.compareTo(new BigDecimal("100")) < 0) {
            return CreditResult.AUTO_APPROVE;
        }
        if (total.compareTo(new BigDecimal("1000")) < 0) {
            if ("gold".equals(tier)) return CreditResult.AUTO_APPROVE;
            if ("silver".equals(tier)) return CreditResult.REVIEW;
            return CreditResult.DECLINE;
        }
        if ("gold".equals(tier)) return CreditResult.REVIEW;
        return CreditResult.DECLINE;
    }
}
```

**OrderProcessorJob.java (L1 - Process)**
```java
package com.nexflow.flow;

public class OrderProcessorJob {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Source: Kafka with Confluent Avro
        KafkaSource<Order> source = KafkaSource.<Order>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setTopics("orders-input")
            .setGroupId("order-processors")
            .setValueOnlyDeserializer(
                ConfluentRegistryAvroDeserializationSchema.forSpecific(
                    Order.class, SCHEMA_REGISTRY_URL))
            .build();

        DataStream<Order> orders = env.fromSource(source, ...);

        // Transform (L3)
        DataStream<EnrichedOrder> enriched = orders
            .map(new OrderEnrichment())
            .name("enrich-order");

        // Evaluate (L4)
        DataStream<Tuple2<EnrichedOrder, CreditResult>> evaluated = enriched
            .map(order -> Tuple2.of(order, new CreditDecision().evaluate(order)))
            .name("credit-decision");

        // Route by decision
        OutputTag<EnrichedOrder> reviewTag = new OutputTag<>("review") {};
        OutputTag<EnrichedOrder> declineTag = new OutputTag<>("decline") {};

        SingleOutputStreamOperator<EnrichedOrder> approved = evaluated
            .process(new ProcessFunction<>() {
                @Override
                public void processElement(...) {
                    switch (value.f1) {
                        case AUTO_APPROVE -> out.collect(value.f0);
                        case REVIEW -> ctx.output(reviewTag, value.f0);
                        case DECLINE -> ctx.output(declineTag, value.f0);
                    }
                }
            });

        // Sinks
        approved.sinkTo(buildKafkaSink("approved-orders"));
        approved.getSideOutput(reviewTag).sinkTo(buildKafkaSink("review-queue"));
        approved.getSideOutput(declineTag).sinkTo(buildKafkaSink("declined-orders"));

        env.execute("OrderProcessor");
    }
}
```

---

## Phase 3: Deploy Time

### Infrastructure Configuration (L5)

**nexflow.toml**
```toml
[project]
name = "order-processing"
version = "1.0.0"

[kafka]
bootstrap_servers = "kafka:9092"

[serialization]
default_format = "confluent_avro"

[serialization.registry]
url = "http://schema-registry:8081"

[serialization.avro]
compatibility = "BACKWARD"
subject_naming = "TopicNameStrategy"

[targets.flink]
parallelism = 4
checkpoint_interval = "60s"
state_backend = "rocksdb"
```

**Environment Overlays**

```toml
# nexflow.dev.toml
[kafka]
bootstrap_servers = "localhost:9092"

[serialization]
default_format = "json"  # Human readable for development
```

```toml
# nexflow.prod.toml
[kafka]
bootstrap_servers = "prod-kafka-1:9092,prod-kafka-2:9092,prod-kafka-3:9092"

[serialization.registry]
url = "https://prod-registry.company.com:8081"
api_key = "${SCHEMA_REGISTRY_API_KEY}"
api_secret = "${SCHEMA_REGISTRY_API_SECRET}"

[targets.flink]
parallelism = 16
checkpoint_interval = "30s"
```

---

## Phase 4: Runtime

### Message Flow Through the Pipeline

```
+-------------------------------------------------------------------------+
|                         Runtime Data Flow                               |
+-------------------------------------------------------------------------+
|                                                                         |
|  KAFKA SOURCE TOPIC: orders-input                                       |
|  +-------------------------------------------------------------+        |
|  |  Message (Confluent Avro Wire Format)                        |       |
|  |  +-------+--------------+----------------------------------+ |       |
|  |  | 0x00  | Schema ID    | Avro Binary Payload              | |       |
|  |  | magic | (4 bytes)    | (Order data)                     | |       |
|  |  | byte  | = 42         |                                  | |       |
|  |  +-------+--------------+----------------------------------+ |       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------+        |
|  |  1. DESERIALIZE (L2 Schema)                                  |       |
|  |                                                              |       |
|  |  ConfluentRegistryAvroDeserializer:                          |       |
|  |    1. Read magic byte (0x00) - validate Confluent format     |       |
|  |    2. Read schema ID (42) from bytes 1-4                     |       |
|  |    3. Lookup schema from registry (cached)                   |       |
|  |    4. Deserialize Avro binary to Order.java Record           |       |
|  |                                                              |       |
|  |  Registry Interaction:                                       |       |
|  |  +----------------------------------------------------------+|       |
|  |  | GET /schemas/ids/42                                      ||       |
|  |  | Response: { "schema": "{\"type\":\"record\",...}" }      ||       |
|  |  +----------------------------------------------------------+|       |
|  |                                                              |       |
|  |  Output: Order(orderId="ORD-123", amount=500.00, ...)        |       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------+        |
|  |  2. TRANSFORM (L3 Transform)                                 |       |
|  |                                                              |       |
|  |  OrderEnrichment.apply(order):                               |       |
|  |    - Copy existing fields                                    |       |
|  |    - Calculate: taxAmount = 500.00 * 0.1 = 50.00             |       |
|  |    - Calculate: totalAmount = 500.00 + 50.00 = 550.00        |       |
|  |    - Transform: currencyCode = "USD".toUpperCase() = "USD"   |       |
|  |                                                              |       |
|  |  Output: EnrichedOrder(orderId="ORD-123", totalAmount=550.00)|       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------+        |
|  |  3. EVALUATE (L4 Rules)                                      |       |
|  |                                                              |       |
|  |  CreditDecision.evaluate(enrichedOrder):                     |       |
|  |    - totalAmount = 550.00                                    |       |
|  |    - customerTier = "gold"                                   |       |
|  |                                                              |       |
|  |  Decision Table Execution:                                   |       |
|  |    +--------------+---------------+----------------+         |       |
|  |    | total_amount | customer_tier | decision       |         |       |
|  |    +--------------+---------------+----------------+         |       |
|  |    | < 100        | *             | AUTO_APPROVE   | skip    |       |
|  |    | < 1000       | "gold"        | AUTO_APPROVE   | MATCH   |       |
|  |    +--------------+---------------+----------------+         |       |
|  |                                                              |       |
|  |  Output: CreditResult.AUTO_APPROVE                           |       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------+        |
|  |  4. ROUTE (L1 Process)                                       |       |
|  |                                                              |       |
|  |  Decision: AUTO_APPROVE -> Route to "approved-orders" sink   |       |
|  |                                                              |       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------+        |
|  |  5. SERIALIZE (L2 Schema)                                    |       |
|  |                                                              |       |
|  |  ConfluentRegistryAvroSerializer:                            |       |
|  |    1. Get/register schema for EnrichedOrder (schema ID = 57) |       |
|  |    2. Serialize EnrichedOrder to Avro binary                 |       |
|  |    3. Prepend: magic byte (0x00) + schema ID (57)            |       |
|  |                                                              |       |
|  |  Registry Interaction (first message only):                  |       |
|  |  +----------------------------------------------------------+|       |
|  |  | POST /subjects/approved-orders-value/versions            ||       |
|  |  | Body: { "schema": "{\"type\":\"record\",...}" }          ||       |
|  |  | Response: { "id": 57 }                                   ||       |
|  |  +----------------------------------------------------------+|       |
|  |                                                              |       |
|  +-------------------------------------------------------------+        |
|                                    |                                    |
|                                    v                                    |
|  KAFKA SINK TOPIC: approved-orders                                      |
|  +-------------------------------------------------------------+        |
|  |  Message (Confluent Avro Wire Format)                        |       |
|  |  +-------+--------------+----------------------------------+ |       |
|  |  | 0x00  | Schema ID    | Avro Binary Payload              | |       |
|  |  | magic | (4 bytes)    | (EnrichedOrder data)             | |       |
|  |  | byte  | = 57         |                                  | |       |
|  |  +-------+--------------+----------------------------------+ |       |
|  +-------------------------------------------------------------+        |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Schema Registry Interaction

### Subject Naming Strategies

| Strategy | Subject Name | Use Case |
|----------|--------------|----------|
| `TopicNameStrategy` | `{topic}-value` | One schema per topic (default) |
| `RecordNameStrategy` | `{namespace}.{name}` | Same schema across topics |
| `TopicRecordNameStrategy` | `{topic}-{namespace}.{name}` | Multiple schemas per topic |

### Wire Format (Confluent Avro)

```
+-------------------------------------------------------------+
|                    Message Binary Layout                    |
+---------+------------------+--------------------------------+
| Byte 0  | Bytes 1-4        | Bytes 5+                       |
+---------+------------------+--------------------------------+
| 0x00    | Schema ID        | Avro Binary Data               |
| (magic) | (big-endian int) | (serialized record)            |
+---------+------------------+--------------------------------+
| 1 byte  | 4 bytes          | Variable length                |
+---------+------------------+--------------------------------+
```

### Schema Registration Flow

```
                                    First Message Written
                                           |
                                           v
                              +------------------------+
                              | Schema in local cache? |
                              +-----------+------------+
                                          |
                         +----------------+----------------+
                         | No                              | Yes
                         v                                 v
              +---------------------+           +---------------------+
              | POST to registry    |           | Use cached ID       |
              | /subjects/{topic}-  |           |                     |
              | value/versions      |           |                     |
              +----------+----------+           +----------+----------+
                         |                                 |
                         v                                 |
              +---------------------+                      |
              | Registry checks     |                      |
              | compatibility       |                      |
              +----------+----------+                      |
                         |                                 |
              +----------+----------+                      |
              | Compatible          | Incompatible         |
              v                     v                      |
    +-----------------+   +-----------------+              |
    | Return/assign   |   | Reject with     |              |
    | schema ID       |   | 409 Conflict    |              |
    +--------+--------+   +-----------------+              |
             |                                             |
             +---------------------+-----------------------+
                                   |
                                   v
                    +---------------------+
                    | Serialize message   |
                    | with schema ID      |
                    +---------------------+
```

---

## State Management

### Checkpointing Flow

```
+-------------------------------------------------------------------------+
|                         Flink Checkpointing                             |
+-------------------------------------------------------------------------+
|                                                                         |
|  Normal Processing                                                      |
|  -----------------                                                      |
|                                                                         |
|  Kafka ---> [Operator 1] ---> [Operator 2] ---> [Operator 3] ---> Kafka |
|               |                  |                  |                   |
|               |                  |                  |                   |
|  Checkpoint Trigger (every 60s)                                         |
|  ------------------------------                                         |
|               |                  |                  |                   |
|               v                  v                  v                   |
|         +----------+       +----------+       +----------+              |
|         | Snapshot |       | Snapshot |       | Snapshot |              |
|         | State    |       | State    |       | State    |              |
|         +----+-----+       +----+-----+       +----+-----+              |
|              |                  |                  |                    |
|              +------------------+------------------+                    |
|                                 |                                       |
|                                 v                                       |
|                        +---------------+                                |
|                        | State Backend |                                |
|                        |  (RocksDB)    |                                |
|                        +-------+-------+                                |
|                                |                                        |
|                                v                                        |
|                        +---------------+                                |
|                        |   S3 / HDFS   |                                |
|                        |  (Durable)    |                                |
|                        +---------------+                                |
|                                                                         |
|  Recovery (on failure)                                                  |
|  ---------------------                                                  |
|                                                                         |
|  1. Load latest checkpoint from S3/HDFS                                 |
|  2. Restore operator states                                             |
|  3. Reset Kafka offsets to checkpoint position                          |
|  4. Resume processing (exactly-once semantics)                          |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Metrics and Observability

### Key Metrics by Layer

| Layer | Metric | Description |
|-------|--------|-------------|
| **L0 (Kafka)** | `records-consumed-rate` | Input throughput |
| **L0 (Kafka)** | `records-produced-rate` | Output throughput |
| **L1 (Process)** | `numRecordsIn` | Records entering operator |
| **L1 (Process)** | `numRecordsOut` | Records leaving operator |
| **L2 (Schema)** | `deserialize-time-ms` | Schema deserialization latency |
| **L2 (Schema)** | `serialize-time-ms` | Schema serialization latency |
| **L3 (Transform)** | `transform-time-ms` | Transformation latency |
| **L4 (Rules)** | `evaluate-time-ms` | Rule evaluation latency |
| **L4 (Rules)** | `decision-distribution` | Count by decision outcome |

---

## Error Handling

### Dead Letter Queue Pattern

```
+-------------------------------------------------------------------------+
|                         Error Handling Flow                             |
+-------------------------------------------------------------------------+
|                                                                         |
|  +---------------+                                                      |
|  | Input Message |                                                      |
|  +-------+-------+                                                      |
|          |                                                              |
|          v                                                              |
|  +---------------+     +---------------------------------------------+  |
|  |  Deserialize  |---->| DeserializationException                    |  |
|  +-------+-------+     | - Invalid Avro format                       |  |
|          |             | - Schema not found                          |  |
|          |             | - Schema incompatible                       |  |
|          |             +----------------------+----------------------+  |
|          |                                    |                         |
|          v                                    |                         |
|  +---------------+     +---------------------------------------------+  |
|  |   Transform   |---->| TransformException                          |  |
|  +-------+-------+     | - Null pointer                              |  |
|          |             | - Computation error                         |  |
|          |             | - Type mismatch                             |  |
|          |             +----------------------+----------------------+  |
|          |                                    |                         |
|          v                                    |                         |
|  +---------------+     +---------------------------------------------+  |
|  |    Evaluate   |---->| RuleEvaluationException                     |  |
|  +-------+-------+     | - No matching rule                          |  |
|          |             | - Ambiguous match                           |  |
|          |             +----------------------+----------------------+  |
|          |                                    |                         |
|          v                                    |                         |
|  +---------------+                            |                         |
|  |   Serialize   |                            |                         |
|  +-------+-------+                            |                         |
|          |                                    |                         |
|          v                                    v                         |
|  +---------------+                    +---------------+                 |
|  |  Output Topic |                    |  DLQ Topic    |                 |
|  | (Success)     |                    | (Failures)    |                 |
|  +---------------+                    +---------------+                 |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Getting started guide |
| [SETUP-GUIDE.md](SETUP-GUIDE.md) | Installation and configuration |
| [SERIALIZATION-CONFIG.md](specs/SERIALIZATION-CONFIG.md) | Serialization formats and registry |
| [L1-ProcDSL-Reference.md](L1-ProcDSL-Reference.md) | Process DSL reference |
| [L2-SchemaDSL-Reference.md](L2-SchemaDSL-Reference.md) | Schema DSL reference |
| [L3-TransformDSL-Reference.md](L3-TransformDSL-Reference.md) | Transform DSL reference |
| [L4-RulesDSL-Reference.md](L4-RulesDSL-Reference.md) | Rules DSL reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture overview |
