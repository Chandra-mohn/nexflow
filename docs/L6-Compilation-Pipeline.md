# L6: Compilation Pipeline Specification

> **Layer**: L6 - Code Generation
> **Status**: Specification
> **Version**: 1.0.0
> **Last Updated**: 2025-01-XX

---

## 1. Overview

### 1.1 Purpose

L6 is the **Compilation Pipeline** layer — transforms Nexflow into executable runtime code:

- Lexing and parsing (ANTLR4)
- AST construction and validation
- Semantic analysis and type checking
- Code generation (Flink SQL, Spark)
- UDF compilation from L4 business rules
- Deployment artifact packaging

The compiled code executes according to the runtime behavior defined in [`L1-Runtime-Semantics.md`](./L1-Runtime-Semantics.md).

### 1.2 Compilation Philosophy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Nexflow Compilation Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Source Text                                                        │
│       │                                                              │
│       ▼                                                              │
│   ┌───────────┐     ┌───────────┐     ┌───────────┐                │
│   │   Lexer   │ ──► │  Parser   │ ──► │    AST    │                │
│   │ (ANTLR4)  │     │ (ANTLR4)  │     │           │                │
│   └───────────┘     └───────────┘     └─────┬─────┘                │
│                                             │                        │
│                                             ▼                        │
│                                   ┌───────────────────┐             │
│                                   │ Semantic Analysis │             │
│                                   │                   │             │
│                                   │ • Reference Check │             │
│                                   │ • Type Validation │             │
│                                   │ • Cycle Detection │             │
│                                   └─────────┬─────────┘             │
│                                             │                        │
│           ┌─────────────────────────────────┼─────────────────┐     │
│           │                                 │                 │     │
│           ▼                                 ▼                 ▼     │
│   ┌───────────────┐               ┌───────────────┐   ┌───────────┐│
│   │  L2 Schema    │               │  L4 Business  │   │    L5     ││
│   │  Resolution   │               │  Rule Compile │   │  Binding  ││
│   └───────┬───────┘               └───────┬───────┘   └─────┬─────┘│
│           │                               │                 │       │
│           └───────────────┬───────────────┴─────────────────┘       │
│                           │                                          │
│                           ▼                                          │
│                   ┌───────────────┐                                 │
│                   │     IR        │   Intermediate Representation   │
│                   │ (Unified DAG) │                                 │
│                   └───────┬───────┘                                 │
│                           │                                          │
│           ┌───────────────┼───────────────┐                         │
│           │               │               │                         │
│           ▼               ▼               ▼                         │
│   ┌───────────────┐ ┌───────────┐ ┌───────────────┐                │
│   │  Flink SQL    │ │  Spark    │ │   Kafka       │                │
│   │  Generator    │ │ Generator │ │   Streams     │                │
│   └───────┬───────┘ └─────┬─────┘ └───────┬───────┘                │
│           │               │               │                         │
│           ▼               ▼               ▼                         │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │              Deployment Artifacts                          │    │
│   │  • DDL/DML statements  • JAR files  • Config files        │    │
│   └───────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Relationship to Other Layers

| Layer | Compilation Role |
|-------|-----------------|
| L1 | Source input - process definitions |
| L2 | Schema resolution - field types and structures |
| L3 | Transform expansion - UDF signatures |
| L4 | Rule compilation - decision logic to UDFs |
| L5 | Binding application - physical resource mapping |
| L6 | Orchestrates entire compilation |

---

## 2. Compilation Phases

### 2.1 Phase 1: Lexical Analysis

**Input**: Nexflow source text
**Output**: Token stream

```
Source: "process auth_enrichment parallelism 128"

Tokens:
  PROCESS_KW     → "process"
  IDENTIFIER     → "auth_enrichment"
  PARALLELISM_KW → "parallelism"
  INTEGER        → "128"
```

**ANTLR4 Lexer Rules** (from ProcDSL.g4):
- Keywords matched case-sensitively as lowercase
- Identifiers: `[a-z_][a-z0-9_]*`
- Duration literals: `[0-9]+('s'|'m'|'h'|'d')`
- Arrow operators: `→` or `->`

**Error Handling**:
- Invalid characters → Lexer error with position
- Unterminated strings → Recovery to next line
- Reserved word misuse → Suggest alternatives

### 2.2 Phase 2: Syntactic Analysis (Parsing)

**Input**: Token stream
**Output**: Parse tree (Concrete Syntax Tree)

```
ParseTree for "process auth_enrichment parallelism 128 receive events from kafka_topic end":

program
└── processDefinition
    ├── PROCESS_KW: "process"
    ├── processName
    │   └── IDENTIFIER: "auth_enrichment"
    ├── executionBlock
    │   └── parallelismDecl
    │       ├── PARALLELISM_KW: "parallelism"
    │       └── INTEGER: "128"
    ├── inputBlock
    │   └── receiveDecl
    │       ├── RECEIVE_KW: "receive"
    │       ├── IDENTIFIER: "events"
    │       ├── FROM_KW: "from"
    │       └── IDENTIFIER: "kafka_topic"
    └── END_KW: "end"
```

