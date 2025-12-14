# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
State Machine Visitor Mixin

Handles parsing of state machine blocks: states, transitions, and actions.
Updated for grammar v0.5.0+ with intuitive state and transition syntax.
"""

from typing import List, Optional

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class StateMachineVisitorMixin:
    """Mixin for state machine visitor methods."""

    def visitStateMachineBlock(self, ctx: SchemaDSLParser.StateMachineBlockContext) -> ast.StateMachineBlock:
        for_entity = None
        if ctx.forEntityDecl():
            for_entity = ctx.forEntityDecl().IDENTIFIER().getText()

        states = []
        initial_state = None
        terminal_states = []

        # v0.5.0+: statesBlock replaces statesDecl
        if ctx.statesBlock():
            states, initial_state, terminal_states = self.visitStatesBlock(ctx.statesBlock())

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
            terminal_states=terminal_states,
            location=self._get_location(ctx)
        )

    def visitStatesBlock(self, ctx: SchemaDSLParser.StatesBlockContext) -> tuple:
        """Visit states block - supports both compact and intuitive syntax."""
        states = []
        initial_state = None
        terminal_states = []

        # Compact syntax: states: [s1, s2, s3]
        if ctx.statesDecl() and ctx.statesDecl().stateArray():
            for ident in ctx.statesDecl().stateArray().IDENTIFIER():
                states.append(ident.getText())

        # Intuitive syntax: individual state definitions
        if ctx.stateDefList():
            for state_def in ctx.stateDefList().stateDef():
                state_name = state_def.IDENTIFIER().getText()
                states.append(state_name)

                # Check for qualifier (initial, terminal, final)
                if state_def.stateQualifier():
                    qualifier = self._get_text(state_def.stateQualifier())
                    if qualifier == 'initial':
                        initial_state = state_name
                    elif qualifier in ('terminal', 'final'):
                        terminal_states.append(state_name)

        return states, initial_state, terminal_states

    def visitTransitionsBlock(self, ctx: SchemaDSLParser.TransitionsBlockContext) -> List[ast.TransitionDecl]:
        """Visit transitions block - supports both original and arrow syntax."""
        transitions = []

        # Original syntax: from state: [target1, target2]
        if ctx.transitionDecl():
            for trans_ctx in ctx.transitionDecl():
                transitions.append(self.visitTransitionDecl(trans_ctx))

        # Arrow syntax: state -> state: trigger
        if ctx.transitionArrowDecl():
            for arrow_ctx in ctx.transitionArrowDecl():
                transitions.append(self.visitTransitionArrowDecl(arrow_ctx))

        return transitions

    def visitTransitionDecl(self, ctx: SchemaDSLParser.TransitionDeclContext) -> ast.TransitionDecl:
        """Original transition syntax: from state: [targets]"""
        from_state = ctx.IDENTIFIER().getText()
        to_states = [ident.getText() for ident in ctx.stateArray().IDENTIFIER()]
        return ast.TransitionDecl(
            from_state=from_state,
            to_states=to_states,
            location=self._get_location(ctx)
        )

    def visitTransitionArrowDecl(self, ctx: SchemaDSLParser.TransitionArrowDeclContext) -> ast.TransitionDecl:
        """Arrow transition syntax: from -> to: trigger"""
        identifiers = ctx.IDENTIFIER()

        # Handle wildcard (*) for from_state
        if ctx.getChild(0).getText() == '*':
            from_state = '*'
            to_state = identifiers[0].getText()
            trigger = identifiers[1].getText() if len(identifiers) > 1 else None
        else:
            from_state = identifiers[0].getText()
            to_state = identifiers[1].getText()
            trigger = identifiers[2].getText() if len(identifiers) > 2 else None

        return ast.TransitionDecl(
            from_state=from_state,
            to_states=[to_state],
            trigger=trigger,
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
        action_name = identifiers[0].getText() if identifiers else ""
        # Parameters come from STRING tokens now
        parameters = []
        if ctx.STRING():
            parameters = [s.getText().strip('"') for s in ctx.STRING()]
        return ast.ActionCall(
            action_name=action_name,
            parameters=parameters,
            location=self._get_location(ctx)
        )
