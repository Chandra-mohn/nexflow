# ADR: Stream-Based Process Composition

**Status**: Accepted
**Date**: December 2024
**Authors**: Nexflow Architecture Team

## Context

During the design of Nexflow's process orchestration layer (L1), the question arose: should Nexflow support direct process-to-process invocation, such as `call process X` or `spawn process Y`?

This pattern is common in traditional programming (function calls) and some workflow engines (subprocess invocation). The appeal is intuitive composition - "Process A calls Process B to do some work."

## Decision

**Nexflow will NOT support direct process-to-process invocation.**

Processes compose exclusively through:
- **Streams** (emit/receive via Kafka topics)
- **Business signals** (markers and phase triggers)
- **Shared state** (state stores for coordination)
- **Correlation** (await/hold patterns for synchronization)

## Rationale

### 1. Streaming-First Philosophy

Nexflow is built on Apache Flink and Kafka. These systems are designed around continuous data streams, not request-response patterns. Direct process calls would:
- Introduce blocking semantics in a non-blocking runtime
- Fight against Flink's checkpoint/recovery model
- Create synchronous coupling in an asynchronous system

### 2. Fault Isolation

With stream-based composition:
```
Process A → [Kafka Topic] → Process B
```

If Process B fails:
- Process A continues operating (messages buffer in Kafka)
- Process B recovers independently and replays from offset
- No cascading failures

With direct invocation:
```
Process A --call--> Process B
```

If Process B fails:
- Process A blocks or fails
- Retry logic becomes complex
- Cascading failures are likely

### 3. Independent Scaling

Stream-based processes scale independently based on their own load characteristics:
- Process A: 10 instances (high input volume)
- Process B: 2 instances (computationally expensive)

Direct invocation couples scaling decisions and can create bottlenecks.

### 4. Explicit Topology

With streams, the data flow is explicit and visible:
```proc
// Clear: order_intake produces to enriched_orders
process order_intake
    receive orders from kafka_orders
    emit to enriched_orders
end

// Clear: fraud_check consumes from enriched_orders
process fraud_check
    receive enriched from enriched_orders
    emit to checked_orders
end
```

With direct calls, dependencies become hidden in code, making the topology harder to reason about.

### 5. Testability

Stream-based processes can be tested in complete isolation:
- Mock the input stream
- Assert on the output stream
- No need to stand up dependent processes

### 6. Existing Primitives Are Sufficient

Every use case for "call process" has a streaming equivalent:

| Desired Pattern | Streaming Solution |
|-----------------|-------------------|
| Sync enrichment | `emit` request → `await` response `matching on` correlation_id |
| Fire-and-forget | `emit to` topic (consumer picks up) |
| Fan-out/aggregate | `parallel` branches + `aggregate using` |
| Pipeline stages | Sequential `emit`/`receive` chains |
| Conditional routing | `route using` with multiple destinations |

## Consequences

### Positive
- Simpler mental model once understood (everything is streams)
- Better alignment with Flink/Kafka operational model
- Cleaner failure handling and recovery
- Independent deployment and scaling

### Negative
- Learning curve for developers expecting imperative composition
- Some patterns require more explicit configuration (correlation IDs)
- Request-response patterns require await/hold constructs

### Neutral
- Topology is defined by stream connections, not code structure
- Monitoring focuses on stream lag/throughput, not call latency

## Alternatives Considered

### Alternative 1: Synchronous `call process`
```proc
call process fraud_check
    params: { ... }
    timeout 5 seconds
```
**Rejected**: Introduces blocking in streaming context, tight coupling.

### Alternative 2: Asynchronous `spawn process`
```proc
spawn process notification_sender
    params: { ... }
```
**Rejected**: Equivalent to `emit to topic` but with hidden topology.

### Alternative 3: Pipeline `delegate to`
```proc
delegate to next_process
```
**Rejected**: Same as `emit to` but implies ownership transfer semantics that complicate reasoning.

## Implementation Notes

No implementation required - this ADR documents the intentional absence of a feature.

Documentation should:
1. Frame stream-based composition as a design strength
2. Provide clear patterns for common use cases
3. Show how await/hold handles correlation scenarios

## References

- [Flink Documentation: Async I/O](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/asyncio/)
- [Kafka Streams: Topology](https://kafka.apache.org/documentation/streams/developer-guide/processor-api.html)
- [Reactive Manifesto: Message-Driven](https://www.reactivemanifesto.org/)
