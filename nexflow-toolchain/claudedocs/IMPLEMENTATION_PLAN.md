# Nexflow Toolchain - Remaining Implementation Plan

**Created:** December 6, 2024
**Status:** Ready for Implementation

---

## Executive Summary

The core generators (L1-L4) are complete but **not wired to the CLI**. The `nexflow build` command currently writes placeholder files. This plan addresses all remaining gaps to achieve production readiness.

---

## Gap Analysis

| Component | Current State | Gap |
|-----------|--------------|-----|
| CLI build command | Placeholder in `generate_code()` | Not using actual generators |
| Validators | Empty module (3 lines) | No semantic validation |
| Unit Tests | Empty directories | No test coverage |
| Code Verification | None | Can't verify Java compiles |
| Documentation | None | No user guides |

---

## Phase 1: CLI-Generator Integration (Critical Path)

**Goal:** Enable `nexflow build` to generate actual Java code

**Impact:** HIGH - Enables end-to-end functionality

### Task 1.1: Update Generator Registry
**File:** `backend/generators/__init__.py`

```python
# Add generator registry
GENERATORS = {
    'schema': SchemaGenerator,
    'flow': FlowGenerator,
    'transform': TransformGenerator,
    'rules': RulesGenerator,
}

def get_generator(lang: str, config: GeneratorConfig):
    """Factory function for generators."""
    generator_class = GENERATORS.get(lang)
    if generator_class:
        return generator_class(config)
    return None
```

### Task 1.2: Wire Generators to Build Command
**File:** `backend/cli/commands/build.py`

Replace placeholder `generate_code()` with actual generator calls:

```python
def generate_code(asts: Dict[str, Dict[Path, Any]], target: str,
                  output_path: Path, project: Project, verbose: bool) -> BuildResult:
    """Generate code using actual generators."""
    from ...generators import get_generator, GeneratorConfig

    result = BuildResult(success=True)

    # Create config from project settings
    config = GeneratorConfig(
        package_prefix=project.package_prefix,
        output_dir=output_path,
        target=target,
    )

    for lang, file_asts in asts.items():
        generator = get_generator(lang, config)
        if not generator:
            if verbose:
                print(f"  No generator for {lang}, skipping...")
            continue

        for file_path, ast in file_asts.items():
            if ast is None:
                continue

            try:
                gen_result = generator.generate(ast)

                # Write generated files
                for gen_file in gen_result.files:
                    full_path = output_path / gen_file.path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(gen_file.content)
                    result.files.append(str(full_path))

                    if verbose:
                        print(f"  Generated {gen_file.path}")

            except Exception as e:
                result.errors.append(f"{file_path}: Generation failed - {e}")
                result.success = False

    return result
```

### Task 1.3: Update Project Configuration
**File:** `backend/cli/project.py`

Add generator configuration fields:

```python
@dataclass
class Project:
    # ... existing fields ...
    package_prefix: str = "com.nexflow.generated"

    @classmethod
    def load(cls, config_path: Path = None):
        # Load from nexflow.toml
        # Add package_prefix from [generate] section
```

**File:** `nexflow.toml` (update template)

```toml
[project]
name = "my-project"
version = "0.1.0"

[generate]
package_prefix = "com.example.pipeline"
target = "flink"

[output]
directory = "generated"
```

### Task 1.4: End-to-End Test
```bash
# Test the full pipeline
nexflow build -v
# Should generate actual Java files in generated/
```

---

## Phase 2: Validators Module

**Goal:** Validate AST semantically before generation

**Impact:** MEDIUM - Catches errors before code generation

### Task 2.1: Base Validator
**File:** `backend/validators/base.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class ValidationError:
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: str = "error"  # error, warning, info

@dataclass
class ValidationResult:
    success: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def add_error(self, message: str, **kwargs):
        self.errors.append(ValidationError(message=message, **kwargs))
        self.success = False

    def add_warning(self, message: str, **kwargs):
        self.warnings.append(ValidationError(message=message, severity="warning", **kwargs))

class BaseValidator:
    """Base class for AST validators."""

    def __init__(self, context: 'ValidationContext' = None):
        self.context = context or ValidationContext()

    def validate(self, ast) -> ValidationResult:
        raise NotImplementedError

@dataclass
class ValidationContext:
    """Shared context for cross-file validation."""
    schemas: dict = field(default_factory=dict)
    transforms: dict = field(default_factory=dict)
    rules: dict = field(default_factory=dict)
    flows: dict = field(default_factory=dict)
```

