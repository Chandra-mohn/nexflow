# L1 Flow (ProcDSL) Stabilization Plan

**Date**: December 7, 2024
**Priority**: Critical - Foundation layer for L2-L4
**Goal**: Generate compilable, runnable Flink jobs from L1 DSL

---

## Strategic Rationale

L1 (Process Orchestration) is the **foundational layer** that:
- Defines the pipeline structure that consumes L2-L4 outputs
- Orchestrates transforms (L3), rules (L4), and schemas (L2)
- Must be stable before other layers can be properly tested end-to-end

**Key Insight**: L1 doesn't need every feature complete - it needs a **minimal viable pipeline** that can:
1. Read from Kafka
2. Apply a transform (L3)
3. Apply a rule (L4)
4. Write to Kafka

Once this core works, other features can be incrementally added.

---

## Current State Analysis

### What Works
| Component | Status | Notes |
|-----------|--------|-------|
| Grammar (`ProcDSL.g4`) | ✅ Complete | 539 lines, all constructs defined |
| Parser/Visitors | ✅ Complete | 10 visitor modules, ~2,500 lines |
| AST Definitions | ✅ Complete | 14 AST modules with all node types |
| Job Class Structure | ✅ Works | Main class, constants, environment setup |
| Kafka Source | ⚠️ Partial | Missing deserializer |
| Checkpoint Config | ✅ Works | Generates correctly |

### What's Missing (TODOs in Generated Code)
| Component | Current State | Required |
|-----------|--------------|----------|
| Operator Wiring | TODO comments | Wire operators in sequence |
| Transform Invocation | Not generated | Call L3 transform functions |
| Enrich Operator | Skeleton only | AsyncDataStream lookup |
| Route Operator | Skeleton only | L4 rule evaluation |
| Window Operator | Not connected | Apply window before aggregate |
| Sink Generation | Comments only | KafkaSink with serializer |

---

## Phased Implementation Plan

### Phase 1: Minimal Viable Pipeline (MVP)
**Goal**: Source → Transform → Sink (simplest possible working pipeline)
**Estimated Complexity**: Medium

#### 1.1 Fix Kafka Source (Deserializer)
**File**: `source_generator.py`
```java
// Current (missing deserializer)
KafkaSource<Transaction> source = KafkaSource
    .<Transaction>builder()
    .setBootstrapServers(...)
    .build();

// Required (add JSON deserializer)
KafkaSource<Transaction> source = KafkaSource
    .<Transaction>builder()
    .setBootstrapServers(...)
    .setDeserializer(new JsonDeserializationSchema<>(Transaction.class))
    .build();
```

#### 1.2 Wire Transform Operator
**File**: `job_generator.py` - modify `_generate_build_pipeline_method`

Instead of TODO comments, generate:
```java
// Transform: normalize_amount
DataStream<EnrichedTransaction> transformedStream = kafkaTransactionsStream
    .map(new NormalizeAmountFunction())
    .name("transform-normalize_amount");
```

#### 1.3 Add Kafka Sink
**File**: `sink_generator.py`
```java
// Sink: processed_transactions
KafkaSink<EnrichedTransaction> processedSink = KafkaSink
    .<EnrichedTransaction>builder()
    .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
    .setRecordSerializer(
        KafkaRecordSerializationSchema.builder()
            .setTopic("processed_transactions")
            .setValueSerializationSchema(new JsonSerializationSchema<>())
            .build()
    )
    .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
    .build();

transformedStream.sinkTo(processedSink).name("sink-processed_transactions");
```

#### 1.4 Add Required Imports
- `org.apache.flink.formats.json.JsonDeserializationSchema`
- `org.apache.flink.formats.json.JsonSerializationSchema`
- Schema class imports from `{package}.schema.*`

**Phase 1 Deliverable**: A generated Flink job that:
- Reads JSON from Kafka topic
- Applies a single transform
- Writes JSON to output Kafka topic
- **Can compile and run** (assuming L2 schemas exist)

---

### Phase 2: Multi-Operator Pipeline
**Goal**: Source → Enrich → Transform → Route → Sink
**Estimated Complexity**: Medium-High

#### 2.1 Sequential Operator Chaining
**File**: `job_generator.py`

Refactor `_generate_build_pipeline_method` to:
1. Track current stream variable through operators
2. Generate each operator in sequence
3. Pass correct types between operators

```python
def _generate_build_pipeline_method(self, process):
    lines = [...]

    # Track stream through pipeline
    current_stream = self._generate_source(process)
    current_type = self._get_input_type(process)

    if process.processing:
        for op in process.processing:
            stream_code, current_stream, current_type = self._wire_operator(
                op, current_stream, current_type
            )
            lines.append(stream_code)

    # Generate sinks with final stream
    lines.append(self._generate_sinks(process, current_stream))
```

#### 2.2 Enrich Operator (AsyncDataStream)
**File**: `operator_generator.py`

Generate proper async lookup:
```java
// Enrich: customer_lookup on [customer_id]
SingleOutputStreamOperator<EnrichedRecord> enrichedStream = AsyncDataStream
    .unorderedWait(
        kafkaTransactionsStream,
        new CustomerLookupFunction(),
        30, TimeUnit.SECONDS,
        100  // async capacity
    )
    .name("enrich-customer_lookup");
```

**Note**: Requires `CustomerLookupFunction` to be either:
- Generated from a lookup definition (future L5/L6?)
- A stub that users implement

#### 2.3 Route Operator (ProcessFunction)
**File**: `operator_generator.py`

