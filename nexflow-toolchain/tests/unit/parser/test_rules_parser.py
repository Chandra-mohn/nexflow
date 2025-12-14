# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Unit tests for Rules DSL Parser.
Tests validate correct parsing of L4 Rules DSL syntax.
"""

import pytest

from backend.parser import parse


class TestDecisionTableParser:
    """Decision table parsing tests."""

    def test_simple_decision_table(self):
        """Test parsing a simple decision table."""
        dsl = """
        decision_table risk_tier
            given:
                score: number

            decide:
                | score     | risk_tier   |
                |========================|
                | > 80      | "low"       |
                | < 50      | "high"      |
                | *         | "medium"    |

            return:
                risk_tier: text
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"
        assert result.ast is not None
        assert len(result.ast.decision_tables) == 1
        assert result.ast.decision_tables[0].name == 'risk_tier'

    def test_decision_table_with_description(self):
        """Test parsing decision table with description."""
        dsl = '''
        decision_table calculate_discount
            description "Determines discount based on customer tier"

            given:
                tier: text

            decide:
                | tier       | discount |
                |======================|
                | "gold"     | 0.20     |
                | "silver"   | 0.10     |
                | *          | 0.05     |

            return:
                discount: number
        end
        '''
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"

    def test_decision_table_with_hit_policy(self):
        """Test parsing decision table with hit policy."""
        dsl = """
        decision_table route_transaction
            hit_policy first_match

            given:
                amount: money
                risk: text

            decide:
                | amount   | risk     | route       |
                |================================|
                | > 10000  | "high"   | "manual"    |
                | > 10000  | *        | "review"    |
                | *        | "high"   | "review"    |
                | *        | *        | "auto"      |

            return:
                route: text
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"


class TestProceduralRuleParser:
    """Procedural rule parsing tests."""

    def test_simple_procedural_rule(self):
        """Test parsing a simple procedural rule."""
        dsl = """
        rule validate_transaction:
            if amount > 10000 then
                flag_for_review()
            endif
            return
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.procedural_rules) == 1
        assert result.ast.procedural_rules[0].name == 'validate_transaction'

    def test_procedural_rule_with_else(self):
        """Test parsing procedural rule with else block."""
        dsl = """
        rule categorize_amount:
            if amount > 1000 then
                set_category("large")
            else
                set_category("small")
            endif
            return
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"

    def test_procedural_rule_with_elseif(self):
        """Test parsing procedural rule with elseif branches."""
        dsl = """
        rule tier_assignment:
            if score >= 90 then
                set_tier("platinum")
            elseif score >= 70 then
                set_tier("gold")
            elseif score >= 50 then
                set_tier("silver")
            else
                set_tier("bronze")
            endif
            return
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"

    def test_nested_procedural_rule(self):
        """Test parsing nested procedural rules."""
        dsl = """
        rule complex_routing:
            if region == "US" then
                if amount > 5000 then
                    route_to("us_high_value")
                else
                    route_to("us_standard")
                endif
            else
                route_to("international")
            endif
            return
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"


class TestRulesParserErrors:
    """Rules parser error handling tests."""

    def test_invalid_syntax(self):
        """Test that invalid syntax produces errors."""
        dsl = """
        decision_table broken {
            x: integer
        }
        """
        result = parse(dsl, 'rules')
        assert not result.success


class TestRulesParserMixed:
    """Mixed rules parsing tests."""

    def test_decision_table_and_rule(self):
        """Test parsing decision table and procedural rule together."""
        dsl = """
        decision_table table_rule
            given:
                x: number

            decide:
                | x   | y   |
                |==========|
                | > 0 | 1   |
                | *   | 0   |

            return:
                y: number
        end

        rule proc_rule:
            if x > 0 then
                set_positive()
            endif
            return
        end
        """
        result = parse(dsl, 'rules')
        assert result.success, f"Parse failed: {result.errors}"
        assert len(result.ast.decision_tables) == 1
        assert len(result.ast.procedural_rules) == 1