### Task 2.2: Schema Validator
**File:** `backend/validators/schema_validator.py`

Validates:
- Field type constraints (precision, scale, length)
- Required field presence
- State machine validity (states exist for transitions)
- Version format

### Task 2.3: Transform Validator
**File:** `backend/validators/transform_validator.py`

Validates:
- Input/output schema references exist
- Function calls reference valid transforms
- Expression type compatibility
- Cache key fields exist in input

### Task 2.4: Rules Validator
**File:** `backend/validators/rules_validator.py`

Validates:
- Decision table column types match given clause
- Condition patterns are valid for types
- Return clause matches decide columns
- Procedural rule action signatures

### Task 2.5: Flow Validator
**File:** `backend/validators/flow_validator.py`

Validates:
- Schema references exist
- Transform/rule references exist
- State references valid
- Emit targets are valid

### Task 2.6: Wire to Build Pipeline
**File:** `backend/cli/commands/build.py`

Add Phase 2 semantic validation:

```python
# Phase 2: Semantic validation
from ...validators import validate_project_asts

validation_result = validate_project_asts(parsed_asts, verbose)
if not validation_result.success:
    for error in validation_result.errors:
        result.errors.append(f"{error.file}:{error.line}: {error.message}")
    result.success = False
    return result
```

---

## Phase 3: Unit Tests

**Goal:** Ensure reliability through automated testing

**Impact:** MEDIUM - Prevents regressions

### Test Structure
```
tests/
├── conftest.py              # Pytest fixtures
├── parser/
│   ├── __init__.py
│   ├── test_schema_parser.py
│   ├── test_transform_parser.py
│   ├── test_rules_parser.py
│   └── test_flow_parser.py
├── generators/
│   ├── __init__.py
│   ├── test_schema_generator.py
│   ├── test_transform_generator.py
│   ├── test_rules_generator.py
│   └── test_flow_generator.py
├── validators/
│   ├── __init__.py
│   └── test_validators.py
└── fixtures/
    ├── schema/
    ├── transform/
    ├── rules/
    └── flow/
```

### Task 3.1: Parser Tests
**Example:** `tests/parser/test_schema_parser.py`

```python
import pytest
from backend.parser import SchemaParser

class TestSchemaParser:
    def test_parse_simple_schema(self):
        dsl = '''
        schema test
            fields
                id: string required
            end
        end
        '''
        parser = SchemaParser()
        result = parser.parse(dsl)
        assert result is not None
        assert result.name == "test"
        assert len(result.fields) == 1

    def test_parse_streaming_config(self):
        # Test streaming block parsing
        pass

    def test_parse_state_machine(self):
        # Test state machine parsing
        pass

    def test_syntax_error_handling(self):
        dsl = "schema broken { invalid }"
        parser = SchemaParser()
        with pytest.raises(ParseError):
            parser.parse(dsl)
```

### Task 3.2: Generator Tests
**Example:** `tests/generators/test_rules_generator.py`

```python
import pytest
from backend.parser import RulesParser
from backend.generators import RulesGenerator, GeneratorConfig

class TestRulesGenerator:
    @pytest.fixture
    def generator(self):
        config = GeneratorConfig(package_prefix="com.test")
        return RulesGenerator(config)

    def test_decision_table_generation(self, generator):
        dsl = '''
        decision_table test_table
            hit_policy first_match
            given:
                amount: number
            decide:
                | amount | action |
                | > 100  | "review" |
            return:
                action: text
        end
        '''
        parser = RulesParser()
        ast = parser.parse(dsl)
        result = generator.generate(ast)

        assert len(result.files) == 1
        assert "TestTableTable.java" in result.files[0].path
        assert "public class TestTableTable" in result.files[0].content

    def test_procedural_rule_generation(self, generator):
        # Test procedural rule generation
        pass
```

---

## Phase 4: Generated Code Verification

**Goal:** Verify generated Java code compiles and runs

**Impact:** HIGH - Confidence in output quality

### Task 4.1: Maven Project Template
**File:** `templates/maven/pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>${package_prefix}</groupId>
    <artifactId>nexflow-generated</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <flink.version>1.18.0</flink.version>
        <java.version>11</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${flink.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients</artifactId>
            <version>${flink.version}</version>
        </dependency>
        <dependency>
            <groupId>com.github.ben-manes.caffeine</groupId>
            <artifactId>caffeine</artifactId>
            <version>3.1.8</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.9</version>
        </dependency>
    </dependencies>
</project>
```

