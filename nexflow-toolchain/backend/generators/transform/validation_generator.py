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
        use_map: bool = False
    ) -> str:
        """Generate code for a single validation rule.

        Args:
            rule: The validation rule AST node
            context: The base variable name to use ('input' or 'output')
            use_map: If True, generate Map.get() access instead of getter methods
        """
        # Generate expression with the correct base variable
        # For now, we use local_vars to make the first part of field paths reference the context var
        condition = self.generate_expression(rule.condition, use_map=use_map)
        # Replace 'input.' with the actual context variable name if different
        if context != 'input':
            condition = condition.replace('input.', f'{context}.')
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
                nested_code = self._generate_validation_rule(nested, context, use_map)
                lines.append(self.indent(nested_code, 2))
            lines.append("        }")

        return '\n'.join(lines)

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
