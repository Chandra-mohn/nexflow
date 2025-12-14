# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
nexflow build --target spark

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

## Programmatic API

### Using MasterCompiler

```python
from pathlib import Path
from backend.compiler.master_compiler import MasterCompiler, compile_project

# Option 1: Using convenience function
result = compile_project(
    src_dir=Path("src"),
    output_dir=Path("generated"),
    package_prefix="com.example.flow",
    environment="production",
    verbose=True
)

if result.success:
    print(f"Generated {result.total_files_generated} files")
    for file_path in result.generated_files:
        print(f"  - {file_path}")
else:
    for error in result.errors:
        print(f"Error: {error}")

# Option 2: Using MasterCompiler directly
compiler = MasterCompiler(
    src_dir=Path("src"),
    output_dir=Path("generated"),
    package_prefix="com.example.flow",
    environment="production",  # Selects production.infra
    infra_file=None,           # Or specify explicit path
    verbose=True,
)

result = compiler.compile()

# Access infrastructure config
if result.infra_config:
    print(f"Environment: {result.infra_config.environment}")
    print(f"Streams: {len(result.infra_config.streams)}")

# Validate bindings
errors = compiler.validate_bindings()
for error in errors:
    print(f"Binding error: {error}")
```

### Using Individual Parsers

```python
from backend.parser import parse

# Parse a ProcDSL file
content = open("flow.proc").read()
result = parse(content, "flow")

if result.success:
    ast = result.ast
    for process in ast.processes:
        print(f"Process: {process.name}")
        for receive in process.receives:
            print(f"  Receives from: {receive.source}")
else:
    for error in result.errors:
        print(f"Error at line {error.location.line}: {error.message}")
```

### Using Individual Generators

```python
from backend.generators import get_generator
from backend.generators.base import GeneratorConfig
from pathlib import Path

# Configure generator
config = GeneratorConfig(
    package_prefix="com.example",
    output_dir=Path("generated"),
)

# Get generator for a DSL type
generator = get_generator("schema", config)

# Generate code from AST
result = generator.generate(ast)

for gen_file in result.files:
    print(f"Generated: {gen_file.path}")
    print(gen_file.content)
```

## Compilation Pipeline

The Master Compiler executes phases in dependency order:

```
Phase 1: L5 Infrastructure (.infra)
    └── Parse infrastructure bindings
    └── Create BindingResolver

Phase 2: L2 Schema (.schema)
    └── Parse schema definitions
    └── Generate Java POJOs
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
    │   ├── Order.java                   # POJO
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
// Date/Time functions
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
