"""
State Machine Generator Module

Generates Java state machine code from Schema AST definitions.
Supports state enums, transition validation, and action dispatch.
"""

from typing import List, Dict

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class StateMachineGeneratorMixin:
    """Mixin providing state machine code generation capabilities.

    Generates:
    - State enum with all valid states
    - Transition validation methods
    - State transition matrix
    - Action dispatch for on_transition

    Note: Uses to_java_constant() from BaseGenerator.
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
                              sm: ast.StateMachineBlock,
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

        # Safe access with bounds checking - use initial_state if provided, else first state
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

    def _generate_transition_matrix(self: BaseGenerator,
                                     sm: ast.StateMachineBlock) -> str:
        """Generate transition matrix for valid state transitions.

        Returns Java code defining allowed transitions.
        """
        if not sm.transitions:
            return """    // No transitions defined - all transitions allowed
    private static final Map<State, Set<State>> VALID_TRANSITIONS = Collections.emptyMap();"""

        # Build transition map: from_state -> set of valid to_states
        transition_map: Dict[str, List[str]] = {}
        for trans in sm.transitions:
            from_state = self.to_java_constant(trans.from_state)
            to_states = [self.to_java_constant(s) for s in trans.to_states]
            transition_map[from_state] = to_states

        # Generate static initializer
        init_lines = []
        for from_state, to_states in transition_map.items():
            to_set = ', '.join(f"State.{s}" for s in to_states)
            init_lines.append(
                f"        VALID_TRANSITIONS.put(State.{from_state}, "
                f"new HashSet<>(Arrays.asList({to_set})));"
            )

        init_block = '\n'.join(init_lines)

        return f'''    /**
     * Transition matrix defining valid state transitions.
     * Key: from state, Value: set of valid target states
     */
    private static final Map<State, Set<State>> VALID_TRANSITIONS = new HashMap<>();

    static {{
{init_block}
    }}'''

    def _generate_transition_validation_methods(self: BaseGenerator,
                                                  sm: ast.StateMachineBlock,
                                                  class_name: str) -> str:
        """Generate transition validation methods.

        Returns Java methods for checking valid transitions.
        """
        return f'''    /**
     * Check if a transition from one state to another is valid.
     *
     * @param from Current state
     * @param to Target state
     * @return true if transition is valid
     */
    public static boolean isValidTransition(State from, State to) {{
        if (from == null || to == null) {{
            return false;
        }}
        Set<State> validTargets = VALID_TRANSITIONS.get(from);
        if (validTargets == null) {{
            // No explicit transitions defined - check if any transitions exist
            return VALID_TRANSITIONS.isEmpty();
        }}
        return validTargets.contains(to);
    }}

    /**
     * Get all valid target states from a given state.
     *
     * @param from Current state
     * @return Set of valid target states
     */
    public static Set<State> getValidTransitions(State from) {{
        if (from == null) {{
            return Collections.emptySet();
        }}
        Set<State> validTargets = VALID_TRANSITIONS.get(from);
        return validTargets != null ? Collections.unmodifiableSet(validTargets) : Collections.emptySet();
    }}

    /**
     * Validate and perform a state transition.
     *
     * @param current Current state
     * @param target Target state
     * @return Target state if transition is valid
     * @throws IllegalStateException if transition is not valid
     */
    public static State transition(State current, State target) {{
        if (!isValidTransition(current, target)) {{
            throw new IllegalStateException(
                "Invalid state transition from " + current + " to " + target);
        }}
        return target;
    }}

    /**
     * Check if the given state is a terminal state (no outgoing transitions).
     *
     * @param state State to check
     * @return true if state has no valid outgoing transitions
     */
    public static boolean isTerminalState(State state) {{
        return getValidTransitions(state).isEmpty();
    }}'''

    def _generate_action_dispatch(self: BaseGenerator,
                                   sm: ast.StateMachineBlock,
                                   class_name: str) -> str:
        """Generate action dispatch for on_transition actions.

        Returns Java methods for handling transition actions.
        """
        if not sm.on_transition_actions:
            return """    /**
     * No transition actions defined.
     * Subclasses can override this method to add custom transition handling.
     */
    public static void onTransition(State from, State to, Object entity) {
        // No actions defined
    }"""

        # Build action handlers for each transition target
        action_cases = []
        for action in sm.on_transition_actions:
            to_state = self.to_java_constant(action.to_state)
            action_call = action.action

            # Convert action name to method call
            method_name = self.to_java_field_name(action_call.action_name)
            params = ', '.join(f'"{p}"' for p in action_call.parameters) if action_call.parameters else ''
            param_list = f", {params}" if params else ""

            action_cases.append(f'''            case {to_state}:
                {method_name}(entity{param_list});
                break;''')

        cases_block = '\n'.join(action_cases)

        # Generate action method signatures
        action_methods = []
        seen_methods = set()
        for action in sm.on_transition_actions:
            method_name = self.to_java_field_name(action.action.action_name)
            if method_name not in seen_methods:
                seen_methods.add(method_name)
                param_count = len(action.action.parameters)
                params_sig = ', '.join(f'String param{i+1}' for i in range(param_count))
                params_block = f", {params_sig}" if params_sig else ""

                action_methods.append(f'''    /**
     * Action: {action.action.action_name}
     * Override this method to implement custom action logic.
     */
    protected static void {method_name}(Object entity{params_block}) {{
        // Implement action logic
        System.out.println("Action {method_name} triggered for entity: " + entity);
    }}''')

        action_methods_block = '\n\n'.join(action_methods)

        return f'''    /**
     * Dispatch transition actions based on target state.
     *
     * @param from Previous state
     * @param to New state
     * @param entity The entity undergoing transition
     */
    public static void onTransition(State from, State to, Object entity) {{
        if (to == null) return;

        switch (to) {{
{cases_block}
            default:
                // No action for this state
                break;
        }}
    }}

{action_methods_block}'''

    def _generate_state_machine_helpers(self: BaseGenerator,
                                         sm: ast.StateMachineBlock,
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
