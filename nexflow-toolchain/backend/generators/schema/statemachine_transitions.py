"""
State Machine Transitions Mixin

Generates transition validation and action dispatch for state machines.
"""

from typing import Dict, List

from backend.generators.base import BaseGenerator


class StateMachineTransitionsMixin:
    """Mixin providing state machine transition generation."""

    def _generate_transition_matrix(self: BaseGenerator,
                                     sm) -> str:
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
                                                  sm,
                                                  class_name: str) -> str:
        """Generate transition validation methods.

        Returns Java methods for checking valid transitions.
        """
        return f'''    /**
     * Check if a transition from one state to another is valid.
     */
    public static boolean isValidTransition(State from, State to) {{
        if (from == null || to == null) {{
            return false;
        }}
        Set<State> validTargets = VALID_TRANSITIONS.get(from);
        if (validTargets == null) {{
            return VALID_TRANSITIONS.isEmpty();
        }}
        return validTargets.contains(to);
    }}

    /**
     * Get all valid target states from a given state.
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
     */
    public static boolean isTerminalState(State state) {{
        return getValidTransitions(state).isEmpty();
    }}'''

    def _generate_action_dispatch(self: BaseGenerator,
                                   sm,
                                   class_name: str) -> str:
        """Generate action dispatch for on_transition actions.

        Returns Java methods for handling transition actions.
        """
        if not sm.on_transition_actions:
            return """    /**
     * No transition actions defined.
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
     */
    protected static void {method_name}(Object entity{params_block}) {{
        System.out.println("Action {method_name} triggered for entity: " + entity);
    }}''')

        action_methods_block = '\n\n'.join(action_methods)

        return f'''    /**
     * Dispatch transition actions based on target state.
     */
    public static void onTransition(State from, State to, Object entity) {{
        if (to == null) return;

        switch (to) {{
{cases_block}
            default:
                break;
        }}
    }}

{action_methods_block}'''
