"""
Scaffold Completion Mixin

Generates scaffold classes for completion patterns:
- CompletionEvent class for sink callback notifications
"""

from pathlib import Path

from backend.ast import proc_ast as ast


class ScaffoldCompletionMixin:
    """Mixin for generating completion event scaffolds."""

    def _generate_completion_scaffold(self, process: ast.ProcessDefinition) -> None:
        """Generate CompletionEvent class for sink callback notifications."""
        completion_package = f"{self.config.package_prefix}.completion"
        completion_path = Path("src/main/java") / self.get_package_path(completion_package)

        completion_event_content = self._generate_completion_event(completion_package)
        self.result.add_file(completion_path / "CompletionEvent.java", completion_event_content, "java")

    def _generate_completion_event(self, package: str) -> str:
        """Generate CompletionEvent class for sink callback notifications."""
        return f'''/**
 * CompletionEvent
 *
 * Event emitted after successful or failed sink writes.
 * Contains correlation ID and status for tracking processing outcomes.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class CompletionEvent {{

    public enum Status {{
        SUCCESS,
        FAILURE
    }}

    private final String correlationId;
    private final Status status;
    private final long timestamp;
    private final Map<String, Object> additionalFields;
    private final String errorMessage;

    private CompletionEvent(String correlationId, Status status, Map<String, Object> additionalFields, String errorMessage) {{
        this.correlationId = correlationId;
        this.status = status;
        this.timestamp = Instant.now().toEpochMilli();
        this.additionalFields = additionalFields != null ? additionalFields : new HashMap<>();
        this.errorMessage = errorMessage;
    }}

    /**
     * Create a success completion event.
     */
    public static CompletionEvent success(Object record, String correlationField) {{
        String correlationId = extractField(record, correlationField);
        return new CompletionEvent(correlationId, Status.SUCCESS, null, null);
    }}

    /**
     * Create a success completion event with additional fields.
     */
    public static CompletionEvent success(Object record, String correlationField, String[] includeFields) {{
        String correlationId = extractField(record, correlationField);
        Map<String, Object> additional = extractFields(record, includeFields);
        return new CompletionEvent(correlationId, Status.SUCCESS, additional, null);
    }}

    /**
     * Create a failure completion event.
     */
    public static CompletionEvent failure(Object record, String correlationField, String errorMessage) {{
        String correlationId = extractField(record, correlationField);
        return new CompletionEvent(correlationId, Status.FAILURE, null, errorMessage);
    }}

    /**
     * Create a failure completion event with additional fields.
     */
    public static CompletionEvent failure(Object record, String correlationField, String[] includeFields, String errorMessage) {{
        String correlationId = extractField(record, correlationField);
        Map<String, Object> additional = extractFields(record, includeFields);
        return new CompletionEvent(correlationId, Status.FAILURE, additional, errorMessage);
    }}

    private static String extractField(Object record, String fieldName) {{
        // TODO: Implement actual field extraction using reflection or schema-aware access
        try {{
            java.lang.reflect.Method getter = record.getClass().getMethod("get" + capitalize(fieldName));
            Object value = getter.invoke(record);
            return value != null ? value.toString() : null;
        }} catch (Exception e) {{
            return record.toString();
        }}
    }}

    private static Map<String, Object> extractFields(Object record, String[] fieldNames) {{
        Map<String, Object> fields = new HashMap<>();
        for (String fieldName : fieldNames) {{
            try {{
                java.lang.reflect.Method getter = record.getClass().getMethod("get" + capitalize(fieldName));
                Object value = getter.invoke(record);
                fields.put(fieldName, value);
            }} catch (Exception e) {{
                // Skip field if not accessible
            }}
        }}
        return fields;
    }}

    private static String capitalize(String str) {{
        if (str == null || str.isEmpty()) return str;
        return Character.toUpperCase(str.charAt(0)) + str.substring(1);
    }}

    // Getters
    public String getCorrelationId() {{
        return correlationId;
    }}

    public Status getStatus() {{
        return status;
    }}

    public long getTimestamp() {{
        return timestamp;
    }}

    public Map<String, Object> getAdditionalFields() {{
        return additionalFields;
    }}

    public String getErrorMessage() {{
        return errorMessage;
    }}

    public boolean isSuccess() {{
        return status == Status.SUCCESS;
    }}

    public String getKey() {{
        return correlationId;
    }}

    @Override
    public String toString() {{
        return "CompletionEvent{{" +
            "correlationId='" + correlationId + "'" +
            ", status=" + status +
            ", timestamp=" + timestamp +
            (errorMessage != null ? ", error='" + errorMessage + "'" : "") +
            "}}";
    }}
}}
'''
