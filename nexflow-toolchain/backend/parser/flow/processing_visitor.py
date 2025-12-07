"""
Processing Block Visitor Mixin for Flow Parser

Handles parsing of processing operations: enrich, transform, route,
aggregate, window, join, and merge declarations.
"""

from typing import Optional, Union

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowProcessingVisitorMixin:
    """Mixin for processing block visitor methods."""

    def visitProcessingBlock(self, ctx: ProcDSLParser.ProcessingBlockContext) -> Union[
        ast.EnrichDecl, ast.TransformDecl, ast.RouteDecl, ast.AggregateDecl,
        ast.WindowDecl, ast.JoinDecl, ast.MergeDecl
    ]:
        if ctx.enrichDecl():
            return self.visitEnrichDecl(ctx.enrichDecl())
        elif ctx.transformDecl():
            return self.visitTransformDecl(ctx.transformDecl())
        elif ctx.routeDecl():
            return self.visitRouteDecl(ctx.routeDecl())
        elif ctx.aggregateDecl():
            return self.visitAggregateDecl(ctx.aggregateDecl())
        elif ctx.windowDecl():
            return self.visitWindowDecl(ctx.windowDecl())
        elif ctx.joinDecl():
            return self.visitJoinDecl(ctx.joinDecl())
        elif ctx.mergeDecl():
            return self.visitMergeDecl(ctx.mergeDecl())
        return None

    def visitEnrichDecl(self, ctx: ProcDSLParser.EnrichDeclContext) -> ast.EnrichDecl:
        lookup_name = ctx.IDENTIFIER().getText()
        on_fields = self._get_field_list(ctx.fieldList())

        select_fields = None
        if ctx.selectClause():
            select_fields = self._get_field_list(ctx.selectClause().fieldList())

        return ast.EnrichDecl(
            lookup_name=lookup_name,
            on_fields=on_fields,
            select_fields=select_fields,
            location=self._get_location(ctx)
        )

    def visitTransformDecl(self, ctx: ProcDSLParser.TransformDeclContext) -> ast.TransformDecl:
        transform_name = ctx.IDENTIFIER().getText()
        return ast.TransformDecl(
            transform_name=transform_name,
            location=self._get_location(ctx)
        )

    def visitRouteDecl(self, ctx: ProcDSLParser.RouteDeclContext) -> ast.RouteDecl:
        rule_name = ctx.IDENTIFIER().getText()
        return ast.RouteDecl(
            rule_name=rule_name,
            location=self._get_location(ctx)
        )

    def visitAggregateDecl(self, ctx: ProcDSLParser.AggregateDeclContext) -> ast.AggregateDecl:
        transform_name = ctx.IDENTIFIER().getText()
        return ast.AggregateDecl(
            transform_name=transform_name,
            location=self._get_location(ctx)
        )

    def visitMergeDecl(self, ctx: ProcDSLParser.MergeDeclContext) -> ast.MergeDecl:
        identifiers = ctx.IDENTIFIER()
        streams = [ident.getText() for ident in identifiers]

        output_alias = None
        has_into = any(
            self._get_text(child) == 'into'
            for child in ctx.getChildren()
        )
        if has_into and len(streams) > 2:
            output_alias = streams[-1]
            streams = streams[:-1]

        return ast.MergeDecl(
            streams=streams,
            output_alias=output_alias,
            location=self._get_location(ctx)
        )

    def visitWindowDecl(self, ctx: ProcDSLParser.WindowDeclContext) -> ast.WindowDecl:
        window_type_ctx = ctx.windowType()
        duration_ctx = ctx.duration()

        window_type_text = self._get_text(window_type_ctx)
        if 'tumbling' in window_type_text:
            window_type = ast.WindowType.TUMBLING
            size = self.visitDuration(duration_ctx)
            slide = None
        elif 'sliding' in window_type_text:
            window_type = ast.WindowType.SLIDING
            if window_type_ctx.duration():
                slide = self.visitDuration(window_type_ctx.duration())
            else:
                slide = None
            size = self.visitDuration(duration_ctx)
        elif 'session' in window_type_text:
            window_type = ast.WindowType.SESSION
            size = self.visitDuration(duration_ctx)
            slide = None
        else:
            window_type = ast.WindowType.TUMBLING
            size = self.visitDuration(duration_ctx)
            slide = None

        options = None
        if ctx.windowOptions():
            options = self.visitWindowOptions(ctx.windowOptions())

        return ast.WindowDecl(
            window_type=window_type,
            size=size,
            slide=slide,
            options=options,
            location=self._get_location(ctx)
        )

    def visitWindowOptions(self, ctx: ProcDSLParser.WindowOptionsContext) -> ast.WindowOptions:
        lateness = None
        late_data = None

        if ctx.latenessDecl():
            lateness = self.visitLatenessDecl(ctx.latenessDecl())
        if ctx.lateDataDecl():
            late_data = self.visitLateDataDecl(ctx.lateDataDecl())

        return ast.WindowOptions(
            lateness=lateness,
            late_data=late_data
        )

    def visitJoinDecl(self, ctx: ProcDSLParser.JoinDeclContext) -> ast.JoinDecl:
        identifiers = ctx.IDENTIFIER()
        left = identifiers[0].getText()
        right = identifiers[1].getText()
        on_fields = self._get_field_list(ctx.fieldList())
        within = self.visitDuration(ctx.duration())

        join_type = ast.JoinType.INNER
        if ctx.joinType():
            join_type = self.visitJoinType(ctx.joinType())

        return ast.JoinDecl(
            left=left,
            right=right,
            on_fields=on_fields,
            within=within,
            join_type=join_type,
            location=self._get_location(ctx)
        )

    def visitJoinType(self, ctx: ProcDSLParser.JoinTypeContext) -> ast.JoinType:
        type_text = self._get_text(ctx).lower()
        if 'left' in type_text:
            return ast.JoinType.LEFT
        elif 'right' in type_text:
            return ast.JoinType.RIGHT
        elif 'outer' in type_text:
            return ast.JoinType.OUTER
        return ast.JoinType.INNER
