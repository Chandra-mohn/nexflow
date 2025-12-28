#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Backend Usage Guide

## Overview

The Nexflow backend is a Python-based compiler toolchain that transforms DSL files into production-ready Apache Flink Java code. This guide covers CLI usage, programmatic API, and project configuration.

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- ANTLR4 runtime

### Install Dependencies
```bash
pip install click rich toml antlr4-python3-runtime
```

### Generate ANTLR Parsers (Development)
```bash
cd grammar
antlr4 -Dlanguage=Python3 ProcDSL.g4 -visitor -o ../backend/parser/generated
antlr4 -Dlanguage=Python3 SchemaDSL.g4 -visitor -o ../backend/parser/generated
antlr4 -Dlanguage=Python3 TransformDSL.g4 -visitor -o ../backend/parser/generated
antlr4 -Dlanguage=Python3 RulesDSL.g4 -visitor -o ../backend/parser/generated
```

## Command Line Interface

### Initialize a Project
```bash
# Create new project
nexflow init --name my-project

# Creates:
# - nexflow.toml (project configuration)
# - src/flow/
# - src/schema/
# - src/transform/
# - src/rules/
# - src/infra/
```

### Build Project
```bash
# Full build (parse → validate → generate)
nexflow build

# Build for specific target
nexflow build --target flink
nexflow build --target spark # Not implemented yet, planned for future 

# Dry run (validate only)
nexflow build --dry-run

# Build and verify Java compilation
nexflow build --verify

# Verbose output
nexflow -v build
```

### Validate Files
```bash
# Validate entire project
nexflow validate

# Validate specific directory
nexflow validate src/rules/

# Validate single file
nexflow validate src/rules/credit.rules
```

### Parse and Inspect
```bash
# Parse file and show summary
nexflow parse src/rules/credit.rules

# Output as JSON
nexflow parse src/rules/credit.rules --format json

# Output as tree structure
nexflow parse src/rules/credit.rules --format tree

# Output as graph (nodes/edges for visual designer)
nexflow parse src/flow/order.proc --format graph
```

The `--format graph` output is used by the VS Code visual designer and returns:
```json
{
  "nodes": [
    {"id": "receive_0", "type": "source", "label": "orders-topic", ...},
    {"id": "transform_1", "type": "transform", "label": "OrderEnrichment", ...},
    {"id": "emit_2", "type": "sink", "label": "processed-orders", ...}
  ],
  "edges": [
    {"source": "receive_0", "target": "transform_1"},
    {"source": "transform_1", "target": "emit_2"}
  ]
}
```

### Project Information
```bash
# Show project details
nexflow info

# Output:
# ┌──────────────────────────────┐
# │  Nexflow Project Info        │
# ├────────────────┬─────────────┤
# │ Property       │ Value       │
# ├────────────────┼─────────────┤
# │ Name           │ my-project  │
# │ Version        │ 0.1.0       │
# │ Source Dir     │ src         │
# │ Output Dir     │ generated   │
# │ Targets        │ flink       │
# └────────────────┴─────────────┘
```

### Clean Build Artifacts
```bash
# Remove generated directory
nexflow clean

# Remove all build artifacts
nexflow clean --all
```

### Language Server
```bash
# Start LSP server in stdio mode (for VS Code)
nexflow lsp

# Start LSP server in TCP mode (for debugging)
nexflow lsp --tcp --port 2087

# With verbose logging
nexflow lsp --log-level DEBUG
```

The LSP server provides IDE features:
- Real-time diagnostics
- Code completion
- Hover documentation
- Document symbols/outline
- Go to definition

## Project Configuration (nexflow.toml)

```toml
# Nexflow Project Configuration

[project]
name = "order-processing"
version = "1.0.0"

[paths]
src = "src"
output = "generated"

# Source directories for each DSL type
[sources.flow]
path = "src/flow"
include = ["**/*"]
exclude = ["**/test_*"]

[sources.schema]
path = "src/schema"

[sources.transform]
path = "src/transform"

[sources.rules]
path = "src/rules"

[sources.infra]
path = "src/infra"

# Code generation targets
[targets.flink]
enabled = true
output = "generated/flink"

[targets.flink.options]
package = "com.example.orders"
java_version = "17"

[targets.spark]
enabled = false
output = "generated/spark"

# External dependencies
dependencies = ["../shared-schemas"]
```

## Project Structure

```
my-project/
├── nexflow.toml           # Project configuration
├── src/
│   ├── flow/              # L1 ProcDSL files
│   │   └── order_flow.proc
│   ├── schema/            # L2 SchemaDSL files
│   │   ├── order.schema
│   │   └── customer.schema
│   ├── transform/         # L3 TransformDSL files
│   │   └── enrichment.xform
│   ├── rules/             # L4 RulesDSL files
│   │   └── validation.rules
│   └── infra/             # L5 Infrastructure files
│       └── production.infra
└── generated/             # Generated Java code
    └── flink/
        └── src/main/java/
            └── com/example/orders/
                ├── flow/
                ├── schema/
                ├── transform/
                └── rules/
```