**Parser Recovery Strategies**:
- Missing `end` → Auto-close at next `process`
- Missing keyword → Suggest based on context
- Block order errors → Reorder with warning

### 2.3 Phase 3: AST Construction

**Input**: Parse tree
**Output**: Abstract Syntax Tree (typed, validated)

```java
// AST Node Hierarchy

sealed interface ASTNode permits ProcessNode, BlockNode, DeclNode

record ProcessNode(
    String name,
    ExecutionBlock execution,
    List<ReceiveDecl> inputs,
    List<ProcessingDecl> processing,
    CorrelationBlock correlation,
    List<EmitDecl> outputs,
    StateBlock state,
    ResilienceBlock resilience
) implements ASTNode

record ExecutionBlock(
    Integer parallelism,
    List<String> partitionKeys,
    TimeConfig time,
    ExecutionMode mode
) implements ASTNode

record ReceiveDecl(
    String alias,
    String source,
    String schema,
    ProjectClause projection,
    String storeTarget
) implements ASTNode

// ... additional node types
```

**AST Transformations**:
1. Remove syntactic sugar → normalize to canonical form
2. Expand defaults → explicit values for all optional elements
3. Validate structure → ensure required blocks present

### 2.4 Phase 4: Semantic Analysis

**Input**: AST
**Output**: Validated AST with resolved references

#### 2.4.1 Reference Resolution

```
L1 Reference          Resolution Target
─────────────────────────────────────────
schema customer_v1    → L2 schema definition
transform using xyz   → L3 transform definition
route using abc       → L4 rule set definition
customers (lookup)    → L5 physical binding
```

**Resolution Algorithm**:
```
for each reference in AST:
    1. Identify reference type (schema, transform, rule, source/sink)
    2. Lookup in appropriate catalog (L2, L3, L4, L5)
    3. If not found → Error: "Undefined reference: {name}"
    4. If found → Attach resolved definition to AST node
    5. Validate compatibility (types, arities, etc.)
```

#### 2.4.2 Type Checking

```
Field Type Propagation:

receive events from auth_events
    schema auth_event_v1        // L2 defines: { card_id: string, amount: decimal }
    project card_id, amount     // Validate: fields exist in schema

enrich using customer_lookup
    on card_id                  // Validate: card_id exists and is joinable
    select customer_name        // Validate: customer_name in lookup result
```

**Type Rules**:
- Partition keys must be hashable types
- Time fields must be timestamp types
- Join keys must have compatible types
- Aggregations require numeric types (for sum, avg, etc.)

#### 2.4.3 Cycle Detection

```
Process DAG Validation:

auth_enrichment → fraud_detection → routing → approved_handler
                                          ↘ declined_handler
                                          ↘ review_handler

✓ Valid: Directed Acyclic Graph (DAG)

auth_a → auth_b → auth_c → auth_a
✗ Invalid: Cycle detected
```

#### 2.4.4 Correlation Validation

```
await/hold Validation:

await auths
    until capture arrives
        matching on authorization_code    // Validate: field exists in both
    timeout 7 days
        emit to orphan_auths              // Validate: target exists

Checks:
- Correlation keys exist in both streams
- Correlation key types are compatible
- Timeout duration is reasonable (configurable limits)
- Timeout action target is valid
```

### 2.5 Phase 5: Intermediate Representation (IR)

**Input**: Validated AST
**Output**: Unified execution DAG

```
┌─────────────────────────────────────────────────────────────────┐
│                    Intermediate Representation                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  IR is a unified, runtime-agnostic representation that:         │
│                                                                  │
│  • Captures data flow as directed edges                         │
│  • Represents operators as nodes with typed inputs/outputs      │
│  • Preserves execution semantics (parallelism, time, state)     │
│  • Enables optimization passes before code generation           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**IR Node Types**:

```java
sealed interface IRNode permits SourceNode, SinkNode, OperatorNode

record SourceNode(
    String id,
    String physicalSource,      // From L5 binding
    Schema outputSchema,        // From L2
    List<String> projection,    // Fields to extract
    Watermark watermark
) implements IRNode

record SinkNode(
    String id,
    String physicalSink,        // From L5 binding
    Schema inputSchema,
    FanoutStrategy fanout
) implements IRNode

record OperatorNode(
    String id,
    OperatorType type,          // TRANSFORM, ROUTE, JOIN, AGGREGATE, etc.
    List<IREdge> inputs,
    Schema outputSchema,
    ExecutionConfig config
) implements IRNode

record IREdge(
    String sourceId,
    String targetId,
    List<String> partitionKeys,
    boolean broadcast
)
```

**IR Example**:
```
Process: auth_enrichment

IR Graph:
  SourceNode("kafka_auths")
      │
      ▼ partitionBy(card_id)
  OperatorNode("enrich_customer", LOOKUP_JOIN)
      │
      ▼
  OperatorNode("enrich_merchant", LOOKUP_JOIN)
      │
      ▼
  OperatorNode("fraud_check", UDF_TRANSFORM)
      │
      ▼
  OperatorNode("route_decision", UDF_ROUTE)
      │
      ├──► SinkNode("approved")
      ├──► SinkNode("declined")
      └──► SinkNode("review")
