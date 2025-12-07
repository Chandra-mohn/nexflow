"""
Action Visitor Mixin for Rules Parser

Handles parsing of action types: assign, calculate, lookup, call, emit.
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesActionVisitorMixin:
    """Mixin for action visitor methods."""

    def visitAction(self, ctx: RulesDSLParser.ActionContext) -> ast.Action:
        if ctx.STAR():
            return ast.NoAction(location=self._get_location(ctx))
        elif ctx.assignAction():
            literal = self.visitLiteral(ctx.assignAction().literal())
            return ast.AssignAction(value=literal, location=self._get_location(ctx))
        elif ctx.calculateAction():
            expr = self.visitValueExpr(ctx.calculateAction().arithmeticExpr().valueExpr())
            return ast.CalculateAction(expression=expr, location=self._get_location(ctx))
        elif ctx.lookupAction():
            return self.visitLookupAction(ctx.lookupAction())
        elif ctx.callAction():
            return self.visitCallAction(ctx.callAction())
        elif ctx.emitAction():
            return self.visitEmitAction(ctx.emitAction())

        return ast.NoAction(location=self._get_location(ctx))

    def visitLookupAction(self, ctx: RulesDSLParser.LookupActionContext) -> ast.LookupAction:
        table_name = ctx.IDENTIFIER()[0].getText()
        keys = []
        default_value = None
        as_of = None

        if ctx.AS_OF():
            as_of = self.visitValueExpr(ctx.valueExpr()[0])
        else:
            value_exprs = ctx.valueExpr()
            for i, val_ctx in enumerate(value_exprs):
                if ctx.DEFAULT() and i == len(value_exprs) - 1:
                    default_value = self.visitValueExpr(val_ctx)
                else:
                    keys.append(self.visitValueExpr(val_ctx))

        return ast.LookupAction(
            table_name=table_name,
            keys=keys,
            default_value=default_value,
            as_of=as_of,
            location=self._get_location(ctx)
        )

    def visitCallAction(self, ctx: RulesDSLParser.CallActionContext) -> ast.CallAction:
        func_name = ctx.IDENTIFIER().getText()
        arguments = []

        if ctx.actionArg():
            for arg_ctx in ctx.actionArg():
                arguments.append(self.visitActionArg(arg_ctx))

        return ast.CallAction(
            function_name=func_name,
            arguments=arguments,
            location=self._get_location(ctx)
        )

    def visitActionArg(self, ctx: RulesDSLParser.ActionArgContext) -> ast.ActionArg:
        value = self.visitValueExpr(ctx.valueExpr())
        name = None
        if ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()

        return ast.ActionArg(value=value, name=name, location=self._get_location(ctx))

    def visitEmitAction(self, ctx: RulesDSLParser.EmitActionContext) -> ast.EmitAction:
        target = ctx.IDENTIFIER().getText()
        return ast.EmitAction(target=target, location=self._get_location(ctx))
