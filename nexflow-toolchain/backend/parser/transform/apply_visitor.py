"""
Apply Block Visitor Mixin for Transform Parser

Handles parsing of apply blocks, statements, assignments, mappings, and compose blocks.
"""

from typing import Union

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformApplyVisitorMixin:
    """Mixin for apply block and mappings visitor methods."""

    # =========================================================================
    # Apply Block
    # =========================================================================

    def visitApplyBlock(self, ctx: TransformDSLParser.ApplyBlockContext) -> ast.ApplyBlock:
        statements = []
        for stmt_ctx in ctx.statement():
            statements.append(self.visitStatement(stmt_ctx))
        return ast.ApplyBlock(
            statements=statements,
            location=self._get_location(ctx)
        )

    def visitStatement(self, ctx: TransformDSLParser.StatementContext) -> Union[ast.Assignment, ast.LocalAssignment]:
        if ctx.assignment():
            return self.visitAssignment(ctx.assignment())
        elif ctx.localAssignment():
            return self.visitLocalAssignment(ctx.localAssignment())
        return None

    def visitAssignment(self, ctx: TransformDSLParser.AssignmentContext) -> ast.Assignment:
        target = self.visitFieldPath(ctx.fieldPath())
        value = self.visitExpression(ctx.expression())
        return ast.Assignment(
            target=target,
            value=value,
            location=self._get_location(ctx)
        )

    def visitLocalAssignment(self, ctx: TransformDSLParser.LocalAssignmentContext) -> ast.LocalAssignment:
        name = ctx.IDENTIFIER().getText()
        value = self.visitExpression(ctx.expression())
        return ast.LocalAssignment(
            name=name,
            value=value,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Mappings Block
    # =========================================================================

    def visitMappingsBlock(self, ctx: TransformDSLParser.MappingsBlockContext) -> ast.MappingsBlock:
        mappings = []
        for mapping_ctx in ctx.mapping():
            mappings.append(self.visitMapping(mapping_ctx))
        return ast.MappingsBlock(
            mappings=mappings,
            location=self._get_location(ctx)
        )

    def visitMapping(self, ctx: TransformDSLParser.MappingContext) -> ast.Mapping:
        target = self.visitFieldPath(ctx.fieldPath())
        expression = self.visitExpression(ctx.expression())
        return ast.Mapping(
            target=target,
            expression=expression,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Compose Block
    # =========================================================================

    def visitComposeBlock(self, ctx: TransformDSLParser.ComposeBlockContext) -> ast.ComposeBlock:
        compose_type = None
        refs = []
        then_type = None
        then_refs = []

        if ctx.composeType():
            compose_type = self.visitComposeType(ctx.composeType())

        for ref_ctx in ctx.composeRef():
            refs.append(self.visitComposeRef(ref_ctx))

        if ctx.thenBlock():
            then_ctx = ctx.thenBlock()
            if then_ctx.composeType():
                then_type = self.visitComposeType(then_ctx.composeType())
            for ref_ctx in then_ctx.composeRef():
                then_refs.append(self.visitComposeRef(ref_ctx))

        return ast.ComposeBlock(
            compose_type=compose_type,
            refs=refs,
            then_type=then_type,
            then_refs=then_refs,
            location=self._get_location(ctx)
        )

    def visitComposeType(self, ctx: TransformDSLParser.ComposeTypeContext) -> ast.ComposeType:
        type_text = self._get_text(ctx).lower()
        type_map = {
            'sequential': ast.ComposeType.SEQUENTIAL,
            'parallel': ast.ComposeType.PARALLEL,
            'conditional': ast.ComposeType.CONDITIONAL,
        }
        return type_map.get(type_text, ast.ComposeType.SEQUENTIAL)

    def visitComposeRef(self, ctx: TransformDSLParser.ComposeRefContext) -> ast.ComposeRef:
        transform_name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else ""

        condition = None
        is_otherwise = False

        if ctx.expression():
            condition = self.visitExpression(ctx.expression())

        ctx_text = self._get_text(ctx)
        if 'otherwise' in ctx_text.lower():
            is_otherwise = True

        return ast.ComposeRef(
            transform_name=transform_name,
            condition=condition,
            is_otherwise=is_otherwise,
            location=self._get_location(ctx)
        )