```

### 2.6 Phase 6: Optimization Passes

**Input**: IR
**Output**: Optimized IR

#### 2.6.1 Predicate Pushdown

```
Before:
  Source → Transform → Filter(amount > 1000)

After:
  Source(filter: amount > 1000) → Transform

Benefit: Reduce data volume early
```

#### 2.6.2 Projection Pushdown

```
Before:
  Source(all 5000 fields) → Project(10 fields) → Transform

After:
  Source(project: 10 fields) → Transform

Benefit: Reduce serialization/network overhead
```

#### 2.6.3 Operator Fusion

```
Before:
  Transform_A → Transform_B → Transform_C

After:
  FusedTransform_ABC

Benefit: Reduce operator overhead, single UDF call
```

#### 2.6.4 Partition Alignment

```
Before:
  Stream_A(partition: card_id) JOIN Stream_B(partition: account_id)
  // Requires shuffle

After:
  Stream_A(partition: card_id) JOIN Stream_B(repartition: card_id)
  // Explicit repartition inserted

Benefit: Optimize shuffle operations
```

---

## 3. Code Generation

### 3.1 Flink SQL Generation

#### 3.1.1 DDL Generation (Table Definitions)

**From L1 + L2 + L5**:
```sql
-- Generated from: receive events from auth_events schema auth_event_v1

CREATE TABLE auth_events (
    -- Fields from L2 schema: auth_event_v1
    event_id STRING,
    card_id STRING,
    merchant_id STRING,
    amount DECIMAL(15, 2),
    currency STRING,
    event_timestamp TIMESTAMP(3),

    -- Watermark from L1: watermark delay 30 seconds
    WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '30' SECOND,

    -- Metadata
    proc_time AS PROCTIME()
) WITH (
    -- Connector config from L5 binding
    'connector' = 'kafka',
    'topic' = 'prod.auth.events.v3',
    'properties.bootstrap.servers' = '${KAFKA_BROKERS}',
    'properties.group.id' = 'auth_enrichment_consumer',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'avro-confluent',
    'avro-confluent.url' = '${SCHEMA_REGISTRY_URL}'
);
```

**Lookup Table (from L1 enrich + L5)**:
```sql
-- Generated from: enrich using customer_lookup on card_id

CREATE TABLE customer_lookup (
    card_id STRING,
    customer_id STRING,
    customer_name STRING,
    credit_limit DECIMAL(15, 2),
    risk_tier STRING,
    PRIMARY KEY (card_id) NOT ENFORCED
) WITH (
    -- Connector config from L5 binding
    'connector' = 'mongodb',
    'uri' = '${MONGO_URI}',
    'database' = 'credit_card',
    'collection' = 'customers',
    'lookup.cache.max-rows' = '100000',
    'lookup.cache.ttl' = '1h'
);
```

**Sink Table**:
```sql
-- Generated from: emit to approved_auths

CREATE TABLE approved_auths (
    -- Fields from output schema
    event_id STRING,
    card_id STRING,
    customer_name STRING,
    amount DECIMAL(15, 2),
    approval_code STRING,
    processed_at TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'prod.auth.approved.v3',
    'properties.bootstrap.servers' = '${KAFKA_BROKERS}',
    'format' = 'avro-confluent',
    'avro-confluent.url' = '${SCHEMA_REGISTRY_URL}'
);
```

#### 3.1.2 DML Generation (Processing Logic)

**Enrichment Join**:
```sql
-- Generated from: enrich using customer_lookup on card_id select customer_name, risk_tier

INSERT INTO enriched_events
SELECT
    e.event_id,
    e.card_id,
    e.merchant_id,
    e.amount,
    e.currency,
    e.event_timestamp,
    -- Enriched fields from lookup
    c.customer_name,
    c.risk_tier
FROM auth_events e
LEFT JOIN customer_lookup FOR SYSTEM_TIME AS OF e.proc_time AS c
    ON e.card_id = c.card_id;
```

**Routing (with L4 UDF)**:
```sql
-- Generated from: route using fraud_detection_v2

INSERT INTO approved_auths
SELECT * FROM enriched_events
WHERE fraud_detection_v2(
    card_id, amount, risk_tier, merchant_id
) = 'approved';

INSERT INTO declined_auths
SELECT * FROM enriched_events
WHERE fraud_detection_v2(
    card_id, amount, risk_tier, merchant_id
) = 'declined';

INSERT INTO review_auths
SELECT * FROM enriched_events
WHERE fraud_detection_v2(
    card_id, amount, risk_tier, merchant_id
) = 'review';
```

**Windowed Aggregation**:
```sql
-- Generated from: window tumbling 1 hour, aggregate using hourly_summary_rules

INSERT INTO hourly_summaries
SELECT
    account_id,
    TUMBLE_START(event_timestamp, INTERVAL '1' HOUR) AS window_start,
    TUMBLE_END(event_timestamp, INTERVAL '1' HOUR) AS window_end,
    -- Aggregations from L4 rule: hourly_summary_rules
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MAX(amount) AS max_amount
FROM posted_transactions
GROUP BY
    account_id,
    TUMBLE(event_timestamp, INTERVAL '1' HOUR);
