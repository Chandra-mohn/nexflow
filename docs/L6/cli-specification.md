# L6: Compiler CLI Specification

> **Layer**: L6 - Compilation Pipeline
> **Status**: Specification
> **Version**: 1.0.0
> **Last Updated**: 2025-11-30

---

## 1. Overview

The `nexflow` CLI is the primary interface for compiling Nexflow source files into deployable artifacts. It supports validation, compilation, explanation, and development workflows.

### 1.1 Installation

```bash
# Via package manager (future)
brew install nexflow

# Via pip (future)
pip install nexflow

# From source
git clone https://github.com/org/nexflow
cd nexflow && make install
```

### 1.2 Basic Usage

```bash
nexflow <command> [options] [arguments]
```

---

## 2. Commands

### 2.1 Command Summary

| Command | Description |
|---------|-------------|
| `compile` | Compile .proc files to deployment artifacts |
| `validate` | Validate without generating code |
| `explain` | Show compilation plan and IR |
| `format` | Format source files |
| `lint` | Check style and best practices |
| `init` | Initialize a new project |
| `schema` | Schema registry operations |
| `version` | Show version information |
| `help` | Show help for commands |

---

## 3. compile

Compile Nexflow source files into deployable artifacts.

### 3.1 Synopsis

```bash
nexflow compile <source> [options]
```

### 3.2 Arguments

| Argument | Description |
|----------|-------------|
| `<source>` | Source file (.proc) or directory |

### 3.3 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--binding <file>` | `-b` | L5 infrastructure binding file | Required |
| `--output <dir>` | `-o` | Output directory | `./deployment/` |
| `--target <runtime>` | `-t` | Target runtime | `flink` |
| `--only <artifacts>` | | Generate only specified artifacts | All |
| `--parallel` | `-p` | Compile multiple processes in parallel | false |
| `--watch` | `-w` | Watch for changes and recompile | false |
| `--verbose` | `-v` | Verbose output | false |
| `--quiet` | `-q` | Suppress non-error output | false |
| `--json` | | Output as JSON | false |

### 3.4 Target Runtimes

| Target | Description |
|--------|-------------|
| `flink` | Apache Flink SQL + Java UDFs |
| `flink-java` | Apache Flink Java API |
| `spark` | Apache Spark Structured Streaming |
| `kafka-streams` | Kafka Streams DSL |

### 3.5 Artifact Types

| Artifact | Description | File Extension |
|----------|-------------|----------------|
| `ddl` | Table definitions | `.sql` |
| `dml` | Processing queries | `.sql` |
| `udf` | User-defined functions | `.jar` |
| `config` | Runtime configuration | `.yaml` |
| `manifest` | Deployment manifest | `.json` |
| `schema` | Avro/Protobuf schemas | `.avsc` / `.proto` |
| `k8s` | Kubernetes manifests | `.yaml` |

### 3.6 Examples

```bash
# Compile single process
nexflow compile auth_enrichment.proc \
  --binding production.infra \
  --output deployment/auth/

# Compile all processes in directory
nexflow compile processes/ \
  --binding production.infra \
  --output deployment/ \
  --parallel

# Generate only SQL artifacts
nexflow compile auth_enrichment.proc \
  --binding production.infra \
  --only ddl,dml \
  --output sql/

# Compile for Spark
nexflow compile auth_enrichment.proc \
  --binding production.infra \
  --target spark \
  --output spark-jobs/

# Watch mode for development
nexflow compile processes/ \
  --binding development.infra \
  --watch

# JSON output for CI/CD
nexflow compile auth_enrichment.proc \
  --binding production.infra \
  --json
```

### 3.7 Output Structure

```
deployment/
├── auth_enrichment/
│   ├── sql/
│   │   ├── 01_ddl_sources.sql
│   │   ├── 02_ddl_lookups.sql
│   │   ├── 03_ddl_sinks.sql
│   │   └── 04_dml_processing.sql
│   ├── udfs/
│   │   └── fraud-detection-v2.jar
│   ├── config/
│   │   ├── flink-conf.yaml
│   │   └── log4j.properties
│   ├── schemas/
│   │   └── auth_event_v1.avsc
│   └── manifest.json
└── compile-report.json
```

---

## 4. validate

Validate Nexflow files without generating code.

### 4.1 Synopsis

```bash
nexflow validate <source> [options]
```

### 4.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--binding <file>` | `-b` | L5 binding file (optional) | None |
| `--strict` | | Treat warnings as errors | false |
| `--schema-only` | | Validate only L2 schemas | false |
| `--json` | | Output as JSON | false |

### 4.3 Validation Levels

| Level | Description | With Binding |
|-------|-------------|--------------|
| Syntax | Parse without errors | No |
| Semantic | References resolve, types match | No |
| Binding | All L5 bindings present | Yes |
| Full | All validations | Yes |

### 4.4 Examples

