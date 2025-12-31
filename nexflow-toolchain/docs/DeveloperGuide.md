#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Developer Guide - Codebase Reference

Quick reference for each source file in the Nexflow toolchain.

---

## Grammar Files (ANTLR4)

| File | Description |
|------|-------------|
| `grammar/ProcDSL.g4` | L1 Process DSL grammar for streaming/batch pipelines with connectors, aggregation, branching, and state machines. |
| `grammar/SchemaDSL.g4` | L2 Schema DSL grammar for data definitions with mutation patterns, type system, and streaming annotations. |
| `grammar/TransformDSL.g4` | L3 Transform DSL grammar for data transformations with type-safe expressions and null handling. |
| `grammar/RulesDSL.g4` | L4 Rules DSL grammar for decision tables and procedural rules with hit policies and conditions. |

---

## Backend - CLI

| File | Description |
|------|-------------|
| `backend/__init__.py` | Package initialization for Nexflow Backend DSL toolchain. |
| `backend/cli/__init__.py` | CLI module initialization and exports. |
| `backend/cli/main.py` | Main CLI entry point with subcommands (build, validate, parse, init, clean, graph, stream). |
| `backend/cli/commands/__init__.py` | Exports all CLI command implementations and result types. |
| `backend/cli/commands/types.py` | Data classes for CLI command results (BuildResult, ValidateResult, ParseResult). |
| `backend/cli/commands/build.py` | Orchestrates full project build with multi-layer compilation and Java code generation. |
| `backend/cli/commands/validate.py` | Validates DSL files without code generation, detects parse and semantic errors. |
| `backend/cli/commands/parse.py` | Parses single DSL file and returns AST in JSON, tree, or summary format. |
| `backend/cli/commands/init.py` | Initializes new Nexflow projects with directory structure and config file. |
| `backend/cli/commands/clean.py` | Removes generated files and optional cache directories from projects. |
| `backend/cli/commands/graph.py` | Generates flow graph visualization from .proc files. |
| `backend/cli/commands/graph_converter.py` | Converts process AST to visual graph format with node positioning. |

---

## Backend - Parsers

### Base Infrastructure

| File | Description |
|------|-------------|
| `backend/parser/base.py` | Base parser with error handling, source location tracking, and ANTLR integration. |
| `backend/parser/proc_parser.py` | L1 Process DSL parser with composite visitor pattern. |
| `backend/parser/schema_parser.py` | L2 Schema DSL parser with modular visitor mixins. |
| `backend/parser/transform_parser.py` | L3 Transform DSL parser with composition-based architecture. |
| `backend/parser/rules_parser.py` | L4 Rules DSL parser with composite visitor pattern. |
| `backend/parser/infra/infra_parser.py` | L5 Infrastructure YAML parser with environment variable substitution. |

### Process DSL Visitors (L1)

| File | Description |
|------|-------------|
| `backend/parser/proc/core_visitor.py` | Parses program structure, imports, and top-level process definitions. |
| `backend/parser/proc/execution_visitor.py` | Parses execution config (parallelism, partition, time semantics, watermark). |
| `backend/parser/proc/input_visitor.py` | Parses receive declarations and connector configurations. |
| `backend/parser/proc/processing_visitor.py` | Parses processing operations (enrich, transform, route, aggregate). |
| `backend/parser/proc/correlation_visitor.py` | Parses correlation blocks (await, hold, timeout, completion). |
| `backend/parser/proc/output_visitor.py` | Parses emit and persist declarations. |
| `backend/parser/proc/state_visitor.py` | Parses state blocks (local state, TTL, cleanup). |
| `backend/parser/proc/resilience_visitor.py` | Parses error handling and resilience patterns. |
| `backend/parser/proc/markers_visitor.py` | Parses EOD markers and phase definitions. |

### Schema DSL Visitors (L2)

| File | Description |
|------|-------------|
| `backend/parser/schema/core_visitor.py` | Parses schema definitions, patterns, versions, identity, and fields. |
| `backend/parser/schema/types_visitor.py` | Parses field types, collections, constraints, and qualifiers. |
| `backend/parser/schema/streaming_visitor.py` | Parses streaming blocks (watermarks, time semantics, late data). |
| `backend/parser/schema/state_machine_visitor.py` | Parses state machine blocks with states and transitions. |
| `backend/parser/schema/pattern_visitor.py` | Parses pattern-specific blocks (parameters, reference data, business logic). |

