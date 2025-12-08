# Nexflow Zero-Code Generation Implementation Plan

**Date**: December 8, 2024
**Goal**: Achieve complete zero-code generation across all layers
**Reference**: COVENANT-Code-Generation-Principles.md

---

## Executive Summary

To achieve the zero-code vision where developers write only DSL and get production-ready Java, we need to fix/implement the following in priority order:

| Phase | Focus | Blocks | Effort | Priority |
|-------|-------|--------|--------|----------|
| **A** | Fix L4 Rules Generator | L1 route operator | Medium | **P0** |
| **B** | L3 Enrich/Lookup Support | L1 enrich operator | High | **P1** |
| **C** | Complete L1 Operator Wiring | Full pipeline | Low | **P1** |
| **D** | L5 Infrastructure Parser | L3 lookups | Medium | **P2** |
| **E** | L6 Compilation Orchestrator | Cross-layer | High | **P3** |

---

## Phase A: Fix L4 Rules Generator (CRITICAL)

### Problem Statement
L4 currently generates broken code:
1. Decision tables return `null` instead of actual values
2. Procedural rules have `if (true)` instead of real conditions

### A1: Fix Decision Table Result Generation

**Current Bug** (`rules/decision_table_generator.py`):
```java
private String getRow1Result(FraudCheckTableInput input) {
    return null;  // BUG: Should return "block"
}
```

**Required Fix**:
```java
private String getRow1Result(FraudCheckTableInput input) {
    return "block";  // Actual value from DSL
}
```

**Investigation Needed**:
- Locate where result values are stored in L4 AST
- Modify `DecisionTableGeneratorMixin` to extract and generate return values

### A2: Fix Procedural Rule Conditions

**Current Bug** (`rules/condition_generator.py`):
```java
if (true) {  // BUG: Should be actual condition
    if (true) {  // BUG: Should be account_age < 30
        applyAgeMultiplier(new BigDecimal("0.5"));
    }
}
```

**Required Fix**:
```java
if (input.getBaseLimit().compareTo(BigDecimal.ZERO) > 0
    && input.getAccountAge() >= 0) {
    if (input.getAccountAge() < 30) {
        applyAgeMultiplier(new BigDecimal("0.5"));
    }
}
```

**Investigation Needed**:
- Locate condition AST nodes in `rules_ast.py`
- Implement expression-to-Java conversion in `ConditionGeneratorMixin`

### A3: Generate ProcessFunction for Route Operator

**New Capability Needed**:
```java
// L4 should generate:
public class FraudRulesRouter
    extends ProcessFunction<Transaction, RoutedEvent> {

    public static final OutputTag<RoutedEvent> APPROVED_TAG =
        new OutputTag<RoutedEvent>("approved"){};
    public static final OutputTag<RoutedEvent> FLAGGED_TAG =
        new OutputTag<RoutedEvent>("flagged"){};
    public static final OutputTag<RoutedEvent> BLOCKED_TAG =
        new OutputTag<RoutedEvent>("blocked"){};

    @Override
    public void processElement(Transaction value, Context ctx,
            Collector<RoutedEvent> out) {
        String decision = evaluate(value);
        RoutedEvent event = new RoutedEvent(value, decision);

        switch(decision) {
            case "approve": ctx.output(APPROVED_TAG, event); break;
            case "flag": ctx.output(FLAGGED_TAG, event); break;
            case "block": ctx.output(BLOCKED_TAG, event); break;
            default: out.collect(event);
        }
    }

    private String evaluate(Transaction input) {
        // Decision table evaluation logic
        if (input.getAmount() > 50000 && "high".equals(input.getRiskTier())) {
            return "block";
        }
        // ... more rules
        return "approve";  // default
    }
}
```

**Implementation**:
- New generator: `rules/router_generator.py`
- Output type: Flink `ProcessFunction` with `OutputTag`s
- Integration: L1 references by name, L4 generates complete implementation

### A4: Generate AggregateFunction for Aggregate Operator

