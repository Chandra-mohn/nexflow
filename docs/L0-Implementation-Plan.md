# Nexflow Implementation Plan

> **Status**: Planning
> **Version**: 1.0
> **Last Updated**: 2025-12-04

---

## Overview

This document outlines the phased implementation plan for building the Nexflow development toolchain. The approach follows an incremental strategy, starting with the foundational parser infrastructure and progressively adding layers.

**Reference Architecture**: Based on existing `rules-dsl` project patterns at `~/workspace/rules_engine/rules-dsl/`

---

## Implementation Phases

```
Phase 1: Foundation          Phase 2: Core DSLs         Phase 3: Advanced DSLs
┌─────────────────┐         ┌─────────────────┐        ┌─────────────────┐
│ Project Setup   │         │ L1 Flow DSL     │        │ L3 Mapping DSL  │
│ L4 Rules DSL    │   ───▶  │ L2 Schema DSL   │  ───▶  │ L5 Config DSL   │
│ VS Code Ext     │         │ Code Generation │        │ L6 Deploy DSL   │
└─────────────────┘         └─────────────────┘        └─────────────────┘
     4 weeks                      6 weeks                    4 weeks

Phase 4: Integration         Phase 5: Production
┌─────────────────┐         ┌─────────────────┐
│ End-to-End Test │         │ CI/CD Pipeline  │
│ Flink/Spark Gen │   ───▶  │ Documentation   │
│ Sample Projects │         │ Release 1.0     │
└─────────────────┘         └─────────────────┘
     4 weeks                      2 weeks
```

---

## Phase 1: Foundation (Weeks 1-4)

### Goals
- Establish project structure mirroring rules-dsl
- Implement L4 Rules DSL (simplest grammar, proven patterns)
- Create VS Code extension skeleton
- Validate end-to-end: DSL → Parse → Generate Java

### 1.1 Project Structure Setup

```
nexflow/
├── docs/                       # Existing specs
├── grammar/                    # ANTLR4 grammars
│   └── RulesDSL.g4            # Start with L4
├── backend/
│   ├── __init__.py
│   ├── requirements.txt
│   ├── app.py                  # Flask API
│   ├── config.py
│   ├── parser/                 # ANTLR-generated + wrappers
│   │   ├── __init__.py
│   │   └── rules_parser.py
│   ├── ast/                    # Python dataclass AST
│   │   ├── __init__.py
│   │   └── rules_ast.py
│   ├── validators/             # Semantic validation
│   │   ├── __init__.py
│   │   └── rules_validator.py
│   ├── generators/             # Code generators
│   │   ├── __init__.py
│   │   └── rules_generator.py
│   └── api/                    # REST endpoints
│       ├── __init__.py
│       └── routes.py
├── extension/                  # VS Code extension
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   └── extension.ts
│   └── syntaxes/
│       └── rules.tmLanguage.json
├── rules/                      # Sample DSL files
│   ├── schemas/
│   ├── decisions/
│   └── contexts/
├── generated/                  # Output directory
│   └── java/
├── tests/
│   ├── grammar/
│   ├── parser/
│   └── generators/
└── nexflow.config.yaml        # Workspace config
```

### 1.2 Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| **1.2.1** | Initialize Python project with dependencies | `requirements.txt`, `setup.py` |
| **1.2.2** | Port/adapt RulesDSL.g4 from existing grammar | `grammar/RulesDSL.g4` |
| **1.2.3** | Generate ANTLR Python parser | `backend/parser/` files |
| **1.2.4** | Create AST dataclasses for decision tables | `backend/ast/rules_ast.py` |
| **1.2.5** | Implement parser wrapper with error handling | `backend/parser/rules_parser.py` |
| **1.2.6** | Create Flask API skeleton | `backend/app.py`, `api/routes.py` |
| **1.2.7** | Implement Java code generator (f-strings) | `backend/generators/rules_generator.py` |
| **1.2.8** | Create VS Code extension skeleton | `extension/` structure |
| **1.2.9** | Implement TextMate grammar for syntax highlighting | `syntaxes/rules.tmLanguage.json` |
| **1.2.10** | Write unit tests for parser and generator | `tests/` |

### 1.3 L4 Rules DSL Grammar (Simplified Start)

