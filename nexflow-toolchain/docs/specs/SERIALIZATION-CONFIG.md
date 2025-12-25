# Nexflow Serialization Configuration

## Overview

Nexflow supports multiple serialization formats for Kafka Streams with a hierarchical configuration system designed for multi-team environments.

### Supported Formats

| Format | Use Case | Schema Registry |
|--------|----------|-----------------|
| `json` | Development, debugging, low volume | Optional |
| `avro` | Production, high volume, schema evolution | Required |
| `confluent_avro` | Enterprise, multi-team, governed schemas | Required |
| `protobuf` | Performance critical, cross-language | Optional |

---

## Architecture: Hybrid Model

```
┌─────────────────────────────────────────────────────────────┐
│           Shared Schema Library (Central Repo)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  schemas/                                            │   │
│  │  ├── order.schema      (format: avro)               │   │
│  │  ├── customer.schema   (format: avro)               │   │
│  │  └── event.schema      (format: protobuf)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                    Published as                             │
│                    Maven/npm artifact                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Team: Payments   │ │ Team: Fraud      │ │ Team: Analytics  │
│ ──────────────── │ │ ──────────────── │ │ ──────────────── │
│ nexflow.toml     │ │ nexflow.toml     │ │ nexflow.toml     │
│ payment.proc     │ │ fraud.proc       │ │ metrics.proc     │
│                  │ │                  │ │                  │
│ Uses: order,     │ │ Uses: order,     │ │ Uses: all        │
│       customer   │ │       event      │ │       schemas    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Configuration Hierarchy

### Resolution Order (highest priority first)

1. **Process-level override** - Explicit `format` in `.proc` file
2. **Schema-level declaration** - `serialization` block in `.schema` file
3. **Team config** - `nexflow.toml` in process directory
4. **Environment overlay** - `nexflow.{env}.toml`
5. **Built-in default** - JSON

### Priority Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Process Override (in .proc file)                            │
│   format json  ──────────────────────────────► Highest      │
└─────────────────────────────────────────────────────────────┘
                          │ if not specified
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Schema Declaration (in .schema file)                        │
│   serialization { format: avro }                            │
└─────────────────────────────────────────────────────────────┘
                          │ if not specified
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Team Config (nexflow.toml in process directory)             │
│   [serialization]                                           │
│   default_format = "avro"                                   │
└─────────────────────────────────────────────────────────────┘
                          │ if not specified
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Environment Overlay (nexflow.{env}.toml)                    │
│   Loaded based on NEXFLOW_ENV or --env flag                 │
└─────────────────────────────────────────────────────────────┘
                          │ if not specified
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Built-in Default                                            │
│   json ──────────────────────────────────────► Lowest       │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Files

### nexflow.toml (Team Configuration)

```toml
# Team-level serialization defaults
[serialization]
default_format = "avro"                    # json | avro | confluent_avro | protobuf

[serialization.registry]
url = "http://schema-registry:8081"        # Schema Registry URL
# For Confluent Cloud:
# url = "https://psrc-xxxxx.us-east-2.aws.confluent.cloud"
# api_key = "${SCHEMA_REGISTRY_API_KEY}"
# api_secret = "${SCHEMA_REGISTRY_API_SECRET}"

[serialization.avro]
compatibility = "BACKWARD"                  # BACKWARD | FORWARD | FULL | NONE
subject_naming = "TopicNameStrategy"        # TopicNameStrategy | RecordNameStrategy | TopicRecordNameStrategy
use_logical_types = true                    # Map decimal, date, timestamp to Avro logical types

[serialization.protobuf]
include_default_values = false
use_proto3 = true

[serialization.json]
include_null_fields = false
date_format = "ISO8601"
```

### nexflow.dev.toml (Environment Override)

```toml
# Development environment - human readable
[serialization]
default_format = "json"

[serialization.json]
pretty_print = true
include_null_fields = true
```

### nexflow.prod.toml (Production Override)

```toml
# Production environment - optimized
[serialization]
default_format = "avro"

[serialization.registry]
url = "https://prod-registry.company.com:8081"
```

---

## Schema-Level Declaration

Schemas can declare their preferred serialization format. This is useful for shared schemas that should always use a specific format.

### SchemaDSL Syntax

```
schema order
    // Optional: declare serialization preference
    serialization
        format avro
        compatibility BACKWARD
    end

    fields
        order_id: string
        customer_id: string
        amount: decimal(10, 2)
        order_date: timestamp
        status: string
    end
end
```

### Serialization Block Options

| Option | Values | Description |
|--------|--------|-------------|
| `format` | `json`, `avro`, `protobuf` | Serialization format |
| `compatibility` | `BACKWARD`, `FORWARD`, `FULL`, `NONE` | Schema evolution strategy |
| `subject` | string | Custom subject name for registry |

---

## Process-Level Override

Processes can override the format for specific connectors. Use sparingly.

### ProcDSL Syntax

```
process payment_processor
    // Uses schema's declared format (or team default)
    receive orders
        from kafka "orders"
        schema order

    // Override: legacy system requires JSON
    receive legacy_events
        from kafka "legacy_system"
        schema legacy_event
        format json                    // Explicit override

    // Uses schema's declared format
    emit to processed_orders
        schema processed_order
end
```

---

## Generated Code Examples

### JSON Serialization (Default)

```java
// Source
KafkaSource<Order> orderSource = KafkaSource.<Order>builder()
    .setBootstrapServers(brokers)
    .setTopics("orders")
    .setValueOnlyDeserializer(new JsonDeserializationSchema<>(Order.class))
    .build();