**New Capability Needed**:
```java
// L4 should generate:
public class FraudSummaryAggregator
    implements AggregateFunction<Transaction, FraudSummaryAccumulator, FraudSummary> {

    @Override
    public FraudSummaryAccumulator createAccumulator() {
        return new FraudSummaryAccumulator();
    }

    @Override
    public FraudSummaryAccumulator add(Transaction value, FraudSummaryAccumulator acc) {
        acc.count++;
        acc.totalAmount = acc.totalAmount.add(value.getAmount());
        if (value.isFraud()) acc.fraudCount++;
        return acc;
    }

    @Override
    public FraudSummary getResult(FraudSummaryAccumulator acc) {
        return new FraudSummary(acc.count, acc.totalAmount, acc.fraudCount);
    }

    @Override
    public FraudSummaryAccumulator merge(FraudSummaryAccumulator a,
            FraudSummaryAccumulator b) {
        // Merge logic for parallel execution
        return new FraudSummaryAccumulator(
            a.count + b.count,
            a.totalAmount.add(b.totalAmount),
            a.fraudCount + b.fraudCount
        );
    }
}
```

**Implementation**:
- New generator: `rules/aggregator_generator.py`
- Must parse aggregate DSL definitions
- Generate accumulator class + aggregate function

---

## Phase B: L3 Enrich/Lookup Support

### Problem Statement
L1 `enrich using X` operators need L3 to generate AsyncFunction implementations that perform lookups.

### B1: Define Lookup in L3 DSL

**Current L3 Syntax** (transforms only):
```xform
transform normalize_amount
    input: amount decimal
    output: result decimal
    apply
        result = amount * exchange_rate
    end
end
```

**Required L3 Syntax** (add lookups):
```xform
lookup customer_lookup
    source: mongodb.customers  // L5 reference
    key: card_id
    select
        customer_name
        risk_tier
        credit_score
    end
    cache: 5 minutes
end
```

### B2: Generate AsyncFunction

**L3 Should Generate**:
```java
public class CustomerLookupAsyncFunction
    extends RichAsyncFunction<Transaction, EnrichedTransaction> {

    private transient MongoClient client;
    private transient MongoCollection<Document> collection;

    // Configuration from L5
    private final String connectionUri;
    private final String database;
    private final String collectionName;

    public CustomerLookupAsyncFunction(LookupConfig config) {
        this.connectionUri = config.getUri();
        this.database = config.getDatabase();
        this.collectionName = config.getCollection();
    }

    @Override
    public void open(Configuration parameters) {
        client = MongoClients.create(connectionUri);
        collection = client.getDatabase(database)
            .getCollection(collectionName);
    }

    @Override
    public void asyncInvoke(Transaction input,
            ResultFuture<EnrichedTransaction> future) {
        CompletableFuture.supplyAsync(() -> {
            Document doc = collection
                .find(eq("card_id", input.getCardId()))
                .first();

            if (doc == null) {
                return EnrichedTransaction.from(input);  // No enrichment
            }

            return EnrichedTransaction.builder()
                .from(input)
                .customerName(doc.getString("customer_name"))
                .riskTier(doc.getString("risk_tier"))
                .creditScore(doc.getInteger("credit_score"))
                .build();
        }).whenComplete((result, error) -> {
            if (error != null) {
                future.completeExceptionally(error);
            } else {
                future.complete(Collections.singleton(result));
            }
        });
    }

    @Override
    public void close() {
        if (client != null) client.close();
    }
}
```

### B3: L5 Binding Integration

**L5 Provides** (`production.infra`):
```yaml
lookups:
  customer_lookup:
    type: mongodb
    uri: ${MONGO_URI}
    database: credit_card
    collection: customers
```

**L3 Generator Receives**:
```python
class LookupConfig:
    name: str
    type: str  # mongodb, redis, postgresql
    uri: str
    database: str
    collection: str
```

---

## Phase C: Complete L1 Operator Wiring

### C1: Wire Route Operator to L4 ProcessFunction

**Current** (stub):
```java
// [STUB] Route: fraud_rules
DataStream<Map<String, Object>> routed2Stream = transformed1Stream;
```

**Required**:
```java
// Route: fraud_rules
SingleOutputStreamOperator<RoutedEvent> routedMain = transformed1Stream
    .process(new FraudRulesRouter())
    .name("route-fraud_rules");

DataStream<RoutedEvent> approved = routedMain
    .getSideOutput(FraudRulesRouter.APPROVED_TAG);
DataStream<RoutedEvent> flagged = routedMain
    .getSideOutput(FraudRulesRouter.FLAGGED_TAG);
DataStream<RoutedEvent> blocked = routedMain
    .getSideOutput(FraudRulesRouter.BLOCKED_TAG);
```