```antlr
// grammar/RulesDSL.g4
grammar RulesDSL;

// Parser rules
ruleFile: (decisionTable | ruleBlock)+ EOF;

decisionTable
    : 'decision_table' IDENTIFIER
      hitPolicy?
      description?
      givenBlock
      decideBlock
      returnBlock?
      'end'
    ;

hitPolicy: 'hit_policy' ('first_match' | 'single_hit' | 'multi_hit');
description: 'description' STRING;

givenBlock: 'given' ':' inputParam+;
inputParam: '-' IDENTIFIER ':' typeSpec;
typeSpec: 'number' | 'text' | 'boolean' | 'money' | 'percentage' | IDENTIFIER;

decideBlock: 'decide' ':' tableRow+;
tableRow: '|' cell+ '|';
cell: cellValue | '*';
cellValue: comparison | STRING | NUMBER | BOOLEAN;
comparison: compOp value;
compOp: '>=' | '<=' | '>' | '<' | '==' | '!=';
value: NUMBER | STRING | MONEY;

returnBlock: 'return' ':' returnParam+;
returnParam: '-' IDENTIFIER ':' typeSpec;

ruleBlock: 'rule' ruleName ':' ruleStatement+;
ruleName: STRING | IDENTIFIER;
ruleStatement: ifStatement | action;
ifStatement: 'if' condition 'then' action+ ('elseif' condition 'then' action+)* ('else' action+)? 'endif';
condition: orExpr;
orExpr: andExpr ('or' andExpr)*;
andExpr: notExpr ('and' notExpr)*;
notExpr: 'not'? primaryExpr;
primaryExpr: comparison | '(' orExpr ')';
action: IDENTIFIER ('(' paramList? ')')?;
paramList: expr (',' expr)*;
expr: term (('+' | '-') term)*;
term: factor (('*' | '/') factor)*;
factor: atom | '(' expr ')';
atom: attribute | NUMBER | STRING | BOOLEAN;
attribute: IDENTIFIER ('.' IDENTIFIER)*;

// Lexer rules
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
STRING: '"' (~["\r\n])* '"' | '\'' (~['\r\n])* '\'';
NUMBER: [0-9]+ ('.' [0-9]+)?;
MONEY: '$' [0-9]+ (',' [0-9]{3})* ('.' [0-9]{2})?;
BOOLEAN: 'true' | 'false';
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
```

### 1.4 Milestone Criteria

- [ ] Parse sample decision table without errors
- [ ] Generate compilable Java code from decision table
- [ ] VS Code extension provides syntax highlighting
- [ ] Flask API responds to `/api/validate` and `/api/generate`

---

## Phase 2: Core DSLs (Weeks 5-10)

### Goals
- Implement L1 Flow DSL (pipeline definitions)
- Implement L2 Schema DSL (entity definitions)
- Generate Avro schemas from L2
- Generate Flink job skeletons from L1

### 2.1 L1 Flow DSL Grammar

```antlr
// grammar/ProcDSL.g4 (L1 Flow)
grammar ProcDSL;

flowFile: flowDefinition+ EOF;

flowDefinition
    : 'flow' IDENTIFIER
      description?
      sourceBlock
      transformBlock*
      sinkBlock
      'end'
    ;

sourceBlock: 'source' ':' sourceSpec;
sourceSpec
    : 'kafka' kafkaConfig
    | 'file' fileConfig
    ;

kafkaConfig: 'topic' STRING 'schema' IDENTIFIER ('group' STRING)?;

transformBlock
    : 'transform' IDENTIFIER ':' transformSpec
    | 'enrich' IDENTIFIER ':' enrichSpec
    | 'filter' IDENTIFIER ':' filterSpec
    | 'apply_rules' IDENTIFIER ':' rulesSpec
    ;

transformSpec: 'using' IDENTIFIER;  // Reference to L3 mapping
enrichSpec: 'lookup' IDENTIFIER 'from' IDENTIFIER;
filterSpec: 'where' condition;
rulesSpec: 'decision_table' IDENTIFIER;  // Reference to L4

sinkBlock: 'sink' ':' sinkSpec;
sinkSpec
    : 'kafka' 'topic' STRING
    | 'mongo' 'collection' STRING
    ;
```

