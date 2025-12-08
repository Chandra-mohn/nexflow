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
        """Generate error handling code.

        Collects all error actions and generates code in proper order:
        1. Logging statements (from all actions)
        2. Error emission to side outputs (from all actions)
        3. Terminal action (throw/return) - only ONE, must be last
        """
        if not on_error:
            return ""

        lines = [
            "    /**",
            f"     * Error handler for {transform_name}",
            "     */",
            "    private Object handleError(Exception e, Object input) {",
        ]

        # Collect all actions to generate in proper order
        log_lines = []
        emit_lines = []
        terminal_lines = []

        for action in on_error.actions:
            # 1. Collect log statements
            if action.log_level:
                # SLF4J uses 'warn' not 'warning'
                log_method = action.log_level.value.lower()
                if log_method == 'warning':
                    log_method = 'warn'
                log_lines.append(
                    f'        LOG.{log_method}("Transform error: {{}}", e.getMessage());'
                )

            # 2. Collect emit_to statements
            if action.emit_to:
                emit_lines.extend([
                    f'        // Emit error to {action.emit_to}',
                    '        ErrorRecord errorRecord = new ErrorRecord();',
                    '        errorRecord.setOriginalRecord(input);',
                    '        errorRecord.setErrorMessage(e.getMessage());',
                    '        errorRecord.setErrorCode('
                    f'"{action.error_code if action.error_code else "TRANSFORM_ERROR"}");',
                    '        errorRecord.setTimestamp(Instant.now());',
                    f'        emitToSideOutput("{action.emit_to}", errorRecord);',
                ])

            # 3. Collect terminal action (only take the first one)
            if action.action_type and not terminal_lines:
                if action.action_type == ast.ErrorActionType.REJECT:
                    terminal_lines.append('        throw new TransformRejectedException(e);')
                elif action.action_type == ast.ErrorActionType.SKIP:
                    terminal_lines.append('        // Skip this record')
                    terminal_lines.append('        return null;')
                elif action.action_type == ast.ErrorActionType.USE_DEFAULT:
                    if action.default_value:
                        default_val = self.generate_expression(action.default_value)
                        terminal_lines.append(f'        return {default_val};')
                    else:
                        terminal_lines.append('        return getDefaultValue();')
                elif action.action_type == ast.ErrorActionType.RAISE:
                    terminal_lines.append(
                        '        throw new TransformException("Transform failed", e);'
                    )

        # Generate in proper order: log -> emit -> terminal
        lines.extend(log_lines)
        lines.extend(emit_lines)
        lines.extend(terminal_lines)

        # Only add return null if no terminal action (throw/return) was generated
        if not terminal_lines:
            lines.append("        return null;")
        lines.append("    }")

        return '\n'.join(lines)

    def _generate_error_action(self, action: ast.ErrorAction) -> str:
        """Generate code for a single error action.

        Order of generated code:
        1. Logging (if configured)
        2. Error emission to side output (if configured)
        3. Action (throw/return) - must be last as it terminates flow
        """
        lines = []

        # 1. Log level handling - always first
        if action.log_level:
            # SLF4J uses 'warn' not 'warning'
            log_method = action.log_level.value.lower()
            if log_method == 'warning':
                log_method = 'warn'
            lines.append(
                f'        LOG.{log_method}("Transform error: {{}}", e.getMessage());'
            )

        # 2. Error emission handling - before any throw/return
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

        # 3. Action type handling - must be last (throw/return terminates)
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
