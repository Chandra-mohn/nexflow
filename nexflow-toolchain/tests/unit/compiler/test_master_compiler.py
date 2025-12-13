"""
Tests for L6 Master Compiler

Tests the compilation orchestration and infrastructure integration.
"""

import pytest
import tempfile
from pathlib import Path

from backend.compiler import (
    MasterCompiler,
    CompilationResult,
    CompilationPhase,
    LayerResult,
)


class TestMasterCompilerBasic:
    """Basic compiler tests."""

    def test_compiler_initialization(self):
        """Test compiler can be initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
            )

            assert compiler.src_dir == src_dir
            assert compiler.output_dir == output_dir
            assert compiler.package_prefix == "com.test.flow"

    def test_compile_empty_project(self):
        """Test compiling empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
            )

            result = compiler.compile()

            # Empty project should succeed with no files
            assert result.success
            assert result.total_files_generated == 0
            assert len(result.errors) == 0


class TestMasterCompilerInfrastructure:
    """Tests for L5 infrastructure integration."""

    def test_no_infra_file_uses_defaults(self):
        """Test that missing .infra file uses development defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
            )

            result = compiler.compile()

            # Should succeed with warning
            assert result.success
            assert any("default" in w.lower() for w in result.warnings)
            assert result.binding_resolver is not None
            assert result.binding_resolver.has_config is False

    def test_parse_infra_file(self):
        """Test parsing infrastructure configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            infra_dir = src_dir / "infra"
            infra_dir.mkdir()

            # Create a minimal .infra file
            infra_content = """
kafka:
  brokers: kafka.prod:9092
  security_protocol: PLAINTEXT

streams:
  auth_events:
    topic: prod.auth.events
    parallelism: 4
"""
            (infra_dir / "prod.infra").write_text(infra_content)

            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
                environment="prod",
            )

            result = compiler.compile()

            # Should parse infra successfully
            assert result.success
            assert result.infra_config is not None
            assert result.infra_config.kafka.brokers == "kafka.prod:9092"
            assert "auth_events" in result.infra_config.streams

    def test_infra_file_environment_selection(self):
        """Test that environment parameter selects correct .infra file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            infra_dir = src_dir / "infra"
            infra_dir.mkdir(parents=True)

            # Create multiple .infra files
            dev_content = """
kafka:
  brokers: localhost:9092
streams:
  events:
    topic: dev.events
"""
            prod_content = """
kafka:
  brokers: kafka.prod:9092
streams:
  events:
    topic: prod.events
"""
            (infra_dir / "dev.infra").write_text(dev_content)
            (infra_dir / "prod.infra").write_text(prod_content)

            output_dir = Path(tmpdir) / "output"

            # Compile with prod environment
            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
                environment="prod",
            )

            result = compiler.compile()

            assert result.success
            assert result.infra_config.kafka.brokers == "kafka.prod:9092"
            assert result.infra_config.streams["events"].topic == "prod.events"


class TestMasterCompilerPhases:
    """Tests for compilation phases."""

    def test_all_phases_executed(self):
        """Test that all compilation phases are executed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
            )

            result = compiler.compile()

            # All phases should have results
            assert CompilationPhase.INFRA in result.layers
            assert CompilationPhase.SCHEMA in result.layers
            assert CompilationPhase.TRANSFORM in result.layers
            assert CompilationPhase.RULES in result.layers
            assert CompilationPhase.FLOW in result.layers

    def test_infra_phase_failure_stops_compilation(self):
        """Test that infrastructure failure stops compilation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            infra_dir = src_dir / "infra"
            infra_dir.mkdir(parents=True)

            # Create invalid .infra file
            invalid_content = """
# Missing kafka config with streams defined
streams:
  events:
    topic: events
"""
            (infra_dir / "dev.infra").write_text(invalid_content)

            output_dir = Path(tmpdir) / "output"

            compiler = MasterCompiler(
                src_dir=src_dir,
                output_dir=output_dir,
                package_prefix="com.test.flow",
            )

            result = compiler.compile()

            # Should fail at infra phase
            assert not result.success
            assert len(result.errors) > 0
            assert any("kafka" in e.lower() for e in result.errors)


class TestLayerResult:
    """Tests for LayerResult dataclass."""

    def test_layer_result_creation(self):
        """Test creating a layer result."""
        result = LayerResult(phase=CompilationPhase.SCHEMA)

        assert result.phase == CompilationPhase.SCHEMA
        assert result.success is True
        assert result.files_parsed == 0
        assert result.files_generated == 0
        assert len(result.errors) == 0

    def test_layer_result_with_errors(self):
        """Test layer result with errors."""
        result = LayerResult(
            phase=CompilationPhase.FLOW,
            success=False,
            errors=["Error 1", "Error 2"]
        )

        assert not result.success
        assert len(result.errors) == 2


class TestCompilationResult:
    """Tests for CompilationResult dataclass."""

    def test_add_layer_result_success(self):
        """Test adding successful layer result."""
        result = CompilationResult()

        layer = LayerResult(
            phase=CompilationPhase.SCHEMA,
            files_parsed=3,
            files_generated=3,
        )

        result.add_layer_result(layer)

        assert result.success
        assert CompilationPhase.SCHEMA in result.layers
        assert result.total_files_generated == 3

    def test_add_layer_result_failure(self):
        """Test adding failed layer result."""
        result = CompilationResult()

        layer = LayerResult(
            phase=CompilationPhase.TRANSFORM,
            success=False,
            errors=["Parse error"],
        )

        result.add_layer_result(layer)

        assert not result.success
        assert "Parse error" in result.errors