```

#### 3.1.3 Correlation Pattern Generation

**Await Pattern (Temporal Join with Timeout)**:
```sql
-- Generated from: await auths until capture arrives matching on authorization_code timeout 7 days

-- Pending authorizations state table
CREATE TABLE pending_auth_state (
    authorization_code STRING,
    auth_data ROW<...>,
    created_at TIMESTAMP(3),
    PRIMARY KEY (authorization_code) NOT ENFORCED
) WITH (
    'connector' = 'upsert-kafka',
    'topic' = 'pending-auth-state',
    ...
);

-- Matched transactions
INSERT INTO matched_transactions
SELECT
    a.authorization_code,
    a.auth_data,
    c.capture_data,
    c.event_timestamp AS match_timestamp
FROM pending_auth_state a
JOIN capture_events c
    ON a.authorization_code = c.authorization_code
WHERE c.event_timestamp <= a.created_at + INTERVAL '7' DAY;

-- Timeout handler (CEP pattern or scheduled trigger)
INSERT INTO orphan_authorizations
SELECT
    authorization_code,
    auth_data,
    created_at,
    CURRENT_TIMESTAMP AS timeout_at
FROM pending_auth_state
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '7' DAY;
```

### 3.2 Completion Event Code Generation

The L6 compiler generates Flink code that implements the **Sink Callback Pattern** for transaction confirmation.

#### 3.2.1 Completion Event AST Node

```java
// AST representation of completion event declaration
record CompletionEventBlock(
    CompletionTrigger trigger,           // COMMIT or COMMIT_FAILURE
    String targetTopic,                  // Logical name from L1
    String correlationField,             // Field for correlation_id
    List<String> includedFields,         // Fields to include in event
    Optional<String> schemaOverride      // Optional custom schema
) implements ASTNode

enum CompletionTrigger {
    COMMIT,           // on commit
    COMMIT_FAILURE    // on commit failure
}
```

#### 3.2.2 Generated Flink Sink with Callback

**From L1:**
```proc
emit to accounts_collection
    schema account_v1

on commit
    emit completion to transaction_completions
        correlation correlation_id
        include account_id, customer_id, status
```

**Generated Java (Flink MongoDB Sink with Completion Callback):**
```java
// Generated from L6 compiler: account_creation process
public class AccountCreationPipeline {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Source: account_requests
        DataStream<AccountRequest> requests = env
            .fromSource(kafkaSource("account_requests"), watermarkStrategy(), "account-requests");

        // Processing: enrich + transform
        DataStream<Account> accounts = requests
            .keyBy(AccountRequest::getCorrelationId)
            .process(new AccountEnrichmentFunction())
            .process(new AccountSetupTransform());

        // Sink with completion callback
        accounts.sinkTo(
            new CompletionCallbackSink<>(
                // Primary sink: MongoDB
                createMongoDbSink(),

                // Completion event producer
                new CompletionEventProducer(
                    kafkaProducer("transaction_completions"),
                    CompletionEventConfig.builder()
                        .correlationField("correlation_id")
                        .includedFields(List.of("account_id", "customer_id", "status"))
                        .processName("account_creation")
                        .build()
                ),

                // Failure event producer (optional)
                new CompletionEventProducer(
                    kafkaProducer("transaction_failures"),
                    CompletionEventConfig.builder()
                        .correlationField("correlation_id")
                        .includedFields(List.of("error_code", "retry_count"))
                        .processName("account_creation")
                        .build()
                )
            )
        );

        env.execute("account_creation");
    }
}
```

#### 3.2.3 CompletionCallbackSink Implementation Pattern

```java
/**
 * Generated sink wrapper that emits completion events after successful writes.
 * Implements Flink's TwoPhaseCommitSinkFunction for exactly-once semantics.
 */
public class CompletionCallbackSink<T> extends TwoPhaseCommitSinkFunction<T, Transaction, Void> {

    private final SinkFunction<T> primarySink;
    private final CompletionEventProducer successProducer;
    private final CompletionEventProducer failureProducer;

    @Override
    protected void invoke(Transaction transaction, T value, Context context) throws Exception {
        try {
            // Write to primary sink (e.g., MongoDB)
            WriteResult result = primarySink.invoke(value);

            // On success: emit completion event
            CompletionEvent completion = CompletionEvent.builder()
                .correlationId(extractCorrelationId(value))
                .transactionId(UUID.randomUUID().toString())
                .status(CompletionStatus.COMMITTED)
                .targetSystem(primarySink.getTargetSystem())  // "mongodb"
                .targetId(result.getInsertedId())             // MongoDB _id
                .timestamp(Instant.now())
                .processingDurationMs(calculateDuration(context))
                .includedFields(extractIncludedFields(value))
                .processName(config.getProcessName())
                .build();

            successProducer.send(completion);

        } catch (Exception e) {
            // On failure: emit failure event
            CompletionEvent failure = CompletionEvent.builder()
                .correlationId(extractCorrelationId(value))
                .transactionId(UUID.randomUUID().toString())
                .status(CompletionStatus.FAILED)
                .targetSystem(primarySink.getTargetSystem())
                .errorCode(classifyError(e))
                .errorMessage(e.getMessage())
                .retryCount(getRetryCount(context))
                .timestamp(Instant.now())
                .processName(config.getProcessName())
                .build();

            failureProducer.send(failure);
            throw e;  // Re-throw to trigger Flink's error handling
        }
    }