### C2: Wire Enrich Operator to L3 AsyncFunction

**Current** (stub):
```java
// [STUB] Enrich: customer_lookup
DataStream<Transaction> enriched0Stream = kafkaTransactionsStream;
```

**Required**:
```java
// Enrich: customer_lookup
DataStream<EnrichedTransaction> enriched0Stream = AsyncDataStream
    .unorderedWait(
        kafkaTransactionsStream,
        new CustomerLookupAsyncFunction(lookupConfig),
        30, TimeUnit.SECONDS,
        100  // async capacity
    )
    .name("enrich-customer_lookup");
```

### C3: Wire Aggregate Operator to L4 AggregateFunction

**Current** (stub):
```java
// [STUB] Aggregate: fraud_summary
DataStream<Map<String, Object>> aggregated4Stream = routed2Stream;
```

**Required**:
```java
// Aggregate: fraud_summary (after window)
DataStream<FraudSummary> aggregated4Stream = windowedStream
    .aggregate(new FraudSummaryAggregator())
    .name("aggregate-fraud_summary");
```

### C4: Wire Window Operator

**Current** (stub):
```java
// [STUB] Window: tumbling (keyed window applied with aggregate)
```

**Required**:
```java
// Window: tumbling 1 minute
WindowedStream<RoutedEvent, String, TimeWindow> windowedStream = routed2Stream
    .keyBy(event -> event.getCustomerId())
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .allowedLateness(Time.seconds(10));
```

---

## Phase D: L5 Infrastructure Parser

### D1: YAML Parser

**New Module**: `backend/parser/infra_parser.py`

```python
import yaml
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class StreamBinding:
    name: str
    type: str  # kafka, kinesis, pulsar
    topic: str
    brokers: str
    properties: Dict[str, str]

@dataclass
class LookupBinding:
    name: str
    type: str  # mongodb, redis, postgresql
    uri: str
    database: str
    collection: str
    cache_ttl: Optional[int]

@dataclass
class InfraConfig:
    environment: str
    streams: Dict[str, StreamBinding]
    lookups: Dict[str, LookupBinding]
    checkpoints: Dict[str, Any]
    resources: Dict[str, Any]

def parse_infra(file_path: str) -> InfraConfig:
    with open(file_path) as f:
        data = yaml.safe_load(f)
    return InfraConfig(
        environment=data.get('environment'),
        streams=parse_streams(data.get('streams', {})),
        lookups=parse_lookups(data.get('lookups', {})),
        # ...
    )
```

### D2: Binding Resolution API

```python
class BindingResolver:
    def __init__(self, infra_config: InfraConfig):
        self.config = infra_config

    def resolve_stream(self, logical_name: str) -> StreamBinding:
        if logical_name not in self.config.streams:
            raise BindingError(f"No stream binding for '{logical_name}'")
        return self.config.streams[logical_name]

    def resolve_lookup(self, logical_name: str) -> LookupBinding:
        if logical_name not in self.config.lookups:
            raise BindingError(f"No lookup binding for '{logical_name}'")
        return self.config.lookups[logical_name]
```

---

## Phase E: L6 Compilation Orchestrator

### E1: Multi-DSL Discovery

```python
class NexflowCompiler:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.proc_files = list(project_root.glob("**/*.proc"))
        self.schema_files = list(project_root.glob("**/*.schema"))
        self.xform_files = list(project_root.glob("**/*.xform"))
        self.rules_files = list(project_root.glob("**/*.rules"))
        self.infra_files = list(project_root.glob("**/*.infra"))
```

### E2: Dependency Graph

```python
class DependencyGraph:
    def __init__(self):
        self.nodes = {}  # name -> definition
        self.edges = []  # (from, to, type)

    def add_process(self, proc: ProcessDefinition):
        self.nodes[proc.name] = proc

        # Extract dependencies
        for receive in proc.input.receives:
            if receive.schema:
                self.edges.append((proc.name, receive.schema.schema_name, 'schema'))

        for op in proc.processing:
            if isinstance(op, TransformDecl):
                self.edges.append((proc.name, op.transform_name, 'transform'))
            elif isinstance(op, RouteDecl):
                self.edges.append((proc.name, op.rule_name, 'rule'))
            elif isinstance(op, EnrichDecl):
                self.edges.append((proc.name, op.lookup_name, 'lookup'))

    def topological_sort(self) -> List[str]:
        # Return generation order
        ...
```

