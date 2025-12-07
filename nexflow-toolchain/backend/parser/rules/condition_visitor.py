"""
Condition Visitor Mixin for Rules Parser

Handles parsing of condition types: range, set, pattern, null, comparison, expression.
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesConditionVisitorMixin:
    """Mixin for condition visitor methods."""

    def visitCondition(self, ctx: RulesDSLParser.ConditionContext) -> ast.Condition:
        if ctx.STAR():
            return ast.WildcardCondition(location=self._get_location(ctx))
        elif ctx.exactMatch():
            literal = self.visitLiteral(ctx.exactMatch().literal())
            return ast.ExactMatchCondition(value=literal, location=self._get_location(ctx))
        elif ctx.rangeCondition():
            return self.visitRangeCondition(ctx.rangeCondition())
        elif ctx.setCondition():
            return self.visitSetCondition(ctx.setCondition())
        elif ctx.patternCondition():
            return self.visitPatternCondition(ctx.patternCondition())
        elif ctx.nullCondition():
            return self.visitNullCondition(ctx.nullCondition())
        elif ctx.comparisonCondition():
            return self.visitComparisonCondition(ctx.comparisonCondition())
        elif ctx.expressionCondition():
            return self.visitExpressionCondition(ctx.expressionCondition())

        return ast.WildcardCondition(location=self._get_location(ctx))

    def visitRangeCondition(self, ctx: RulesDSLParser.RangeConditionContext) -> ast.RangeCondition:
        if ctx.numberLiteral():
            nums = ctx.numberLiteral()
            min_val = self.visitNumberLiteral(nums[0])
            max_val = self.visitNumberLiteral(nums[1])
        elif ctx.MONEY_LITERAL():
            moneys = ctx.MONEY_LITERAL()
            min_val = self._parse_money(moneys[0].getText())
            max_val = self._parse_money(moneys[1].getText())
        else:
            return ast.RangeCondition(
                min_value=ast.IntegerLiteral(0),
                max_value=ast.IntegerLiteral(0),
                location=self._get_location(ctx)
            )

        return ast.RangeCondition(
            min_value=min_val,
            max_value=max_val,
            location=self._get_location(ctx)
        )

    def visitSetCondition(self, ctx: RulesDSLParser.SetConditionContext) -> ast.SetCondition:
        values = []
        if ctx.valueList():
            for val_ctx in ctx.valueList().valueExpr():
                values.append(self.visitValueExpr(val_ctx))

        negated = ctx.NOT() is not None

        return ast.SetCondition(
            values=values,
            negated=negated,
            location=self._get_location(ctx)
        )

    def visitPatternCondition(self, ctx: RulesDSLParser.PatternConditionContext) -> ast.PatternCondition:
        string_lit = ctx.stringLiteral()
        if string_lit.DQUOTED_STRING():
            pattern = self._strip_quotes(string_lit.DQUOTED_STRING().getText())
        else:
            pattern = self._strip_quotes(string_lit.SQUOTED_STRING().getText())

        if ctx.MATCHES():
            match_type = ast.PatternMatchType.MATCHES
        elif ctx.ENDS_WITH():
            match_type = ast.PatternMatchType.ENDS_WITH
        elif ctx.STARTS_WITH():
            match_type = ast.PatternMatchType.STARTS_WITH
        elif ctx.CONTAINS():
            match_type = ast.PatternMatchType.CONTAINS
        else:
            match_type = ast.PatternMatchType.MATCHES

        return ast.PatternCondition(
            match_type=match_type,
            pattern=pattern,
            location=self._get_location(ctx)
        )

    def visitNullCondition(self, ctx: RulesDSLParser.NullConditionContext) -> ast.NullCondition:
        is_null = ctx.IS_NULL() is not None or \
                  (ctx.IS() is not None and ctx.NULL() is not None and ctx.NOT() is None)

        return ast.NullCondition(
            is_null=is_null,
            location=self._get_location(ctx)
        )

    def visitComparisonCondition(self, ctx: RulesDSLParser.ComparisonConditionContext) -> ast.ComparisonCondition:
        op = self.visitComparisonOp(ctx.comparisonOp())
        value = self.visitValueExpr(ctx.valueExpr())

        return ast.ComparisonCondition(
            operator=op,
            value=value,
            location=self._get_location(ctx)
        )

    def visitExpressionCondition(self, ctx: RulesDSLParser.ExpressionConditionContext) -> ast.ExpressionCondition:
        expr = self.visitBooleanExpr(ctx.booleanExpr())
        return ast.ExpressionCondition(
            expression=expr,
            location=self._get_location(ctx)
        )