    @Override
    protected void preCommit(Transaction transaction) throws Exception {
        // Ensure completion events are flushed before checkpoint commit
        successProducer.flush();
        failureProducer.flush();
    }
}
```

#### 3.2.4 Completion Event Serialization

```java
/**
 * Generates Avro schema for completion_event_v1
 */
public class CompletionEventAvroGenerator {

    public static Schema generateSchema() {
        return SchemaBuilder.record("CompletionEvent")
            .namespace("com.procdsl.completion")
            .fields()
                .requiredString("correlation_id")
                .requiredString("transaction_id")
                .name("status").type().enumeration("CompletionStatus")
                    .symbols("COMMITTED", "FAILED").noDefault()
                .requiredString("target_system")
                .optionalString("target_id")
                .requiredLong("timestamp")
                .optionalLong("processing_duration_ms")
                .name("included_fields").type().map().values().stringType().noDefault()
                .optionalString("error_code")
                .optionalString("error_message")
                .optionalInt("retry_count")
                .requiredString("process_name")
                .optionalString("source_topic")
            .endRecord();
    }
}
```

#### 3.2.5 Generated DDL for Completion Topic

```sql
-- Generated from L1: on commit emit completion to transaction_completions

CREATE TABLE transaction_completions (
    correlation_id STRING NOT NULL,
    transaction_id STRING NOT NULL,
    status STRING NOT NULL,
    target_system STRING NOT NULL,
    target_id STRING,
    `timestamp` TIMESTAMP(3) NOT NULL,
    processing_duration_ms BIGINT,
    included_fields MAP<STRING, STRING>,
    error_code STRING,
    error_message STRING,
    retry_count INT,
    process_name STRING NOT NULL,
    source_topic STRING,
    PRIMARY KEY (correlation_id, transaction_id) NOT ENFORCED
) WITH (
    'connector' = 'upsert-kafka',
    'topic' = 'prod.transaction.completions.v1',
    'properties.bootstrap.servers' = '${KAFKA_BROKERS}',
    'key.format' = 'json',
    'value.format' = 'avro-confluent',
    'value.avro-confluent.url' = '${SCHEMA_REGISTRY_URL}'
);
```

### 3.3 UDF Generation (from L4)

#### 3.3.1 Routing UDF

**L4 Rule Definition**:
```
rule_set fraud_detection_v2
    routes approved, review, declined

    when risk_score < 0.7 and fraud_flag = false
        → route approved

    when risk_score >= 0.7 and risk_score < 0.9
        → route review

    otherwise → route declined
```

**Generated Java UDF**:
```java
@FunctionHint(
    input = @DataTypeHint("ROW<card_id STRING, amount DECIMAL, risk_tier STRING, merchant_id STRING>"),
    output = @DataTypeHint("STRING")
)
public class FraudDetectionV2 extends ScalarFunction {

    // Injected risk scoring service (from L5 binding)
    private transient RiskScoringService riskService;

    @Override
    public void open(FunctionContext context) {
        this.riskService = RiskScoringServiceFactory.create(
            context.getJobParameter("risk.service.url", "")
        );
    }

    public String eval(String cardId, BigDecimal amount, String riskTier, String merchantId) {
        // Compute risk score (this logic from L4 or external service)
        double riskScore = riskService.computeScore(cardId, amount, riskTier, merchantId);
        boolean fraudFlag = riskService.checkFraudFlag(cardId);

        // Generated from L4 rule conditions
        if (riskScore < 0.7 && !fraudFlag) {
            return "approved";
        } else if (riskScore >= 0.7 && riskScore < 0.9) {
            return "review";
        } else {
            return "declined";
        }
    }
}
```

#### 3.3.2 Transform UDF

**L3 Transform Definition** (conceptual):
```
transform customer_enrichment_block
    input auth_event_v1, customer_data_v1
    output enriched_auth_v1

    map
        enriched_amount = amount * exchange_rate
        full_name = concat(first_name, ' ', last_name)
        risk_adjusted_limit = credit_limit * risk_factor
```

**Generated Java UDF**:
```java
public class CustomerEnrichmentBlock extends ScalarFunction {

