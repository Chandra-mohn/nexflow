#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Quick Start Guide

Get up and running with Nexflow in 5 minutes.

## What is Nexflow?

Nexflow is a domain-specific language (DSL) toolchain for building stream processing applications. Write declarative DSL code, compile to production-ready Apache Flink Java.

**Four DSL Layers:**
| Layer | Extension | Purpose |
|-------|-----------|---------|
| L1 ProcDSL | `.proc` | Process orchestration (receive, transform, emit) |
| L2 SchemaDSL | `.schema` | Data schema definitions |
| L3 TransformDSL | `.xform` | Field mappings and transformations |
| L4 RulesDSL | `.rules` | Business decision logic (decision tables) |

---

## Installation

### Option A: VS Code Extension (Recommended)

1. **Install the extension:**
   ```bash
   code --install-extension nexflow-0.2.0.vsix
   ```

2. **The extension includes:**
   - Syntax highlighting for all DSL files
   - Real-time error diagnostics
   - Visual flow designer for `.proc` files
   - Code completion and hover docs

### Option B: Command Line Only

1. **Prerequisites:**
   - Python 3.11+
   - pip

2. **Install dependencies:**
   ```bash
   pip install click rich toml antlr4-python3-runtime pygls lsprotocol
   ```

3. **Run from source:**
   ```bash
   cd nexflow-toolchain
   python -m backend.cli.main --help
   ```

### Option C: Standalone Executable (Windows)

Use `nexflow.exe` - no Python installation required.
```bash
nexflow.exe --help
```

---

## Your First Project

### 1. Initialize

```bash
nexflow init --name my-first-flow
cd my-first-flow
```

This creates:
```
my-first-flow/
├── nexflow.toml          # Project configuration
├── src/
│   ├── flow/             # L1 .proc files
│   ├── schema/           # L2 .schema files
│   ├── transform/        # L3 .xform files
│   └── rules/            # L4 .rules files
└── generated/            # Output directory
```

### 2. Create a Schema (L2)

**`src/schema/order.schema`**
```
schema Order {
    entity Order {
        order_id: string required
        customer_id: string required
        amount: decimal(10,2) required
        status: string = "pending"
        created_at: timestamp
    }
}
```

### 3. Create a Process (L1)

**`src/flow/order_processor.proc`**
```
process OrderProcessor {
    receive Order from "orders-topic"
        format confluent_avro
        consumer_group "order-processors"

    transform using OrderEnrichment

    emit to "processed-orders"
        format confluent_avro
}
```

### 4. Build

```bash
# Validate and generate Flink Java code
nexflow build

# Or validate only (no code generation)
nexflow build --dry-run

# Build and verify Java compiles
nexflow build --verify
```

Output appears in `generated/`:
```
generated/
├── src/main/java/
│   └── com/nexflow/
│       ├── OrderProcessor.java
│       ├── model/Order.java
│       └── ...
└── pom.xml
```

---

## VS Code Visual Designer

For `.proc` files, click the **"Open Visual Designer"** button (top-right of editor) to see your flow as an interactive diagram.

**Features:**
- Drag-and-drop node positioning
- Zoom and pan navigation
- Export as PNG image
- Real-time sync with code

---

## Common Commands

| Command | Description |
|---------|-------------|
| `nexflow init --name NAME` | Create new project |
| `nexflow build` | Compile DSL to Flink Java |
| `nexflow build --verify` | Build + verify Java compiles |
| `nexflow validate` | Check files without generating |
| `nexflow parse FILE` | Parse single file, show AST |
| `nexflow parse FILE --format graph` | Output as nodes/edges (for UI) |
| `nexflow info` | Show project details |
| `nexflow clean` | Remove generated files |
| `nexflow lsp` | Start language server (for IDE) |

---

## Project Configuration

**`nexflow.toml`**
```toml
[project]
name = "my-first-flow"
version = "1.0.0"

[build]
src_dir = "src"
output_dir = "generated"
targets = ["flink"]

[serialization]
default_format = "confluent_avro"

[registry]
url = "http://localhost:8081"
```

---

## Next Steps

| Topic | Document |
|-------|----------|
| VS Code extension details | [VSCODE-EXTENSION-GUIDE.md](VSCODE-EXTENSION-GUIDE.md) |
| CLI and programmatic API | [BACKEND-USAGE.md](BACKEND-USAGE.md) |
| L1 ProcDSL reference | [L1-ProcDSL-Reference.md](L1-ProcDSL-Reference.md) |
| L2 SchemaDSL reference | [L2-SchemaDSL-Reference.md](L2-SchemaDSL-Reference.md) |
| L3 TransformDSL reference | [L3-TransformDSL-Reference.md](L3-TransformDSL-Reference.md) |
| L4 RulesDSL reference | [L4-RulesDSL-Reference.md](L4-RulesDSL-Reference.md) |
| Architecture overview | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Windows deployment | [WINDOWS-DEPLOYMENT.md](WINDOWS-DEPLOYMENT.md) |

---

## Getting Help

- **Diagnostics**: Check VS Code "Problems" panel or run `nexflow validate`
- **LSP logs**: VS Code Output panel → "Nexflow LSP"
- **Verbose mode**: `nexflow -v build`