### Transform DSL Visitors (L3)

| File | Description |
|------|-------------|
| `backend/parser/transform/core_visitor.py` | Parses top-level transform definitions and transform blocks. |
| `backend/parser/transform/metadata_visitor.py` | Parses metadata (version, cache, compatibility info). |
| `backend/parser/transform/types_visitor.py` | Parses field type specifications. |
| `backend/parser/transform/specs_visitor.py` | Parses input/output field specifications. |
| `backend/parser/transform/apply_visitor.py` | Parses apply block with field mappings and transformations. |
| `backend/parser/transform/validation_visitor.py` | Parses validation rules and error conditions. |
| `backend/parser/transform/error_visitor.py` | Parses error handling blocks. |
| `backend/parser/transform/expression_visitor.py` | Parses expressions in transform blocks. |

### Rules DSL Visitors (L4)

| File | Description |
|------|-------------|
| `backend/parser/rules/core_visitor.py` | Parses program structure and import statements. |
| `backend/parser/rules/decision_table_visitor.py` | Parses decision tables, given blocks, decide blocks, and table matrices. |
| `backend/parser/rules/condition_visitor.py` | Parses condition types (range, set, pattern, null, comparison). |
| `backend/parser/rules/action_visitor.py` | Parses action types (assign, lookup, call, no-action). |
| `backend/parser/rules/expression_visitor.py` | Parses expressions and operators used in rules. |
| `backend/parser/rules/literal_visitor.py` | Parses literal values (strings, numbers, money, boolean, null). |
| `backend/parser/rules/procedural_visitor.py` | Parses procedural rules and sequential blocks. |
| `backend/parser/rules/services_visitor.py` | Parses services block with service definitions. |
| `backend/parser/rules/actions_visitor.py` | Parses actions block with action definitions. |
| `backend/parser/rules/collection_visitor.py` | Parses collection operations (any, all, filter, map). |

### Common Visitors

| File | Description |
|------|-------------|
| `backend/parser/common/import_visitor.py` | Common mixin for parsing import statements across all DSL levels. |

---

## Backend - AST (Abstract Syntax Trees)

### Common

| File | Description |
|------|-------------|
| `backend/ast/common/source.py` | Source location data class for error reporting with line and column. |

### Process AST (L1)

| File | Description |
|------|-------------|
| `backend/ast/proc/program.py` | Top-level process definitions with input, processing, output, state blocks. |
| `backend/ast/proc/execution.py` | Execution types (watermark, mode, time declarations). |
| `backend/ast/proc/input.py` | Input types (receive declarations, connector configs). |
| `backend/ast/proc/processing.py` | Processing types (enrich, transform, route, aggregate, join). |
| `backend/ast/proc/correlation.py` | Correlation types (await, hold, timeout, completion conditions). |
| `backend/ast/proc/output.py` | Output types (emit, persist, fanout). |
| `backend/ast/proc/state.py` | State block types (local, uses, TTL, cleanup). |
| `backend/ast/proc/markers.py` | EOD markers and phase definitions. |
| `backend/ast/proc/resilience.py` | Error handling and resilience patterns. |
| `backend/ast/proc/common.py` | Common types for process DSL. |

### Schema AST (L2)

| File | Description |
|------|-------------|
| `backend/ast/schema/common.py` | Common types (Duration, SizeSpec, FieldPath, SourceLocation). |
| `backend/ast/schema/enums.py` | Enumerations for mutation patterns, compatibility modes, watermarking. |
| `backend/ast/schema/types.py` | Field type system with constraints, collection types, qualifiers. |
| `backend/ast/schema/blocks.py` | Block-level types (streaming, version, state machine, parameters). |
| `backend/ast/schema/literals.py` | Literal value types for schema constants. |
| `backend/ast/schema/rules.py` | Rule-related AST types for business_logic pattern. |

### Transform AST (L3)

| File | Description |
|------|-------------|
| `backend/ast/transform/common.py` | Common types (SourceLocation, FieldPath, Duration). |
| `backend/ast/transform/enums.py` | Enumerations for compose types, severity levels, error actions. |
| `backend/ast/transform/types.py` | Field type specifications with constraints. |
| `backend/ast/transform/specs.py` | Input/output field specifications. |
| `backend/ast/transform/blocks.py` | Apply, mappings, compose, validation, error handling blocks. |
| `backend/ast/transform/expressions.py` | Expression types in transform blocks. |
| `backend/ast/transform/literals.py` | Literal types used in transforms. |

### Rules AST (L4)

| File | Description |
|------|-------------|
| `backend/ast/rules/common.py` | Common types (SourceLocation, FieldPath, ComparisonOp). |
| `backend/ast/rules/enums.py` | Enumerations for operators, pattern types, and rule concepts. |
| `backend/ast/rules/program.py` | Top-level program containing decision tables and procedural rules. |
| `backend/ast/rules/decision_table.py` | Decision table definitions with given/decide/return blocks. |
| `backend/ast/rules/conditions.py` | Condition types (wildcard, exact match, range, set, pattern). |
| `backend/ast/rules/actions.py` | Action types (assign, calculate, lookup, call). |
| `backend/ast/rules/expressions.py` | Expression types (function call, unary, binary, parenthesized). |
| `backend/ast/rules/literals.py` | Literal value types (string, integer, decimal, money, boolean). |
| `backend/ast/rules/procedural.py` | Procedural rule types with statements. |
| `backend/ast/rules/services.py` | Service definitions and service blocks. |
| `backend/ast/rules/collections.py` | Collection operation types (any, all, filter, distinct). |

### Infrastructure AST (L5)

| File | Description |
|------|-------------|
| `backend/ast/infra/infrastructure.py` | Infrastructure configuration types for Kafka, MongoDB, Flink resources. |

---

## Backend - Validators

| File | Description |
|------|-------------|
| `backend/validators/__init__.py` | Validator exports and common validation utilities. |
| `backend/validators/base.py` | Base validator classes with validation error and result types. |
| `backend/validators/schema_validator.py` | Semantic validation for L2 Schema DSL ASTs. |
| `backend/validators/transform_validator.py` | Semantic validation for L3 Transform DSL ASTs. |
| `backend/validators/rules_validator.py` | Semantic validation for L4 Rules DSL ASTs. |
| `backend/validators/proc_validator.py` | Semantic validation for L1 Process DSL ASTs. |

---

## Backend - Generators

### Base and Common

| File | Description |
|------|-------------|
| `backend/generators/base.py` | Abstract base class providing common utilities for all code generators. |
| `backend/generators/pom_generator.py` | Generates Maven pom.xml with Flink and Voltage SDK dependencies. |
| `backend/generators/voltage.py` | Manages Voltage FPE profiles for PII field encryption. |
| `backend/generators/scaffold_generator.py` | Generates scaffold/template code for new DSL files. |
| `backend/generators/common/java_utils.py` | Java code generation utilities (naming, type mapping, templates). |
| `backend/generators/common/record_builder.py` | Shared record building utilities for Java record generation. |

### Process Generators (L1)

| File | Description |
|------|-------------|
| `backend/generators/proc/proc_generator.py` | Main L1 generator orchestrating Flink job code generation. |
| `backend/generators/proc/job_generator.py` | Generates Flink job main class with execution environment setup. |
| `backend/generators/proc/job_imports.py` | Manages Java import statements for generated Flink jobs. |
| `backend/generators/proc/source_generator.py` | Generates Flink source operators from receive declarations. |
| `backend/generators/proc/source_projection.py` | Generates field projection logic for source schemas. |
| `backend/generators/proc/source_correlation.py` | Generates correlation ID extraction for sources. |
| `backend/generators/proc/sink_generator.py` | Generates Flink sink operators from emit declarations. |
| `backend/generators/proc/job_sinks.py` | Low-level sink wiring and configuration. |
| `backend/generators/proc/operator_generator.py` | Generates Flink operators for processing steps. |
| `backend/generators/proc/job_operators.py` | Wires operators into the Flink job graph. |
| `backend/generators/proc/job_correlation.py` | Generates correlation tracking for multi-source flows. |
| `backend/generators/proc/window_generator.py` | Generates Flink window operators (tumbling, sliding, session). |
| `backend/generators/proc/state_generator.py` | Generates Flink state backend configuration. |
| `backend/generators/proc/state_context_generator.py` | Generates state context classes for process functions. |
| `backend/generators/proc/resilience_generator.py` | Generates error handling and retry logic. |
| `backend/generators/proc/metrics_generator.py` | Generates Flink metrics instrumentation. |
| `backend/generators/proc/phase_generator.py` | Generates phase-based processing for EOD markers. |
| `backend/generators/proc/mongo_sink_generator.py` | Generates MongoDB sink connector code. |
| `backend/generators/proc/proc_process_function.py` | Generates custom ProcessFunction implementations. |

