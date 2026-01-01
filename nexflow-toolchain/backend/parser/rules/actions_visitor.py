# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Actions Visitor Mixin for Rules Parser

Handles parsing of actions block for action method declarations.
RFC REFERENCE: See docs/RFC-Method-Implementation-Strategy.md (Solution 5)
"""


from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesActionsVisitorMixin:
    """Mixin for actions block visitor methods."""

    def visitActionsBlock(self, ctx: RulesDSLParser.ActionsBlockContext) -> ast.ActionsBlock:
        """Parse actions { } block."""
        actions = []
        for action_ctx in ctx.actionDecl():
            actions.append(self.visitActionDecl(action_ctx))

        return ast.ActionsBlock(
            actions=actions,
            location=self._get_location(ctx)
        )

    def visitActionDecl(self, ctx: RulesDSLParser.ActionDeclContext) -> ast.ActionDecl:
        """Parse single action declaration."""
        name = self._get_text(ctx.actionDeclName())

        # Parse parameters
        params = []
        param_list_ctx = ctx.actionParamList()
        if param_list_ctx:
            for param_ctx in param_list_ctx.actionParam():
                params.append(self.visitActionDeclParam(param_ctx))

        # Parse target
        target_ctx = ctx.actionTarget()
        target_type, emit_target, state_target, audit_target, call_target = \
            self._parse_action_target(target_ctx)

        return ast.ActionDecl(
            name=name,
            params=params,
            target_type=target_type,
            emit_target=emit_target,
            state_target=state_target,
            audit_target=audit_target,
            call_target=call_target,
            location=self._get_location(ctx)
        )

    def visitActionDeclParam(self, ctx: RulesDSLParser.ActionParamContext) -> ast.ActionDeclParam:
        """Parse action parameter."""
        name = ctx.IDENTIFIER().getText()
        param_type = self._get_text(ctx.paramType())

        return ast.ActionDeclParam(
            name=name,
            param_type=param_type,
            location=self._get_location(ctx)
        )

    def _parse_action_target(self, ctx: RulesDSLParser.ActionTargetContext) -> tuple:
        """Parse action target (emit, state, audit, call).

        Returns:
            Tuple of (ActionTargetType, emit_target, state_target, audit_target, call_target)
        """
        emit_target = None
        state_target = None
        audit_target = None
        call_target = None

        emit_ctx = ctx.emitTarget()
        state_ctx = ctx.stateTarget()
        audit_ctx = ctx.auditTarget()
        call_ctx = ctx.callTarget()

        if emit_ctx:
            target_type = ast.ActionTargetType.EMIT
            output_name = emit_ctx.IDENTIFIER().getText()
            emit_target = ast.EmitTarget(
                output_name=output_name,
                location=self._get_location(emit_ctx)
            )
        elif state_ctx:
            target_type = ast.ActionTargetType.STATE
            state_name = state_ctx.IDENTIFIER().getText()
            operation = self._parse_state_operation(state_ctx.stateOperation())
            state_target = ast.StateTarget(
                state_name=state_name,
                operation=operation,
                location=self._get_location(state_ctx)
            )
        elif audit_ctx:
            target_type = ast.ActionTargetType.AUDIT
            audit_target = ast.AuditTarget(
                location=self._get_location(audit_ctx)
            )
        elif call_ctx:
            target_type = ast.ActionTargetType.CALL
            identifiers = call_ctx.IDENTIFIER()
            service_name = identifiers[0].getText()
            method_name = identifiers[1].getText()
            call_target = ast.CallTarget(
                service_name=service_name,
                method_name=method_name,
                location=self._get_location(call_ctx)
            )
        else:
            # Default to audit if no target specified
            target_type = ast.ActionTargetType.AUDIT
            audit_target = ast.AuditTarget(
                location=self._get_location(ctx)
            )

        return target_type, emit_target, state_target, audit_target, call_target

    def _parse_state_operation(self, ctx: RulesDSLParser.StateOperationContext) -> ast.StateOperation:
        """Parse state operation (e.g., add, add(flag))."""
        identifiers = ctx.IDENTIFIER()
        operation_name = identifiers[0].getText() if identifiers else "set"

        argument = None
        arg_ctx = ctx.stateOperationArg()
        if arg_ctx:
            if arg_ctx.IDENTIFIER():
                argument = arg_ctx.IDENTIFIER().getText()
            elif arg_ctx.DQUOTED_STRING():
                # Remove quotes
                argument = arg_ctx.DQUOTED_STRING().getText()[1:-1]

        return ast.StateOperation(
            operation_name=operation_name,
            argument=argument,
            location=self._get_location(ctx)
        )
