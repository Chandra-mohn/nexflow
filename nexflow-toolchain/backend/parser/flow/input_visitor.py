"""
Input Block Visitor Mixin for Flow Parser

Handles parsing of input declarations: receive statements, schema references,
projections, store actions, and match actions.
"""

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowInputVisitorMixin:
    """Mixin for input block visitor methods."""

    def visitInputBlock(self, ctx: ProcDSLParser.InputBlockContext) -> ast.InputBlock:
        receives = []
        for recv_ctx in ctx.receiveDecl():
            receives.append(self.visitReceiveDecl(recv_ctx))
        return ast.InputBlock(
            receives=receives,
            location=self._get_location(ctx)
        )

    def visitReceiveDecl(self, ctx: ProcDSLParser.ReceiveDeclContext) -> ast.ReceiveDecl:
        identifiers = ctx.IDENTIFIER()

        if len(identifiers) == 2:
            alias = identifiers[0].getText()
            source = identifiers[1].getText()
        else:
            alias = None
            source = identifiers[0].getText()

        schema = None
        if ctx.schemaDecl():
            schema = self.visitSchemaDecl(ctx.schemaDecl())

        project = None
        if ctx.projectClause():
            project = self.visitProjectClause(ctx.projectClause())

        store_action = None
        match_action = None
        if ctx.receiveAction():
            action_ctx = ctx.receiveAction()
            if action_ctx.storeAction():
                store_action = self.visitStoreAction(action_ctx.storeAction())
            elif action_ctx.matchAction():
                match_action = self.visitMatchAction(action_ctx.matchAction())

        return ast.ReceiveDecl(
            source=source,
            alias=alias,
            schema=schema,
            project=project,
            store_action=store_action,
            match_action=match_action,
            location=self._get_location(ctx)
        )

    def visitSchemaDecl(self, ctx: ProcDSLParser.SchemaDeclContext) -> ast.SchemaDecl:
        schema_name = ctx.IDENTIFIER().getText()
        return ast.SchemaDecl(
            schema_name=schema_name,
            location=self._get_location(ctx)
        )

    def visitProjectClause(self, ctx: ProcDSLParser.ProjectClauseContext) -> ast.ProjectClause:
        fields = self._get_field_list(ctx.fieldList())
        is_except = any(
            self._get_text(child) == 'except'
            for child in ctx.getChildren()
        )
        return ast.ProjectClause(
            fields=fields,
            is_except=is_except,
            location=self._get_location(ctx)
        )

    def visitStoreAction(self, ctx: ProcDSLParser.StoreActionContext) -> ast.StoreAction:
        state_name = ctx.IDENTIFIER().getText()
        return ast.StoreAction(
            state_name=state_name,
            location=self._get_location(ctx)
        )

    def visitMatchAction(self, ctx: ProcDSLParser.MatchActionContext) -> ast.MatchAction:
        state_name = ctx.IDENTIFIER().getText()
        on_fields = self._get_field_list(ctx.fieldList())
        return ast.MatchAction(
            state_name=state_name,
            on_fields=on_fields,
            location=self._get_location(ctx)
        )