// Sink
KafkaSink<ProcessedOrder> sink = KafkaSink.<ProcessedOrder>builder()
    .setBootstrapServers(brokers)
    .setRecordSerializer(
        KafkaRecordSerializationSchema.<ProcessedOrder>builder()
            .setTopic("processed_orders")
            .setValueSerializationSchema(new JsonSerializationSchema<>())
            .build()
    )
    .build();
```

### Avro Serialization

```java
// Imports
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import org.apache.flink.formats.avro.AvroDeserializationSchema;
import org.apache.flink.formats.avro.AvroSerializationSchema;

// Source with Schema Registry
KafkaSource<Order> orderSource = KafkaSource.<Order>builder()
    .setBootstrapServers(brokers)
    .setTopics("orders")
    .setValueOnlyDeserializer(
        ConfluentRegistryAvroDeserializationSchema.forSpecific(
            Order.class,
            "http://schema-registry:8081"
        )
    )
    .build();

// Sink with Schema Registry
KafkaSink<ProcessedOrder> sink = KafkaSink.<ProcessedOrder>builder()
    .setBootstrapServers(brokers)
    .setRecordSerializer(
        KafkaRecordSerializationSchema.<ProcessedOrder>builder()
            .setTopic("processed_orders")
            .setValueSerializationSchema(
                ConfluentRegistryAvroSerializationSchema.forSpecific(
                    ProcessedOrder.class,
                    "processed_orders-value",
                    "http://schema-registry:8081"
                )
            )
            .build()
    )
    .build();
```

### Protobuf Serialization

```java
// Imports
import org.apache.flink.formats.protobuf.PbFormatConfig;
import org.apache.flink.formats.protobuf.deserialize.PbRowDataDeserializationSchema;
import org.apache.flink.formats.protobuf.serialize.PbRowDataSerializationSchema;

// Source
KafkaSource<Order> orderSource = KafkaSource.<Order>builder()
    .setBootstrapServers(brokers)
    .setTopics("orders")
    .setValueOnlyDeserializer(
        new ProtobufDeserializationSchema<>(Order.class)
    )
    .build();
```

---

## Maven Dependencies

Generated `pom.xml` includes format-specific dependencies:

### JSON (Always included)

```xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-json</artifactId>
    <version>${flink.version}</version>
</dependency>
```

### Avro (When format = avro or confluent_avro)

```xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-avro</artifactId>
    <version>${flink.version}</version>
</dependency>
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-avro-confluent-registry</artifactId>
    <version>${flink.version}</version>
</dependency>
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.5.0</version>
</dependency>
```

### Protobuf (When format = protobuf)

```xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-protobuf</artifactId>
    <version>${flink.version}</version>
</dependency>
<dependency>
    <groupId>com.google.protobuf</groupId>
    <artifactId>protobuf-java</artifactId>
    <version>3.25.0</version>
</dependency>
```

---

## Environment Variables

Configuration values can reference environment variables:

```toml
[serialization.registry]
url = "${SCHEMA_REGISTRY_URL}"
api_key = "${SCHEMA_REGISTRY_API_KEY}"
api_secret = "${SCHEMA_REGISTRY_API_SECRET}"
```

### Standard Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXFLOW_ENV` | Environment name (dev, staging, prod) |
| `SCHEMA_REGISTRY_URL` | Schema Registry URL |
| `SCHEMA_REGISTRY_API_KEY` | API key for Confluent Cloud |
| `SCHEMA_REGISTRY_API_SECRET` | API secret for Confluent Cloud |

---

## CLI Usage

### Build with environment

```bash
# Uses nexflow.dev.toml overlay
nexflow build --env dev

# Uses nexflow.prod.toml overlay
nexflow build --env prod

# Override format for testing
nexflow build --format json
```

### Validate configuration

```bash
# Show effective serialization config
nexflow config show serialization

# Validate schema registry connectivity
nexflow config validate --registry
```

---

## Migration Guide

### From JSON-only to Multi-Format

1. **Add nexflow.toml** to your process directory:
   ```toml
   [serialization]
   default_format = "json"  # Start with current behavior
   ```

2. **Add schema declarations** (optional):
   ```
   schema order
       serialization
           format avro
       end
       ...
   end
   ```

3. **Set up Schema Registry** and update config:
   ```toml
   [serialization]
   default_format = "avro"

   [serialization.registry]
   url = "http://localhost:8081"
   ```

4. **Test with environment overlay**:
   ```bash
   # Dev stays JSON
   nexflow build --env dev

   # Prod uses Avro
   nexflow build --env prod
   ```

---

## Best Practices

### 1. Schema-Level Format Declaration

Prefer declaring format in shared schemas rather than per-process overrides:

```
# Good: Format declared with schema (shared across teams)
schema order
    serialization
        format avro
    end
    ...
end

# Avoid: Format scattered across processes
receive orders
    format avro  # Don't do this for every process
```

### 2. Environment-Based Defaults

Use environment overlays for dev/prod differences:

```toml
# nexflow.dev.toml - Human readable
[serialization]
default_format = "json"

# nexflow.prod.toml - Optimized
[serialization]
default_format = "avro"
```

### 3. Override Only for Legacy Integration

Use process-level `format` override only for legacy systems:

```
receive legacy_events
    from kafka "legacy_system"
    format json  # OK: Legacy system can't change
```

### 4. Consistent Registry Configuration

All teams should use the same Schema Registry for schema governance:

```toml
# Org-level standard (nexflow.toml at repo root)
[serialization.registry]
url = "https://registry.company.com:8081"
```
