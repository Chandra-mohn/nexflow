# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
State Machine Generator Module

Generates Java state machine code from Schema AST definitions.
Supports state enums, transition validation, and action dispatch.
"""


from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator
from backend.generators.schema.statemachine_transitions import StateMachineTransitionsMixin


class StateMachineGeneratorMixin(StateMachineTransitionsMixin):
    """Mixin providing state machine code generation capabilities.

    Generates:
    - State enum with all valid states
    - Transition validation methods
    - State transition matrix
    - Action dispatch for on_transition
    """

    def _generate_state_machine_class(self: BaseGenerator,
                                       schema: ast.SchemaDefinition,
                                       class_name: str,
                                       package: str) -> str:
        """Generate state machine helper class.

        Returns complete Java class for state machine support.
        """
        if not schema.state_machine:
            return ""

        sm = schema.state_machine

        header = self.generate_java_header(
            f"{class_name}StateMachine",
            f"State machine implementation for {schema.name}"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'java.util.Set',
            'java.util.HashSet',
            'java.util.Map',
            'java.util.HashMap',
            'java.util.Collections',
            'java.util.Arrays',
            'java.util.function.Consumer',
        ])

        # Generate components
        state_enum = self._generate_state_enum(sm, class_name)
        transition_matrix = self._generate_transition_matrix(sm)
        validation_methods = self._generate_transition_validation_methods(sm, class_name)
        action_dispatch = self._generate_action_dispatch(sm, class_name)
        helper_methods = self._generate_state_machine_helpers(sm, class_name)

        return f'''{header}
{package_decl}
{imports}

/**
 * State machine implementation for {schema.name}.
 *
 * Entity: {sm.for_entity or schema.name}
 * States: {', '.join(sm.states)}
 * Initial State: {sm.initial_state or sm.states[0] if sm.states else 'UNKNOWN'}
 */
public class {class_name}StateMachine {{

{state_enum}

{transition_matrix}

{validation_methods}

{action_dispatch}

{helper_methods}
}}
'''

    def _generate_state_enum(self: BaseGenerator,
                              sm,
                              class_name: str) -> str:
        """Generate State enum with all valid states.

        Returns Java enum definition for states.
        """
        if not sm.states:
            return """    /**
     * State enum - no states defined.
     */
    public enum State {
        UNKNOWN
    }"""

        # Convert state names to valid Java enum constants
        enum_values = []
        for state in sm.states:
            java_const = self.to_java_constant(state)
            enum_values.append(f"        {java_const}")

        enum_block = ',\n'.join(enum_values)

        initial_state = sm.initial_state if sm.initial_state else (sm.states[0] if sm.states else "UNKNOWN")
        initial_const = self.to_java_constant(initial_state)

        return f'''    /**
     * Valid states for the {class_name} entity.
     */
    public enum State {{
{enum_block};

        /**
         * Get the initial state for new entities.
         */
        public static State getInitialState() {{
            return {initial_const};
        }}

        /**
         * Parse state from string (case-insensitive).
         */
        public static State fromString(String name) {{
            if (name == null) return null;
            String upper = name.toUpperCase().replace("-", "_").replace(" ", "_");
            try {{
                return State.valueOf(upper);
            }} catch (IllegalArgumentException e) {{
                return null;
            }}
        }}
    }}'''

    def _generate_state_machine_helpers(self: BaseGenerator,
                                         sm,
                                         class_name: str) -> str:
        """Generate helper methods for state machine operations.

        Returns Java utility methods for state management.
        """
        entity_name = sm.for_entity if sm.for_entity else class_name

        return f'''    /**
     * Get all defined states.
     */
    public static State[] getAllStates() {{
        return State.values();
    }}

    /**
     * Get the entity type this state machine manages.
     */
    public static String getEntityType() {{
        return "{entity_name}";
    }}

    /**
     * Create a state machine context for tracking entity state.
     */
    public static StateMachineContext createContext() {{
        return new StateMachineContext();
    }}

    /**
     * Context class for tracking state machine state.
     */
    public static class StateMachineContext {{
        private State currentState;

        public StateMachineContext() {{
            this.currentState = State.getInitialState();
        }}

        public State getCurrentState() {{
            return currentState;
        }}

        public void transitionTo(State target) {{
            State from = this.currentState;
            this.currentState = transition(from, target);
        }}

        public void transitionTo(State target, Object entity) {{
            State from = this.currentState;
            this.currentState = transition(from, target);
            onTransition(from, target, entity);
        }}

        public boolean canTransitionTo(State target) {{
            return isValidTransition(currentState, target);
        }}

        public Set<State> getAvailableTransitions() {{
            return getValidTransitions(currentState);
        }}

        public boolean isInTerminalState() {{
            return isTerminalState(currentState);
        }}
    }}'''
