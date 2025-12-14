# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Unit tests for Transform DSL Parser.
Tests validate correct parsing of L3 Transform DSL syntax.
"""

import pytest

from backend.parser import parse


class TestTransformParserBasic:
    """Basic transform parsing tests."""

    def test_simple_transform(self):
        """Test parsing a simple transform definition."""
        dsl = """
        transform normalize_value
            input
                value: decimal, required
            end
            output
                result: decimal, required
            end
            apply
                result = value
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast is not None
        assert len(result.ast.transforms) == 1
        assert result.ast.transforms[0].name == 'normalize_value'

    def test_transform_with_multiple_inputs(self):
        """Test parsing transform with multiple input fields."""
        dsl = """
        transform calculate_total
            input
                price: decimal, required
                quantity: integer, required
            end
            output
                total: decimal, required
            end
            apply
                total = price * quantity
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast.transforms[0].input is not None

    def test_pure_transform(self):
        """Test parsing a pure transform."""
        dsl = """
        transform format_currency
            pure: true

            input
                amount: decimal, required
            end
            output
                formatted: string, required
            end
            apply
                formatted = amount
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"


class TestTransformBlockParser:
    """Transform block parsing tests."""

    def test_transform_block(self):
        """Test parsing a transform_block definition."""
        dsl = """
        transform_block enrich_customer
            version: 1.0.0
            description: "Enriches customer data"

            input
                customer_id: string, required
            end

            output
                enriched: string, required
            end

            mappings
                enriched.customer_id = customer_id
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.transform_blocks) == 1
        assert result.ast.transform_blocks[0].name == 'enrich_customer'


class TestTransformParserExpressions:
    """Transform expression parsing tests."""

    def test_arithmetic_expressions(self):
        """Test parsing arithmetic expressions."""
        dsl = """
        transform calculate
            input
                a: decimal, required
                b: decimal, required
            end
            output
                result: decimal, required
            end
            apply
                result = a + b
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"

    def test_function_calls(self):
        """Test parsing function calls in expressions."""
        dsl = """
        transform apply_rate
            input
                amount: decimal, required
                currency: string, required
            end
            output
                converted: decimal, required
            end
            apply
                rate = get_exchange_rate(currency, "USD")
                converted = amount * rate
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"

    def test_when_expressions(self):
        """Test parsing when (conditional) expressions."""
        dsl = """
        transform categorize
            input
                value: integer, required
            end
            output
                category: string, required
            end
            apply
                category = when value > 100: "high"
                    when value > 50: "medium"
                    otherwise: "low"
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"


class TestTransformParserValidation:
    """Transform validation block parsing tests."""

    def test_validate_input(self):
        """Test parsing input validation."""
        dsl = """
        transform safe_divide
            input
                numerator: decimal, required
                denominator: decimal, required
            end
            output
                result: decimal, required
            end

            validate_input
                denominator > 0: "Denominator must be positive"
            end

            apply
                result = numerator / denominator
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"


class TestTransformParserCache:
    """Transform cache configuration tests."""

    def test_cache_config(self):
        """Test parsing cache configuration."""
        dsl = """
        transform lookup_rate
            cache
                ttl: 1 hour
                key: [currency]
            end

            input
                currency: string, required
            end
            output
                rate: decimal, required
            end
            apply
                rate = get_rate(currency)
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"


class TestTransformParserErrors:
    """Transform parser error handling tests."""

    def test_invalid_syntax(self):
        """Test that invalid syntax produces errors."""
        dsl = """
        transform broken {
            input: string
        }
        """
        result = parse(dsl, 'transform')
        assert not result.success


class TestTransformParserMultiple:
    """Multiple transform parsing tests."""

    def test_multiple_transforms(self):
        """Test parsing multiple transform definitions."""
        dsl = """
        transform normalize_a
            input
                value: decimal, required
            end
            output
                result: decimal, required
            end
            apply
                result = value
            end
        end

        transform normalize_b
            input
                value: decimal, required
            end
            output
                result: decimal, required
            end
            apply
                result = value * 2
            end
        end
        """
        result = parse(dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.transforms) == 2
