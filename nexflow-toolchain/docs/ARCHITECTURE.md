#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Architecture Document

## Overview

Nexflow is a multi-layer Domain-Specific Language (DSL) toolchain for building streaming and batch data processing pipelines. It compiles high-level DSL specifications into production-ready Apache Flink Java code.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nexflow DSL Toolchain                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ L1 Proc  │  │ L2 Schema│  │ L3 Xform │  │ L4 Rules │         │
│  │  .proc   │  │ .schema  │  │  .xform  │  │  .rules  │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │             │               │
│       ▼             ▼             ▼             ▼               │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              ANTLR4 Parser Layer                    │        │
│  │   ProcDSL   SchemaDSL   TransformDSL   RulesDSL     │        │
│  └─────────────────────────┬───────────────────────────┘        │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Abstract Syntax Trees                  │        │
│  │   proc_ast   schema_ast   transform_ast   rules_ast │        │
│  └─────────────────────────┬───────────────────────────┘        │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Semantic Validation                    │        │
│  │   Cross-reference │ Type checking │ Import resolver │        │
│  └─────────────────────────┬───────────────────────────┘        │
│                            │                                    │
│       ┌────────────────────┼────────────────────┐               │
│       ▼                    ▼                    ▼               │
│  ┌─────────┐         ┌──────────┐         ┌─────────┐           │
│  │L5 Infra │         │L6 Master │         │L0 Runtme│           │
│  │ .infra  │────────▶│ Compiler │◀────────│ Library │           │
│  └─────────┘         └────┬─────┘         └─────────┘           │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Code Generators                        │        │
│  │   FlowGen  SchemaGen  TransformGen  RulesGen        │        │
│  └─────────────────────────┬───────────────────────────┘        │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Generated Java Code                    │        │
│  │   Flink Jobs │ Java Recs │ Functions │ Rule Engines │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Definitions

### L0: Runtime Library
Base classes, operators, and utility functions available to all generated code.
- `NexflowRuntime.java` - Built-in functions (time, math, string, collections)
- Voltage encryption functions
- Date context functions (`processing_date()`, `business_date()`)

### L1: Process Orchestration (ProcDSL)
Defines streaming/batch data pipelines.
- File extensions: `.proc`, `.flow`
- Concepts: receive, transform, route, emit, state, resilience
- **Business Date & EOD Markers**: Phase-based processing for end-of-day workflows

### L2: Schema Registry (SchemaDSL)
Defines data structures with constraints and evolution rules.
- File extension: `.schema`
- 9 mutation patterns (master_data, immutable_ledger, event_log, etc.)

### L3: Transform Catalog (TransformDSL)
Defines reusable data transformations.
- File extensions: `.xform`, `.transform`
- Pure functional transforms with composition

### L4: Business Rules (RulesDSL)
Defines decision tables and procedural rules.
- File extension: `.rules`
- Hit policies: first_match, single_hit, multi_hit

### L5: Infrastructure Binding
Maps logical names to physical infrastructure.
- File extension: `.infra`
- Kafka topics, MongoDB connections, resource configs

### L6: Master Compiler
Orchestrates multi-layer compilation with infrastructure awareness.
- Topological ordering of dependencies
- Cross-layer validation
- Infrastructure-aware code generation

## Directory Structure

```
nexflow-toolchain/
├── backend/
│   ├── ast/                   # AST node definitions
│   │   ├── proc/              # L1 AST
│   │   ├── schema/            # L2 AST
│   │   ├── transform/         # L3 AST
│   │   └── rules/             # L4 AST
│   ├── parser/                # ANTLR4 parsers
│   │   ├── flow/              # L1 visitor mixins
│   │   ├── schema/            # L2 visitor
│   │   ├── transform/         # L3 visitor
│   │   ├── rules/             # L4 visitor
│   │   └── generated/         # ANTLR4 output
│   ├── generators/            # Code generators
│   │   ├── flow/              # L1 → Flink jobs
│   │   ├── schema/            # L2 → Java Records
│   │   ├── transform/         # L3 → Functions
│   │   ├── rules/             # L4 → Rule engines
│   │   └── runtime/           # L0 → Runtime lib
│   ├── validators/            # Semantic validation
│   ├── compiler/              # L6 Master Compiler
│   ├── resolver/              # Import resolution
│   └── cli/                   # Command-line interface
├── grammar/                   # ANTLR4 grammar files
│   ├── ProcDSL.g4             # Process language grammar
│   ├── SchemaDSL.g4           # Schema language grammar
│   ├── TransformDSL.g4        # Transaformation language grammar
│   └── RulesDSL.g4            # Business Rules language grammar
├── lsp/                       # VS Code extension
│   ├── server/                # Python LSP server
│   └── client/                # VS Code client
├── tests/                     # Unit tests
├── docs/                      # Documentation
└── examples/                  # Example projects
```

## Build Pipeline

```
1. PARSE
   DSL Files → ANTLR4 Parsers → Abstract Syntax Trees

2. VALIDATE
   ASTs → Semantic Validation → Cross-Reference Resolution

3. RESOLVE IMPORTS
   Import Statements → Topological Ordering → Dependency Graph

4. GENERATE
   ASTs + Infra Config → Code Generators → Java Source Files

5. WRITE
   Generated Code → Output Directory → pom.xml
```

## Key Design Principles

### Zero-Code Covenant
Users should never write Java code. All business logic is expressed in DSLs.

### Layer Separation
- L1 is the "railroad" - orchestrates data flow, NOT business logic
- L3/L4 contain business logic
- L2 defines data contracts

### Infrastructure Abstraction
Logical names in DSL files are resolved to physical resources via L5 bindings.

### Compile-Time Safety
All type mismatches and reference errors are caught at compile time.

### Three-Date Model for Financial Services
Nexflow implements a three-date model essential for financial processing:
- **Processing Date**: System time when record is processed
- **Business Date**: Logical business day from calendar context
- **EOD Markers**: Named conditions that signal phase transitions

## End-of-Day (EOD) Marker Architecture

EOD markers enable phase-based processing for financial workflows:

```
┌────────────────────────────────────────────────────────────────┐
│                    EOD MARKER LIFECYCLE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  MARKERS BLOCK (L1)                                            │
│  ├── time-based:     when after "16:00"                        │
│  ├── data-drained:   when trades.drained                       │
│  ├── count-based:    when prices.count >= 1000                 │
│  └── composite:      when marker1 and marker2                  │
│                                                                │
│  PHASES (L1)                                                   │
│  ├── phase before eod_marker: [intraday processing]            │
│  └── phase after eod_marker:  [settlement processing]          │
│                                                                │
│  RULES CONDITIONS (L4)                                         │
│  └── marker eod_1 fired | marker eod_1 pending                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Parser Generator | ANTLR4 |
| Backend Language | Python 3.11+ |
| Generated Code | Java 17+ |
| Target Runtime | Apache Flink |
| Build Tool | Maven |
| IDE Support | VS Code + LSP |
