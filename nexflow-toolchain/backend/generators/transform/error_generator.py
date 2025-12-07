"""
Error Generator Mixin

Generates Java error handling code from L3 Transform on_error blocks.
"""

from typing import Set

from backend.ast import transform_ast as ast


class ErrorGeneratorMixin:
    """
    Mixin for generating Java error handling code.

    Generates:
    - Error handling strategies (reject, skip, default)
    - Error logging
    - Error emission to side outputs
    """

    def generate_error_handling_code(
        self,
        on_error: ast.OnErrorBlock,
        transform_name: str
    ) -> str:
        """Generate error handling code."""
        if not on_error:
            return ""

        lines = [
            "    /**",
            f"     * Error handler for {transform_name}",
            "     */",
            "    private Object handleError(Exception e, Object input) {",
        ]

        # Process each error action
        for action in on_error.actions:
            lines.append(self._generate_error_action(action))

        lines.extend([
            "        return null;",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_error_action(self, action: ast.ErrorAction) -> str:
        """Generate code for a single error action."""
        lines = []

        # Log level handling
        if action.log_level:
            log_method = action.log_level.value.lower()
            lines.append(
                f'        LOG.{log_method}("Transform error: {{}}", e.getMessage());'
            )

        # Action type handling
        if action.action_type:
            if action.action_type == ast.ErrorActionType.REJECT:
                lines.append('        throw new TransformRejectedException(e);')

            elif action.action_type == ast.ErrorActionType.SKIP:
                lines.append('        // Skip this record')
                lines.append('        return null;')

            elif action.action_type == ast.ErrorActionType.USE_DEFAULT:
                if action.default_value:
                    default_val = self.generate_expression(action.default_value)
                    lines.append(f'        return {default_val};')
                else:
                    lines.append('        return getDefaultValue();')

            elif action.action_type == ast.ErrorActionType.RAISE:
                lines.append(
                    '        throw new TransformException("Transform failed", e);'
                )

        # Error emission handling
        if action.emit_to:
            lines.extend([
                f'        // Emit error to {action.emit_to}',
                '        ErrorRecord errorRecord = new ErrorRecord();',
                '        errorRecord.setOriginalRecord(input);',
                '        errorRecord.setErrorMessage(e.getMessage());',
                '        errorRecord.setErrorCode('
                f'"{action.error_code if action.error_code else "TRANSFORM_ERROR"}");',
                '        errorRecord.setTimestamp(Instant.now());',
                f'        emitToSideOutput("{action.emit_to}", errorRecord);',
            ])

        return '\n'.join(lines)

    def generate_error_record_class(self) -> str:
        """Generate ErrorRecord inner class."""
        return '''    /**
     * Error record for side output emission.
     */
    public static class ErrorRecord {
        private Object originalRecord;
        private String errorMessage;
        private String errorCode;
        private Instant timestamp;

        public Object getOriginalRecord() { return originalRecord; }
        public void setOriginalRecord(Object originalRecord) {
            this.originalRecord = originalRecord;
        }

        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
        }

        public String getErrorCode() { return errorCode; }
        public void setErrorCode(String errorCode) {
            this.errorCode = errorCode;
        }

        public Instant getTimestamp() { return timestamp; }
        public void setTimestamp(Instant timestamp) {
            this.timestamp = timestamp;
        }
    }'''

    def generate_exception_classes(self) -> str:
        """Generate custom exception classes."""
        return '''    /**
     * Exception thrown when a record should be rejected.
     */
    public static class TransformRejectedException extends RuntimeException {
        public TransformRejectedException(Throwable cause) {
            super("Record rejected during transform", cause);
        }
    }

    /**
     * General transform exception.
     */
    public static class TransformException extends RuntimeException {
        public TransformException(String message, Throwable cause) {
            super(message, cause);
        }
    }'''

    def generate_try_catch_wrapper(
        self,
        transform_name: str,
        has_error_handler: bool
    ) -> tuple:
        """Generate try-catch wrapper for transform logic."""
        if not has_error_handler:
            return ("", "")

        try_start = "        try {"
        catch_block = f'''        }} catch (Exception e) {{
            return handleError(e, input);
        }}'''

        return (try_start, catch_block)

    def get_error_imports(self) -> Set[str]:
        """Get required imports for error handling generation."""
        return {
            'java.time.Instant',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }
