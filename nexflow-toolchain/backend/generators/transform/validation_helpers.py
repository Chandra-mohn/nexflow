# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Validation Helpers Mixin

Generates Java validation helper classes:
- ValidationError record class
- ValidationSeverity enum
- ValidationException class
- InvariantViolationException class
"""

from typing import Set, List

from backend.ast import transform_ast as ast


class ValidationHelpersMixin:
    """Mixin for generating validation helper classes."""

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
        """Check if any validation rules use structured messages (code/severity)."""
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
        """Generate all validation helper classes needed."""
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