### Process Operators

| File | Description |
|------|-------------|
| `backend/generators/proc/operators/dispatcher.py` | Dispatches operator generation based on operator type. |
| `backend/generators/proc/operators/basic_operators.py` | Generates basic operators (map, filter, flatMap). |
| `backend/generators/proc/operators/advanced_operators.py` | Generates advanced operators (enrich, aggregate, route). |
| `backend/generators/proc/operators/window_join_operators.py` | Generates window and join operators. |
| `backend/generators/proc/operators/sql_operators.py` | Generates Flink SQL-based operators. |

### Process Sources

| File | Description |
|------|-------------|
| `backend/generators/proc/sources/dispatcher.py` | Dispatches source generation based on connector type. |
| `backend/generators/proc/sources/kafka_source.py` | Generates Kafka source connector code. |
| `backend/generators/proc/sources/file_sources.py` | Generates file-based source connectors (CSV, JSON, Parquet). |
| `backend/generators/proc/sources/alternative_sources.py` | Generates alternative source connectors (Redis, state store). |
| `backend/generators/proc/sources/serialization.py` | Generates serialization/deserialization code (Avro, Protobuf, JSON). |

### Schema Generators (L2)

| File | Description |
|------|-------------|
| `backend/generators/schema/record_generator.py` | Generates Java Record classes from schema definitions. |
| `backend/generators/schema/builder_generator.py` | Generates builder pattern classes for records. |
| `backend/generators/schema/streaming_generator.py` | Generates streaming annotations and watermark extractors. |
| `backend/generators/schema/statemachine_generator.py` | Generates state machine implementations from schema. |
| `backend/generators/schema/statemachine_transitions.py` | Generates state transition logic. |
| `backend/generators/schema/entries_generator.py` | Generates reference data entry classes. |
| `backend/generators/schema/entries_lookup.py` | Generates lookup table code from reference_data pattern. |
| `backend/generators/schema/rule_generator.py` | Generates rule evaluation code from business_logic pattern. |
| `backend/generators/schema/rule_io_classes.py` | Generates input/output classes for embedded rules. |
| `backend/generators/schema/parameters_generator.py` | Generates parameter classes from schema parameters block. |
| `backend/generators/schema/parameters_validation.py` | Generates parameter validation logic. |
| `backend/generators/schema/computed_generator.py` | Generates computed field implementations. |
| `backend/generators/schema/migration_generator.py` | Generates schema migration utilities. |
| `backend/generators/schema/migration_fields.py` | Generates field-level migration transformations. |
| `backend/generators/schema/pii_helper_generator.py` | Generates PII encryption/decryption helpers. |

### Transform Generators (L3)

