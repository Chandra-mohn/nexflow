"""
Validation Generator Mixin

Generates Java validation code from L3 Transform validation blocks.

Supports:
- Basic validation rules with conditions
- Structured validation messages (code, severity, message)
- Nested validation rules (when blocks)
- Validation result objects with detailed error info
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class ValidationGeneratorMixin:
    """
    Mixin for generating Java validation code.

    Generates:
    - Input validation methods
    - Output validation methods
    - Invariant checks
    - Validation exception handling
    """

    def generate_validation_code(
        self,
        validate_input: ast.ValidateInputBlock = None,
        validate_output: ast.ValidateOutputBlock = None,
        invariant: ast.InvariantBlock = None,
        use_map: bool = False,
        invariant_context: str = "input"
    ) -> str:
        """Generate all validation methods.

        Args:
            validate_input: Input validation block
            validate_output: Output validation block
            invariant: Invariant block
            use_map: If True, generate Map.get() access for fields
            invariant_context: Variable name to use in invariant checks
        """
        lines = []

        if validate_input:
            lines.append(self._generate_input_validation(validate_input, use_map))
            lines.append("")

        if validate_output:
            lines.append(self._generate_output_validation(validate_output, use_map))
            lines.append("")

        if invariant:
            lines.append(self._generate_invariant_check(invariant, invariant_context, use_map))
            lines.append("")

        return '\n'.join(lines)

    def _generate_input_validation(
        self,
        block: ast.ValidateInputBlock,
        use_map: bool = False
    ) -> str:
        """Generate input validation method.

        Args:
            block: The validation block AST node
            use_map: If True, generate Map.get() access for fields
        """
        # Use appropriate type for parameter
        param_type = "Map<String, Object>" if use_map else "Object"

        lines = [
            "    /**",
            "     * Validates input data before transformation.",
            "     */",
            f"    private void validateInput({param_type} input) throws ValidationException {{",
            "        List<String> errors = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_validation_rule(rule, "input", use_map))

        lines.extend([
            "",
            "        if (!errors.isEmpty()) {",
            '            throw new ValidationException("Input validation failed", errors);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_output_validation(
        self,
        block: ast.ValidateOutputBlock,
        use_map: bool = False
    ) -> str:
        """Generate output validation method.

        Args:
            block: The validation block AST node
            use_map: If True, generate Map.get() access for fields
        """
        # Use appropriate type for parameter
        param_type = "Map<String, Object>" if use_map else "Object"

        lines = [
            "    /**",
            "     * Validates output data after transformation.",
            "     */",
            f"    private void validateOutput({param_type} output) throws ValidationException {{",
            "        List<String> errors = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_validation_rule(rule, "output", use_map))

        lines.extend([
            "",
            "        if (!errors.isEmpty()) {",
            '            throw new ValidationException("Output validation failed", errors);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_invariant_check(
        self,
        block: ast.InvariantBlock,
        context: str = "input",
        use_map: bool = False
    ) -> str:
        """Generate invariant checking method.

        Args:
            block: The invariant block AST node
            context: The base variable name to use in expressions
            use_map: If True, generate Map.get() access for fields
        """
        lines = [
            "    /**",
            "     * Checks invariant conditions.",
            "     */",
            f"    private void checkInvariants(Object {context}) throws InvariantViolationException {{",
            "        List<String> violations = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_invariant_rule(rule, context, use_map))

        lines.extend([
            "",
            "        if (!violations.isEmpty()) {",
            '            throw new InvariantViolationException("Invariant violated", violations);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_validation_rule(
        self,
        rule: ast.ValidationRule,
        context: str,
        use_map: bool = False,
        use_structured: bool = True
    ) -> str:
        """Generate code for a single validation rule.

        Args:
            rule: The validation rule AST node
            context: The base variable name to use ('input' or 'output')
            use_map: If True, generate Map.get() access instead of getter methods
            use_structured: If True, generate structured ValidationError objects
        """
        # Generate expression with the correct base variable
        condition = self.generate_expression(rule.condition, use_map=use_map)
        # Replace 'input.' with the actual context variable name if different
        if context != 'input':
            condition = condition.replace('input.', f'{context}.')

        # Extract message info (structured or simple)
        msg_info = self._extract_message_info(rule.message)

        if use_structured and (msg_info['code'] or msg_info['severity']):
            # Generate structured ValidationError
            code_arg = f'"{msg_info["code"]}"' if msg_info['code'] else 'null'
            severity_arg = f'ValidationSeverity.{msg_info["severity"]}' if msg_info['severity'] else 'ValidationSeverity.ERROR'
            lines = [
                f"        // Validation: {msg_info['message']}",
                f"        if (!({condition})) {{",
                f'            errors.add(new ValidationError("{msg_info["message"]}", {code_arg}, {severity_arg}));',
                "        }",
            ]
        else:
            # Generate simple string error
            lines = [
                f"        // Validation: {msg_info['message']}",
                f"        if (!({condition})) {{",
                f'            errors.add("{msg_info["message"]}");',
                "        }",
            ]

        # Handle nested rules (when blocks)
        if rule.nested_rules:
            lines.append(f"        if ({condition}) {{")
            for nested in rule.nested_rules:
                nested_code = self._generate_validation_rule(nested, context, use_map, use_structured)
                lines.append(self.indent(nested_code, 2))
            lines.append("        }")

        return '\n'.join(lines)

    def _extract_message_info(self, msg: ast.ValidationMessageObject | str) -> dict:
        """Extract message, code, and severity from validation message.

        Returns dict with 'message', 'code', and 'severity' keys.
        """
        if isinstance(msg, str):
            return {
                'message': msg.replace('"', '\\"'),
                'code': None,
                'severity': None
            }
        if isinstance(msg, ast.ValidationMessageObject):
            return {
                'message': msg.message.replace('"', '\\"'),
                'code': msg.code if msg.code else None,
                'severity': msg.severity.value.upper() if msg.severity else None
            }
        return {
            'message': "Validation failed",
            'code': None,
            'severity': None
        }

    def _generate_invariant_rule(
        self,
        rule: ast.ValidationRule,
        context: str = "input",
        use_map: bool = False
    ) -> str:
        """Generate code for an invariant rule."""
        condition = self.generate_expression(rule.condition, use_map=use_map)
        # Replace 'input.' with the actual context variable name if different
        if context != 'input':
            condition = condition.replace('input.', f'{context}.')
        message = self._get_validation_message(rule.message)

        return f'''        // Invariant: {message}
        if (!({condition})) {{
            violations.add("{message}");
        }}'''

    def _get_validation_message(
        self,
        msg: ast.ValidationMessageObject | str
    ) -> str:
        """Extract message string from ValidationRule message.

        Note: For structured messages with code/severity, use _extract_message_info() instead.
        """
        if isinstance(msg, str):
            return msg.replace('"', '\\"')
        if isinstance(msg, ast.ValidationMessageObject):
            return msg.message.replace('"', '\\"')
        return "Validation failed"

    def generate_validation_error_class(self) -> str:
        """Generate ValidationError record class for structured validation errors."""
        return '''    /**
     * Structured validation error with code and severity.
     */
    public static class ValidationError {
        private final String message;
        private final String code;
        private final ValidationSeverity severity;

        public ValidationError(String message, String code, ValidationSeverity severity) {
            this.message = message;
            this.code = code;
            this.severity = severity;
        }

        public String getMessage() { return message; }
        public String getCode() { return code; }
        public ValidationSeverity getSeverity() { return severity; }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            if (code != null) {
                sb.append("[").append(code).append("] ");
            }
            if (severity != null) {
                sb.append(severity.name()).append(": ");
            }
            sb.append(message);
            return sb.toString();
        }
    }'''

    def generate_validation_severity_enum(self) -> str:
        """Generate ValidationSeverity enum."""
        return '''    /**
     * Severity level for validation errors.
     */
    public enum ValidationSeverity {
        ERROR,
        WARNING,
        INFO
    }'''

    def _generate_validation_exception_class(self) -> str:
        """Generate ValidationException class."""
        return '''    /**
     * Exception thrown when validation fails.
     * Supports both simple string errors and structured ValidationError objects.
     */
    public static class ValidationException extends Exception {
        private final List<?> errors;

        public ValidationException(String message, List<?> errors) {
            super(message + ": " + formatErrors(errors));
            this.errors = errors;
        }

        @SuppressWarnings("unchecked")
        public <T> List<T> getErrors() {
            return (List<T>) errors;
        }

        /**
         * Get errors as strings (works for both String and ValidationError lists).
         */
        public List<String> getErrorMessages() {
            return errors.stream()
                .map(Object::toString)
                .collect(java.util.stream.Collectors.toList());
        }

        /**
         * Get errors filtered by severity (only for structured ValidationError lists).
         */
        public List<ValidationError> getErrorsBySeverity(ValidationSeverity severity) {
            return errors.stream()
                .filter(e -> e instanceof ValidationError)
                .map(e -> (ValidationError) e)
                .filter(e -> e.getSeverity() == severity)
                .collect(java.util.stream.Collectors.toList());
        }

        /**
         * Check if any error has the specified code.
         */
        public boolean hasErrorCode(String code) {
            return errors.stream()
                .filter(e -> e instanceof ValidationError)
                .map(e -> (ValidationError) e)
                .anyMatch(e -> code.equals(e.getCode()));
        }

        private static String formatErrors(List<?> errors) {
            return errors.stream()
                .map(Object::toString)
                .collect(java.util.stream.Collectors.joining(", "));
        }
    }'''

    def _generate_invariant_exception_class(self) -> str:
        """Generate InvariantViolationException class."""
        return '''    /**
     * Exception thrown when invariant is violated.
     */
    public static class InvariantViolationException extends Exception {
        private final List<String> violations;

        public InvariantViolationException(String message, List<String> violations) {
            super(message + ": " + String.join(", ", violations));
            this.violations = violations;
        }

        public List<String> getViolations() {
            return violations;
        }
    }'''

    def get_validation_imports(self) -> Set[str]:
        """Get required imports for validation generation."""
        return {
            'java.util.List',
            'java.util.ArrayList',
        }

    def get_structured_validation_imports(self) -> Set[str]:
        """Get additional imports for structured validation (with error codes/severity)."""
        return {
            'java.util.stream.Collectors',
        }

    def has_structured_validation(
        self,
        validate_input: ast.ValidateInputBlock = None,
        validate_output: ast.ValidateOutputBlock = None
    ) -> bool:
        """Check if any validation rules use structured messages (code/severity).

        Returns True if any rule has a ValidationMessageObject with code or severity.
        """
        def check_rules(rules: List[ast.ValidationRule]) -> bool:
            for rule in rules:
                if isinstance(rule.message, ast.ValidationMessageObject):
                    if rule.message.code or rule.message.severity:
                        return True
                if rule.nested_rules and check_rules(rule.nested_rules):
                    return True
            return False

        if validate_input and check_rules(validate_input.rules):
            return True
        if validate_output and check_rules(validate_output.rules):
            return True
        return False

    def generate_validation_helper_classes(
        self,
        validate_input: ast.ValidateInputBlock = None,
        validate_output: ast.ValidateOutputBlock = None
    ) -> str:
        """Generate all validation helper classes needed.

        Includes ValidationError and ValidationSeverity if structured validation is used.
        Always includes ValidationException and InvariantViolationException.
        """
        lines = []

        # Add structured validation classes if needed
        if self.has_structured_validation(validate_input, validate_output):
            lines.append(self.generate_validation_severity_enum())
            lines.append("")
            lines.append(self.generate_validation_error_class())
            lines.append("")

        # Always add exception classes
        lines.append(self._generate_validation_exception_class())
        lines.append("")
        lines.append(self._generate_invariant_exception_class())

        return '\n'.join(lines)
