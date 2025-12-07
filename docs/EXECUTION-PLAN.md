# Nexflow CLI Toolchain - Execution Plan

> **Created**: 2025-12-05
> **Status**: Active Development
> **Target**: Complete CLI toolchain for Nexflow DSL → Flink/Spark code generation

---

## Current State Summary

### ✅ Completed

| Component | Status | Location |
|-----------|--------|----------|
| ANTLR Grammars (L1-L4) | ✅ Complete | `nexflow-toolchain/grammar/*.g4` |
| AST Definitions (L1-L4) | ✅ Complete | `nexflow-toolchain/backend/ast/*.py` |
| ANTLR Generated Parsers | ✅ Complete | `nexflow-toolchain/backend/parser/generated/` |
| L4 Rules Parser Wrapper | ✅ Complete | `nexflow-toolchain/backend/parser/rules_parser.py` |
| CLI Framework | ✅ Complete | `nexflow-toolchain/backend/cli/` |
| Project Config | ✅ Complete | `nexflow.toml` support |
| Rebranding | ✅ Complete | PROC-DSL → Nexflow |

### ❌ Not Yet Implemented

| Component | Status | Priority |
|-----------|--------|----------|
| L1 Flow Parser Wrapper | ❌ Missing | P1 |
| L2 Schema Parser Wrapper | ❌ Missing | P1 |
| L3 Transform Parser Wrapper | ❌ Missing | P1 |
| Semantic Validation | ❌ Missing | P2 |
| Code Generators | ❌ Placeholder | P2 |
| VS Code Extension | ❌ Scaffolded | P3 |
| Sample Projects | ❌ Missing | P3 |

---

## Phase 1: Parser Completion (Foundation)

**Goal**: All 4 DSL types can be parsed via CLI

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 1.1 | Create L1 Flow Parser Wrapper | `backend/parser/flow_parser.py` | - |
| 1.2 | Create L2 Schema Parser Wrapper | `backend/parser/schema_parser.py` | - |
| 1.3 | Create L3 Transform Parser Wrapper | `backend/parser/transform_parser.py` | - |
| 1.4 | Update PARSERS registry | `backend/parser/__init__.py` | 1.1-1.3 |
| 1.5 | Create sample DSL files | `nexflow-toolchain/src/` | - |
| 1.6 | Test all parsers via CLI | Manual testing | 1.4, 1.5 |

### Parser Wrapper Pattern (from rules_parser.py)

```python
class FlowParser(BaseParser):
    def parse(self, content: str) -> ParseResult:
        # 1. Create ANTLR lexer/parser
        # 2. Walk parse tree with listener
        # 3. Build AST using dataclasses
        # 4. Return ParseResult with AST or errors
```

### Deliverables
- [ ] `nexflow parse src/flow/example.flow` works
- [ ] `nexflow parse src/schema/example.schema` works
- [ ] `nexflow parse src/transform/example.transform` works
- [ ] `nexflow validate` checks all 4 DSL types

---

## Phase 2: Semantic Validation

**Goal**: CLI validates cross-file references and type compatibility

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 2.1 | Create Symbol Table | `backend/validators/symbol_table.py` | Phase 1 |
| 2.2 | Create Reference Resolver | `backend/validators/reference_resolver.py` | 2.1 |
| 2.3 | Create Type Checker | `backend/validators/type_checker.py` | 2.1 |
| 2.4 | Create Import Resolver | `backend/validators/import_resolver.py` | 2.1 |
| 2.5 | Integrate into build pipeline | `backend/cli/commands.py` | 2.2-2.4 |

### Validation Rules

```
L1 Flow References:
  - schema <name> → must exist in L2
  - transform using <name> → must exist in L3
  - route using <name> → must exist in L4

L2 Schema References:
  - Field types must be valid base/domain types
  - Nested schemas must exist

L3 Transform References:
  - input/output schemas must exist in L2
  - Field mappings must reference valid fields

L4 Rules References:
  - Condition fields must be valid types
  - Actions must be in action catalog
```

### Deliverables
- [ ] `nexflow validate` detects undefined schema references
- [ ] `nexflow validate` detects undefined rule references
- [ ] `nexflow validate` reports type mismatches
- [ ] Error messages include file:line:column

---

## Phase 3: Code Generation - L4 Rules

**Goal**: `.rules` files compile to Flink Java UDFs

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 3.1 | Create Rules Generator | `backend/generators/rules_generator.py` | Phase 2 |
| 3.2 | Decision Table Codegen | `backend/generators/decision_table_codegen.py` | 3.1 |
| 3.3 | Procedural Rule Codegen | `backend/generators/procedural_rule_codegen.py` | 3.1 |
| 3.4 | Flink UDF Template | `backend/generators/templates/flink_udf.py` | - |
| 3.5 | Test with sample rules | Manual testing | 3.1-3.4 |

