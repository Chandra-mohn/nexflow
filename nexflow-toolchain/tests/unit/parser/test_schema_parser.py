"""
Unit tests for Schema DSL Parser.
"""

import pytest

from backend.parser import parse


class TestSchemaParserBasic:
    """Basic schema parsing tests."""

    def test_simple_schema(self):
        """Test parsing a simple schema definition."""
        dsl = """
        schema user
            fields
                id: integer required
                name: string required
                email: string optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast is not None
        assert len(result.ast.schemas) == 1
        assert result.ast.schemas[0].name == 'user'

    def test_schema_with_version(self):
        """Test parsing schema with version block."""
        dsl = """
        schema product
            version 1.0.0
                compatibility backward
                previous_version 0.9.0

            fields
                sku: string required
                price: decimal required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast.schemas[0].version is not None
        assert result.ast.schemas[0].version.version == '1.0.0'

    def test_schema_with_identity(self):
        """Test parsing schema with identity block."""
        dsl = """
        schema order
            identity
                order_id: uuid required
                customer_id: string required
            end

            fields
                total: decimal required
                status: string required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast.schemas[0].identity is not None
        assert len(result.ast.schemas[0].identity.fields) == 2


class TestSchemaParserTypes:
    """Schema field type parsing tests."""

    def test_basic_types(self):
        """Test parsing basic field types."""
        dsl = """
        schema types_test
            fields
                int_field: integer required
                str_field: string required
                bool_field: boolean required
                dec_field: decimal required
                ts_field: timestamp required
                uuid_field: uuid required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        fields_block = result.ast.schemas[0].fields
        assert len(fields_block.fields) == 6

    def test_constrained_types(self):
        """Test parsing constrained field types."""
        dsl = """
        schema constrained_test
            fields
                price: decimal[precision: 10, scale: 2] required
                code: string[length: 10] required
                score: integer[range: 0..100] required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

    def test_collection_types(self):
        """Test parsing collection field types."""
        dsl = """
        schema collection_test
            fields
                tags: list<string> optional
                scores: list<integer> optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"


class TestSchemaParserStreaming:
    """Schema streaming configuration tests."""

    def test_streaming_block(self):
        """Test parsing streaming configuration."""
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
                event_type: string required
                created_at: timestamp required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast.schemas[0].streaming is not None


class TestSchemaParserStateMachine:
    """Schema state machine tests."""

    def test_state_machine(self):
        """Test parsing state machine configuration."""
        dsl = """
        schema order_with_state
            fields
                status: string required
            end

            for_entity: status
            states: [pending, approved, rejected, fulfilled]
            initial_state: pending
            transitions
                from pending: [approved, rejected]
                from approved: [fulfilled]
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        sm = result.ast.schemas[0].state_machine
        assert sm is not None
        assert len(sm.states) == 4


class TestSchemaParserErrors:
    """Schema parser error handling tests."""

    def test_invalid_syntax(self):
        """Test that invalid syntax produces errors."""
        dsl = """
        schema invalid
            fields
                name: string required
            // missing 'end' keyword
        end
        """
        result = parse(dsl, 'schema')
        assert not result.success

    def test_empty_schema(self):
        """Test parsing empty schema."""
        dsl = """
        schema empty
        end
        """
        result = parse(dsl, 'schema')
        # Empty schema should parse but may produce warnings
        assert result.success


class TestSchemaParserMultiple:
    """Multiple schema parsing tests."""

    def test_multiple_schemas(self):
        """Test parsing multiple schema definitions in one file."""
        dsl = """
        schema user
            fields
                id: integer required
                name: string required
            end
        end

        schema profile
            fields
                user_id: integer required
                bio: string optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.schemas) == 2
        assert result.ast.schemas[0].name == 'user'
        assert result.ast.schemas[1].name == 'profile'
