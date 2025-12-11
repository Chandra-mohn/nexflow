"""
Unit tests for Flow DSL Parser.
Tests validate correct parsing of L1 Flow DSL syntax.
"""

import pytest

from backend.parser import parse


class TestFlowParserBasic:
    """Basic flow parsing tests."""

    def test_simple_process(self):
        """Test parsing a simple process definition."""
        dsl = """
        process simple_flow
            mode stream

            receive orders from kafka_orders
                schema order

            emit to processed_orders
                schema order
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast is not None
        assert len(result.ast.processes) == 1
        assert result.ast.processes[0].name == 'simple_flow'


class TestFlowParserTransform:
    """Flow transform operations tests."""

    def test_transform_reference(self):
        """Test parsing transform reference in flow."""
        dsl = """
        process with_transform
            mode stream

            receive input_data from kafka_input
                schema input_schema

            transform using normalize_data

            emit to output_data
                schema output_schema
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserRouting:
    """Flow routing operations tests."""

    def test_route_with_rules(self):
        """Test parsing route with rules reference."""
        dsl = """
        process with_routing
            mode stream

            receive incoming_events from kafka_events
                schema event

            route using event_router

            emit to high_priority_output
                schema event
            emit to normal_output
                schema event
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserEnrich:
    """Flow enrichment operations tests."""

    def test_enrich_with_lookup(self):
        """Test parsing enrich with lookup."""
        dsl = """
        process with_enrichment
            mode stream

            receive orders from kafka_orders
                schema order

            enrich using customer_lookup
                on customer_id
                select name, email, tier

            emit to enriched_orders
                schema enriched_order
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserWindow:
    """Flow windowing operations tests."""

    def test_tumbling_window(self):
        """Test parsing tumbling window."""
        dsl = """
        process windowed_aggregation
            mode stream

            receive raw_events from kafka_events
                schema event

            window tumbling 1 minute

            emit to aggregated_events
                schema aggregated_event
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserState:
    """Flow state management tests."""

    def test_state_configuration(self):
        """Test parsing state configuration."""
        dsl = """
        process stateful_flow
            mode stream

            receive transactions from kafka_transactions
                schema transaction

            emit to processed_transactions
                schema processed_transaction

            state
                uses customer_state
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserErrorHandling:
    """Flow error handling tests."""

    def test_error_handling_config(self):
        """Test parsing error handling configuration."""
        dsl = """
        process with_error_handling
            mode stream

            receive messages from kafka_messages
                schema message

            emit to processed_messages
                schema message

            on error
                transform_error dead_letter dlq_transforms
            end
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserParallelism:
    """Flow parallelism tests."""

    def test_parallelism_hint(self):
        """Test parsing parallelism hint."""
        dsl = """
        process parallel_flow
            parallelism hint 4
            mode stream

            receive high_volume_events from kafka_events
                schema event

            emit to processed_events
                schema event
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"


class TestFlowParserErrors:
    """Flow parser error handling tests."""

    def test_invalid_syntax(self):
        """Test that invalid syntax produces errors."""
        dsl = """
        process broken {
            from input
        }
        """
        result = parse(dsl, 'flow')
        assert not result.success


class TestFlowParserMultiple:
    """Multiple flow parsing tests."""

    def test_multiple_processes(self):
        """Test parsing multiple process definitions."""
        dsl = """
        process first_flow
            mode stream

            receive input_a from kafka_a
                schema type_a

            emit to output_a
                schema type_a
        end

        process second_flow
            mode stream

            receive input_b from kafka_b
                schema type_b

            emit to output_b
                schema type_b
        end
        """
        result = parse(dsl, 'flow')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.processes) == 2