    public Row eval(Row authEvent, Row customerData) {
        BigDecimal amount = authEvent.getFieldAs("amount");
        BigDecimal exchangeRate = customerData.getFieldAs("exchange_rate");
        String firstName = customerData.getFieldAs("first_name");
        String lastName = customerData.getFieldAs("last_name");
        BigDecimal creditLimit = customerData.getFieldAs("credit_limit");
        BigDecimal riskFactor = customerData.getFieldAs("risk_factor");

        return Row.of(
            // Pass through original fields
            authEvent.getFieldAs("event_id"),
            authEvent.getFieldAs("card_id"),
            // Computed fields
            amount.multiply(exchangeRate),                              // enriched_amount
            firstName + " " + lastName,                                 // full_name
            creditLimit.multiply(riskFactor)                           // risk_adjusted_limit
        );
    }
}
```

### 3.3 Flink Job Configuration

**Generated flink-conf.yaml**:
```yaml
# Generated from L1 process: auth_enrichment
# Generated from L5 binding: production

# Parallelism from L1: parallelism 128
taskmanager.numberOfTaskSlots: 4
parallelism.default: 128

# State backend from L5
state.backend: rocksdb
state.backend.rocksdb.localdir: /tmp/rocksdb
state.backend.incremental: true

# Checkpointing from L1: checkpoint every 5 minutes to auth_checkpoints
execution.checkpointing.interval: 300000
execution.checkpointing.mode: EXACTLY_ONCE
execution.checkpointing.min-pause: 60000
state.checkpoints.dir: s3://company-checkpoints/auth/enrichment/

# Resource allocation from L5
taskmanager.memory.process.size: 8g
taskmanager.memory.managed.fraction: 0.4

# Restart strategy from L1 resilience block
restart-strategy: fixed-delay
restart-strategy.fixed-delay.attempts: 3
restart-strategy.fixed-delay.delay: 10s
```

### 3.4 Spark Structured Streaming Generation

For batch/micro-batch modes, generate Spark code:

```scala
// Generated from L1 process: hourly_transaction_summary
// Mode: micro_batch 1 minute

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger

object HourlyTransactionSummary {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("hourly_transaction_summary")
      .config("spark.sql.shuffle.partitions", "64")  // From L1: parallelism 64
      .getOrCreate()

    // Source from L5 binding
    val transactions = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", sys.env("KAFKA_BROKERS"))
      .option("subscribe", "prod.transactions.posted.v3")
      .option("startingOffsets", "latest")
      .load()
      .select(from_avro($"value", "transaction_v1").as("data"))
      .select("data.*")

    // Windowed aggregation from L1 + L4
    val summaries = transactions
      .withWatermark("event_timestamp", "1 minute")
      .groupBy(
        $"account_id",
        window($"event_timestamp", "1 hour")
      )
      .agg(
        count("*").as("transaction_count"),
        sum("amount").as("total_amount"),
        avg("amount").as("avg_amount"),
        max("amount").as("max_amount")
      )

    // Sink to L5 binding
    summaries.writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", sys.env("KAFKA_BROKERS"))
      .option("topic", "prod.summaries.hourly.v3")
      .option("checkpointLocation", "s3://checkpoints/hourly-summary/")
      .trigger(Trigger.ProcessingTime("1 minute"))  // From L1: micro_batch 1 minute
      .start()
      .awaitTermination()
  }
}
```

---

## 4. Deployment Artifacts

### 4.1 Artifact Structure

```
deployment/
├── auth_enrichment/
│   ├── sql/
│   │   ├── 01_ddl_sources.sql
│   │   ├── 02_ddl_lookups.sql
│   │   ├── 03_ddl_sinks.sql
│   │   └── 04_dml_processing.sql
│   ├── udfs/
│   │   ├── fraud-detection-v2.jar
│   │   └── customer-enrichment-block.jar
│   ├── config/
│   │   ├── flink-conf.yaml
│   │   └── log4j.properties
│   └── manifest/
│       ├── kubernetes.yaml
│       └── deployment-spec.json
│
├── hourly_summary/
│   ├── spark/
│   │   └── hourly-summary-job.jar
│   ├── config/
│   │   └── spark-defaults.conf
│   └── manifest/
│       └── kubernetes.yaml
│
└── shared/
    ├── schemas/
    │   └── avro/
    │       ├── auth_event_v1.avsc
    │       └── enriched_auth_v1.avsc
    └── udfs/
        └── common-transforms.jar