| File | Description |
|------|-------------|
| `backend/generators/transform/transform_generator.py` | Main L3 generator orchestrating transform function generation. |
| `backend/generators/transform/function_generator.py` | Generates transform function classes. |
| `backend/generators/transform/function_process.py` | Generates ProcessFunction wrappers for transforms. |
| `backend/generators/transform/record_generator.py` | Generates input/output record types for transforms. |
| `backend/generators/transform/mapping_generator.py` | Generates field mapping implementations. |
| `backend/generators/transform/expression_generator.py` | Generates expression evaluation code. |
| `backend/generators/transform/expression_operators.py` | Generates operator implementations (+, -, *, /). |
| `backend/generators/transform/expression_special.py` | Generates special expression handling (null coalescing, ternary). |
| `backend/generators/transform/validation_generator.py` | Generates validation logic from transform validation blocks. |
| `backend/generators/transform/validation_helpers.py` | Helper functions for validation code generation. |
| `backend/generators/transform/error_generator.py` | Generates error handling code for transforms. |
| `backend/generators/transform/compose_generator.py` | Generates composed transform chains. |
| `backend/generators/transform/cache_generator.py` | Generates caching logic for transform results. |
| `backend/generators/transform/lookups_generator.py` | Generates lookup integration for transforms. |
| `backend/generators/transform/onchange_generator.py` | Generates change detection logic. |
| `backend/generators/transform/params_generator.py` | Generates transform parameter handling. |
| `backend/generators/transform/metadata_generator.py` | Generates transform metadata classes. |

### Rules Generators (L4)

| File | Description |
|------|-------------|
| `backend/generators/rules/rules_generator.py` | Main L4 generator orchestrating rule evaluator generation. |
| `backend/generators/rules/decision_table_generator.py` | Generates decision table evaluator classes. |
| `backend/generators/rules/condition_generator.py` | Generates condition matching code. |
| `backend/generators/rules/action_generator.py` | Generates action execution code. |
| `backend/generators/rules/expression_generator.py` | Generates expression evaluation for rules. |
| `backend/generators/rules/procedural_generator.py` | Generates procedural rule implementations. |
| `backend/generators/rules/procedural_expressions.py` | Generates procedural rule expressions. |
| `backend/generators/rules/lookup_generator.py` | Generates lookup service integrations. |
| `backend/generators/rules/utils.py` | Common utilities for rules generation. |
| `backend/generators/rules/utils_naming.py` | Naming conventions for generated rule classes. |
| `backend/generators/rules/utils_imports.py` | Import management for generated rule code. |

### Runtime Generators (L0)

| File | Description |
|------|-------------|
| `backend/generators/runtime/runtime_generator.py` | Generates NexflowRuntime.java with built-in functions. |
| `backend/generators/runtime/functions/string_functions.py` | Generates string manipulation functions. |
| `backend/generators/runtime/functions/math_functions.py` | Generates mathematical functions. |
| `backend/generators/runtime/functions/time_functions.py` | Generates time/date functions. |
| `backend/generators/runtime/functions/date_context.py` | Generates processing_date() and business_date() functions. |
| `backend/generators/runtime/functions/collection_functions.py` | Generates collection manipulation functions. |
| `backend/generators/runtime/functions/comparison_functions.py` | Generates comparison utilities. |
| `backend/generators/runtime/functions/conversion_functions.py` | Generates type conversion functions. |
| `backend/generators/runtime/functions/voltage_functions.py` | Generates Voltage encryption/decryption functions. |

### Infrastructure Generators (L5)

| File | Description |
|------|-------------|
| `backend/generators/infra/binding_resolver.py` | Resolves logical names to physical infrastructure configurations. |

### Scaffold Generators

| File | Description |
|------|-------------|
| `backend/generators/scaffold/scaffold_operators.py` | Generates scaffold for process operators. |
| `backend/generators/scaffold/scaffold_correlation.py` | Generates scaffold for correlation blocks. |
| `backend/generators/scaffold/scaffold_completion.py` | Generates scaffold for completion handlers. |

---

## Backend - Compiler

| File | Description |
|------|-------------|
| `backend/compiler/master_compiler.py` | Orchestrates full compilation pipeline (L1-L5) with import resolution. |

---

## Backend - Resolver

| File | Description |
|------|-------------|
| `backend/resolver/import_resolver.py` | Resolves import paths and detects circular dependencies across DSL files. |

---

## Backend - Config

| File | Description |
|------|-------------|
| `backend/config/org_policy.py` | Loads organization-level policies from nexflow-org.toml with governance hierarchy. |
| `backend/config/serialization_resolver.py` | Resolves serialization config using hierarchical lookup with org policy enforcement. |
| `backend/config/policy_validator.py` | Validates serialization choices against org policies with violation severity tracking. |