### 2.2 L2 Schema DSL Grammar

```antlr
// grammar/SchemaDSL.g4 (L2 Schema)
grammar SchemaDSL;

schemaFile: entityDefinition+ EOF;

entityDefinition
    : 'entity' IDENTIFIER
      description?
      fieldBlock
      constraintBlock?
      'end'
    ;

fieldBlock: 'fields' ':' fieldDef+;
fieldDef: '-' IDENTIFIER ':' fieldType fieldModifiers?;
fieldType
    : 'string' | 'number' | 'boolean' | 'money' | 'date' | 'timestamp'
    | 'list' '<' fieldType '>'
    | IDENTIFIER  // Reference to another entity
    ;
fieldModifiers: ('required' | 'optional' | 'unique')*;

constraintBlock: 'constraints' ':' constraint+;
constraint: '-' constraintExpr;
constraintExpr: IDENTIFIER comparison value;
```

### 2.3 Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| **2.3.1** | Create ProcDSL.g4 grammar | `grammar/ProcDSL.g4` |
| **2.3.2** | Create SchemaDSL.g4 grammar | `grammar/SchemaDSL.g4` |
| **2.3.3** | Generate ANTLR parsers for L1, L2 | Parser files |
| **2.3.4** | Create AST dataclasses for L1, L2 | `ast/flow_ast.py`, `ast/schema_ast.py` |
| **2.3.5** | Implement Avro schema generator | `generators/schema_generator.py` |
| **2.3.6** | Implement Flink job generator | `generators/flow_generator.py` |
| **2.3.7** | Add L1, L2 syntax to VS Code extension | TextMate grammars |
| **2.3.8** | Implement cross-reference validation | Schema references in flows |
| **2.3.9** | Write integration tests | End-to-end tests |

### 2.4 Milestone Criteria

- [ ] Parse flow definition referencing schemas and rules
- [ ] Generate Avro `.avsc` files from L2 schemas
- [ ] Generate Flink DataStream job skeleton from L1 flow
- [ ] VS Code provides completion for schema/rule references

---

## Phase 3: Advanced DSLs (Weeks 11-14)

### Goals
- Implement L3 Mapping DSL
- Implement L5 Config DSL (YAML-based)
- Implement L6 Deploy DSL (YAML-based)
- Complete code generation for all layers

### 3.1 L3 Mapping DSL Grammar

```antlr
// grammar/MappingDSL.g4
grammar MappingDSL;

mappingFile: mappingDefinition+ EOF;

mappingDefinition
    : 'mapping' IDENTIFIER
      'from' IDENTIFIER 'to' IDENTIFIER  // Source and target schemas
      fieldMappings
      'end'
    ;

fieldMappings: 'fields' ':' fieldMapping+;
fieldMapping
    : '-' targetField ':' sourceExpr
    | '-' targetField ':' 'lookup' '(' lookupExpr ')'
    | '-' targetField ':' 'compute' '(' computeExpr ')'
    ;

targetField: IDENTIFIER;
sourceExpr: IDENTIFIER ('.' IDENTIFIER)*;
lookupExpr: IDENTIFIER ',' sourceExpr;  // collection, key
computeExpr: expr;
```

### 3.2 L5/L6 (YAML-based)

No ANTLR grammar needed - use PyYAML with JSON Schema validation.

```yaml
# L5 Config Example
config:
  name: fraud-detection
  environment: production

  kafka:
    bootstrap_servers: kafka-cluster:9092
    schema_registry: http://schema-registry:8081

  flink:
    checkpointing:
      interval: 60000
      mode: EXACTLY_ONCE
    state_backend: rocksdb
```

```yaml
# L6 Deploy Example
deployment:
  name: fraud-detection-pipeline
  type: flink

  resources:
    job_manager:
      memory: 2048m
      cpu: 1
    task_manager:
      memory: 4096m
      cpu: 2
      replicas: 3

  scaling:
    min_replicas: 2
    max_replicas: 10
```

### 3.3 Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| **3.3.1** | Create MappingDSL.g4 grammar | `grammar/MappingDSL.g4` |
| **3.3.2** | Implement mapping code generator | `generators/mapping_generator.py` |
| **3.3.3** | Create JSON schemas for L5, L6 | `schemas/config.schema.json`, `deploy.schema.json` |
| **3.3.4** | Implement YAML validators | `validators/config_validator.py` |
| **3.3.5** | Implement K8s manifest generator | `generators/deploy_generator.py` |
| **3.3.6** | Add YAML support to VS Code extension | Schema validation |

