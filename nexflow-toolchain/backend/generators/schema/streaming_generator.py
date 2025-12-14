# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Streaming Metadata Generator Module

Generates streaming configuration constants and metadata from Schema AST.
Supports idle timeout, retention policies, sparsity hints, and late data handling.
"""

from typing import Dict

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


# Newline constant for readability in f-strings
_NL = '\n'


class StreamingGeneratorMixin:
    """Mixin providing streaming metadata generation capabilities.

    Generates:
    - Idle timeout/behavior constants
    - Retention policy configuration
    - Sparsity field annotations
    - Late data handling configuration
    - Watermark configuration constants

    Note: Uses duration_to_ms() and size_to_bytes() from BaseGenerator.
    """

    def _generate_streaming_constants(self: BaseGenerator,
                                       schema: ast.SchemaDefinition) -> str:
        """Generate streaming configuration constants for Record.

        Returns Java constants block for streaming metadata.
        """
        if not schema.streaming:
            return ""

        streaming = schema.streaming
        constants = []

        # Idle timeout configuration
        if streaming.idle_timeout:
            ms = self.duration_to_ms(streaming.idle_timeout)
            constants.append(f"    public static final long IDLE_TIMEOUT_MS = {ms}L;")

        if streaming.idle_behavior:
            behavior = streaming.idle_behavior.value.upper()
            constants.append(f'    public static final String IDLE_BEHAVIOR = "{behavior}";')

        # Watermark configuration
        if streaming.watermark_delay:
            ms = self.duration_to_ms(streaming.watermark_delay)
            constants.append(f"    public static final long WATERMARK_DELAY_MS = {ms}L;")

        if streaming.max_out_of_orderness:
            ms = self.duration_to_ms(streaming.max_out_of_orderness)
            constants.append(f"    public static final long MAX_OUT_OF_ORDERNESS_MS = {ms}L;")

        if streaming.watermark_interval:
            ms = self.duration_to_ms(streaming.watermark_interval)
            constants.append(f"    public static final long WATERMARK_INTERVAL_MS = {ms}L;")

        if streaming.watermark_strategy:
            strategy = streaming.watermark_strategy.value.upper()
            constants.append(f'    public static final String WATERMARK_STRATEGY = "{strategy}";')

        # Allowed lateness
        if streaming.allowed_lateness:
            ms = self.duration_to_ms(streaming.allowed_lateness)
            constants.append(f"    public static final long ALLOWED_LATENESS_MS = {ms}L;")

        # Late data handling
        if streaming.late_data_handling:
            strategy = streaming.late_data_handling.value.upper()
            constants.append(f'    public static final String LATE_DATA_HANDLING = "{strategy}";')

        if streaming.late_data_stream:
            constants.append(f'    public static final String LATE_DATA_STREAM = "{streaming.late_data_stream}";')

        # Time semantics
        if streaming.time_semantics:
            semantics = streaming.time_semantics.value.upper()
            constants.append(f'    public static final String TIME_SEMANTICS = "{semantics}";')

        # Time field
        if streaming.time_field:
            time_field_parts = getattr(streaming.time_field, 'parts', None)
            time_field = '.'.join(time_field_parts) if time_field_parts else str(streaming.time_field)
            constants.append(f'    public static final String TIME_FIELD = "{time_field}";')

        # Key fields array
        if streaming.key_fields:
            key_fields_str = ', '.join(f'"{f}"' for f in streaming.key_fields)
            constants.append(f"    public static final String[] KEY_FIELDS = {{{key_fields_str}}};")

        if not constants:
            return ""

        return f'''    // =========================================================================
    // Streaming Configuration Constants
    // =========================================================================

{_NL.join(constants)}
'''

    def _generate_retention_config(self: BaseGenerator,
                                    schema: ast.SchemaDefinition) -> str:
        """Generate retention configuration constants.

        Returns Java constants for retention policy.
        """
        if not schema.streaming or not schema.streaming.retention:
            # Also check top-level retention
            if schema.retention:
                ms = self.duration_to_ms(schema.retention)
                return f'''    // =========================================================================
    // Retention Configuration
    // =========================================================================

    public static final long RETENTION_MS = {ms}L;
'''
            return ""

        retention = schema.streaming.retention
        constants = []

        if retention.time:
            ms = self.duration_to_ms(retention.time)
            constants.append(f"    public static final long RETENTION_TIME_MS = {ms}L;")

        if retention.size:
            size_bytes = self.size_to_bytes(retention.size)
            constants.append(f"    public static final long RETENTION_SIZE_BYTES = {size_bytes}L;")

        if retention.policy:
            policy = retention.policy.value.upper()
            constants.append(f'    public static final String RETENTION_POLICY = "{policy}";')

        if not constants:
            return ""

        return f'''    // =========================================================================
    // Retention Configuration
    // =========================================================================

{_NL.join(constants)}
'''

    def _generate_sparsity_annotations(self: BaseGenerator,
                                        schema: ast.SchemaDefinition) -> Dict[str, str]:
        """Generate sparsity hints for fields.

        Returns dict mapping field names to sparsity level.
        """
        if not schema.streaming or not schema.streaming.sparsity:
            return {}

        sparsity = schema.streaming.sparsity
        field_sparsity: Dict[str, str] = {}

        if sparsity.dense_fields:
            for field_name in sparsity.dense_fields:
                field_sparsity[field_name] = 'DENSE'

        if sparsity.moderate_fields:
            for field_name in sparsity.moderate_fields:
                field_sparsity[field_name] = 'MODERATE'

        if sparsity.sparse_fields:
            for field_name in sparsity.sparse_fields:
                field_sparsity[field_name] = 'SPARSE'

        return field_sparsity

    def _generate_sparsity_constants(self: BaseGenerator,
                                      schema: ast.SchemaDefinition) -> str:
        """Generate sparsity field arrays as constants."""
        if not schema.streaming or not schema.streaming.sparsity:
            return ""

        sparsity = schema.streaming.sparsity
        constants = []

        if sparsity.dense_fields:
            fields_str = ', '.join(f'"{f}"' for f in sparsity.dense_fields)
            constants.append(f"    public static final String[] DENSE_FIELDS = {{{fields_str}}};")

        if sparsity.moderate_fields:
            fields_str = ', '.join(f'"{f}"' for f in sparsity.moderate_fields)
            constants.append(f"    public static final String[] MODERATE_FIELDS = {{{fields_str}}};")

        if sparsity.sparse_fields:
            fields_str = ', '.join(f'"{f}"' for f in sparsity.sparse_fields)
            constants.append(f"    public static final String[] SPARSE_FIELDS = {{{fields_str}}};")

        if not constants:
            return ""

        return f'''    // =========================================================================
    // Field Sparsity Configuration
    // =========================================================================

{_NL.join(constants)}
'''

    def _generate_streaming_methods(self: BaseGenerator,
                                     schema: ast.SchemaDefinition) -> str:
        """Generate streaming utility methods (legacy POJO pattern with getField()).

        DEPRECATED: Use _generate_streaming_methods_record() for Java Records.
        Returns Java methods for streaming configuration access.
        """
        if not schema.streaming:
            return ""

        streaming = schema.streaming
        methods = []

        # getTimestampField method if time_field is specified
        if streaming.time_field:
            time_field_parts = streaming.time_field.parts if hasattr(streaming.time_field, 'parts') else [str(streaming.time_field)]
            field_name = time_field_parts[-1] if time_field_parts else 'timestamp'
            getter_name = f"get{self.to_java_field_name(field_name)[0].upper()}{self.to_java_field_name(field_name)[1:]}"

            methods.append(f'''    /**
     * Get the timestamp value for event time processing.
     * Configured time field: {'.'.join(time_field_parts)}
     */
    public long getEventTimestamp() {{
        Object ts = {getter_name}();
        if (ts == null) return System.currentTimeMillis();
        if (ts instanceof Long) return (Long) ts;
        if (ts instanceof java.time.Instant) return ((java.time.Instant) ts).toEpochMilli();
        if (ts instanceof java.util.Date) return ((java.util.Date) ts).getTime();
        return System.currentTimeMillis();
    }}''')

        # isIdle method if idle configuration exists
        if streaming.idle_timeout:
            methods.append('''    /**
     * Check if this record's source should be considered idle.
     * @param lastEventTime Last event timestamp in milliseconds
     * @param currentTime Current processing time in milliseconds
     */
    public static boolean isSourceIdle(long lastEventTime, long currentTime) {
        return (currentTime - lastEventTime) > IDLE_TIMEOUT_MS;
    }''')

        # isLate method if allowed lateness exists
        if streaming.allowed_lateness:
            methods.append('''    /**
     * Check if this record would be considered late.
     * @param eventTime Event timestamp in milliseconds
     * @param watermark Current watermark in milliseconds
     */
    public static boolean isLate(long eventTime, long watermark) {
        return eventTime < (watermark - ALLOWED_LATENESS_MS);
    }''')

        if not methods:
            return ""

        return '\n\n'.join(methods)

    def _generate_streaming_methods_record(self: BaseGenerator,
                                            schema: ast.SchemaDefinition) -> str:
        """Generate streaming utility methods (Record pattern with field()).

        Returns Java methods for streaming configuration access.
        Uses record accessor pattern: fieldName() instead of getFieldName()
        """
        if not schema.streaming:
            return ""

        streaming = schema.streaming
        methods = []

        # getTimestampField method if time_field is specified
        if streaming.time_field:
            time_field_parts = streaming.time_field.parts if hasattr(streaming.time_field, 'parts') else [str(streaming.time_field)]
            field_name = time_field_parts[-1] if time_field_parts else 'timestamp'
            # Record accessor pattern: fieldName() instead of getFieldName()
            accessor_name = self.to_java_field_name(field_name)

            methods.append(f'''    /**
     * Get the timestamp value for event time processing.
     * Configured time field: {'.'.join(time_field_parts)}
     */
    public long getEventTimestamp() {{
        Object ts = {accessor_name}();
        if (ts == null) return System.currentTimeMillis();
        if (ts instanceof Long) return (Long) ts;
        if (ts instanceof java.time.Instant) return ((java.time.Instant) ts).toEpochMilli();
        if (ts instanceof java.util.Date) return ((java.util.Date) ts).getTime();
        return System.currentTimeMillis();
    }}''')

        # isIdle method if idle configuration exists
        if streaming.idle_timeout:
            methods.append('''    /**
     * Check if this record's source should be considered idle.
     * @param lastEventTime Last event timestamp in milliseconds
     * @param currentTime Current processing time in milliseconds
     */
    public static boolean isSourceIdle(long lastEventTime, long currentTime) {
        return (currentTime - lastEventTime) > IDLE_TIMEOUT_MS;
    }''')

        # isLate method if allowed lateness exists
        if streaming.allowed_lateness:
            methods.append('''    /**
     * Check if this record would be considered late.
     * @param eventTime Event timestamp in milliseconds
     * @param watermark Current watermark in milliseconds
     */
    public static boolean isLate(long eventTime, long watermark) {
        return eventTime < (watermark - ALLOWED_LATENESS_MS);
    }''')

        if not methods:
            return ""

        return '\n\n'.join(methods)
