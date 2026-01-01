# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Output and Completion Block Visitor Mixin for Proc Parser

Handles parsing of output declarations (emit) and completion
callbacks (on_commit, on_commit_failure).

Updated for grammar v0.5.0+ which uses emitDecl directly in bodyContent
instead of a separate outputBlock.
"""


from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcOutputVisitorMixin:
    """Mixin for output and completion block visitor methods."""

    # =========================================================================
    # Emit Declaration (v0.5.0+ - direct in bodyContent)
    # =========================================================================

    def visitEmitDecl(self, ctx: ProcDSLParser.EmitDeclContext) -> ast.EmitDecl:
        """
        Visit an emit declaration.

        Grammar: EMIT TO sinkName emitClause*
        sinkName: keywordOrIdentifier
        emitClause: schemaDecl | connectorClause | emitOptions | fanoutDecl | persistClause
        """
        # Grammar: emitDecl: EMIT TO sinkName emitClause*
        # sinkName: keywordOrIdentifier
        target = ctx.sinkName().getText()

        schema = None
        fanout = None
        persist = None
        connector = None
        options = {}

        # Process clauses in any order
        for clause_ctx in ctx.emitClause():
            if clause_ctx.schemaDecl():
                schema = self.visitSchemaDecl(clause_ctx.schemaDecl())
            elif clause_ctx.fanoutDecl():
                fanout = self.visitFanoutDecl(clause_ctx.fanoutDecl())
            elif clause_ctx.persistClause():
                persist = self.visitPersistClause(clause_ctx.persistClause())
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
            persist=persist,
            options=options if options else None,
            location=self._get_location(ctx)
        )

    def visitPersistClause(self, ctx: ProcDSLParser.PersistClauseContext) -> ast.PersistDecl:
        """
        Visit a persist clause for MongoDB async persistence.

        Grammar: PERSIST TO persistTarget persistOption*
        persistTarget: IDENTIFIER
        persistOption: ASYNC | SYNC | BATCH SIZE INTEGER | FLUSH INTERVAL duration | ON ERROR persistErrorAction
        """
        target = ctx.persistTarget().getText()

        # Defaults
        mode = ast.PersistMode.ASYNC
        batch_size = None
        flush_interval = None
        error_handler = None

        # Process options
        for opt_ctx in ctx.persistOption():
            opt_text = self._get_text(opt_ctx).lower().strip()

            # Check for ASYNC/SYNC using exact match (not substring)
            if opt_text == 'async':
                mode = ast.PersistMode.ASYNC
            elif opt_text == 'sync':
                mode = ast.PersistMode.SYNC
            elif 'batch' in opt_text and opt_ctx.INTEGER():
                batch_size = int(opt_ctx.INTEGER().getText())
            elif 'flush' in opt_text and opt_ctx.duration():
                flush_interval = self._get_text(opt_ctx.duration())
            elif 'error' in opt_text and opt_ctx.persistErrorAction():
                error_handler = self.visitPersistErrorAction(opt_ctx.persistErrorAction())

        return ast.PersistDecl(
            target=target,
            mode=mode,
            batch_size=batch_size,
            flush_interval=flush_interval,
            error_handler=error_handler,
            location=self._get_location(ctx)
        )

    def visitPersistErrorAction(self, ctx: ProcDSLParser.PersistErrorActionContext) -> ast.PersistErrorHandler:
        """
        Visit persist error action.

        Grammar: CONTINUE | FAIL | EMIT TO sinkName
        """
        action_text = self._get_text(ctx).lower()

        if 'emit' in action_text:
            # EMIT TO sinkName - get the DLQ target
            dlq_target = ctx.sinkName().getText() if ctx.sinkName() else None
            return ast.PersistErrorHandler(
                action=ast.PersistErrorAction.EMIT,
                dlq_target=dlq_target,
                location=self._get_location(ctx)
            )
        elif 'fail' in action_text:
            return ast.PersistErrorHandler(
                action=ast.PersistErrorAction.FAIL,
                location=self._get_location(ctx)
            )
        else:
            # Default: continue
            return ast.PersistErrorHandler(
                action=ast.PersistErrorAction.CONTINUE,
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
