# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Processing Block Visitor Mixin for Proc Parser

Handles parsing of processing operations: enrich, transform, route,
aggregate, window, join, and merge declarations.
"""

from typing import Optional, Union

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcProcessingVisitorMixin:
    """Mixin for processing block visitor methods."""

    def _get_identifier_text(self, identifier, index=0):
        """Safely get text from an IDENTIFIER which may be a list or single token."""
        if identifier is None:
            return ""
        if isinstance(identifier, list):
            return identifier[index].getText() if len(identifier) > index else ""
        return identifier.getText()

    def visitProcessingBlock(self, ctx: ProcDSLParser.ProcessingBlockContext) -> Union[
        ast.EnrichDecl, ast.TransformDecl, ast.RouteDecl, ast.AggregateDecl,
        ast.WindowDecl, ast.JoinDecl, ast.MergeDecl, ast.EvaluateDecl,
        ast.TransitionDecl, ast.EmitAuditDecl, ast.DeduplicateDecl,
        ast.LookupDecl, ast.BranchDecl, ast.ParallelDecl, ast.ValidateInputDecl,
        ast.CallDecl, ast.ScheduleDecl, ast.SetDecl,
        ast.SqlTransformDecl
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
        # Additional statement types
        elif ctx.evaluateStatement():
            return self.visitEvaluateStatement(ctx.evaluateStatement())
        elif ctx.transitionStatement():
            return self.visitTransitionStatement(ctx.transitionStatement())
        elif ctx.emitAuditStatement():
            return self.visitEmitAuditStatement(ctx.emitAuditStatement())
        elif ctx.deduplicateStatement():
            return self.visitDeduplicateStatement(ctx.deduplicateStatement())
        elif ctx.lookupStatement():
            return self.visitLookupStatement(ctx.lookupStatement())
        elif ctx.branchStatement():
            return self.visitBranchStatement(ctx.branchStatement())
        elif ctx.parallelStatement():
            return self.visitParallelStatement(ctx.parallelStatement())
        elif ctx.validateInputStatement():
            return self.visitValidateInputStatement(ctx.validateInputStatement())
        elif ctx.callStatement():
            return self.visitCallStatement(ctx.callStatement())
        elif ctx.scheduleStatement():
            return self.visitScheduleStatement(ctx.scheduleStatement())
        elif ctx.setStatement():
            return self.visitSetStatement(ctx.setStatement())
        # v0.8.0+: SQL statement
        elif hasattr(ctx, 'sqlStatement') and ctx.sqlStatement():
            return self.visitSqlStatement(ctx.sqlStatement())
        return None

    def visitEnrichDecl(self, ctx: ProcDSLParser.EnrichDeclContext) -> ast.EnrichDecl:
        lookup_name = self._get_identifier_text(ctx.IDENTIFIER())
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
        transform_name = self._get_identifier_text(ctx.IDENTIFIER())

        # Parse on_success block if present
        on_success = []
        if hasattr(ctx, 'onSuccessBlock') and ctx.onSuccessBlock():
            success_block = ctx.onSuccessBlock()
            if hasattr(success_block, 'actionContent') and success_block.actionContent():
                action_content = success_block.actionContent()
                on_success = self._parse_action_content(action_content)

        # Parse on_failure block if present
        on_failure = []
        if hasattr(ctx, 'onFailureBlock') and ctx.onFailureBlock():
            failure_block = ctx.onFailureBlock()
            if hasattr(failure_block, 'actionContent') and failure_block.actionContent():
                action_content = failure_block.actionContent()
                on_failure = self._parse_action_content(action_content)

        return ast.TransformDecl(
            transform_name=transform_name,
            on_success=on_success if on_success else None,
            on_failure=on_failure if on_failure else None,
            location=self._get_location(ctx)
        )

    def _parse_action_content(self, action_content) -> list:
        """Parse actionContent which contains processingStatement, emitDecl, CONTINUE, TERMINATE."""
        result = []

        # processingStatement*
        if hasattr(action_content, 'processingStatement'):
            stmts = action_content.processingStatement()
            if stmts:
                stmts = stmts if isinstance(stmts, list) else [stmts]
                for stmt in stmts:
                    parsed = self.visitProcessingStatement(stmt)
                    if parsed:
                        result.append(parsed)

        # emitDecl*
        if hasattr(action_content, 'emitDecl'):
            emits = action_content.emitDecl()
            if emits:
                emits = emits if isinstance(emits, list) else [emits]
                for emit in emits:
                    parsed = self.visitEmitDecl(emit) if hasattr(self, 'visitEmitDecl') else None
                    if parsed:
                        result.append(parsed)

        return result

    def visitRouteDecl(self, ctx: ProcDSLParser.RouteDeclContext) -> ast.RouteDecl:
        # Grammar: routeDecl: ROUTE (USING routeSource | WHEN expression) ...
        # routeSource: fieldPath  (e.g., simple_approval or result.decision)
        rule_name = None
        condition = None
        if ctx.routeSource():
            # 'route using <rule_name>' form
            rule_name = ctx.routeSource().getText()
        elif ctx.expression():
            # 'route when <condition>' form - capture expression as string
            condition = ctx.expression().getText()
        return ast.RouteDecl(
            rule_name=rule_name,
            condition=condition,
            location=self._get_location(ctx)
        )

    def visitAggregateDecl(self, ctx: ProcDSLParser.AggregateDeclContext) -> ast.AggregateDecl:
        transform_name = self._get_identifier_text(ctx.IDENTIFIER())
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
        """
        Visit a window declaration.

        Grammar v0.5.0+: WINDOW windowType duration windowBody?
        windowBody: keyByClause? inlineAggregateBlock? stateClause? windowOptions?
        """
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

        # v0.5.0+: windowOptions is now inside windowBody
        options = None
        key_by = None
        if ctx.windowBody():
            body_ctx = ctx.windowBody()
            if body_ctx.keyByClause():
                key_by = self._get_text(body_ctx.keyByClause().fieldPath())
            if body_ctx.windowOptions():
                options = self.visitWindowOptions(body_ctx.windowOptions())

        return ast.WindowDecl(
            window_type=window_type,
            size=size,
            slide=slide,
            key_by=key_by,
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

    # =========================================================================
    # Additional Statement Visitors
    # =========================================================================

    def visitEvaluateStatement(self, ctx) -> ast.EvaluateDecl:
        """Visit evaluate statement."""
        expression = self._get_text(ctx.expression()) if hasattr(ctx, 'expression') and ctx.expression() else ""
        return ast.EvaluateDecl(
            expression=expression,
            location=self._get_location(ctx)
        )

    def visitTransitionStatement(self, ctx) -> ast.TransitionDecl:
        """Visit transition statement."""
        target_state = ctx.STRING().getText().strip('"\'') if ctx.STRING() else ""
        return ast.TransitionDecl(
            target_state=target_state,
            location=self._get_location(ctx)
        )

    def visitEmitAuditStatement(self, ctx) -> ast.EmitAuditDecl:
        """Visit emit_audit_event statement."""
        event_name = ctx.STRING().getText().strip('"\'') if ctx.STRING() else ""
        return ast.EmitAuditDecl(
            event_name=event_name,
            location=self._get_location(ctx)
        )

    def visitDeduplicateStatement(self, ctx) -> ast.DeduplicateDecl:
        """Visit deduplicate statement."""
        key_field = self._get_text(ctx.fieldPath()) if hasattr(ctx, 'fieldPath') and ctx.fieldPath() else ""
        return ast.DeduplicateDecl(
            key_field=key_field,
            location=self._get_location(ctx)
        )

    def visitLookupStatement(self, ctx) -> ast.LookupDecl:
        """Visit lookup statement."""
        source_name = self._get_identifier_text(ctx.IDENTIFIER()) if ctx.IDENTIFIER() else ""
        return ast.LookupDecl(
            source_name=source_name,
            location=self._get_location(ctx)
        )

    def visitBranchStatement(self, ctx) -> ast.BranchDecl:
        """Visit branch statement with nested body."""
        branch_name = self._get_identifier_text(ctx.IDENTIFIER())

        # Parse branch body - contains processingStatement and emitDecl
        body = []
        if hasattr(ctx, 'branchBody') and ctx.branchBody():
            branch_body = ctx.branchBody()
            # processingStatement*
            if hasattr(branch_body, 'processingStatement'):
                stmts = branch_body.processingStatement()
                if stmts:
                    stmts = stmts if isinstance(stmts, list) else [stmts]
                    for stmt in stmts:
                        parsed = self.visitProcessingStatement(stmt)
                        if parsed:
                            body.append(parsed)
            # emitDecl*
            if hasattr(branch_body, 'emitDecl'):
                emits = branch_body.emitDecl()
                if emits:
                    emits = emits if isinstance(emits, list) else [emits]
                    for emit in emits:
                        parsed = self.visitEmitDecl(emit)
                        if parsed:
                            body.append(parsed)

        return ast.BranchDecl(
            branch_name=branch_name,
            body=body,
            location=self._get_location(ctx)
        )

    def visitParallelStatement(self, ctx) -> ast.ParallelDecl:
        """Visit parallel statement with branches."""
        name = self._get_identifier_text(ctx.IDENTIFIER())

        # Parse parallel branches
        branches = []
        if hasattr(ctx, 'parallelBranch'):
            branch_list = ctx.parallelBranch()
            if branch_list:
                branch_list = branch_list if isinstance(branch_list, list) else [branch_list]
                for branch_ctx in branch_list:
                    branch_name = self._get_identifier_text(branch_ctx.IDENTIFIER())
                    branch_body = []

                    # Parse branch body
                    if hasattr(branch_ctx, 'branchBody') and branch_ctx.branchBody():
                        bb = branch_ctx.branchBody()
                        if hasattr(bb, 'processingStatement'):
                            stmts = bb.processingStatement()
                            if stmts:
                                stmts = stmts if isinstance(stmts, list) else [stmts]
                                for stmt in stmts:
                                    parsed = self.visitProcessingStatement(stmt)
                                    if parsed:
                                        branch_body.append(parsed)
                        if hasattr(bb, 'emitDecl'):
                            emits = bb.emitDecl()
                            if emits:
                                emits = emits if isinstance(emits, list) else [emits]
                                for emit in emits:
                                    parsed = self.visitEmitDecl(emit)
                                    if parsed:
                                        branch_body.append(parsed)

                    branches.append(ast.BranchDecl(
                        branch_name=branch_name,
                        body=branch_body,
                        location=self._get_location(branch_ctx)
                    ))

        return ast.ParallelDecl(
            name=name,
            branches=branches,
            location=self._get_location(ctx)
        )

    def visitProcessingStatement(self, ctx):
        """Visit a processing statement - delegating to specific handlers."""
        # Check each possible statement type
        if hasattr(ctx, 'transformDecl') and ctx.transformDecl():
            return self.visitTransformDecl(ctx.transformDecl())
        elif hasattr(ctx, 'evaluateStatement') and ctx.evaluateStatement():
            return self.visitEvaluateStatement(ctx.evaluateStatement())
        elif hasattr(ctx, 'routeDecl') and ctx.routeDecl():
            return self.visitRouteDecl(ctx.routeDecl())
        elif hasattr(ctx, 'transitionStatement') and ctx.transitionStatement():
            return self.visitTransitionStatement(ctx.transitionStatement())
        elif hasattr(ctx, 'emitAuditStatement') and ctx.emitAuditStatement():
            return self.visitEmitAuditStatement(ctx.emitAuditStatement())
        elif hasattr(ctx, 'branchStatement') and ctx.branchStatement():
            return self.visitBranchStatement(ctx.branchStatement())
        elif hasattr(ctx, 'parallelStatement') and ctx.parallelStatement():
            return self.visitParallelStatement(ctx.parallelStatement())
        elif hasattr(ctx, 'lookupStatement') and ctx.lookupStatement():
            return self.visitLookupStatement(ctx.lookupStatement())
        elif hasattr(ctx, 'callStatement') and ctx.callStatement():
            return self.visitCallStatement(ctx.callStatement())
        elif hasattr(ctx, 'scheduleStatement') and ctx.scheduleStatement():
            return self.visitScheduleStatement(ctx.scheduleStatement())
        elif hasattr(ctx, 'setStatement') and ctx.setStatement():
            return self.visitSetStatement(ctx.setStatement())
        elif hasattr(ctx, 'validateInputStatement') and ctx.validateInputStatement():
            return self.visitValidateInputStatement(ctx.validateInputStatement())
        elif hasattr(ctx, 'deduplicateStatement') and ctx.deduplicateStatement():
            return self.visitDeduplicateStatement(ctx.deduplicateStatement())
        elif hasattr(ctx, 'windowDecl') and ctx.windowDecl():
            return self.visitWindowDecl(ctx.windowDecl())
        elif hasattr(ctx, 'joinDecl') and ctx.joinDecl():
            return self.visitJoinDecl(ctx.joinDecl())
        elif hasattr(ctx, 'mergeDecl') and ctx.mergeDecl():
            return self.visitMergeDecl(ctx.mergeDecl())
        elif hasattr(ctx, 'enrichDecl') and ctx.enrichDecl():
            return self.visitEnrichDecl(ctx.enrichDecl())
        elif hasattr(ctx, 'aggregateDecl') and ctx.aggregateDecl():
            return self.visitAggregateDecl(ctx.aggregateDecl())
        return None

    def visitValidateInputStatement(self, ctx) -> ast.ValidateInputDecl:
        """Visit validate_input statement."""
        expression = self._get_text(ctx.expression()) if hasattr(ctx, 'expression') and ctx.expression() else ""
        return ast.ValidateInputDecl(
            expression=expression,
            location=self._get_location(ctx)
        )

    def visitCallStatement(self, ctx) -> ast.CallDecl:
        """Visit call statement."""
        target = self._get_identifier_text(ctx.IDENTIFIER())
        return ast.CallDecl(
            target=target,
            location=self._get_location(ctx)
        )

    def visitScheduleStatement(self, ctx) -> ast.ScheduleDecl:
        """Visit schedule statement.

        Grammar: SCHEDULE IDENTIFIER AFTER scheduleDuration ACTION IDENTIFIER (REPEAT UNTIL expression)?
        """
        target = self._get_identifier_text(ctx.IDENTIFIER()) if ctx.IDENTIFIER() else ""
        delay = None
        if hasattr(ctx, 'scheduleDuration') and ctx.scheduleDuration():
            delay = self.visitScheduleDuration(ctx.scheduleDuration())
        elif hasattr(ctx, 'duration') and ctx.duration():
            delay = self.visitDuration(ctx.duration())
        return ast.ScheduleDecl(
            delay=delay,
            target=target,
            location=self._get_location(ctx)
        )

    def visitSetStatement(self, ctx) -> ast.SetDecl:
        """Visit set statement: SET fieldPath ASSIGN expression."""
        variable = ""
        if hasattr(ctx, 'fieldPath') and ctx.fieldPath():
            variable = self._get_text(ctx.fieldPath())
        value = ""
        if hasattr(ctx, 'expression') and ctx.expression():
            value = self._get_text(ctx.expression())
        return ast.SetDecl(
            variable=variable,
            value=value,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # v0.8.0+ Statement Visitors
    # =========================================================================

    def visitSqlStatement(self, ctx) -> ast.SqlTransformDecl:
        """Visit SQL statement: SQL SQL_BLOCK (AS IDENTIFIER)?

        Example:
            sql ```
                SELECT region, SUM(amount) as total
                FROM sales
                GROUP BY region
            ```
            as SalesSummary
        """
        sql_content = ""
        if hasattr(ctx, 'SQL_BLOCK') and ctx.SQL_BLOCK():
            # Extract SQL content from triple-backtick block
            raw_block = ctx.SQL_BLOCK().getText()
            # Remove the surrounding ``` markers
            sql_content = raw_block[3:-3].strip()

        output_type = None
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            output_type = self._get_identifier_text(ctx.IDENTIFIER())

        return ast.SqlTransformDecl(
            sql_content=sql_content,
            output_type=output_type,
            location=self._get_location(ctx)
        )