```bash
# Basic validation
nexflow validate auth_enrichment.proc

# Validate with binding
nexflow validate auth_enrichment.proc \
  --binding production.infra

# Validate directory
nexflow validate processes/ --strict

# JSON output for CI
nexflow validate auth_enrichment.proc --json
```

### 4.5 Output

```
Validating auth_enrichment.proc...

✓ Syntax valid
✓ References resolved
✓ Types checked
⚠ 2 warnings

Warnings:
  auth_enrichment.proc:15:5: warning[W020]: Potential overlapping rules in fraud_detection_v2

Validation passed with 2 warnings.
```

---

## 5. explain

Show compilation plan, IR, and debug information.

### 5.1 Synopsis

```bash
nexflow explain <source> [options]
```

### 5.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--binding <file>` | `-b` | L5 binding file | None |
| `--format <format>` | `-f` | Output format | `text` |
| `--phase <phase>` | | Show specific phase | all |
| `--verbose` | `-v` | Include all details | false |

### 5.3 Output Formats

| Format | Description |
|--------|-------------|
| `text` | Human-readable text |
| `json` | Structured JSON |
| `dot` | Graphviz DOT format |
| `mermaid` | Mermaid diagram |

### 5.4 Phases

| Phase | Description |
|-------|-------------|
| `tokens` | Lexer output |
| `parse-tree` | Parser output |
| `ast` | Abstract syntax tree |
| `semantic` | Semantic analysis results |
| `ir` | Intermediate representation |
| `optimized` | After optimization passes |
| `all` | All phases |

### 5.5 Examples

```bash
# Show IR
nexflow explain auth_enrichment.proc --phase ir

# Generate DAG diagram
nexflow explain auth_enrichment.proc \
  --format dot > pipeline.dot
dot -Tpng pipeline.dot -o pipeline.png

# Verbose with binding
nexflow explain auth_enrichment.proc \
  --binding production.infra \
  --verbose

# Mermaid for documentation
nexflow explain auth_enrichment.proc \
  --format mermaid > docs/pipeline.mmd
```

### 5.6 Example Output

```
PROCESS: authorization_enrichment
VERSION: 1.0.0
PARALLELISM: 128
MODE: streaming

═══════════════════════════════════════════════════════════════

SOURCES:
  [src_auth_events] Kafka<prod.auth.events.v3>
    Schema: auth_event_v1
    Watermark: event_timestamp - 30s
    Parallelism: 128

OPERATORS:
  [enrich_customer] EnrichLookup
    ← src_auth_events (hash: card_id)
    Lookup: customers (MongoDB)
    Join: LEFT on card_id
    Select: customer_name, risk_tier

  [transform_amount] Transform
    ← enrich_customer (forward)
    Transform: normalize_amount_v1
    Pure: true

  [route_fraud] Route
    ← transform_amount (forward)
    Rules: fraud_detection_v2 (decision_table)
    Outcomes: approved, declined, review

SINKS:
  [sink_approved] Kafka<prod.auth.approved.v3>
    ← route_fraud:approved (forward)

  [sink_declined] Kafka<prod.auth.declined.v3>
    ← route_fraud:declined (forward)

  [sink_review] Kafka<prod.auth.review.v3>
    ← route_fraud:review (forward)

═══════════════════════════════════════════════════════════════

OPTIMIZATION PASSES APPLIED:
  ✓ Predicate Pushdown: 1 filter moved to source
  ✓ Projection Pushdown: 12 unused fields removed
  ✓ Operator Fusion: 2 transforms fused
```

---

## 6. format

Format Nexflow source files.

### 6.1 Synopsis

```bash
nexflow format <source> [options]
```

### 6.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--check` | `-c` | Check if formatted, don't modify | false |
| `--diff` | `-d` | Show diff instead of modifying | false |
| `--config <file>` | | Formatting config file | `.procdsl-format.yaml` |

### 6.3 Examples

```bash
# Format single file
nexflow format auth_enrichment.proc

# Format directory
nexflow format processes/

# Check formatting (for CI)
nexflow format processes/ --check

# Show diff
nexflow format auth_enrichment.proc --diff
```

---

## 7. lint

Check for style issues and best practices.

### 7.1 Synopsis

```bash
nexflow lint <source> [options]
```

### 7.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config <file>` | | Lint config file | `.procdsl-lint.yaml` |
| `--fix` | | Auto-fix issues where possible | false |
| `--json` | | Output as JSON | false |

### 7.3 Lint Rules

| Rule | Description | Severity |
|------|-------------|----------|
| `naming-convention` | Check identifier naming | warning |
| `unused-import` | Detect unused schemas | warning |
| `complexity` | Flag overly complex rules | warning |
| `deprecated` | Flag deprecated features | warning |
| `missing-description` | Require descriptions | info |
| `missing-version` | Require versioning | info |
| `exhaustive-rules` | Require wildcard case | warning |

### 7.4 Examples

