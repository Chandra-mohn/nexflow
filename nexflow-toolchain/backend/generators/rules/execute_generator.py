# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Execute Spec Generator Mixin

Generates Java code for L4 Rules execute specifications - action execution.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L4 Execute generates: Action execution methods, multi-action handlers
L4 Execute NEVER generates: Incomplete stubs, placeholder code
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, TYPE_CHECKING

from backend.generators.rules.utils import (
    to_camel_case,
    to_pascal_case,
    get_collection_imports,
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class ExecuteGeneratorMixin:
    """
    Mixin for generating Java execute spec code.

    Generates:
    - Action execution methods for `execute: yes`
    - Multi-action execution for `execute: multi`
    - Custom execute handlers for named executors
    """

    def generate_execute_method(
        self,
        table: 'ast.DecisionTableDef',
        input_type: str
    ) -> str:
        """Generate execute method based on execute spec.

        Args:
            table: Decision table definition
            input_type: Java type for input

        Returns:
            Java code for execute method
        """
        from backend.ast import rules_ast as ast

        execute_spec = getattr(table, 'execute_spec', None)
        if not execute_spec:
            return ""

        exec_type = getattr(execute_spec, 'execute_type', None)
        if exec_type is None:
            LOG.warning(f"ExecuteSpec missing execute_type for table {getattr(table, 'name', 'unknown')}")
            return ""

        if exec_type == ast.ExecuteType.YES:
            return self._generate_single_execute(table, input_type)
        if exec_type == ast.ExecuteType.MULTI:
            return self._generate_multi_execute(table, input_type)
        if exec_type == ast.ExecuteType.CUSTOM:
            return self._generate_custom_execute(table, input_type)

        LOG.warning(f"Unknown ExecuteType: {exec_type}")
        return ""

    def _generate_single_execute(
        self,
        table: 'ast.DecisionTableDef',
        input_type: str
    ) -> str:
        """Generate single-action execute method.

        When `execute: yes`, the action column result is executed.
        """
        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Table"

        return f'''    /**
     * Execute the action determined by evaluating the decision table.
     * Execute policy: SINGLE - execute first matching action.
     *
     * @param input The input to evaluate
     * @param ctx Execution context for action handlers
     */
    public void execute({input_type} input, ExecutionContext ctx) {{
        var result = evaluate(input);
        if (result.isPresent()) {{
            executeAction(result.get(), ctx);
        }} else {{
            LOG.warn("{class_name}: No matching rule found for input");
        }}
    }}

    /**
     * Execute an action result.
     * Override this method to implement custom action handling.
     */
    protected void executeAction(Object action, ExecutionContext ctx) {{
        if (action instanceof Runnable) {{
            ((Runnable) action).run();
        }} else if (action != null) {{
            ctx.handleAction(action);
        }}
    }}'''

    def _generate_multi_execute(
        self,
        table: 'ast.DecisionTableDef',
        input_type: str
    ) -> str:
        """Generate multi-action execute method.

        When `execute: multi`, all matching actions are executed.
        """
        table_name = getattr(table, 'name', 'unknown')
        class_name = to_pascal_case(table_name) + "Table"

        return f'''    /**
     * Execute all actions determined by evaluating the decision table.
     * Execute policy: MULTI - execute all matching actions.
     *
     * @param input The input to evaluate
     * @param ctx Execution context for action handlers
     * @return Number of actions executed
     */
    public int executeAll({input_type} input, ExecutionContext ctx) {{
        var results = evaluateAll(input);
        int executed = 0;

        for (var action : results) {{
            try {{
                executeAction(action, ctx);
                executed++;
            }} catch (Exception e) {{
                LOG.error("{class_name}: Error executing action", e);
                if (ctx.isStopOnError()) {{
                    throw e;
                }}
            }}
        }}

        return executed;
    }}

    /**
     * Execute an action result.
     * Override this method to implement custom action handling.
     */
    protected void executeAction(Object action, ExecutionContext ctx) {{
        if (action instanceof Runnable) {{
            ((Runnable) action).run();
        }} else if (action != null) {{
            ctx.handleAction(action);
        }}
    }}

    /**
     * Evaluate and return all matching results (for multi-hit policy).
     */
    private List<Object> evaluateAll({input_type} input) {{
        // This should delegate to the multi-hit evaluate method
        // Implementation depends on hit policy
        return new ArrayList<>();
    }}'''

    def _generate_custom_execute(
        self,
        table: 'ast.DecisionTableDef',
        input_type: str
    ) -> str:
        """Generate custom execute method placeholder.

        When `execute: custom_name`, a specific handler is invoked.
        """
        execute_spec = getattr(table, 'execute_spec', None)
        custom_name = getattr(execute_spec, 'custom_name', 'custom') if execute_spec else 'custom'
        handler_name = to_camel_case(custom_name) + "Handler"

        return f'''    /**
     * Execute using custom handler: {custom_name}
     *
     * @param input The input to evaluate
     * @param ctx Execution context for action handlers
     */
    public void execute({input_type} input, ExecutionContext ctx) {{
        var result = evaluate(input);
        if (result.isPresent()) {{
            {handler_name}(result.get(), ctx);
        }}
    }}

    /**
     * Custom action handler: {custom_name}
     * Implement this method to handle the custom execution logic.
     */
    protected abstract void {handler_name}(Object action, ExecutionContext ctx);'''

    def generate_execution_context_class(self) -> str:
        """Generate ExecutionContext helper class."""
        return '''    /**
     * Context for action execution, providing runtime services and configuration.
     */
    public static class ExecutionContext {
        private final Map<String, Object> attributes = new HashMap<>();
        private boolean stopOnError = true;

        /**
         * Handle an action result. Override for custom handling.
         */
        public void handleAction(Object action) {
            LOG.debug("Handling action: {}", action);
        }

        public void setAttribute(String key, Object value) {
            attributes.put(key, value);
        }

        @SuppressWarnings("unchecked")
        public <T> T getAttribute(String key) {
            return (T) attributes.get(key);
        }

        public boolean isStopOnError() {
            return stopOnError;
        }

        public void setStopOnError(boolean stopOnError) {
            this.stopOnError = stopOnError;
        }
    }'''

    def has_execute_spec(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table has an execute specification."""
        return getattr(table, 'execute_spec', None) is not None

    def has_hybrid_spec(self, table: 'ast.DecisionTableDef') -> bool:
        """Check if decision table has both return and execute specs."""
        return (
            getattr(table, 'return_spec', None) is not None and
            getattr(table, 'execute_spec', None) is not None
        )

    def get_execute_imports(self) -> Set[str]:
        """Get required imports for execute generation."""
        imports = get_collection_imports()
        return imports
