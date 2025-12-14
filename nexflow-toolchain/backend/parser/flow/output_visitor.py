# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Output and Completion Block Visitor Mixin for Flow Parser

Handles parsing of output declarations (emit) and completion
callbacks (on_commit, on_commit_failure).

Updated for grammar v0.5.0+ which uses emitDecl directly in bodyContent
instead of a separate outputBlock.
"""

from typing import Union

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowOutputVisitorMixin:
    """Mixin for output and completion block visitor methods."""

    # =========================================================================
    # Emit Declaration (v0.5.0+ - direct in bodyContent)
    # =========================================================================

    def visitEmitDecl(self, ctx: ProcDSLParser.EmitDeclContext) -> ast.EmitDecl:
        """
        Visit an emit declaration.

        Grammar: EMIT TO sinkName emitClause*
        sinkName: keywordOrIdentifier
        emitClause: schemaDecl | connectorClause | emitOptions | fanoutDecl
        """
        # Grammar: emitDecl: EMIT TO sinkName emitClause*
        # sinkName: keywordOrIdentifier
        target = ctx.sinkName().getText()

        schema = None
        fanout = None
        connector = None
        options = {}

        # Process clauses in any order
        for clause_ctx in ctx.emitClause():
            if clause_ctx.schemaDecl():
                schema = self.visitSchemaDecl(clause_ctx.schemaDecl())
            elif clause_ctx.fanoutDecl():
                fanout = self.visitFanoutDecl(clause_ctx.fanoutDecl())
            elif clause_ctx.connectorClause():
                # Extract connector info if needed
                pass
            elif clause_ctx.emitOptions():
                # Process emit options (reason, preserve_state, etc.)
                opt_ctx = clause_ctx.emitOptions()
                opt_text = self._get_text(opt_ctx)
                if 'reason' in opt_text and opt_ctx.STRING():
                    options['reason'] = opt_ctx.STRING().getText().strip('"')

        return ast.EmitDecl(
            target=target,
            schema=schema,
            fanout=fanout,
            options=options if options else None,
            location=self._get_location(ctx)
        )

    def visitFanoutDecl(self, ctx: ProcDSLParser.FanoutDeclContext) -> ast.FanoutDecl:
        fanout_text = self._get_text(ctx)
        if 'broadcast' in fanout_text:
            strategy = ast.FanoutType.BROADCAST
        else:
            strategy = ast.FanoutType.ROUND_ROBIN
        return ast.FanoutDecl(
            strategy=strategy,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Completion Block
    # =========================================================================

    def visitCompletionBlock(self, ctx: ProcDSLParser.CompletionBlockContext) -> ast.CompletionBlock:
        on_commit = None
        on_commit_failure = None

        for decl_ctx in ctx.completionDecl():
            if decl_ctx.onCommitDecl():
                on_commit = self.visitOnCommitDecl(decl_ctx.onCommitDecl())
            elif decl_ctx.onCommitFailureDecl():
                on_commit_failure = self.visitOnCommitFailureDecl(decl_ctx.onCommitFailureDecl())

        return ast.CompletionBlock(
            on_commit=on_commit,
            on_commit_failure=on_commit_failure,
            location=self._get_location(ctx)
        )

    def visitOnCommitDecl(self, ctx: ProcDSLParser.OnCommitDeclContext) -> ast.OnCommitDecl:
        target = ctx.IDENTIFIER().getText()
        correlation = self.visitCorrelationDecl(ctx.correlationDecl())

        include = None
        if ctx.includeDecl():
            include = self.visitIncludeDecl(ctx.includeDecl())

        schema = None
        if ctx.schemaDecl():
            schema = self.visitSchemaDecl(ctx.schemaDecl())

        return ast.OnCommitDecl(
            target=target,
            correlation=correlation,
            include=include,
            schema=schema,
            location=self._get_location(ctx)
        )

    def visitOnCommitFailureDecl(self, ctx: ProcDSLParser.OnCommitFailureDeclContext) -> ast.OnCommitFailureDecl:
        target = ctx.IDENTIFIER().getText()
        correlation = self.visitCorrelationDecl(ctx.correlationDecl())

        include = None
        if ctx.includeDecl():
            include = self.visitIncludeDecl(ctx.includeDecl())

        schema = None
        if ctx.schemaDecl():
            schema = self.visitSchemaDecl(ctx.schemaDecl())

        return ast.OnCommitFailureDecl(
            target=target,
            correlation=correlation,
            include=include,
            schema=schema,
            location=self._get_location(ctx)
        )

    def visitCorrelationDecl(self, ctx: ProcDSLParser.CorrelationDeclContext) -> ast.CorrelationDecl:
        field_path = self.visitFieldPath(ctx.fieldPath())
        return ast.CorrelationDecl(
            field_path=field_path,
            location=self._get_location(ctx)
        )

    def visitIncludeDecl(self, ctx: ProcDSLParser.IncludeDeclContext) -> ast.IncludeDecl:
        fields = self._get_field_list(ctx.fieldList())
        return ast.IncludeDecl(
            fields=fields,
            location=self._get_location(ctx)
        )