```

### 4.2 Deployment Manifest

```json
{
  "process": "auth_enrichment",
  "version": "1.2.0",
  "generated_at": "2025-01-15T10:30:00Z",
  "generator_version": "nexflow-compiler-0.2.0",

  "source_files": {
    "l1_process": "processes/auth_enrichment.proc",
    "l2_schemas": ["schemas/auth_event_v1.schema", "schemas/customer_v1.schema"],
    "l4_rules": ["rules/fraud_detection_v2.rule"],
    "l5_binding": "bindings/production.yaml"
  },

  "artifacts": {
    "sql_ddl": ["sql/01_ddl_sources.sql", "sql/02_ddl_lookups.sql", "sql/03_ddl_sinks.sql"],
    "sql_dml": ["sql/04_dml_processing.sql"],
    "udfs": ["udfs/fraud-detection-v2.jar"],
    "config": ["config/flink-conf.yaml"]
  },

  "runtime": {
    "engine": "flink",
    "version": "1.18.x",
    "mode": "streaming",
    "parallelism": 128,
    "checkpointing": {
      "interval_ms": 300000,
      "storage": "s3://company-checkpoints/auth/enrichment/"
    }
  },

  "dependencies": {
    "upstream_processes": [],
    "downstream_processes": ["fraud_detection", "approved_handler", "declined_handler"],
    "external_services": ["customer_lookup_mongodb", "risk_scoring_api"]
  },

  "deployment_target": {
    "platform": "kubernetes",
    "namespace": "flink-jobs",
    "resource_profile": "large"
  }
}
```

---

## 5. Compiler Architecture

### 5.1 Module Structure

```
nexflow-compiler/
├── lexer/
│   ├── ProcDSLLexer.g4          # ANTLR4 lexer grammar
│   └── generated/               # ANTLR4 generated code
│
├── parser/
│   ├── ProcDSLParser.g4         # ANTLR4 parser grammar (references ProcDSL.g4)
│   └── generated/               # ANTLR4 generated code
│
├── ast/
│   ├── nodes/                   # AST node definitions
│   ├── builder/                 # Parse tree → AST conversion
│   └── visitor/                 # AST traversal utilities
│
├── semantic/
│   ├── reference/               # L2/L3/L4/L5 reference resolution
│   ├── typecheck/               # Type checking and validation
│   ├── cycle/                   # Cycle detection in process DAG
│   └── validator/               # Semantic rule validation
│
├── ir/
│   ├── nodes/                   # IR node definitions
│   ├── builder/                 # AST → IR conversion
│   └── optimizer/               # Optimization passes
│
├── codegen/
│   ├── flink/
│   │   ├── sql/                 # DDL/DML generation
│   │   ├── udf/                 # UDF Java code generation
│   │   └── config/              # flink-conf.yaml generation
│   ├── spark/
│   │   ├── scala/               # Spark job generation
│   │   └── config/              # spark-defaults.conf generation
│   └── common/
│       ├── avro/                # Avro schema generation
│       └── manifest/            # Deployment manifest generation
│
├── cli/
│   ├── compile.py               # Main compilation entry point
│   ├── validate.py              # Validation-only mode
│   └── explain.py               # Explain compilation plan
│
└── tests/
    ├── lexer/
    ├── parser/
    ├── semantic/
    ├── codegen/
    └── integration/
```

### 5.2 Compiler CLI

```bash
# Compile a single process
nexflow compile auth_enrichment.proc \
    --binding production.yaml \
    --output deployment/auth_enrichment/

# Compile all processes in a directory
nexflow compile processes/ \
    --binding production.yaml \
    --output deployment/

# Validate without generating code
nexflow validate auth_enrichment.proc

# Explain compilation plan
nexflow explain auth_enrichment.proc --verbose

# Generate specific artifacts only
nexflow compile auth_enrichment.proc \
    --binding production.yaml \
    --only ddl,dml \
    --output sql/
```

### 5.3 Error Reporting

```
Error Format:

auth_enrichment.proc:15:5: error: undefined schema reference 'customer_v2'
   |
15 |     schema customer_v2
   |            ^^^^^^^^^^^
   |
   = help: did you mean 'customer_v1'?
   = note: available schemas: auth_event_v1, customer_v1, merchant_v1

auth_enrichment.proc:23:9: error: type mismatch in join key
   |
23 |     on card_id, account_type
   |        ^^^^^^^  ^^^^^^^^^^^^
   |        STRING   INTEGER
   |
   = help: join keys must have compatible types
   = note: card_id is STRING, account_type is INTEGER

Compilation failed with 2 errors.
```

---

## 6. Extensibility

### 6.1 Adding New Runtime Targets

```java
// Implement CodeGenerator interface
public interface CodeGenerator {
    void generateDDL(IRGraph ir, OutputContext ctx);
    void generateDML(IRGraph ir, OutputContext ctx);
    void generateConfig(IRGraph ir, OutputContext ctx);
    List<Artifact> getArtifacts();
}

// Register new generator
CompilerRegistry.registerGenerator("kafka-streams", new KafkaStreamsGenerator());
```

### 6.2 Custom Optimization Passes

```java
// Implement OptimizationPass interface
public interface OptimizationPass {
    IRGraph apply(IRGraph input);
    String getName();
    int getPriority();  // Lower = earlier
}

// Register custom pass
CompilerRegistry.registerOptimization(new CustomPredicatePushdown());
```

### 6.3 Plugin Architecture

```yaml
# compiler-plugins.yaml
plugins:
  - name: enterprise-security
    jar: plugins/enterprise-security.jar
    hooks:
      - phase: semantic-analysis
        class: com.company.SecurityValidator
      - phase: codegen
        class: com.company.AuditLogInjector

  - name: custom-metrics
    jar: plugins/custom-metrics.jar
    hooks:
      - phase: codegen
        class: com.company.MetricsInstrumentor