### Generated Code Pattern

```java
// Input: fraud_detection.rules
// Output: FraudDetectionV2.java

@FunctionHint(output = @DataTypeHint("STRING"))
public class FraudDetectionV2 extends ScalarFunction {
    public String eval(BigDecimal amount, String riskTier, String merchantId) {
        // Generated from decision table
        if (amount.compareTo(new BigDecimal("10000")) > 0 && "high".equals(riskTier)) {
            return "block";
        }
        // ... more conditions
        return "approve";
    }
}
```

### Deliverables
- [ ] `nexflow build` generates `.java` UDF from `.rules`
- [ ] Decision tables generate correct if/else logic
- [ ] Procedural rules generate correct Java
- [ ] Generated code compiles with javac

---

## Phase 4: Code Generation - L2 Schemas

**Goal**: `.schema` files compile to Avro schemas and Java POJOs

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 4.1 | Create Schema Generator | `backend/generators/schema_generator.py` | Phase 2 |
| 4.2 | Avro Schema Codegen | `backend/generators/avro_codegen.py` | 4.1 |
| 4.3 | Java POJO Codegen | `backend/generators/pojo_codegen.py` | 4.1 |
| 4.4 | Type Mapping (DSL→Avro→Java) | `backend/generators/type_mapping.py` | - |
| 4.5 | Test with sample schemas | Manual testing | 4.1-4.4 |

### Generated Artifacts

```
Input: customer.schema
Output:
  - customer_v1.avsc (Avro schema)
  - Customer.java (POJO with @AvroGenerated)
```

### Deliverables
- [ ] `nexflow build` generates `.avsc` from `.schema`
- [ ] `nexflow build` generates `.java` POJO from `.schema`
- [ ] Type mappings handle all L2 types
- [ ] Streaming annotations preserved in Avro

---

## Phase 5: Code Generation - L3 Transforms

**Goal**: `.transform` files compile to Flink MapFunction/ProcessFunction

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 5.1 | Create Transform Generator | `backend/generators/transform_generator.py` | Phase 4 |
| 5.2 | Field Mapping Codegen | `backend/generators/field_mapping_codegen.py` | 5.1 |
| 5.3 | Expression Codegen | `backend/generators/expression_codegen.py` | 5.1 |
| 5.4 | Flink MapFunction Template | `backend/generators/templates/flink_map.py` | - |
| 5.5 | Test with sample transforms | Manual testing | 5.1-5.4 |

### Generated Code Pattern

```java
// Input: customer_enrichment.transform
// Output: CustomerEnrichmentTransform.java

public class CustomerEnrichmentTransform extends MapFunction<AuthEvent, EnrichedEvent> {
    @Override
    public EnrichedEvent map(AuthEvent input) {
        return EnrichedEvent.builder()
            .fullName(input.getFirstName() + " " + input.getLastName())
            .enrichedAmount(input.getAmount().multiply(exchangeRate))
            .build();
    }
}
```

### Deliverables
- [ ] `nexflow build` generates MapFunction from `.transform`
- [ ] Field mappings generate correct Java expressions
- [ ] Computed fields generate correct calculations
- [ ] Generated code compiles with javac

---

## Phase 6: Code Generation - L1 Flows (Crown Jewel)

**Goal**: `.flow` files compile to complete Flink jobs (SQL + UDFs)

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 6.1 | Create Flow Generator | `backend/generators/flow_generator.py` | Phase 3-5 |
| 6.2 | Flink SQL DDL Codegen | `backend/generators/flink_ddl_codegen.py` | 6.1 |
| 6.3 | Flink SQL DML Codegen | `backend/generators/flink_dml_codegen.py` | 6.1 |
| 6.4 | Job Main Class Codegen | `backend/generators/flink_job_codegen.py` | 6.1 |
| 6.5 | Artifact Assembly | `backend/generators/artifact_assembler.py` | 6.1-6.4 |
| 6.6 | Test with sample flows | Manual testing | 6.1-6.5 |

### Generated Artifacts

```
Input: fraud_pipeline.flow
Output:
  generated/flink/fraud_pipeline/
  ├── sql/
  │   ├── 01_ddl_sources.sql
  │   ├── 02_ddl_lookups.sql
  │   ├── 03_ddl_sinks.sql
  │   └── 04_dml_processing.sql
  ├── udfs/
  │   └── FraudDetectionV2.java
  ├── config/
  │   └── flink-conf.yaml
  └── manifest.json
```

