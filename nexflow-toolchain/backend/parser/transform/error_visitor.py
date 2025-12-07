"""
Error Handling Visitor Mixin for Transform Parser

Handles parsing of error handling blocks (on_error, on_change) and related actions.
"""

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformErrorVisitorMixin:
    """Mixin for error handling visitor methods."""

    def visitOnErrorBlock(self, ctx: TransformDSLParser.OnErrorBlockContext) -> ast.OnErrorBlock:
        actions = []
        for action_ctx in ctx.errorAction():
            actions.append(self.visitErrorAction(action_ctx))
        return ast.OnErrorBlock(
            actions=actions,
            location=self._get_location(ctx)
        )

    def visitErrorAction(self, ctx: TransformDSLParser.ErrorActionContext) -> ast.ErrorAction:
        action_type = None
        default_value = None
        log_level = None
        emit_to = None
        error_code = None

        if ctx.errorActionType():
            action_type = self.visitErrorActionType(ctx.errorActionType())

        if ctx.expression():
            default_value = self.visitExpression(ctx.expression())

        if ctx.logLevel():
            log_level = self.visitLogLevel(ctx.logLevel())

        if ctx.IDENTIFIER():
            emit_to = ctx.IDENTIFIER().getText()

        if ctx.STRING():
            error_code = self._strip_quotes(ctx.STRING().getText())

        return ast.ErrorAction(
            action_type=action_type,
            default_value=default_value,
            log_level=log_level,
            emit_to=emit_to,
            error_code=error_code,
            location=self._get_location(ctx)
        )

    def visitErrorActionType(self, ctx: TransformDSLParser.ErrorActionTypeContext) -> ast.ErrorActionType:
        action_text = self._get_text(ctx).lower()
        action_map = {
            'reject': ast.ErrorActionType.REJECT,
            'skip': ast.ErrorActionType.SKIP,
            'use_default': ast.ErrorActionType.USE_DEFAULT,
            'raise': ast.ErrorActionType.RAISE,
        }
        return action_map.get(action_text, ast.ErrorActionType.REJECT)

    def visitLogLevel(self, ctx: TransformDSLParser.LogLevelContext) -> ast.LogLevel:
        level_text = self._get_text(ctx).lower()
        level_map = {
            'error': ast.LogLevel.ERROR,
            'warning': ast.LogLevel.WARNING,
            'info': ast.LogLevel.INFO,
            'debug': ast.LogLevel.DEBUG,
        }
        return level_map.get(level_text, ast.LogLevel.ERROR)

    def visitOnChangeBlock(self, ctx: TransformDSLParser.OnChangeBlockContext) -> ast.OnChangeBlock:
        watched_fields = self._get_field_array(ctx.fieldArray())
        recalculate = self.visitRecalculateBlock(ctx.recalculateBlock())
        return ast.OnChangeBlock(
            watched_fields=watched_fields,
            recalculate=recalculate,
            location=self._get_location(ctx)
        )

    def visitRecalculateBlock(self, ctx: TransformDSLParser.RecalculateBlockContext) -> ast.RecalculateBlock:
        assignments = []
        for assign_ctx in ctx.assignment():
            assignments.append(self.visitAssignment(assign_ctx))
        return ast.RecalculateBlock(
            assignments=assignments,
            location=self._get_location(ctx)
        )