### E3: Coordinated Generation

```python
def compile(self) -> GenerationResult:
    # 1. Parse all DSL files
    schemas = [parse_schema(f) for f in self.schema_files]
    transforms = [parse_transform(f) for f in self.xform_files]
    rules = [parse_rules(f) for f in self.rules_files]
    processes = [parse_process(f) for f in self.proc_files]
    infra = parse_infra(self.infra_files[0]) if self.infra_files else None

    # 2. Build dependency graph
    graph = DependencyGraph()
    for proc in processes:
        graph.add_process(proc)

    # 3. Validate all references resolve
    self.validate_references(graph, schemas, transforms, rules)

    # 4. Generate in dependency order
    results = []

    # L2: Schemas first (no dependencies)
    for schema in schemas:
        results.append(SchemaGenerator(config).generate(schema))

    # L3: Transforms (depend on L2 schemas)
    for transform in transforms:
        results.append(TransformGenerator(config).generate(transform))

    # L4: Rules (depend on L2 schemas)
    for rule in rules:
        results.append(RulesGenerator(config).generate(rule))

    # L1: Processes last (depend on L2, L3, L4)
    for proc in processes:
        results.append(FlowGenerator(config, infra).generate(proc))

    return merge_results(results)
```

---

## Implementation Order

### Week 1: Phase A (L4 Fixes)
- [ ] A1: Investigate decision table AST structure
- [ ] A1: Fix result generation in decision_table_generator.py
- [ ] A2: Investigate procedural rule AST structure
- [ ] A2: Fix condition generation in condition_generator.py
- [ ] A3: Design ProcessFunction generation pattern
- [ ] A3: Implement router_generator.py

### Week 2: Phase C (L1 Wiring for Route) ✅ COMPLETED
- [x] C1: Wire L1 route operator to L4 ProcessFunction
- [x] C2: Wire L1 enrich operator to AsyncDataStream
- [x] C3: Wire aggregate operator to AggregateFunction
- [x] C4: Wire window operator with keyBy/window assigners
- [x] Add JoinDecl and MergeDecl support
- [x] Update imports to include all Flink classes
- [x] Create ScaffoldGenerator for dummy L3/L4 classes

### Week 3: Phase B (L3 Lookup) + Phase D (L5)
- [ ] D1: Implement YAML parser for .infra files
- [ ] B1: Extend L3 grammar for lookup definitions
- [ ] B2: Implement real AsyncFunction generator (replace scaffolds)

### Week 4: Phase A (L4 Fixes) + Phase E (Start)
- [ ] A1: Fix decision table result generation
- [ ] A2: Fix procedural rule condition generation
- [ ] A3: Implement Router ProcessFunction generator
- [ ] E1-E2: Start L6 orchestrator

### Ongoing: Phase E Completion
- [ ] Complete L6 compilation orchestrator
- [ ] Integration testing
- [ ] Documentation

---

## Success Criteria

### Per Phase

**Phase A Complete**:
- [ ] Decision tables return actual values
- [ ] Procedural rules generate real conditions
- [ ] Generated L4 code compiles

**Phase B Complete**:
- [ ] Lookup definitions parse correctly
- [ ] AsyncFunction generates for MongoDB
- [ ] Generated lookup code compiles

**Phase C Complete**: ✅ ACHIEVED (Dec 8, 2024)
- [x] L1 wires all operators to real implementations
- [x] No `[STUB]` comments in generated code
- [x] Generated pipeline references L3/L4 classes correctly
- [x] Scaffold generator provides compilable dummy implementations

**Phase D Complete**:
- [ ] .infra files parse correctly
- [ ] Bindings resolve to physical resources
- [ ] Environment variables substitute

**Phase E Complete**:
- [ ] Single command compiles entire project
- [ ] Cross-layer references all resolve
- [ ] Final artifact is deployable

### Overall Zero-Code Achievement

```
✅ Developer writes: .proc, .schema, .xform, .rules, .infra
✅ Toolchain generates: Complete, compilable, runnable Flink job
✅ No Java coding required
✅ No manual implementation
✅ Production-ready output
```

---

*Implementation plan created December 8, 2024*
*Reference: COVENANT-Code-Generation-Principles.md*