---

## Phase 4: Integration (Weeks 15-18)

### Goals
- End-to-end pipeline: DSL → Parse → Validate → Generate → Compile
- Spark code generation (batch + streaming)
- Sample project demonstrating full workflow

### 4.1 Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| **4.1.1** | Implement Spark batch job generator | `generators/spark_batch_generator.py` |
| **4.1.2** | Implement Spark streaming generator | `generators/spark_stream_generator.py` |
| **4.1.3** | Create CLI tool for batch generation | `cli/nexflow_cli.py` |
| **4.1.4** | Build sample fraud-detection project | `examples/fraud-detection/` |
| **4.1.5** | Integration tests with real Flink/Spark | Test containers |
| **4.1.6** | Performance benchmarking | Benchmark results |

### 4.2 Sample Project Structure

```
examples/fraud-detection/
├── schemas/
│   ├── transaction.schema        # L2
│   └── merchant.schema           # L2
├── flows/
│   └── fraud-pipeline.flow       # L1
├── mappings/
│   └── enrich-transaction.map    # L3
├── decisions/
│   ├── fraud-detection.rules     # L4
│   └── velocity-check.rules      # L4
├── config/
│   └── production.config.yaml    # L5
├── deploy/
│   └── kubernetes.deploy.yaml    # L6
└── generated/
    ├── java/
    ├── avro/
    └── k8s/
```

---

## Phase 5: Production (Weeks 19-20)

### Goals
- CI/CD pipeline for toolchain
- Documentation and examples
- Release 1.0

### 5.1 Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| **5.1.1** | GitHub Actions CI/CD | `.github/workflows/` |
| **5.1.2** | PyPI package setup | `setup.py`, `pyproject.toml` |
| **5.1.3** | VS Code extension marketplace prep | `extension/package.json` |
| **5.1.4** | User documentation | `docs/user-guide/` |
| **5.1.5** | API documentation | `docs/api/` |
| **5.1.6** | Release 1.0 | Tagged release |

---

## Immediate Next Steps (This Week)

### Priority 1: Project Bootstrap

```bash
# 1. Create directory structure
mkdir -p nexflow/{grammar,backend/{parser,ast,validators,generators,api},extension/{src,syntaxes},rules/{schemas,decisions,contexts},generated/java,tests}

# 2. Initialize Python environment
cd nexflow/backend
python -m venv venv
source venv/bin/activate
pip install antlr4-python3-runtime==4.13.2 Flask==2.3.3 Flask-CORS==4.0.0 PyYAML==6.0.1

# 3. Copy/adapt grammar from rules-dsl
cp ~/workspace/rules_engine/rules-dsl/java-bridge/java-bridge/src/main/antlr4/com/rules/grammar/Rules.g4 grammar/RulesDSL.g4

# 4. Generate Python parser
cd grammar
antlr4 -Dlanguage=Python3 -visitor RulesDSL.g4 -o ../backend/parser/generated
```

### Priority 2: First Vertical Slice

1. Parse a simple decision table
2. Generate Java code
3. Verify it compiles

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Grammar complexity | Start with L4 (simplest), iterate |
| Code generation quality | Reference existing rules-dsl templates |
| IDE integration issues | Follow proven VS Code extension patterns |
| Cross-layer references | Implement symbol table early |
| Performance | Profile parser on large files |

---

## Dependencies on External Systems

| System | Phase Needed | Purpose |
|--------|--------------|---------|
| ANTLR4 | Phase 1 | Parser generation |
| Java 17 | Phase 4 | Compile generated code |
| Flink 1.18 | Phase 4 | Integration testing |
| Kafka | Phase 4 | Integration testing |
| Docker | Phase 4 | Test containers |
| Kubernetes | Phase 5 | Deploy testing |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Parse time (1000-line file) | < 100ms |
| Code generation time | < 500ms |
| VS Code extension startup | < 2s |
| Generated code compile rate | 100% |
| Test coverage | > 80% |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-04 | Initial implementation plan |