```

---

## 7. Code Generation Patterns (Reference)

This section references proven code generation patterns from the rules_engine project that can be adapted for Nexflow compilation.

### 7.1 ANTLR Visitor Pattern for AST Traversal

**Source**: `rules_engine/rules-dsl/backend/grammar_parser/template_code_generator.py`

The rules_engine uses ANTLR listeners to extract structured data from parse trees:

```python
class RuleDataExtractor(RulesListener):
    """
    ANTLR listener to extract structured rule data for code generation.
    Walks parse tree and builds Python data structures.
    """

    def __init__(self):
        self.rule_name = None
        self.entities = set()
        self.rule_steps = []
        self.complexity_score = 0

    def enterRule(self, ctx):
        """Extract rule name from parse context."""
        if ctx.ruleName():
            self.rule_name = ctx.ruleName().IDENTIFIER().getText()

    def enterAttribute(self, ctx):
        """Extract entity names from attributes (e.g., 'applicant' from 'applicant.creditScore')."""
        if ctx.attributeIdentifier():
            entity = ctx.attributeIdentifier(0).IDENTIFIER().getText()
            self.entities.add(entity)
```

**Key Patterns**:
- Separate listener classes for different extraction tasks
- Build intermediate data structures before code generation
- Track complexity metrics during traversal
- Handle nested structures via recursion depth tracking

### 7.2 Template-Based Code Generation

**Source**: `rules_engine/rules-dsl/backend/grammar_parser/template_code_generator.py`

Code generation uses Python f-strings as templates rather than external template engines:

```python
def _convert_rule_step(self, ctx):
    """Convert a rule step context to Java code."""
    if ctx.IF():
        condition = self._convert_condition(ctx.condition(0))
        then_block = self._convert_block(ctx.block(0), indent_level=1)

        java_code = f"if ({condition}) {{\n"
        java_code += then_block

        if ctx.ELSE():
            else_block = self._convert_block(ctx.block(1), indent_level=1)
            java_code += "} else {\n"
            java_code += else_block

        java_code += "}"
        return java_code
```

**Key Patterns**:
- No external template dependencies (no Jinja2)
- Recursive conversion of nested structures
- Indent level tracking for proper formatting
- Clean separation between extraction and generation phases

### 7.3 Type-Safe Comparison Generation

**Source**: `rules_engine/CURRENT_STATE_SUMMARY.md`

Generated code includes type-safe comparison utilities:

```java
// Generated comparison utility
java.util.function.BiFunction<Object, Object, Integer> compareValues = (a, b) -> {
    if (a == null && b == null) return 0;
    if (a == null) return -1;
    if (b == null) return 1;
    if (a instanceof Number && b instanceof Number) {
        double da = ((Number) a).doubleValue();
        double db = ((Number) b).doubleValue();
        return Double.compare(da, db);
    }
    return a.toString().compareTo(b.toString());
};

// Usage in generated condition
if (compareValues.apply(ctx.getValue("credit_score"), 700) >= 0) {
    return RuleResult.action("APPROVE");
}
```

**Key Patterns**:
- Null-safe comparisons built into generated code
- Automatic numeric type coercion
- Consistent comparison semantics across all rules
- Inline utility functions avoid external dependencies

### 7.4 Action Framework Generation

The rules_engine generates action invocation code with proper context handling:

```java
// Generated action invocation
List<Action> actions = new ArrayList<>();
actions.add(new Action("sendNotification", Map.of(
    "recipient", ctx.getValue("customer.email"),
    "template", "approval_notice"
)));
actions.add(new Action("updateStatus", Map.of(
    "account_id", ctx.getValue("account_id"),
    "new_status", "APPROVED"
)));
return new RuleResult(true, actions, null);
```

**Application to Nexflow**:
- L4 business rules → UDF code following these patterns
- L3 transforms → Generated transform functions
- Consistent action framework across all generated code

### 7.5 Adaptation for Nexflow

| rules_engine Pattern | Nexflow Application |
|---------------------|---------------------|
| ANTLR Listener extraction | L1 process → IR conversion |
| Template-based generation | Flink SQL, Spark code generation |
| Type-safe comparisons | L4 rule condition compilation |
| Action framework | L4 action execution in UDFs |
| Complexity scoring | Optimization pass prioritization |

**See Also**:
- [rules_engine CURRENT_STATE_SUMMARY.md](file:///Users/chandramohn/workspace/rules_engine/CURRENT_STATE_SUMMARY.md)
- [rules_engine template_code_generator.py](file:///Users/chandramohn/workspace/rules_engine/rules-dsl/backend/grammar_parser/template_code_generator.py)

---

## 8. Open Questions

| Question | Options | Notes |
|----------|---------|-------|
| Implementation language | Java / Kotlin / Scala | ANTLR4 has good Java support |
| IR format | Custom / Apache Calcite | Calcite gives SQL optimization for free |
| UDF packaging | Uber JAR / Modular | Trade-off: simplicity vs size |
| Multi-process compilation | Parallel / Sequential | DAG-aware scheduling |
| Incremental compilation | Full / Delta | Cache AST/IR for unchanged sources |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-01-XX | - | Added code generation patterns from rules_engine |
| 0.1.0 | 2025-01-XX | - | Initial draft |
