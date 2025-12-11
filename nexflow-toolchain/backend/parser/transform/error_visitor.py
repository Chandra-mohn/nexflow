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
        for stmt_ctx in ctx.errorStatement():
            action = self.visitErrorStatement(stmt_ctx)
            if action:
                actions.append(action)
        return ast.OnErrorBlock(
            actions=actions,
            location=self._get_location(ctx)
        )

    def visitErrorStatement(self, ctx: TransformDSLParser.ErrorStatementContext) -> ast.ErrorAction:
        """Visit error statement - can be errorAction, logErrorCall, emitStatement, or rejectStatement."""
        if ctx.errorAction():
            return self.visitErrorAction(ctx.errorAction())
        elif ctx.logErrorCall():
            return self.visitLogErrorCall(ctx.logErrorCall())
        elif ctx.emitStatement():
            return self.visitEmitStatement(ctx.emitStatement())
        elif ctx.rejectStatement():
            return self.visitRejectStatement(ctx.rejectStatement())
        return None

    def visitLogErrorCall(self, ctx: TransformDSLParser.LogErrorCallContext) -> ast.ErrorAction:
        """Visit log_error('message') call."""
        message = self._strip_quotes(ctx.STRING().getText()) if ctx.STRING() else ""
        return ast.ErrorAction(
            action_type=ast.ErrorActionType.LOG_ERROR,
            error_message=message,
            location=self._get_location(ctx)
        )

    def visitEmitStatement(self, ctx: TransformDSLParser.EmitStatementContext) -> ast.ErrorAction:
        """Visit emit with defaults/partial statement."""
        emit_mode = self._get_text(ctx.emitMode()).lower() if ctx.emitMode() else "defaults"
        return ast.ErrorAction(
            action_type=ast.ErrorActionType.EMIT,
            emit_mode=emit_mode,
            location=self._get_location(ctx)
        )

    def visitRejectStatement(self, ctx: TransformDSLParser.RejectStatementContext) -> ast.ErrorAction:
        """Visit reject with code/message statement."""
        reject_arg = ctx.rejectArg()
        error_code = None
        error_message = None
        if reject_arg:
            text = self._get_text(reject_arg)
            if 'code' in text.lower():
                error_code = self._strip_quotes(reject_arg.STRING().getText()) if reject_arg.STRING() else ""
            else:
                error_message = self._strip_quotes(reject_arg.STRING().getText()) if reject_arg.STRING() else ""
        return ast.ErrorAction(
            action_type=ast.ErrorActionType.REJECT,
            error_code=error_code,
            error_message=error_message,
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
