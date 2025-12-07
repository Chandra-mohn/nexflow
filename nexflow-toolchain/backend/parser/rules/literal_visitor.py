"""
Literal Visitor Mixin for Rules Parser

Handles parsing of literal values: strings, numbers, money, percentage, boolean, null.
"""

from typing import Union

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesLiteralVisitorMixin:
    """Mixin for literal visitor methods."""

    def visitLiteral(self, ctx: RulesDSLParser.LiteralContext) -> ast.Literal:
        if ctx.stringLiteral():
            string_lit = ctx.stringLiteral()
            if string_lit.DQUOTED_STRING():
                return ast.StringLiteral(
                    value=self._strip_quotes(string_lit.DQUOTED_STRING().getText()),
                    quote_type='"'
                )
            else:
                return ast.StringLiteral(
                    value=self._strip_quotes(string_lit.SQUOTED_STRING().getText()),
                    quote_type="'"
                )
        elif ctx.numberLiteral():
            return self.visitNumberLiteral(ctx.numberLiteral())
        elif ctx.MONEY_LITERAL():
            return self._parse_money(ctx.MONEY_LITERAL().getText())
        elif ctx.PERCENTAGE_LITERAL():
            text = ctx.PERCENTAGE_LITERAL().getText().rstrip('%')
            return ast.PercentageLiteral(value=float(text))
        elif ctx.BOOLEAN():
            text = ctx.BOOLEAN().getText().lower()
            return ast.BooleanLiteral(value=text in ('true', 'yes'))
        elif ctx.NULL():
            return ast.NullLiteral()

        return ast.NullLiteral()

    def visitNumberLiteral(self, ctx: RulesDSLParser.NumberLiteralContext) -> Union[ast.IntegerLiteral, ast.DecimalLiteral]:
        if ctx.INTEGER():
            return ast.IntegerLiteral(value=int(ctx.INTEGER().getText()))
        elif ctx.DECIMAL():
            return ast.DecimalLiteral(value=float(ctx.DECIMAL().getText()))
        return ast.IntegerLiteral(value=0)

    def visitListLiteral(self, ctx: RulesDSLParser.ListLiteralContext) -> ast.ListLiteral:
        values = []
        for val_ctx in ctx.valueExpr():
            values.append(self.visitValueExpr(val_ctx))
        return ast.ListLiteral(values=values)