## Compilation Pipeline

The Master Compiler executes phases in dependency order:

```
Phase 1: L5 Infrastructure (.infra)
    └── Parse infrastructure bindings
    └── Create BindingResolver

Phase 2: L2 Schema (.schema)
    └── Parse schema definitions
    └── Generate Java Records
    └── Generate builders
    └── Generate migration helpers

Phase 3: L3 Transform (.xform)
    └── Parse transform definitions
    └── Generate transform functions
    └── Generate expression evaluators

Phase 4: L4 Rules (.rules)
    └── Parse rule tables
    └── Generate decision logic
    └── Generate rule engines

Phase 5: L1 Flow (.proc)
    └── Parse process definitions
    └── Resolve infrastructure bindings
    └── Generate Flink jobs
    └── Generate operators
```

## Import System

Nexflow supports imports between DSL files:

```
// In order_flow.proc
import "schemas/order.schema"
import "transforms/enrichment.xform"
import "rules/validation.rules"
```

The import resolver:
- Resolves relative and absolute paths
- Detects circular dependencies
- Processes files in topological order
- Makes imported types available to generators

## Environment Selection

Infrastructure files are selected based on environment:

```bash
# Use production.infra
nexflow build --target flink

# Specify environment explicitly
NEXFLOW_ENV=production nexflow build
```

Search order for .infra files:
1. Explicit `--infra` flag
2. `{environment}.infra` (if environment specified)
3. `default.infra`
4. `local.infra`
5. `dev.infra`
6. First `.infra` file found

## Generated Code Structure

```
generated/flink/
└── src/main/java/com/example/orders/
    ├── flow/
    │   ├── OrderProcessingJob.java      # Main Flink job
    │   ├── OrderReceiveFunction.java    # Source function
    │   └── OrderEmitFunction.java       # Sink function
    ├── schema/
    │   ├── Order.java                   # Immutable Java Record
    │   ├── OrderBuilder.java            # Builder pattern
    │   └── OrderMigration.java          # Version migration
    ├── transform/
    │   ├── EnrichmentTransform.java     # Transform function
    │   └── EnrichmentExpressions.java   # Expression evaluators
    ├── rules/
    │   ├── ValidationRules.java         # Decision table
    │   └── ValidationEngine.java        # Rule engine
    └── runtime/
        └── NexflowRuntime.java          # Runtime utilities
```

## Error Handling

### Parse Errors
```python
result = parse(content, "flow")
if not result.success:
    for error in result.errors:
        print(f"{error.location.line}:{error.location.column}: {error.message}")
```

### Compilation Errors
```python
result = compiler.compile()
if not result.success:
    for phase, layer_result in result.layers.items():
        if not layer_result.success:
            print(f"Phase {phase.name} failed:")
            for error in layer_result.errors:
                print(f"  - {error}")
```

### Binding Validation Errors
```python
errors = compiler.validate_bindings()
# Returns errors like:
# - "Stream 'orders-input' referenced but not defined in infrastructure"
# - "Persistence target 'order-db' has no MongoDB binding"
```

## Runtime Functions

Generated code uses the `NexflowRuntime` class for built-in functions:

```java
// Date/Time functions (Three-Date Model)
NexflowRuntime.processingDate(context)  // Current processing timestamp
NexflowRuntime.businessDate(context)    // Business date from context
NexflowRuntime.businessDateOffset(context, 5)  // Business date + 5 days

// String functions
NexflowRuntime.concat("a", "b", "c")
NexflowRuntime.substring(str, 0, 5)
NexflowRuntime.toUpperCase(str)

// Math functions
NexflowRuntime.round(value, 2)
NexflowRuntime.abs(value)
NexflowRuntime.max(a, b)

// Collection functions
NexflowRuntime.first(list)
NexflowRuntime.last(list)
NexflowRuntime.size(collection)
```

## EOD Markers and Phase-Based Processing

### Three-Date Model

Nexflow implements a three-date model for financial services:

| Date Type | Runtime Method | Description |
|-----------|----------------|-------------|
| Processing Date | `processingDate(context)` | System time when record is processed |
| Business Date | `businessDate(context)` | Logical business day from calendar |
| Business Date Offset | `businessDateOffset(context, n)` | Business date +/- n days |

### Generated Marker Infrastructure

When a `.proc` file contains markers, the compiler generates:

```
generated/flink/
└── src/main/java/com/example/
    ├── flow/
    │   ├── SettlementJob.java           # Main job with phase routing
    │   ├── MarkerStateManager.java      # Tracks marker fired/pending state
    │   ├── PhaseRouter.java             # Routes to before/after phases
    │   └── BeforeEodFunction.java       # Intraday processing logic
    │   └── AfterEodFunction.java        # Settlement processing logic
    └── rules/
        └── MarkerConditionEvaluator.java # For L4 marker conditions
```

### Marker State Management

