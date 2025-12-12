"""
State Context Generator Mixin

Generates typed ProcessContext class with accessor methods from L1 state declarations.

This implements RFC-Method-Implementation-Strategy Solution 3: L1 State Context Generation.

The generated ProcessContext class provides:
- Flag operations: hasFlag(), addFlag(), removeFlag(), clearFlags()
- Value operations: getValue(), setValue()
- Map operations: getMapValue(), putMapValue(), containsMapKey()
- Counter operations: increment(), getCounter(), resetCounter()
- List operations: getList(), addToList(), clearList()
"""

from typing import Set, List, Dict, Optional

from backend.ast import proc_ast as ast


class StateContextGeneratorMixin:
    """
    Mixin for generating ProcessContext class with typed state accessor methods.

    This extends the basic state generation to provide high-level operations
    that can be used in generated business logic code.
    """

    def generate_process_context(self, process: ast.ProcessDefinition, package: str) -> str:
        """Generate ProcessContext class for a process with state declarations."""
        if not process.state:
            return ""

        class_name = self.to_java_class_name(process.name)
        context_class_name = f"{class_name}Context"

        # Collect imports
        imports = self._get_context_imports(process.state)

        # Generate header
        header = self.generate_java_header(
            context_class_name,
            f"Process context for {process.name} with typed state accessor methods"
        )

        # Generate state field declarations
        state_fields = self._generate_context_state_fields(process.state)

        # Generate open() method for state initialization
        open_method = self._generate_context_open_method(process.state)

        # Generate accessor methods for each state declaration
        accessor_methods = self._generate_context_accessor_methods(process.state)

        # Build the class
        imports_str = self._format_context_imports(imports)

        return f'''{header}
package {package};

{imports_str}

public class {context_class_name} implements Serializable {{

    private static final long serialVersionUID = 1L;

    // =========================================================================
    // Flink State Handles (initialized in open())
    // =========================================================================

{state_fields}

    // =========================================================================
    // State Initialization
    // =========================================================================

{open_method}

    // =========================================================================
    // State Accessor Methods
    // =========================================================================

{accessor_methods}
}}
'''

    def _get_context_imports(self, state: ast.StateBlock) -> Set[str]:
        """Get required imports for ProcessContext class."""
        imports = {
            'java.io.Serializable',
            'org.apache.flink.api.common.state.ValueState',
            'org.apache.flink.api.common.state.ValueStateDescriptor',
            'org.apache.flink.api.common.state.MapState',
            'org.apache.flink.api.common.state.MapStateDescriptor',
            'org.apache.flink.api.common.state.ListState',
            'org.apache.flink.api.common.state.ListStateDescriptor',
            'org.apache.flink.api.common.state.StateTtlConfig',
            'org.apache.flink.api.common.state.StateTtlConfig.UpdateType',
            'org.apache.flink.api.common.state.StateTtlConfig.StateVisibility',
            'org.apache.flink.api.common.time.Time',
            'org.apache.flink.configuration.Configuration',
            'org.apache.flink.api.common.functions.RuntimeContext',
        }

        # Add type-specific imports based on state declarations
        for local in state.locals:
            if local.state_type == ast.StateType.COUNTER:
                # Counter uses Long
                pass  # Long is built-in
            elif local.state_type == ast.StateType.GAUGE:
                imports.add('java.math.BigDecimal')
            elif local.state_type == ast.StateType.MAP:
                imports.add('java.util.Map')
                imports.add('java.util.HashMap')
            elif local.state_type == ast.StateType.LIST:
                imports.add('java.util.List')
                imports.add('java.util.ArrayList')

        return imports

    def _format_context_imports(self, imports: Set[str]) -> str:
        """Format imports with proper grouping."""
        sorted_imports = sorted(imports)
        java_imports = [i for i in sorted_imports if i.startswith('java.')]
        flink_imports = [i for i in sorted_imports if i.startswith('org.apache.flink')]
        other_imports = [i for i in sorted_imports if not i.startswith('java.') and not i.startswith('org.apache.flink')]

        lines = []
        if java_imports:
            lines.extend(f'import {i};' for i in java_imports)
            lines.append('')
        if flink_imports:
            lines.extend(f'import {i};' for i in flink_imports)
            lines.append('')
        if other_imports:
            lines.extend(f'import {i};' for i in other_imports)
            lines.append('')

        return '\n'.join(lines)

    def _generate_context_state_fields(self, state: ast.StateBlock) -> str:
        """Generate state field declarations for the context class."""
        lines = []

        for local in state.locals:
            field_name = self._to_camel_case(local.name)
            state_type = local.state_type

            if state_type == ast.StateType.COUNTER:
                lines.append(f'    private transient ValueState<Long> {field_name}State;')
            elif state_type == ast.StateType.GAUGE:
                lines.append(f'    private transient ValueState<BigDecimal> {field_name}State;')
            elif state_type == ast.StateType.MAP:
                # Flag set is implemented as MapState<String, Boolean>
                lines.append(f'    private transient MapState<String, Object> {field_name}State;')
            elif state_type == ast.StateType.LIST:
                lines.append(f'    private transient ListState<Object> {field_name}State;')

        for buffer in state.buffers:
            field_name = self._to_camel_case(buffer.name)
            lines.append(f'    private transient ListState<Object> {field_name}Buffer;')

        return '\n'.join(lines)

    def _generate_context_open_method(self, state: ast.StateBlock) -> str:
        """Generate open() method for state initialization."""
        lines = [
            '    public void open(RuntimeContext runtimeContext) throws Exception {',
        ]

        for local in state.locals:
            field_name = self._to_camel_case(local.name)
            state_type = local.state_type
            desc_name = f'{field_name}Desc'

            if state_type == ast.StateType.COUNTER:
                lines.append(f'        // Counter: {local.name}')
                lines.append(f'        ValueStateDescriptor<Long> {desc_name} = new ValueStateDescriptor<>("{local.name}", Long.class);')
                if local.ttl:
                    lines.append(self._generate_ttl_config_inline(local.ttl, desc_name))
                lines.append(f'        {field_name}State = runtimeContext.getState({desc_name});')
                lines.append('')

            elif state_type == ast.StateType.GAUGE:
                lines.append(f'        // Gauge: {local.name}')
                lines.append(f'        ValueStateDescriptor<BigDecimal> {desc_name} = new ValueStateDescriptor<>("{local.name}", BigDecimal.class);')
                if local.ttl:
                    lines.append(self._generate_ttl_config_inline(local.ttl, desc_name))
                lines.append(f'        {field_name}State = runtimeContext.getState({desc_name});')
                lines.append('')

            elif state_type == ast.StateType.MAP:
                lines.append(f'        // Map/FlagSet: {local.name}')
                lines.append(f'        MapStateDescriptor<String, Object> {desc_name} = new MapStateDescriptor<>("{local.name}", String.class, Object.class);')
                if local.ttl:
                    lines.append(self._generate_ttl_config_inline(local.ttl, desc_name))
                lines.append(f'        {field_name}State = runtimeContext.getMapState({desc_name});')
                lines.append('')

            elif state_type == ast.StateType.LIST:
                lines.append(f'        // List: {local.name}')
                lines.append(f'        ListStateDescriptor<Object> {desc_name} = new ListStateDescriptor<>("{local.name}", Object.class);')
                if local.ttl:
                    lines.append(self._generate_ttl_config_inline(local.ttl, desc_name))
                lines.append(f'        {field_name}State = runtimeContext.getListState({desc_name});')
                lines.append('')

        for buffer in state.buffers:
            field_name = self._to_camel_case(buffer.name)
            desc_name = f'{field_name}Desc'
            lines.append(f'        // Buffer: {buffer.name}')
            lines.append(f'        ListStateDescriptor<Object> {desc_name} = new ListStateDescriptor<>("{buffer.name}", Object.class);')
            if buffer.ttl:
                lines.append(self._generate_ttl_config_inline(buffer.ttl, desc_name))
            lines.append(f'        {field_name}Buffer = runtimeContext.getListState({desc_name});')
            lines.append('')

        lines.append('    }')
        return '\n'.join(lines)

    def _generate_ttl_config_inline(self, ttl: ast.TtlDecl, desc_name: str) -> str:
        """Generate inline TTL configuration."""
        duration_ms = self._duration_to_ms(ttl.duration)
        ttl_type = "UpdateType.OnCreateAndWrite" if ttl.ttl_type == ast.TtlType.SLIDING else "UpdateType.OnReadAndWrite"

        return f'''        StateTtlConfig ttlConfig = StateTtlConfig
            .newBuilder(Time.milliseconds({duration_ms}))
            .setUpdateType({ttl_type})
            .setStateVisibility(StateVisibility.NeverReturnExpired)
            .cleanupFullSnapshot()
            .build();
        {desc_name}.enableTimeToLive(ttlConfig);'''

    def _generate_context_accessor_methods(self, state: ast.StateBlock) -> str:
        """Generate accessor methods for all state declarations."""
        methods = []

        for local in state.locals:
            state_type = local.state_type
            if state_type == ast.StateType.COUNTER:
                methods.append(self._generate_counter_methods(local))
            elif state_type == ast.StateType.GAUGE:
                methods.append(self._generate_gauge_methods(local))
            elif state_type == ast.StateType.MAP:
                methods.append(self._generate_map_methods(local))
            elif state_type == ast.StateType.LIST:
                methods.append(self._generate_list_methods(local))

        # Generate buffer methods
        for buffer in state.buffers:
            methods.append(self._generate_buffer_methods(buffer))

        return '\n\n'.join(methods)

    def _generate_counter_methods(self, local: ast.LocalDecl) -> str:
        """Generate counter accessor methods."""
        field_name = self._to_camel_case(local.name)
        method_suffix = self._to_pascal_case(local.name)
        state_var = f'{field_name}State'

        return f'''    // =========================================================================
    // Counter Operations: {local.name}
    // =========================================================================

    /**
     * Get current counter value for {local.name}.
     * @return Current counter value, 0 if not set
     */
    public long get{method_suffix}() throws Exception {{
        Long value = {state_var}.value();
        return value == null ? 0L : value;
    }}

    /**
     * Increment counter {local.name} by delta.
     * @param delta Amount to add (can be negative)
     */
    public void increment{method_suffix}(long delta) throws Exception {{
        Long current = {state_var}.value();
        {state_var}.update((current == null ? 0L : current) + delta);
    }}

    /**
     * Increment counter {local.name} by 1.
     */
    public void increment{method_suffix}() throws Exception {{
        increment{method_suffix}(1L);
    }}

    /**
     * Reset counter {local.name} to zero.
     */
    public void reset{method_suffix}() throws Exception {{
        {state_var}.clear();
    }}

    /**
     * Set counter {local.name} to specific value.
     * @param value New counter value
     */
    public void set{method_suffix}(long value) throws Exception {{
        {state_var}.update(value);
    }}'''

    def _generate_gauge_methods(self, local: ast.LocalDecl) -> str:
        """Generate gauge (decimal value) accessor methods."""
        field_name = self._to_camel_case(local.name)
        method_suffix = self._to_pascal_case(local.name)
        state_var = f'{field_name}State'

        return f'''    // =========================================================================
    // Gauge Operations: {local.name}
    // =========================================================================

    /**
     * Get current gauge value for {local.name}.
     * @return Current value, null if not set
     */
    public BigDecimal get{method_suffix}() throws Exception {{
        return {state_var}.value();
    }}

    /**
     * Set gauge {local.name} to value.
     * @param value New gauge value
     */
    public void set{method_suffix}(BigDecimal value) throws Exception {{
        {state_var}.update(value);
    }}

    /**
     * Add delta to gauge {local.name}.
     * @param delta Amount to add
     */
    public void add{method_suffix}(BigDecimal delta) throws Exception {{
        BigDecimal current = {state_var}.value();
        BigDecimal newValue = (current == null ? BigDecimal.ZERO : current).add(delta);
        {state_var}.update(newValue);
    }}

    /**
     * Clear gauge {local.name}.
     */
    public void clear{method_suffix}() throws Exception {{
        {state_var}.clear();
    }}'''

    def _generate_map_methods(self, local: ast.LocalDecl) -> str:
        """Generate map/flag set accessor methods."""
        field_name = self._to_camel_case(local.name)
        method_suffix = self._to_pascal_case(local.name)
        state_var = f'{field_name}State'

        # Check if this is likely a flags-type map (name contains 'flag')
        is_flags_map = 'flag' in local.name.lower()

        flag_methods = ""
        if is_flags_map:
            flag_methods = f'''
    /**
     * Check if flag exists in {local.name}.
     * @param flag Flag name to check
     * @return true if flag is set
     */
    public boolean hasFlag(String flag) throws Exception {{
        Object value = {state_var}.get(flag);
        if (value instanceof Boolean) {{
            return (Boolean) value;
        }}
        return value != null;
    }}

    /**
     * Add flag to {local.name}.
     * @param flag Flag name to add
     */
    public void addFlag(String flag) throws Exception {{
        {state_var}.put(flag, Boolean.TRUE);
    }}

    /**
     * Remove flag from {local.name}.
     * @param flag Flag name to remove
     */
    public void removeFlag(String flag) throws Exception {{
        {state_var}.remove(flag);
    }}

    /**
     * Clear all flags in {local.name}.
     */
    public void clearFlags() throws Exception {{
        {state_var}.clear();
    }}
'''

        # Skip generic clear method if we already have clearFlags()
        clear_method = ""
        if not is_flags_map:
            clear_method = f'''

    /**
     * Clear all entries in map {local.name}.
     */
    public void clear{method_suffix}() throws Exception {{
        {state_var}.clear();
    }}'''

        return f'''    // =========================================================================
    // Map Operations: {local.name}
    // =========================================================================
{flag_methods}
    /**
     * Get value from map {local.name}.
     * @param key Map key
     * @return Value associated with key, null if not present
     */
    @SuppressWarnings("unchecked")
    public <T> T get{method_suffix}(String key) throws Exception {{
        return (T) {state_var}.get(key);
    }}

    /**
     * Put value into map {local.name}.
     * @param key Map key
     * @param value Value to store
     */
    public void put{method_suffix}(String key, Object value) throws Exception {{
        {state_var}.put(key, value);
    }}

    /**
     * Check if key exists in map {local.name}.
     * @param key Map key to check
     * @return true if key exists
     */
    public boolean contains{method_suffix}(String key) throws Exception {{
        return {state_var}.contains(key);
    }}

    /**
     * Remove key from map {local.name}.
     * @param key Map key to remove
     */
    public void remove{method_suffix}(String key) throws Exception {{
        {state_var}.remove(key);
    }}{clear_method}'''

    def _generate_list_methods(self, local: ast.LocalDecl) -> str:
        """Generate list accessor methods."""
        field_name = self._to_camel_case(local.name)
        method_suffix = self._to_pascal_case(local.name)
        state_var = f'{field_name}State'

        return f'''    // =========================================================================
    // List Operations: {local.name}
    // =========================================================================

    /**
     * Get all items from list {local.name}.
     * @return List of items
     */
    public List<Object> get{method_suffix}() throws Exception {{
        List<Object> result = new ArrayList<>();
        {state_var}.get().forEach(result::add);
        return result;
    }}

    /**
     * Add item to list {local.name}.
     * @param item Item to add
     */
    public void addTo{method_suffix}(Object item) throws Exception {{
        {state_var}.add(item);
    }}

    /**
     * Add all items to list {local.name}.
     * @param items Items to add
     */
    public void addAllTo{method_suffix}(List<?> items) throws Exception {{
        {state_var}.addAll(items);
    }}

    /**
     * Clear list {local.name}.
     */
    public void clear{method_suffix}() throws Exception {{
        {state_var}.clear();
    }}

    /**
     * Get count of items in list {local.name}.
     * @return Number of items
     */
    public int count{method_suffix}() throws Exception {{
        int count = 0;
        for (Object item : {state_var}.get()) {{
            count++;
        }}
        return count;
    }}'''

    def _generate_buffer_methods(self, buffer: ast.BufferDecl) -> str:
        """Generate buffer accessor methods."""
        field_name = self._to_camel_case(buffer.name)
        method_suffix = self._to_pascal_case(buffer.name)
        state_var = f'{field_name}Buffer'
        buffer_type = buffer.buffer_type

        retrieval_code = self._get_buffer_retrieval_code(buffer, state_var)

        return f'''    // =========================================================================
    // Buffer Operations: {buffer.name} ({buffer_type.value})
    // =========================================================================

    /**
     * Add item to buffer {buffer.name}.
     * @param item Item to add to buffer
     */
    public void addTo{method_suffix}Buffer(Object item) throws Exception {{
        {state_var}.add(item);
    }}

    /**
     * Get items from buffer {buffer.name} in {buffer_type.value} order.
     * @return List of items in buffer order
     */
    public List<Object> get{method_suffix}Buffer() throws Exception {{
{retrieval_code}
    }}

    /**
     * Clear buffer {buffer.name}.
     */
    public void clear{method_suffix}Buffer() throws Exception {{
        {state_var}.clear();
    }}

    /**
     * Get count of items in buffer {buffer.name}.
     * @return Number of items in buffer
     */
    public int count{method_suffix}Buffer() throws Exception {{
        int count = 0;
        for (Object item : {state_var}.get()) {{
            count++;
        }}
        return count;
    }}'''

    def _get_buffer_retrieval_code(self, buffer: ast.BufferDecl, state_var: str) -> str:
        """Get buffer retrieval code based on buffer type."""
        buffer_type = buffer.buffer_type

        if buffer_type == ast.BufferType.FIFO:
            return f'''        // FIFO: first-in, first-out (insertion order)
        List<Object> result = new ArrayList<>();
        {state_var}.get().forEach(result::add);
        return result;'''

        elif buffer_type == ast.BufferType.LIFO:
            return f'''        // LIFO: last-in, first-out (reverse order)
        List<Object> result = new ArrayList<>();
        {state_var}.get().forEach(result::add);
        java.util.Collections.reverse(result);
        return result;'''

        elif buffer_type == ast.BufferType.PRIORITY:
            priority_field = 'priority'
            if hasattr(buffer, 'priority_field') and buffer.priority_field:
                priority_field = buffer.priority_field.parts[0] if buffer.priority_field.parts else 'priority'
            return f'''        // PRIORITY: sorted by {priority_field} (highest first)
        List<Object> result = new ArrayList<>();
        {state_var}.get().forEach(result::add);
        result.sort((a, b) -> {{
            Comparable<?> pa = extractPriority(a, "{priority_field}");
            Comparable<?> pb = extractPriority(b, "{priority_field}");
            return ((Comparable) pb).compareTo(pa);  // Descending
        }});
        return result;'''

        return f'''        // Unknown buffer type
        List<Object> result = new ArrayList<>();
        {state_var}.get().forEach(result::add);
        return result;'''

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)

    def _duration_to_ms(self, duration: ast.Duration) -> int:
        """Convert Duration to milliseconds."""
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return duration.value * multipliers.get(duration.unit, 1)
