"""
Unit tests for route condition compilation.
Tests the _compile_route_condition method in JobOperatorsMixin.
"""

import pytest

from backend.generators.flow.job_operators import JobOperatorsMixin


class TestRouteConditionCompilation:
    """Tests for route condition to Java compilation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mixin = JobOperatorsMixin()

    def test_simple_numeric_comparison(self):
        """Test simple numeric comparisons."""
        result = self.mixin._compile_route_condition("amount > 1000")
        assert "amount()" in result  # Record-style accessor
        assert "> 1000" in result

    def test_numeric_greater_equal(self):
        """Test >= comparison."""
        result = self.mixin._compile_route_condition("risk_score >= 0.8")
        assert "riskScore()" in result  # Record-style accessor
        assert ">= 0.8" in result

    def test_and_operator(self):
        """Test 'and' converts to '&&'."""
        result = self.mixin._compile_route_condition("amount > 1000 and risk_score >= 0.8")
        assert "&&" in result
        assert "amount()" in result  # Record-style accessor
        assert "riskScore()" in result  # Record-style accessor

    def test_or_operator(self):
        """Test 'or' converts to '||'."""
        result = self.mixin._compile_route_condition("status == \"blocked\" or risk_score > 0.9")
        assert "||" in result

    def test_not_operator(self):
        """Test 'not' converts to '!'."""
        result = self.mixin._compile_route_condition("not is_blocked")
        assert "!" in result
        assert "isBlocked()" in result  # Record-style accessor

    def test_string_equality(self):
        """Test string equality uses .equals()."""
        result = self.mixin._compile_route_condition('status == "active"')
        assert '"active".equals(' in result
        assert "status()" in result  # Record-style accessor

    def test_string_not_equal(self):
        """Test string inequality uses !.equals()."""
        result = self.mixin._compile_route_condition('status != "blocked"')
        assert '!"blocked".equals(' in result
        assert "status()" in result  # Record-style accessor

    def test_nested_field_path(self):
        """Test nested field paths like customer.status."""
        result = self.mixin._compile_route_condition("customer.status == \"vip\"")
        assert "customer().status()" in result  # Record-style accessor chain
        assert '"vip".equals(' in result

    def test_complex_condition(self):
        """Test complex condition with multiple operators."""
        condition = 'amount > 10000 and customer.tier == "premium" or risk_score >= 0.9'
        result = self.mixin._compile_route_condition(condition)
        assert "&&" in result
        assert "||" in result
        assert "amount()" in result  # Record-style accessor
        assert "customer().tier()" in result  # Record-style accessor chain
        assert "riskScore()" in result  # Record-style accessor

    def test_true_literal(self):
        """Test 'true' literal is preserved."""
        result = self.mixin._compile_route_condition("true")
        assert result == "true"

    def test_false_literal(self):
        """Test 'false' literal is preserved."""
        result = self.mixin._compile_route_condition("false")
        assert result == "false"

    def test_empty_condition(self):
        """Test empty condition returns true."""
        result = self.mixin._compile_route_condition("")
        assert result == "true"

    def test_none_condition(self):
        """Test None condition returns true."""
        result = self.mixin._compile_route_condition(None)
        assert result == "true"
