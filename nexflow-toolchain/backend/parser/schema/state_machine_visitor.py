"""
State Machine Visitor Mixin

Handles parsing of state machine blocks: states, transitions, and actions.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class StateMachineVisitorMixin:
    """Mixin for state machine visitor methods."""

    def visitStateMachineBlock(self, ctx: SchemaDSLParser.StateMachineBlockContext) -> ast.StateMachineBlock:
        for_entity = None
        if ctx.forEntityDecl():
            for_entity = ctx.forEntityDecl().IDENTIFIER().getText()

        states = []
        if ctx.statesDecl():
            states = self.visitStatesDecl(ctx.statesDecl())

        initial_state = None
        if ctx.initialStateDecl():
            initial_state = ctx.initialStateDecl().IDENTIFIER().getText()

        transitions = []
        if ctx.transitionsBlock():
            transitions = self.visitTransitionsBlock(ctx.transitionsBlock())

        on_transition_actions = []
        if ctx.onTransitionBlock():
            on_transition_actions = self.visitOnTransitionBlock(ctx.onTransitionBlock())

        return ast.StateMachineBlock(
            for_entity=for_entity,
            states=states,
            initial_state=initial_state,
            transitions=transitions,
            on_transition_actions=on_transition_actions,
            location=self._get_location(ctx)
        )

    def visitStatesDecl(self, ctx: SchemaDSLParser.StatesDeclContext) -> List[str]:
        states = []
        if ctx.stateArray():
            for ident in ctx.stateArray().IDENTIFIER():
                states.append(ident.getText())
        return states

    def visitTransitionsBlock(self, ctx: SchemaDSLParser.TransitionsBlockContext) -> List[ast.TransitionDecl]:
        transitions = []
        for trans_ctx in ctx.transitionDecl():
            transitions.append(self.visitTransitionDecl(trans_ctx))
        return transitions

    def visitTransitionDecl(self, ctx: SchemaDSLParser.TransitionDeclContext) -> ast.TransitionDecl:
        from_state = ctx.IDENTIFIER().getText()
        to_states = [ident.getText() for ident in ctx.stateArray().IDENTIFIER()]
        return ast.TransitionDecl(
            from_state=from_state,
            to_states=to_states,
            location=self._get_location(ctx)
        )

    def visitOnTransitionBlock(self, ctx: SchemaDSLParser.OnTransitionBlockContext) -> List[ast.TransitionAction]:
        actions = []
        for action_ctx in ctx.transitionAction():
            actions.append(self.visitTransitionAction(action_ctx))
        return actions

    def visitTransitionAction(self, ctx: SchemaDSLParser.TransitionActionContext) -> ast.TransitionAction:
        to_state = ctx.IDENTIFIER().getText()
        action = self.visitActionCall(ctx.actionCall())
        return ast.TransitionAction(
            to_state=to_state,
            action=action,
            location=self._get_location(ctx)
        )

    def visitActionCall(self, ctx: SchemaDSLParser.ActionCallContext) -> ast.ActionCall:
        identifiers = ctx.IDENTIFIER()
        action_name = identifiers[0].getText()
        parameters = [ident.getText() for ident in identifiers[1:]]
        return ast.ActionCall(
            action_name=action_name,
            parameters=parameters,
            location=self._get_location(ctx)
        )
