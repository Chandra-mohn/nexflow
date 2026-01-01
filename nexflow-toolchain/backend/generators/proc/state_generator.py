# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
State Generator Mixin

Generates Flink state management code from L1 state declarations.
"""

from typing import Set

from backend.ast import proc_ast as ast


class StateGeneratorMixin:
    """
    Mixin for generating Flink state management.

    Generates:
    - ValueState declarations
    - ListState for buffers
    - MapState for keyed counters
    - State TTL configuration
    """

    def generate_state_code(self, process: ast.ProcessDefinition) -> str:
        """Generate state management code for a process."""
        if not process.state:
            return ""

        lines = []

        # Generate state descriptors
        lines.append("// State Descriptors")
        lines.append(self._generate_state_descriptors(process.state))
        lines.append("")

        # Generate state initialization in open()
        lines.append("// State initialization (add to open() method)")
        lines.append(self._generate_state_init(process.state))

        return '\n'.join(lines)

    def _generate_state_descriptors(self, state: ast.StateBlock) -> str:
        """Generate state descriptor declarations."""
        lines = []

        # Local state variables
        for local in state.locals:
            desc_name = self._to_camel_case(local.name) + "StateDesc"
            state_var = self._to_camel_case(local.name) + "State"
            java_type = self._get_state_java_type(local.state_type)
            state_class = self._get_state_class(local.state_type)

            lines.append(f"// Local state: {local.name}")
            lines.append(
                f"private transient {state_class}<{java_type}> {state_var};"
            )

        # Buffer state variables
        for buffer in state.buffers:
            desc_name = self._to_camel_case(buffer.name) + "BufferDesc"
            state_var = self._to_camel_case(buffer.name) + "Buffer"
            java_type = self._get_buffer_java_type(buffer.buffer_type)
            state_class = self._get_buffer_class(buffer.buffer_type)

            lines.append(f"// Buffer: {buffer.name}")
            lines.append(
                f"private transient {state_class}<{java_type}> {state_var};"
            )

        return '\n'.join(lines)

    def _generate_state_init(self, state: ast.StateBlock) -> str:
        """Generate state initialization code for open() method."""
        lines = ["@Override", "public void open(Configuration parameters) throws Exception {"]

        # Initialize local states
        for local in state.locals:
            state_var = self._to_camel_case(local.name) + "State"
            desc_name = self._to_camel_case(local.name) + "StateDesc"
            java_type = self._get_state_java_type(local.state_type)
            state_desc_class = self._get_state_descriptor_class(local.state_type)

            lines.append(f"    // {local.name}: {local.state_type.value}")
            lines.append(
                f"    {state_desc_class}<{java_type}> {desc_name} = "
                f"new {state_desc_class}<>(\"{local.name}\", {java_type}.class);"
            )

            # Add TTL if specified (with cleanup strategy)
            if local.ttl:
                cleanup = local.cleanup.strategy if hasattr(local, 'cleanup') and local.cleanup else None
                lines.append(self._generate_ttl_config(local.ttl, desc_name, cleanup))

            lines.append(
                f"    {state_var} = getRuntimeContext().getState({desc_name});"
            )
            lines.append("")

        # Initialize buffers
        for buffer in state.buffers:
            state_var = self._to_camel_case(buffer.name) + "Buffer"
            desc_name = self._to_camel_case(buffer.name) + "BufferDesc"
            java_type = self._get_buffer_java_type(buffer.buffer_type)

            lines.append(f"    // Buffer: {buffer.name}")
            lines.append(
                f"    ListStateDescriptor<{java_type}> {desc_name} = "
                f"new ListStateDescriptor<>(\"{buffer.name}\", {java_type}.class);"
            )

            if buffer.ttl:
                cleanup = buffer.cleanup.strategy if hasattr(buffer, 'cleanup') and buffer.cleanup else None
                lines.append(self._generate_ttl_config(buffer.ttl, desc_name, cleanup))

            lines.append(
                f"    {state_var} = getRuntimeContext().getListState({desc_name});"
            )
            lines.append("")

        lines.append("}")
        return '\n'.join(lines)

    def _generate_ttl_config(self, ttl: ast.TtlDecl, desc_name: str, cleanup: ast.CleanupStrategy = None) -> str:
        """Generate TTL configuration for a state descriptor.

        Supports cleanup strategies:
        - on_checkpoint: Clean expired state during checkpoint (default)
        - on_access: Clean expired state when accessed (lazy cleanup)
        - background: Clean expired state in background thread (proactive cleanup)
        """
        duration_ms = self._duration_to_ms(ttl.duration)
        ttl_type = "UpdateType.OnCreateAndWrite" if ttl.ttl_type == ast.TtlType.SLIDING else "UpdateType.OnReadAndWrite"

        # Determine cleanup strategy
        cleanup_strategy = cleanup.value if cleanup else "on_checkpoint"

        # Build TTL config with appropriate cleanup settings
        lines = [
            f"    StateTtlConfig ttlConfig = StateTtlConfig",
            f"        .newBuilder(Time.milliseconds({duration_ms}))",
            f"        .setUpdateType({ttl_type})",
            f"        .setStateVisibility(StateVisibility.NeverReturnExpired)",
        ]

        if cleanup_strategy == "on_access":
            # Cleanup on state access - lazy cleanup
            lines.append("        .cleanupIncrementally(10, true)  // Clean 10 entries per access")
        elif cleanup_strategy == "background":
            # Background cleanup thread - proactive cleanup
            lines.append("        .cleanupInRocksdbCompactFilter(1000)  // Clean during RocksDB compaction")
        else:  # on_checkpoint (default)
            # Cleanup during checkpoint - efficient for batch cleanup
            lines.append("        .cleanupFullSnapshot()  // Clean during checkpoint")

        lines.extend([
            "        .build();",
            f"    {desc_name}.enableTimeToLive(ttlConfig);"
        ])

        return '\n'.join(lines)

    def _get_state_java_type(self, state_type: ast.StateType) -> str:
        """Map state type to Java type."""
        type_map = {
            ast.StateType.COUNTER: 'Long',
            ast.StateType.GAUGE: 'Double',
            ast.StateType.MAP: 'Object',
            ast.StateType.LIST: 'Object',
        }
        return type_map.get(state_type, 'Object')

    def _get_state_class(self, state_type: ast.StateType) -> str:
        """Get Flink state class for state type."""
        if state_type == ast.StateType.LIST:
            return 'ListState'
        if state_type == ast.StateType.MAP:
            return 'MapState'
        return 'ValueState'

    def _get_state_descriptor_class(self, state_type: ast.StateType) -> str:
        """Get Flink state descriptor class."""
        return 'ValueStateDescriptor'

    def _get_buffer_java_type(self, buffer_type: ast.BufferType) -> str:
        """Map buffer type to Java element type."""
        return 'Object'  # Generic, will be refined based on schema

    def _get_buffer_class(self, buffer_type: ast.BufferType) -> str:
        """Get Flink state class for buffer type."""
        # All buffer types use ListState - ordering is handled in retrieval
        return 'ListState'

    def _generate_buffer_retrieval(self, buffer: 'ast.BufferDecl', state_var: str) -> str:
        """Generate buffer retrieval code based on buffer type.

        Buffer types:
        - FIFO: First-in, first-out (default - maintains insertion order)
        - LIFO: Last-in, first-out (reverse iteration)
        - PRIORITY: Priority queue based on specified field
        """
        buffer_type = buffer.buffer_type

        if buffer_type == ast.BufferType.FIFO:
            return f'''// FIFO retrieval: first-in, first-out (insertion order)
List<Object> {buffer.name}Items = new ArrayList<>();
{state_var}.get().forEach({buffer.name}Items::add);
// Process in order: for (Object item : {buffer.name}Items) {{ ... }}'''

        elif buffer_type == ast.BufferType.LIFO:
            return f'''// LIFO retrieval: last-in, first-out (reverse order)
List<Object> {buffer.name}Items = new ArrayList<>();
{state_var}.get().forEach({buffer.name}Items::add);
Collections.reverse({buffer.name}Items);
// Process in reverse order: for (Object item : {buffer.name}Items) {{ ... }}'''

        elif buffer_type == ast.BufferType.PRIORITY:
            # Priority buffer - sort by priority field
            priority_field = buffer.priority_field if hasattr(buffer, 'priority_field') else 'priority'
            return f'''// PRIORITY retrieval: sorted by {priority_field} (highest first)
List<Object> {buffer.name}Items = new ArrayList<>();
{state_var}.get().forEach({buffer.name}Items::add);
{buffer.name}Items.sort((a, b) -> {{
    // Sort by priority field descending (highest priority first)
    Comparable pa = getPriorityValue(a, "{priority_field}");
    Comparable pb = getPriorityValue(b, "{priority_field}");
    return pb.compareTo(pa);  // Descending order
}});
// Process in priority order: for (Object item : {buffer.name}Items) {{ ... }}

// Helper method to extract priority value
private Comparable getPriorityValue(Object obj, String field) {{
    try {{
        java.lang.reflect.Method getter = obj.getClass().getMethod(
            "get" + Character.toUpperCase(field.charAt(0)) + field.substring(1));
        return (Comparable) getter.invoke(obj);
    }} catch (Exception e) {{
        return 0;  // Default priority
    }}
}}'''

        return f"// Unknown buffer type: {buffer_type}"

    def _duration_to_ms(self, duration: ast.Duration) -> int:
        """Convert Duration to milliseconds."""
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return duration.value * multipliers.get(duration.unit, 1)

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_state_imports(self) -> Set[str]:
        """Get required imports for state generation."""
        return {
            'org.apache.flink.api.common.state.ValueState',
            'org.apache.flink.api.common.state.ValueStateDescriptor',
            'org.apache.flink.api.common.state.ListState',
            'org.apache.flink.api.common.state.ListStateDescriptor',
            'org.apache.flink.api.common.state.StateTtlConfig',
            'org.apache.flink.api.common.state.StateTtlConfig.UpdateType',
            'org.apache.flink.api.common.state.StateTtlConfig.StateVisibility',
            'org.apache.flink.api.common.time.Time',
            'org.apache.flink.configuration.Configuration',
        }
