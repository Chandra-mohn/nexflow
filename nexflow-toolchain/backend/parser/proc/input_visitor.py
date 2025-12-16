# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Input Block Visitor Mixin for Proc Parser

Handles parsing of input declarations: receive statements, schema references,
projections, store actions, and match actions.

Updated for grammar v0.5.0+ which uses flexible clause ordering.
"""

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcInputVisitorMixin:
    """Mixin for input block visitor methods."""

    def visitReceiveDecl(self, ctx: ProcDSLParser.ReceiveDeclContext) -> ast.ReceiveDecl:
        """
        Visit a receive declaration.

        Grammar: RECEIVE IDENTIFIER (FROM IDENTIFIER)? receiveClause*

        The first IDENTIFIER is the alias, the optional second is an inline source reference.
        Clauses (schema, connector, project, action, filter) can appear in any order.
        """
        identifiers = ctx.IDENTIFIER()

        # First identifier is always the alias
        alias = identifiers[0].getText() if identifiers else None

        # Second identifier (if present) is inline source: "receive X from Y"
        source = identifiers[1].getText() if len(identifiers) > 1 else None

        # Process clauses in any order
        schema = None
        project = None
        store_action = None
        match_action = None
        connector_source = None
        filter_expr = None

        for clause_ctx in ctx.receiveClause():
            if clause_ctx.schemaDecl():
                schema = self.visitSchemaDecl(clause_ctx.schemaDecl())
            elif clause_ctx.projectClause():
                project = self.visitProjectClause(clause_ctx.projectClause())
            elif clause_ctx.receiveAction():
                action_ctx = clause_ctx.receiveAction()
                if action_ctx.storeAction():
                    store_action = self.visitStoreAction(action_ctx.storeAction())
                elif action_ctx.matchAction():
                    match_action = self.visitMatchAction(action_ctx.matchAction())
            elif clause_ctx.connectorClause():
                # Extract source from connector clause if not already set
                connector_ctx = clause_ctx.connectorClause()
                if connector_ctx.connectorConfig():
                    config = connector_ctx.connectorConfig()
                    # Get first string or identifier from config
                    if config.STRING():
                        connector_source = config.STRING(0).getText().strip('"')
                    elif config.IDENTIFIER():
                        connector_source = config.IDENTIFIER(0).getText()
            # Filter clause handled separately if needed

        # Use inline source or connector source
        final_source = source or connector_source or alias

        return ast.ReceiveDecl(
            source=final_source,
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
