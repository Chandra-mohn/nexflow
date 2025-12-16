# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
State Block Visitor Mixin for Proc Parser

Handles parsing of state declarations: uses, local state, buffers,
TTL configuration, and cleanup strategies.
"""

from typing import Optional, Tuple

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcStateVisitorMixin:
    """Mixin for state block visitor methods."""

    def visitStateBlock(self, ctx: ProcDSLParser.StateBlockContext) -> ast.StateBlock:
        uses = []
        locals_list = []
        buffers = []

        for decl_ctx in ctx.stateDecl():
            if decl_ctx.usesDecl():
                uses.append(self.visitUsesDecl(decl_ctx.usesDecl()))
            elif decl_ctx.localDecl():
                locals_list.append(self.visitLocalDecl(decl_ctx.localDecl()))
            elif decl_ctx.bufferDecl():
                buffers.append(self.visitBufferDecl(decl_ctx.bufferDecl()))

        return ast.StateBlock(
            uses=uses,
            locals=locals_list,
            buffers=buffers,
            location=self._get_location(ctx)
        )

    def visitUsesDecl(self, ctx: ProcDSLParser.UsesDeclContext) -> ast.UsesDecl:
        state_name = ctx.IDENTIFIER().getText()
        return ast.UsesDecl(
            state_name=state_name,
            location=self._get_location(ctx)
        )

    def visitLocalDecl(self, ctx: ProcDSLParser.LocalDeclContext) -> ast.LocalDecl:
        name = ctx.IDENTIFIER().getText()
        keyed_by = self._get_field_list(ctx.fieldList())
        state_type = self.visitStateType(ctx.stateType())

        ttl = None
        if ctx.ttlDecl():
            ttl = self.visitTtlDecl(ctx.ttlDecl())

        cleanup = None
        if ctx.cleanupDecl():
            cleanup = self.visitCleanupDecl(ctx.cleanupDecl())

        return ast.LocalDecl(
            name=name,
            keyed_by=keyed_by,
            state_type=state_type,
            ttl=ttl,
            cleanup=cleanup,
            location=self._get_location(ctx)
        )

    def visitStateType(self, ctx: ProcDSLParser.StateTypeContext) -> ast.StateType:
        type_text = self._get_text(ctx).lower()
        if 'counter' in type_text:
            return ast.StateType.COUNTER
        elif 'gauge' in type_text:
            return ast.StateType.GAUGE
        elif 'map' in type_text:
            return ast.StateType.MAP
        elif 'list' in type_text:
            return ast.StateType.LIST
        return ast.StateType.MAP

    def visitTtlDecl(self, ctx: ProcDSLParser.TtlDeclContext) -> ast.TtlDecl:
        duration = self.visitDuration(ctx.duration())

        ttl_type = ast.TtlType.SLIDING
        if ctx.ttlType():
            ttl_type = self.visitTtlType(ctx.ttlType())

        return ast.TtlDecl(
            duration=duration,
            ttl_type=ttl_type,
            location=self._get_location(ctx)
        )

    def visitTtlType(self, ctx: ProcDSLParser.TtlTypeContext) -> ast.TtlType:
        type_text = self._get_text(ctx).lower()
        if 'absolute' in type_text:
            return ast.TtlType.ABSOLUTE
        return ast.TtlType.SLIDING

    def visitCleanupDecl(self, ctx: ProcDSLParser.CleanupDeclContext) -> ast.CleanupDecl:
        strategy = self.visitCleanupStrategy(ctx.cleanupStrategy())
        return ast.CleanupDecl(
            strategy=strategy,
            location=self._get_location(ctx)
        )

    def visitCleanupStrategy(self, ctx: ProcDSLParser.CleanupStrategyContext) -> ast.CleanupStrategy:
        strategy_text = self._get_text(ctx).lower()
        if 'on_access' in strategy_text:
            return ast.CleanupStrategy.ON_ACCESS
        elif 'background' in strategy_text:
            return ast.CleanupStrategy.BACKGROUND
        return ast.CleanupStrategy.ON_CHECKPOINT

    def visitBufferDecl(self, ctx: ProcDSLParser.BufferDeclContext) -> ast.BufferDecl:
        name = ctx.IDENTIFIER().getText()
        keyed_by = self._get_field_list(ctx.fieldList())
        buffer_type, priority_field = self.visitBufferType(ctx.bufferType())

        ttl = None
        if ctx.ttlDecl():
            ttl = self.visitTtlDecl(ctx.ttlDecl())

        return ast.BufferDecl(
            name=name,
            keyed_by=keyed_by,
            buffer_type=buffer_type,
            priority_field=priority_field,
            ttl=ttl,
            location=self._get_location(ctx)
        )

    def visitBufferType(self, ctx: ProcDSLParser.BufferTypeContext) -> Tuple[ast.BufferType, Optional[ast.FieldPath]]:
        type_text = self._get_text(ctx).lower()
        priority_field = None

        if 'priority' in type_text:
            buffer_type = ast.BufferType.PRIORITY
            if ctx.fieldPath():
                priority_field = self.visitFieldPath(ctx.fieldPath())
        elif 'lifo' in type_text:
            buffer_type = ast.BufferType.LIFO
        else:
            buffer_type = ast.BufferType.FIFO

        return buffer_type, priority_field
