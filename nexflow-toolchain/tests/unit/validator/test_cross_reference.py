"""
Unit tests for cross-reference validation.
"""

import pytest

from backend.parser import parse
from backend.validators import (
    SchemaValidator, TransformValidator, FlowValidator,
    ValidationContext, validate_project_asts
)
from pathlib import Path


class TestCrossReferenceValidation:
    """Cross-reference validation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ValidationContext()

    def test_transform_registration(self):
        """Test that transforms are properly registered."""
        transform_dsl = """
        transform normalize_amount
            pure: true

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
        result = parse(transform_dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"

        transform_validator = TransformValidator(self.context)
        transform_validator.validate(result.ast)

        assert self.context.has_transform('normalize_amount')

    def test_schema_registration(self):
        """Test that schemas are properly registered."""
        schema_dsl = """
        schema transaction
            fields
                id: integer required
                amount: decimal required
            end
        end
        """
        result = parse(schema_dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        schema_validator = SchemaValidator(self.context)
        schema_validator.validate(result.ast)

        assert self.context.has_schema('transaction')


class TestValidationContext:
    """Validation context tests."""

    def test_context_isolation(self):
        """Test that each context is isolated."""
        context1 = ValidationContext()
        context2 = ValidationContext()

        context1.register_schema('test', {})
        assert context1.has_schema('test')
        assert not context2.has_schema('test')

    def test_all_registrations(self):
        """Test all registration types."""
        context = ValidationContext()

        context.register_schema('schema1', {})
        context.register_transform('transform1', {})
        context.register_rule('rule1', {})
        context.register_decision_table('table1', {})
        context.register_flow('flow1', {})

        assert context.has_schema('schema1')
        assert context.has_transform('transform1')
        assert context.has_rule('rule1')
        assert context.has_rule('table1')  # decision tables are also rules
        assert context.has_flow('flow1')


class TestValidateProjectAsts:
    """Integration tests for validate_project_asts."""

    def test_schema_only_validation(self):
        """Test validating just schemas."""
        schema_dsl = """
        schema order
            fields
                order_id: string required
                total: decimal required
            end
        end
        """

        result = parse(schema_dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        asts = {
            'schema': {Path('test.schema'): result.ast},
        }

        validation = validate_project_asts(asts)
        assert validation.success or validation.error_count == 0

    def test_transform_only_validation(self):
        """Test validating just transforms."""
        transform_dsl = """
        transform calculate_tax
            input
                amount: decimal, required
            end
            output
                tax: decimal, required
            end
            apply
                tax = amount
            end
        end
        """

        result = parse(transform_dsl, 'transform')
        assert result.success, f"Parse failed: {result.errors}"

        asts = {
            'transform': {Path('test.transform'): result.ast},
        }

        validation = validate_project_asts(asts)
        assert validation.success or validation.error_count == 0

    def test_rules_only_validation(self):
        """Test validating just rules."""
        # Use a procedural rule which has simpler syntax
        rules_dsl = """
        rule check_amount:
            if amount > 100 then
                apply_discount(0.10)
            endif
            return
        end
        """

        result = parse(rules_dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"

        asts = {
            'rules': {Path('test.rules'): result.ast},
        }

        validation = validate_project_asts(asts)
        assert validation.success or validation.error_count == 0

    def test_empty_asts(self):
        """Test validating empty ASTs."""
        asts = {}
        validation = validate_project_asts(asts)
        assert validation.success
