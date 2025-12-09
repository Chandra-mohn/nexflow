"""
Validation Generator Mixin

Generates Java validation code from L3 Transform validation blocks.

Supports:
- Basic validation rules with conditions
- Structured validation messages (code, severity, message)
- Nested validation rules (when blocks)
- Validation result objects with detailed error info
"""

from backend.ast import transform_ast as ast
from backend.generators.transform.validation_helpers import ValidationHelpersMixin


class ValidationGeneratorMixin(ValidationHelpersMixin):
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
        """Generate all validation methods."""
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
        """Generate input validation method."""
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
        """Generate output validation method."""
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
        """Generate invariant checking method."""
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
        """Generate code for a single validation rule."""
        condition = self.generate_expression(rule.condition, use_map=use_map)
        if context != 'input':
            condition = condition.replace('input.', f'{context}.')

        msg_info = self._extract_message_info(rule.message)

        if use_structured and (msg_info['code'] or msg_info['severity']):
            code_arg = f'"{msg_info["code"]}"' if msg_info['code'] else 'null'
            severity_arg = f'ValidationSeverity.{msg_info["severity"]}' if msg_info['severity'] else 'ValidationSeverity.ERROR'
            lines = [
                f"        // Validation: {msg_info['message']}",
                f"        if (!({condition})) {{",
                f'            errors.add(new ValidationError("{msg_info["message"]}", {code_arg}, {severity_arg}));',
                "        }",
            ]
        else:
            lines = [
                f"        // Validation: {msg_info['message']}",
                f"        if (!({condition})) {{",
                f'            errors.add("{msg_info["message"]}");',
                "        }",
            ]

        if rule.nested_rules:
            lines.append(f"        if ({condition}) {{")
            for nested in rule.nested_rules:
                nested_code = self._generate_validation_rule(nested, context, use_map, use_structured)
                lines.append(self.indent(nested_code, 2))
            lines.append("        }")

        return '\n'.join(lines)

    def _extract_message_info(self, msg: ast.ValidationMessageObject | str) -> dict:
        """Extract message, code, and severity from validation message."""
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