### Task 4.2: Verification Script
**File:** `scripts/verify_generated.sh`

```bash
#!/bin/bash
set -e

OUTPUT_DIR=${1:-"generated"}
VERIFY_DIR="$OUTPUT_DIR/.verify"

echo "=== Nexflow Generated Code Verification ==="

# Create verification project
mkdir -p "$VERIFY_DIR"
cp templates/maven/pom.xml "$VERIFY_DIR/"

# Copy generated Java files
mkdir -p "$VERIFY_DIR/src/main/java"
find "$OUTPUT_DIR" -name "*.java" -exec cp {} "$VERIFY_DIR/src/main/java/" \;

# Compile
echo "Compiling generated code..."
cd "$VERIFY_DIR"
mvn compile -q

if [ $? -eq 0 ]; then
    echo "✓ Compilation successful"
else
    echo "✗ Compilation failed"
    exit 1
fi

# Cleanup
cd ..
rm -rf "$VERIFY_DIR"

echo "=== Verification Complete ==="
```

### Task 4.3: Add --verify Flag to Build
**File:** `backend/cli/main.py`

```python
@cli.command()
@click.option("--verify", is_flag=True, help="Compile generated Java code to verify correctness")
def build(ctx, target, output, dry_run, verify):
    # ... existing build logic ...

    if verify and result.success:
        verify_result = verify_generated_code(output_path)
        if not verify_result.success:
            console.print("[red]✗[/red] Generated code verification failed")
            sys.exit(1)
        console.print("[green]✓[/green] Generated code compiles successfully")
```

---

## Phase 5: Documentation

**Goal:** Enable users to adopt the toolchain

**Impact:** LOW (for functionality) / HIGH (for adoption)

### Task 5.1: DSL Reference
**File:** `docs/DSL_REFERENCE.md`

- L1 Flow syntax and semantics
- L2 Schema syntax and semantics
- L3 Transform syntax and semantics
- L4 Rules syntax and semantics
- Examples for each construct

### Task 5.2: CLI Guide
**File:** `docs/CLI_GUIDE.md`

- Installation
- Project initialization
- Building projects
- Validation
- Configuration options

### Task 5.3: Architecture Guide
**File:** `docs/ARCHITECTURE.md`

- System overview
- Grammar → Parser → AST → Generator pipeline
- Extension points
- Contributing guide

---

## Implementation Order

```
Week 1:
├── Phase 1: CLI-Generator Integration (Critical)
│   ├── 1.1 Generator registry
│   ├── 1.2 Wire to build command
│   ├── 1.3 Project config
│   └── 1.4 End-to-end test

Week 2:
├── Phase 2: Validators (in parallel with Phase 4)
│   ├── 2.1 Base validator
│   ├── 2.2-2.5 DSL validators
│   └── 2.6 Wire to build
│
└── Phase 4: Code Verification
    ├── 4.1 Maven template
    ├── 4.2 Verify script
    └── 4.3 --verify flag

Week 3:
├── Phase 3: Unit Tests
│   ├── 3.1 Parser tests
│   └── 3.2 Generator tests
│
└── Phase 5: Documentation
    ├── 5.1 DSL reference
    ├── 5.2 CLI guide
    └── 5.3 Architecture
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `nexflow build` generates actual Java files
- [ ] Generated files are in correct package structure
- [ ] All 4 DSL types generate code

### Phase 2 Complete When:
- [ ] Schema references validated in transforms
- [ ] Invalid DSL files produce clear error messages
- [ ] Cross-file validation works

### Phase 3 Complete When:
- [ ] >80% code coverage on parsers
- [ ] >70% code coverage on generators
- [ ] CI pipeline runs tests

### Phase 4 Complete When:
- [ ] `nexflow build --verify` compiles generated Java
- [ ] Sample project builds and runs

### Phase 5 Complete When:
- [ ] New user can build first project using docs only
- [ ] All DSL constructs documented with examples

---

## Quick Start - Phase 1 Implementation

To begin immediately, start with Task 1.2 (the most impactful change):

```bash
# Edit build.py to use actual generators
vim backend/cli/commands/build.py

# Test with sample files
python -c "
from backend.cli.commands.build import generate_code
from backend.parser import SchemaParser
from pathlib import Path

# Parse sample file
parser = SchemaParser()
ast = parser.parse_file('src/schema/transaction.schema')

# Generate code (after implementing)
# generate_code({'schema': {Path('test.schema'): ast}}, 'flink', Path('generated'), verbose=True)
"
```

---

*Plan created by Claude Code*