The generated `MarkerStateManager` maintains:
- **Fired markers**: Set of markers that have transitioned to fired
- **Pending markers**: Set of markers waiting for conditions
- **Composite evaluation**: Evaluates `and`/`or` conditions

### Phase Routing Logic

Generated `PhaseRouter` implements:
```java
public class PhaseRouter extends ProcessFunction<Record, Record> {
    private final MarkerStateManager markerState;

    @Override
    public void processElement(Record record, Context ctx, Collector<Record> out) {
        if (markerState.isMarkerFired("eod_ready")) {
            // Route to AFTER phase
            afterEodFunction.processElement(record, ctx, out);
        } else {
            // Route to BEFORE phase
            beforeEodFunction.processElement(record, ctx, out);
        }
    }
}
```

### Example: EOD Process Compilation

Given this `.proc` file:
```
process DailySettlement
    business_date from trading_calendar
    processing_date auto

    markers
        market_close: when after "16:00"
        trades_drained: when trades.drained
        eod_ready: when market_close and trades_drained
    end

    phase before eod_ready
        receive trades from kafka "trades"
        transform using accumulate_trade
        emit to trade_buffer
    end

    phase after eod_ready
        receive buffered from state_store "trade_buffer"
        transform using calculate_settlements
        emit to settlements
    end
end
```

The compiler generates:
1. `DailySettlementJob.java` - Main Flink job entry point
2. `MarkerStateManager.java` - Tracks `market_close`, `trades_drained`, `eod_ready`
3. `PhaseRouter.java` - Routes records based on `eod_ready` state
4. `BeforeEodReadyFunction.java` - Implements intraday accumulation
5. `AfterEodReadyFunction.java` - Implements settlement calculation

### L4 Rules with Marker Conditions

When L4 rules reference markers:
```
decision_table routing
    decide:
        | marker eod_1 fired | action |
        ...
end
```

The compiler generates `MarkerConditionEvaluator` that queries `MarkerStateManager`:
```java
public class MarkerConditionEvaluator {
    public boolean isMarkerFired(String markerName) {
        return markerStateManager.isMarkerFired(markerName);
    }

    public boolean isBetweenMarkers(String marker1, String marker2) {
        return markerStateManager.isMarkerFired(marker1)
            && !markerStateManager.isMarkerFired(marker2);
    }
}
```

## Extending the Toolchain

### Adding a New DSL
1. Create ANTLR grammar in `grammar/`
2. Generate parser with `antlr4`
3. Create AST nodes in `backend/ast/`
4. Create visitor in `backend/parser/`
5. Create generator in `backend/generators/`
6. Register in `backend/parser/__init__.py` and `backend/generators/__init__.py`

### Adding a New Target
1. Add target config in `nexflow.toml`
2. Create generator in `backend/generators/{target}/`
3. Register in `backend/generators/__init__.py`

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/parser/test_flow_parser.py

# Run with coverage
pytest --cov=backend tests/

# Verbose output
pytest -v tests/
```

## Build Scripts

### Building the Standalone Executable

The `build-exe.sh` script creates a standalone executable using PyInstaller:

```bash
# Build the executable
./scripts/build-exe.sh

# Output: dist/nexflow/
#   - nexflow (or nexflow.exe on Windows)
#   - Supporting libraries
```

The executable is self-contained and doesn't require Python to be installed.

**Cross-Platform Notes:**
- On macOS/Linux: Uses `python3` if available, falls back to `python`
- On Windows: Uses `python`

### Building the VS Code Extension

The `build-plugin.sh` script packages the VS Code extension:

```bash
# Build extension (Python mode - requires Python at runtime)
./scripts/build-plugin.sh

# Build extension with bundled executable (no Python required)
./scripts/build-exe.sh              # First, build the executable
./scripts/build-plugin.sh --bundled # Then, bundle it into the extension

# Output: plugin/nexflow-X.Y.Z.vsix
```

### Build Output Locations

| Script | Output | Description |
|--------|--------|-------------|
| `build-exe.sh` | `dist/nexflow/` | Standalone executable + libraries |
| `build-plugin.sh` | `plugin/*.vsix` | VS Code extension package |

## Programmatic API

### Parsing Files

```python
from backend.parser import parse

# Parse a file
result = parse(content, "flow")  # or "schema", "transform", "rules"

if result.success:
    ast = result.ast
    # Work with AST
else:
    for error in result.errors:
        print(f"Error: {error}")
```

### Building a Project

```python
from backend.cli.project import Project
from backend.cli.commands import build_project

# Load project
project = Project.load()  # Reads nexflow.toml

# Build
result = build_project(project, target="flink", dry_run=False)

if result.success:
    print(f"Generated {len(result.files)} files")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

### Using the LSP Server Programmatically

```python
from backend.lsp.driver import server
from backend.lsp.modules.proc_module import ProcModule

# Register modules
server.register_module(ProcModule())

# Start server
server.start_io()  # stdio mode
# or
server.start_tcp("127.0.0.1", 2087)  # TCP mode
```
