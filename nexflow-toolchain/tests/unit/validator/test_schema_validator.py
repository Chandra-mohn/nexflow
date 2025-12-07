"""
Unit tests for Schema Validator.
"""

import pytest

from backend.parser import parse
from backend.validators import SchemaValidator, ValidationContext


class TestSchemaValidatorBasic:
    """Basic schema validation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()
        self.validator = SchemaValidator(self.context)

    def test_valid_schema(self):
        """Test validation passes for valid schema."""
        dsl = """
        schema valid_user
            fields
                id: integer required
                name: string required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        validation = self.validator.validate(result.ast)
        assert validation.success, f"Validation failed: {validation.errors}"


class TestSchemaValidatorVersion:
    """Schema version validation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()
        self.validator = SchemaValidator(self.context)

    def test_valid_semver(self):
        """Test validation passes for valid semver."""
        dsl = """
        schema versioned
            version 1.2.3
                compatibility backward
                previous_version 1.0.0

            fields
                id: integer required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        validation = self.validator.validate(result.ast)
        assert validation.success, f"Validation failed: {validation.errors}"


class TestSchemaValidatorStreaming:
    """Schema streaming validation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()
        self.validator = SchemaValidator(self.context)

    def test_valid_streaming_config(self):
        """Test validation passes for valid streaming config."""
        dsl = """
        schema event_stream
            identity
                event_id: uuid required
            end

            streaming
                key_fields: [event_id]
                time_field: created_at
            end

            fields
                created_at: timestamp required
                data: string required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        validation = self.validator.validate(result.ast)
        assert validation.success, f"Validation failed: {validation.errors}"


class TestSchemaValidatorStateMachine:
    """Schema state machine validation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()
        self.validator = SchemaValidator(self.context)

    def test_valid_state_machine(self):
        """Test validation passes for valid state machine."""
        dsl = """
        schema stateful_order
            fields
                status: string required
            end

            for_entity: status
            states: [pending, approved, rejected]
            initial_state: pending
            transitions
                from pending: [approved, rejected]
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        validation = self.validator.validate(result.ast)
        # State machine validation might produce warnings but should pass
        assert not validation.has_errors(), f"Errors: {validation.errors}"


class TestSchemaValidatorRegistration:
    """Schema registration tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()
        self.validator = SchemaValidator(self.context)

    def test_schema_registration(self):
        """Test that validated schemas are registered in context."""
        dsl = """
        schema registered_schema
            fields
                id: integer required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        self.validator.validate(result.ast)

        # Schema should be registered in context
        assert self.context.has_schema('registered_schema')

    def test_multiple_schemas_registered(self):
        """Test that multiple schemas are all registered."""
        dsl = """
        schema first_schema
            fields
                id: integer required
            end
        end

        schema second_schema
            fields
                id: integer required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        self.validator.validate(result.ast)

        assert self.context.has_schema('first_schema')
        assert self.context.has_schema('second_schema')