```bash
# Lint all files
nexflow lint processes/

# Lint with auto-fix
nexflow lint processes/ --fix

# JSON output for CI
nexflow lint processes/ --json
```

---

## 8. init

Initialize a new Nexflow project.

### 8.1 Synopsis

```bash
nexflow init [directory] [options]
```

### 8.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--template <name>` | `-t` | Project template | `basic` |
| `--example` | `-e` | Include example files | false |

### 8.3 Templates

| Template | Description |
|----------|-------------|
| `basic` | Minimal project structure |
| `full` | Complete structure with all layers |
| `streaming` | Streaming-focused template |
| `batch` | Batch processing template |

### 8.4 Examples

```bash
# Initialize in current directory
nexflow init

# Initialize new directory
nexflow init my-project

# Initialize with examples
nexflow init my-project --template full --example
```

### 8.5 Generated Structure

```
my-project/
├── processes/
│   └── example.proc
├── schemas/
│   └── example_event.schema
├── transforms/
│   └── example_transform.xform
├── rules/
│   └── example_rules.rules
├── infra/
│   ├── development.infra
│   └── production.infra
├── .procdsl-format.yaml
├── .procdsl-lint.yaml
└── README.md
```

---

## 9. schema

Schema registry operations.

### 9.1 Synopsis

```bash
nexflow schema <subcommand> [options]
```

### 9.2 Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List available schemas |
| `show <name>` | Show schema details |
| `validate <file>` | Validate schema file |
| `diff <v1> <v2>` | Compare schema versions |
| `evolve <schema>` | Check evolution compatibility |

### 9.3 Examples

```bash
# List schemas
nexflow schema list

# Show schema
nexflow schema show auth_event_v1

# Validate schema file
nexflow schema validate schemas/auth_event_v2.schema

# Compare versions
nexflow schema diff auth_event_v1 auth_event_v2

# Check backward compatibility
nexflow schema evolve auth_event_v2 --from auth_event_v1
```

---

## 10. Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help for command |
| `--version` | Show version information |
| `--no-color` | Disable colored output |
| `--log-level <level>` | Set log level (debug, info, warn, error) |
| `--config <file>` | Specify config file |

---

## 11. Configuration File

### 11.1 Location

Configuration is read from (in order):
1. Command-line flags
2. Environment variables (`PROCDSL_*`)
3. Project config (`.procdsl.yaml`)
4. User config (`~/.config/nexflow/config.yaml`)
5. System config (`/etc/nexflow/config.yaml`)

### 11.2 Config Schema

```yaml
# .procdsl.yaml
version: "1.0"

# Default binding file
binding: infra/development.infra

# Default output directory
output: deployment/

# Default target runtime
target: flink

# Compilation options
compile:
  parallel: true
  optimization_level: 2

# Validation options
validate:
  strict: false

# Formatting options
format:
  indent: 2
  max_line_length: 100

# Lint options
lint:
  rules:
    naming-convention: error
    unused-import: warning
    missing-description: off

# Schema registry
schema_registry:
  url: ${SCHEMA_REGISTRY_URL}
  auth: ${SCHEMA_REGISTRY_AUTH}
```

---

## 12. Environment Variables

| Variable | Description |
|----------|-------------|
| `PROCDSL_BINDING` | Default binding file |
| `PROCDSL_OUTPUT` | Default output directory |
| `PROCDSL_TARGET` | Default target runtime |
| `PROCDSL_LOG_LEVEL` | Log level |
| `PROCDSL_NO_COLOR` | Disable colors |
| `PROCDSL_SCHEMA_REGISTRY_URL` | Schema registry URL |

---

## 13. Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Compilation/validation failed |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Permission denied |
| 5 | Internal error |

---

## 14. Examples

### 14.1 Development Workflow

```bash
# Initialize project
nexflow init my-pipeline --template full --example

# Edit process files
vim processes/auth_enrichment.proc

# Validate changes
nexflow validate processes/

# Watch and compile during development
nexflow compile processes/ \
  --binding infra/development.infra \
  --watch

# Format before commit
nexflow format processes/
nexflow lint processes/
```

### 14.2 CI/CD Pipeline

```yaml
# .github/workflows/build.yml
steps:
  - name: Validate
    run: nexflow validate processes/ --strict --json

  - name: Lint
    run: nexflow lint processes/ --json

  - name: Compile
    run: |
      nexflow compile processes/ \
        --binding infra/production.infra \
        --output deployment/ \
        --json

  - name: Upload Artifacts
    uses: actions/upload-artifact@v3
    with:
      name: deployment
      path: deployment/
```

### 14.3 Production Deployment

```bash
# Compile for production
nexflow compile processes/ \
  --binding infra/production.infra \
  --output deployment/ \
  --target flink

# View deployment plan
nexflow explain auth_enrichment.proc \
  --binding infra/production.infra \
  --format mermaid

# Deploy (using generated artifacts)
kubectl apply -f deployment/auth_enrichment/k8s/
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-30 | - | Initial specification |
