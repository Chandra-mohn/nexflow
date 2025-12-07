"""
State Generator Mixin

Generates Flink state management code from L1 state declarations.
"""

from typing import Set, List

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

            # Add TTL if specified
            if local.ttl:
                lines.append(self._generate_ttl_config(local.ttl, desc_name))

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
                lines.append(self._generate_ttl_config(buffer.ttl, desc_name))

            lines.append(
                f"    {state_var} = getRuntimeContext().getListState({desc_name});"
            )
            lines.append("")

        lines.append("}")
        return '\n'.join(lines)

    def _generate_ttl_config(self, ttl: ast.TtlDecl, desc_name: str) -> str:
        """Generate TTL configuration for a state descriptor."""
        duration_ms = self._duration_to_ms(ttl.duration)
        ttl_type = "UpdateType.OnCreateAndWrite" if ttl.ttl_type == ast.TtlType.SLIDING else "UpdateType.OnReadAndWrite"

        return f'''    StateTtlConfig ttlConfig = StateTtlConfig
        .newBuilder(Time.milliseconds({duration_ms}))
        .setUpdateType({ttl_type})
        .setStateVisibility(StateVisibility.NeverReturnExpired)
        .build();
    {desc_name}.enableTimeToLive(ttlConfig);'''

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
        if buffer_type == ast.BufferType.PRIORITY:
            return 'ListState'  # Use ListState with custom sorting
        return 'ListState'

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
