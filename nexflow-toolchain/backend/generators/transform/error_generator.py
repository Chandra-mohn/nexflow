# Nexflow DSL Toolchain
# Author: Chandra Mohn

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

    def _get_emit_destinations(self, on_error: ast.OnErrorBlock) -> Set[str]:
        """Collect unique emit_to destinations from error block.

        Returns sorted set of destination names.
        """
        if not on_error:
            return set()

        destinations = set()
        for action in on_error.actions:
            if action.emit_to:
                destinations.add(action.emit_to)
        return destinations

    def generate_side_output_tags(self, on_error: ast.OnErrorBlock) -> str:
        """Generate OutputTag declarations for error side outputs.

        Returns Java code declaring OutputTags for each emit_to destination.
        """
        emit_destinations = self._get_emit_destinations(on_error)
        if not emit_destinations:
            return ""

        lines = ["    // Side output tags for error emission"]
        for dest in sorted(emit_destinations):
            tag_name = self.to_java_constant(dest) + "_TAG"
            lines.append(
                f'    private static final OutputTag<ErrorRecord> {tag_name} = '
                f'new OutputTag<ErrorRecord>("{dest}") {{}};'
            )

        return '\n'.join(lines)

    def generate_emit_to_side_output_method(self, on_error: ast.OnErrorBlock) -> str:
        """Generate helper method for emitting to side outputs.

        Returns Java method for routing errors to appropriate OutputTags.
        """
        emit_destinations = self._get_emit_destinations(on_error)
        if not emit_destinations:
            return ""

        lines = [
            "    /**",
            "     * Emit error record to side output.",
            "     * Used by ProcessFunction context for error routing.",
            "     */",
            "    private void emitToSideOutput(String destination, ErrorRecord record) {",
            "        if (ctx == null) {",
            '            LOG.warn("Cannot emit to side output - context not available");',
            "            return;",
            "        }",
            "        switch (destination) {",
        ]

        for dest in sorted(emit_destinations):
            tag_name = self.to_java_constant(dest) + "_TAG"
            lines.append(f'            case "{dest}":')
            lines.append(f'                ctx.output({tag_name}, record);')
            lines.append('                break;')

        lines.extend([
            "            default:",
            '                LOG.warn("Unknown side output destination: {}", destination);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def generate_get_output_tag_method(self, on_error: ast.OnErrorBlock) -> str:
        """Generate method to get OutputTag by name.

        Returns Java method for external access to OutputTags.
        """
        emit_destinations = self._get_emit_destinations(on_error)
        if not emit_destinations:
            return ""

        lines = [
            "    /**",
            "     * Get OutputTag for error side output by name.",
            "     * Use this to access side output streams from the main job.",
            "     */",
            "    public static OutputTag<ErrorRecord> getErrorOutputTag(String name) {",
            "        switch (name) {",
        ]

        for dest in sorted(emit_destinations):
            tag_name = self.to_java_constant(dest) + "_TAG"
            lines.append(f'            case "{dest}": return {tag_name};')

        lines.extend([
            "            default: return null;",
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def get_error_imports(self) -> Set[str]:
        """Get required imports for error handling generation."""
        return {
            'java.time.Instant',
            'org.slf4j.Logger',
            'org.slf4j.LoggerFactory',
        }

    def get_side_output_imports(self) -> Set[str]:
        """Get imports needed for side output emission."""
        return {
            'org.apache.flink.util.OutputTag',
        }