### Deliverables
- [ ] `nexflow build` generates complete Flink SQL
- [ ] DDL includes Kafka connectors from L5 binding
- [ ] DML includes UDF calls from L4 rules
- [ ] Deployment manifest tracks all artifacts

---

## Phase 7: IDE Integration

**Goal**: VS Code extension with syntax highlighting and validation

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 7.1 | TextMate Grammar for L1-L4 | `extension/syntaxes/*.tmLanguage.json` | - |
| 7.2 | Language Configuration | `extension/language-configuration.json` | - |
| 7.3 | Extension Activation | `extension/src/extension.ts` | 7.1-7.2 |
| 7.4 | LSP Server (Python) | `backend/lsp/server.py` | Phase 2 |
| 7.5 | Diagnostics Provider | `backend/lsp/diagnostics.py` | 7.4 |
| 7.6 | Completion Provider | `backend/lsp/completion.py` | 7.4 |

### Deliverables
- [ ] Syntax highlighting for all 4 DSL types
- [ ] Real-time validation errors in editor
- [ ] Auto-completion for keywords
- [ ] Go-to-definition for references

---

## Phase 8: Testing & Documentation

**Goal**: Comprehensive tests and sample projects

### Tasks

| ID | Task | File | Depends On |
|----|------|------|------------|
| 8.1 | Sample Fraud Detection Project | `examples/fraud-detection/` | Phase 6 |
| 8.2 | Parser Unit Tests | `tests/parser/` | Phase 1 |
| 8.3 | Validator Unit Tests | `tests/validators/` | Phase 2 |
| 8.4 | Generator Unit Tests | `tests/generators/` | Phase 3-6 |
| 8.5 | Integration Tests | `tests/integration/` | Phase 6 |
| 8.6 | User Documentation | `docs/user-guide/` | All |

### Sample Project Structure

```
examples/fraud-detection/
├── src/
│   ├── flow/
│   │   └── fraud_pipeline.flow
│   ├── schema/
│   │   ├── transaction.schema
│   │   └── customer.schema
│   ├── transform/
│   │   └── enrich_transaction.transform
│   └── rules/
│       └── fraud_detection.rules
├── infra/
│   └── development.infra
├── nexflow.toml
└── README.md
```

### Deliverables
- [ ] Sample project compiles end-to-end
- [ ] Parser tests cover grammar edge cases
- [ ] 80%+ test coverage
- [ ] User guide with quickstart

---

## Implementation Priority

### Sprint 1: Parser Completion (Phase 1)
- Focus: Get all 4 DSL types parsing
- Effort: ~3-5 hours per parser wrapper

### Sprint 2: L4 Code Generation (Phase 3)
- Focus: End-to-end for one layer
- Effort: ~8-10 hours

### Sprint 3: Semantic Validation (Phase 2)
- Focus: Cross-reference checking
- Effort: ~6-8 hours

### Sprint 4: Remaining Code Generation (Phase 4-6)
- Focus: Complete the pipeline
- Effort: ~15-20 hours

### Sprint 5: Polish (Phase 7-8)
- Focus: IDE + tests + samples
- Effort: ~10-15 hours

---

## Quick Reference: File Locations

```
nexflow-toolchain/
├── grammar/                    # ANTLR4 grammars
│   ├── ProcDSL.g4             # L1
│   ├── SchemaDSL.g4           # L2
│   ├── TransformDSL.g4        # L3
│   └── RulesDSL.g4            # L4
├── backend/
│   ├── ast/                   # ✅ Complete
│   │   ├── proc_ast.py
│   │   ├── schema_ast.py
│   │   ├── transform_ast.py
│   │   └── rules_ast.py
│   ├── parser/
│   │   ├── rules_parser.py    # ✅ Complete
│   │   ├── flow_parser.py     # ❌ TODO
│   │   ├── schema_parser.py   # ❌ TODO
│   │   └── transform_parser.py # ❌ TODO
│   ├── validators/            # ❌ TODO
│   │   ├── symbol_table.py
│   │   ├── reference_resolver.py
│   │   └── type_checker.py
│   ├── generators/            # ❌ TODO
│   │   ├── rules_generator.py
│   │   ├── schema_generator.py
│   │   ├── transform_generator.py
│   │   └── flow_generator.py
│   └── cli/                   # ✅ Complete
│       ├── main.py
│       ├── commands.py
│       └── project.py
├── extension/                 # Scaffolded
└── tests/                     # ❌ TODO
```

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-05 | Claude | Initial execution plan |