---

## Backend - LSP (Language Server Protocol)

| File | Description |
|------|-------------|
| `backend/lsp/__main__.py` | LSP server entry point. |
| `backend/lsp/driver.py` | Main LSP server orchestrating language modules and routing requests by file extension. |
| `backend/lsp/registry.py` | Module registry managing LSP language modules. |
| `backend/lsp/modules/base.py` | Base class for language-specific LSP modules. |
| `backend/lsp/modules/proc_module.py` | LSP support for .proc files (completions, diagnostics, hover). |
| `backend/lsp/modules/schema_module.py` | LSP support for .schema files. |
| `backend/lsp/modules/transform_module.py` | LSP support for .xform files. |
| `backend/lsp/modules/rules_module.py` | LSP support for .rules files. |

---

## Plugin - VS Code Extension (TypeScript)

### Extension Core

| File | Description |
|------|-------------|
| `plugin/src/extension.ts` | Main VS Code extension entry point with LSP, commands, and visual designer. |
| `plugin/src/runtime.ts` | Runtime detection supporting bundled executable and Python module modes. |
| `plugin/src/buildRunner.ts` | Executes Nexflow builds and parses results with formatted console output. |
| `plugin/src/streamExplorer.ts` | Tree view explorer for browsing Kafka clusters, topics, and messages. |
| `plugin/src/visualDesigner/panel.ts` | WebviewPanel manager for visual designer with React frontend integration. |

### Webview (React)

| File | Description |
|------|-------------|
| `plugin/webview/vite.config.ts` | Vite build config for React webview with single-bundle output. |
| `plugin/webview/src/vscode.ts` | VS Code API wrapper for webview communication with dev mode fallback. |
| `plugin/webview/src/store/canvasStore.ts` | Zustand store managing canvas state, selections, and dirty flag. |
| `plugin/webview/src/hooks/useKeyboardShortcuts.ts` | Platform-aware keyboard shortcuts (Cmd/Ctrl) for editor actions. |
| `plugin/webview/src/hooks/useUndoRedo.ts` | Undo/redo history stack with snapshot-based state capture. |
| `plugin/webview/src/utils/trainLaneLayout.ts` | Train-lane layout algorithm for process flow node arrangement. |
| `plugin/webview/src/utils/graphToDsl.ts` | Converts React Flow graph to ProcDSL text format. |
| `plugin/webview/src/utils/exportCanvas.ts` | Canvas export to PNG/SVG using html-to-image. |
| `plugin/webview/src/components/nodes/index.ts` | Node type registry (Stream, Transform, Rules, Route, Window, Join, etc). |

---

## Scripts

| File | Description |
|------|-------------|
| `scripts/build-exe.sh` | Builds standalone nexflow executable using PyInstaller. |
| `scripts/build-plugin.sh` | Builds VS Code plugin with optional bundled executable. |

---

## ANTLR Generated Files (Read-Only)

Located in `backend/parser/generated/`. These are auto-generated from .g4 grammars - do not edit manually.

| Directory | Contents |
|-----------|----------|
| `generated/proc/` | ProcDSL lexer, parser, visitor |
| `generated/schema/` | SchemaDSL lexer, parser, visitor |
| `generated/transform/` | TransformDSL lexer, parser, visitor |
| `generated/rules/` | RulesDSL lexer, parser, visitor |

---

## Architecture Notes

### Layer Responsibilities

- **L0 (Runtime)**: Built-in functions available to generated code
- **L1 (Process)**: Flow orchestration - receive, transform, route, emit
- **L2 (Schema)**: Data contracts with mutation patterns
- **L3 (Transform)**: Pure functional data transformations
- **L4 (Rules)**: Business decision logic
- **L5 (Infra)**: Logical-to-physical resource mapping
- **L6 (Compiler)**: Multi-layer compilation orchestration

### Code Flow

```
DSL File -> Parser -> AST -> Validator -> Generator -> Java Code
```

### Visitor Pattern

Each DSL uses modular visitor mixins for maintainability:
- Core visitor handles top-level structure
- Specialized visitors handle specific constructs
- Composite visitor combines all mixins