Generate L4 rule invocation:
```java
// Route: fraud_rules
SingleOutputStreamOperator<RoutedRecord> routedStream = enrichedStream
    .process(new FraudRulesRouter())
    .name("route-fraud_rules");
```

**Phase 2 Deliverable**: A generated pipeline with multiple operators chained correctly.

---

### Phase 3: Windowing & Aggregation
**Goal**: Support windowed operations
**Estimated Complexity**: Medium

#### 3.1 Window Operator Before Aggregate
**File**: `window_generator.py`

```java
// Window: tumbling 1 minute
WindowedStream<Record, String, TimeWindow> windowedStream = routedStream
    .keyBy(r -> r.getCustomerId())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .allowedLateness(Time.seconds(10));
```

#### 3.2 Aggregate Operator
```java
// Aggregate: fraud_summary
DataStream<AggregatedResult> aggregatedStream = windowedStream
    .aggregate(new FraudSummaryAggregator())
    .name("aggregate-fraud_summary");
```

**Phase 3 Deliverable**: Support for windowed aggregations in the pipeline.

---

### Phase 4: State & Resilience
**Goal**: Production-ready features
**Estimated Complexity**: High

#### 4.1 State Management
- Generate state descriptors
- Add TTL configuration
- Implement cleanup strategies

#### 4.2 Error Handling
- Dead letter queue routing
- Retry logic
- Side output for errors

#### 4.3 Backpressure Handling
- Drop strategy implementation
- Alert configuration

**Phase 4 Deliverable**: Production-ready pipeline with state and error handling.

---

### Phase 5: Advanced Features
**Goal**: Complete L1 feature set
**Estimated Complexity**: High

- Join operators (two-stream joins)
- Await/Hold correlation patterns
- Multiple output routing (fanout)
- Completion event handling

---

## Implementation Priority Matrix

| Phase | Feature | Business Value | Technical Risk | Priority |
|-------|---------|---------------|----------------|----------|
| 1 | Kafka Source w/Deserializer | High | Low | **P0** |
| 1 | Transform Wiring | High | Low | **P0** |
| 1 | Kafka Sink | High | Low | **P0** |
| 2 | Operator Chaining | High | Medium | **P1** |
| 2 | Enrich Operator | Medium | Medium | **P1** |
| 2 | Route Operator | Medium | Medium | **P1** |
| 3 | Window Operator | Medium | Medium | **P2** |
| 3 | Aggregate Operator | Medium | Medium | **P2** |
| 4 | State Management | Medium | High | **P3** |
| 4 | Error Handling | High | Medium | **P3** |
| 5 | Join/Await | Low | High | **P4** |

---

## File Change Summary

### Phase 1 Changes
| File | Changes Required |
|------|-----------------|
| `source_generator.py` | Add deserializer generation |
| `sink_generator.py` | Complete sink generation |
| `job_generator.py` | Wire transform operator, add imports |

### Phase 2 Changes
| File | Changes Required |
|------|-----------------|
| `job_generator.py` | Refactor for sequential operator chaining |
| `operator_generator.py` | Complete enrich/route generation |

### Phase 3 Changes
| File | Changes Required |
|------|-----------------|
| `window_generator.py` | Wire window before aggregate |
| `operator_generator.py` | Complete aggregate generation |

---

## Testing Strategy

### Unit Tests (per phase)
1. **Parser → AST**: Verify DSL parses to correct AST
2. **AST → Code**: Verify generator produces expected Java
3. **Code → Compile**: Verify generated code compiles

### Integration Tests
1. **Phase 1 Complete**: Run generated job against local Kafka
2. **Phase 2 Complete**: Verify operator chaining works
3. **Phase 3 Complete**: Verify windowed aggregation

### Sample DSL for Testing
```
process minimal_test
    parallelism 1
    mode stream

    receive events from test_input
        schema test_event

    transform using double_amount

    emit to test_output
        schema test_result
end
```

---

## Dependencies on Other Layers

| Dependency | Layer | Required For |
|------------|-------|--------------|
| Schema POJOs | L2 | Type-safe streams |
| Transform Functions | L3 | `map()` operators |
| Rule Evaluators | L4 | `process()` operators |

**Critical**: L1 generates code that **references** L2/L3/L4 classes but doesn't generate them. Those layers must also be working.

---

## Success Criteria

### Phase 1 Success
- [ ] Generated job compiles with `mvn compile`
- [ ] Job can be submitted to local Flink cluster
- [ ] Messages flow from input to output topic

### Phase 2 Success
- [ ] Multiple operators chain correctly
- [ ] Type safety maintained through pipeline
- [ ] No runtime ClassCastException

### Phase 3 Success
- [ ] Windowed aggregations produce correct results
- [ ] Late data handled according to config

### Overall L1 Stability
- [ ] Any valid L1 DSL produces compilable Java
- [ ] Generated code follows Flink best practices
- [ ] Performance is acceptable for production use

---

## Recommended Next Steps

1. **Immediate**: Implement Phase 1 (MVP pipeline)
   - Start with `source_generator.py` deserializer fix
   - Then `job_generator.py` transform wiring
   - Finally `sink_generator.py` completion

2. **Short-term**: Set up compilation test
   - Create Maven project structure in `generated/`
   - Add Flink dependencies to `pom.xml`
   - Automate `mvn compile` after generation

3. **Medium-term**: Implement Phases 2-3

---

*Plan created as part of Nexflow L1 stabilization effort - December 7, 2024*
