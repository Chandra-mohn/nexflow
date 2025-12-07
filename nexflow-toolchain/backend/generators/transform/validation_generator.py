"""
Validation Generator Mixin

Generates Java validation code from L3 Transform validation blocks.
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
        invariant: ast.InvariantBlock = None
    ) -> str:
        """Generate all validation methods."""
        lines = []

        if validate_input:
            lines.append(self._generate_input_validation(validate_input))
            lines.append("")

        if validate_output:
            lines.append(self._generate_output_validation(validate_output))
            lines.append("")

        if invariant:
            lines.append(self._generate_invariant_check(invariant))
            lines.append("")

        return '\n'.join(lines)

    def _generate_input_validation(self, block: ast.ValidateInputBlock) -> str:
        """Generate input validation method."""
        lines = [
            "    /**",
            "     * Validates input data before transformation.",
            "     */",
            "    private void validateInput(Object input) throws ValidationException {",
            "        List<String> errors = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_validation_rule(rule, "input"))

        lines.extend([
            "",
            "        if (!errors.isEmpty()) {",
            '            throw new ValidationException("Input validation failed", errors);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_output_validation(self, block: ast.ValidateOutputBlock) -> str:
        """Generate output validation method."""
        lines = [
            "    /**",
            "     * Validates output data after transformation.",
            "     */",
            "    private void validateOutput(Object output) throws ValidationException {",
            "        List<String> errors = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_validation_rule(rule, "output"))

        lines.extend([
            "",
            "        if (!errors.isEmpty()) {",
            '            throw new ValidationException("Output validation failed", errors);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_invariant_check(self, block: ast.InvariantBlock) -> str:
        """Generate invariant checking method."""
        lines = [
            "    /**",
            "     * Checks invariant conditions.",
            "     */",
            "    private void checkInvariants(Object context) throws InvariantViolationException {",
            "        List<String> violations = new ArrayList<>();",
            "",
        ]

        for rule in block.rules:
            lines.append(self._generate_invariant_rule(rule))

        lines.extend([
            "",
            "        if (!violations.isEmpty()) {",
            '            throw new InvariantViolationException("Invariant violated", violations);',
            "        }",
            "    }",
        ])

        return '\n'.join(lines)

    def _generate_validation_rule(self, rule: ast.ValidationRule, context: str) -> str:
        """Generate code for a single validation rule."""
        condition = self.generate_expression(rule.condition)
        message = self._get_validation_message(rule.message)

        lines = [
            f"        // Validation: {message}",
            f"        if (!({condition})) {{",
            f'            errors.add("{message}");',
            "        }",
        ]

        # Handle nested rules (when blocks)
        if rule.nested_rules:
            lines.append(f"        if ({condition}) {{")
            for nested in rule.nested_rules:
                nested_code = self._generate_validation_rule(nested, context)
                lines.append(self.indent(nested_code, 2))
            lines.append("        }")

        return '\n'.join(lines)

    def _generate_invariant_rule(self, rule: ast.ValidationRule) -> str:
        """Generate code for an invariant rule."""
        condition = self.generate_expression(rule.condition)
        message = self._get_validation_message(rule.message)

        return f'''        // Invariant: {message}
        if (!({condition})) {{
            violations.add("{message}");
        }}'''

    def _get_validation_message(
        self,
        msg: ast.ValidationMessageObject | str
    ) -> str:
        """Extract message string from ValidationRule message."""
        if isinstance(msg, str):
            return msg.replace('"', '\\"')
        if isinstance(msg, ast.ValidationMessageObject):
            return msg.message.replace('"', '\\"')
        return "Validation failed"

    def _generate_validation_exception_class(self) -> str:
        """Generate ValidationException class."""
        return '''    /**
     * Exception thrown when validation fails.
     */
    public static class ValidationException extends Exception {
        private final List<String> errors;

        public ValidationException(String message, List<String> errors) {
            super(message + ": " + String.join(", ", errors));
            this.errors = errors;
        }

        public List<String> getErrors() {
            return errors;
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
