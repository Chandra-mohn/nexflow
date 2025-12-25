# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Expression Generator Mixin

Generates Java code from L3 Transform expression AST nodes.
"""

from typing import Set, List, Optional

from backend.ast import transform_ast as ast
from backend.generators.transform.expression_operators import ExpressionOperatorsMixin
from backend.generators.transform.expression_special import ExpressionSpecialMixin


class ExpressionGeneratorMixin(ExpressionOperatorsMixin, ExpressionSpecialMixin):
    """
    Mixin for generating Java expressions from Transform AST.

    Generates:
    - Arithmetic and logical expressions
    - Conditional when/otherwise expressions
    - Function calls
    - Field access and null-safe navigation
    """

    # Maps DSL function names to Java method equivalents
    # Static functions: called as ClassName.methodName(args)
    DSL_TO_JAVA_FUNCTIONS = {
        # Math functions
        "min": "Math.min",
        "max": "Math.max",
        "abs": "Math.abs",
        "round": "Math.round",
        "floor": "Math.floor",
        "ceil": "Math.ceil",
        "sqrt": "Math.sqrt",
        "pow": "Math.pow",
        # Date/time functions
        "now": "Instant.now",
        "today": "LocalDate.now",
        # Utility functions
        "coalesce": "Objects.requireNonNullElse",
    }

    # String instance methods: called as firstArg.methodName(remainingArgs)
    # These are called on the first argument, not as static methods
    STRING_INSTANCE_METHODS = {
        "len": "length",           # len(str) -> str.length()
        "upper": "toUpperCase",    # upper(str) -> str.toUpperCase()
        "lower": "toLowerCase",    # lower(str) -> str.toLowerCase()
        "trim": "trim",            # trim(str) -> str.trim()
        "concat": "concat",        # concat(str1, str2) -> str1.concat(str2)
        "substring": "substring",  # substring(str, start, end) -> str.substring(start, end)
        "contains": "contains",    # contains(str, substr) -> str.contains(substr)
        "starts_with": "startsWith",  # starts_with(str, prefix) -> str.startsWith(prefix)
        "ends_with": "endsWith",      # ends_with(str, suffix) -> str.endsWith(suffix)
    }

    # Voltage encryption/decryption functions routed to NexflowRuntime
    VOLTAGE_FUNCTIONS = {
        "encrypt",      # encrypt(value, profile) - Format-Preserving Encryption
        "decrypt",      # decrypt(value, profile) - Format-Preserving Decryption
        "protect",      # protect(value, profile) - Alias for encrypt (Voltage SDK term)
        "access",       # access(value, profile)  - Alias for decrypt (Voltage SDK term)
        "mask",         # mask(value, pattern)    - Data masking (non-reversible)
        "hash",         # hash(value)             - One-way hash
    }

    # Collection function names (RFC: Collection Operations Instead of Loops)
    COLLECTION_FUNCTIONS = {
        "any", "all", "none",  # Predicate functions
        "sum", "count", "avg",  # Aggregate functions
        "filter", "find", "distinct",  # Transform functions
    }

    # Date context functions (v0.7.0+) routed to NexflowRuntime
    # These require process-level context for calendar resolution
    DATE_CONTEXT_FUNCTIONS = {
        "processing_date",      # processing_date() - System time when record is processed
        "business_date",        # business_date()   - Business date from calendar context
        "business_date_offset", # business_date_offset(n) - Business date +/- n days
    }

    def generate_expression(
        self,
        expr: ast.Expression,
        use_map: bool = False,
        local_vars: Optional[List[str]] = None,
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java code for an expression.

        Args:
            expr: The expression AST node
            use_map: If True, generate Map.get() access instead of getter methods
            local_vars: List of local variable names to reference directly
            assigned_output_fields: List of output fields already assigned to result map
        """
        if local_vars is None:
            local_vars = []
        if assigned_output_fields is None:
            assigned_output_fields = []

        if isinstance(expr, ast.StringLiteral):
            return f'"{expr.value}"'

        if isinstance(expr, ast.IntegerLiteral):
            return f"{expr.value}L"

        if isinstance(expr, ast.DecimalLiteral):
            return f'new BigDecimal("{expr.value}")'

        if isinstance(expr, ast.BooleanLiteral):
            return "true" if expr.value else "false"

        if isinstance(expr, ast.NullLiteral):
            return "null"

        if isinstance(expr, ast.ListLiteral):
            elements = ", ".join(self.generate_expression(e, use_map, local_vars, assigned_output_fields) for e in expr.values)
            return f"Arrays.asList({elements})"

        if isinstance(expr, ast.FieldPath):
            return self._generate_field_path(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.FunctionCall):
            return self._generate_function_call(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.WhenExpression):
            return self._generate_when_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.BinaryExpression):
            return self._generate_binary_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.UnaryExpression):
            return self._generate_unary_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.BetweenExpression):
            return self._generate_between_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.InExpression):
            return self._generate_in_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.IsNullExpression):
            return self._generate_is_null_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.ParenExpression):
            inner = self.generate_expression(expr.inner, use_map, local_vars, assigned_output_fields)
            return f"({inner})"

        if isinstance(expr, ast.OptionalChainExpression):
            return self._generate_optional_chain(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.IndexExpression):
            return self._generate_index_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.LambdaExpression):
            return self._generate_lambda_expression(expr, use_map, local_vars, assigned_output_fields)

        if isinstance(expr, ast.ObjectLiteral):
            return self._generate_object_literal(expr, use_map, local_vars, assigned_output_fields)

        return "/* UNSUPPORTED EXPRESSION */"

    def _generate_field_path(
        self,
        fp: ast.FieldPath,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java getter chain for field path."""
        if assigned_output_fields is None:
            assigned_output_fields = []

        parts = fp.parts
        first_part = parts[0]

        # Check if first part is a local variable
        first_part_camel = self.to_camel_case(first_part)
        if first_part_camel in local_vars:
            if len(parts) == 1:
                return first_part_camel
            # Use record accessor pattern: field() instead of getField()
            rest = ".".join(self.to_record_accessor(p) for p in parts[1:])
            return f"{first_part_camel}.{rest}"

        # Check if this is an already-assigned output field (reference to result map)
        if use_map and first_part in assigned_output_fields:
            if len(parts) == 1:
                return f'result.get("{first_part}")'
            # Use record accessor pattern for nested access
            rest = ".".join(self.to_record_accessor(p) for p in parts[1:])
            return f'((Object)result.get("{first_part}")).{rest}'

        # Input field access
        if use_map:
            if len(parts) == 1:
                return f'input.get("{first_part}")'
            # Use record accessor pattern for nested access
            rest = ".".join(self.to_record_accessor(p) for p in parts[1:])
            return f'((Object)input.get("{first_part}")).{rest}'

        # Standard record accessor chain (Java Records use fieldName() instead of getFieldName())
        if len(parts) == 1:
            return f"input.{self.to_record_accessor(parts[0])}"
        accessors = [self.to_record_accessor(p) for p in parts]
        return f"input.{'.'.join(accessors)}"

    def _generate_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Java function call."""
        if assigned_output_fields is None:
            assigned_output_fields = []

        # Handle collection functions (RFC: Collection Operations Instead of Loops)
        if func.name in self.COLLECTION_FUNCTIONS:
            return self._generate_collection_function_call(func, use_map, local_vars, assigned_output_fields)

        # Handle Voltage encryption/decryption functions
        if func.name in self.VOLTAGE_FUNCTIONS:
            return self._generate_voltage_function_call(func, use_map, local_vars, assigned_output_fields)

        # Handle date context functions (v0.7.0+)
        if func.name in self.DATE_CONTEXT_FUNCTIONS:
            return self._generate_date_context_function_call(func, use_map, local_vars, assigned_output_fields)

        # Handle string instance methods: upper(str) -> str.toUpperCase()
        if func.name in self.STRING_INSTANCE_METHODS:
            return self._generate_string_instance_call(func, use_map, local_vars, assigned_output_fields)

        java_name = self._map_function_name(func.name)

        # For numeric functions like min/max, ensure arguments are numeric
        if func.name in ('min', 'max') and use_map:
            args = ", ".join(
                self._wrap_numeric_if_field(a, use_map, local_vars, assigned_output_fields, force_double=True)
                for a in func.arguments
            )
        else:
            args = ", ".join(
                self.generate_expression(a, use_map, local_vars, assigned_output_fields)
                for a in func.arguments
            )
        return f"{java_name}({args})"

    def _generate_string_instance_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate string instance method call.

        Converts DSL function syntax to Java instance method syntax:
        - upper(str) -> str.toUpperCase()
        - trim(str) -> str.trim()
        - concat(str1, str2) -> str1.concat(str2)
        - substring(str, start, end) -> str.substring(start, end)
        """
        if assigned_output_fields is None:
            assigned_output_fields = []

        java_method = self.STRING_INSTANCE_METHODS[func.name]

        if not func.arguments:
            # Should not happen, but defensive
            return f"/* ERROR: {func.name}() requires at least one argument */"

        # First argument is the target object
        target = self.generate_expression(func.arguments[0], use_map, local_vars, assigned_output_fields)

        # Remaining arguments are method parameters
        if len(func.arguments) > 1:
            params = ", ".join(
                self.generate_expression(a, use_map, local_vars, assigned_output_fields)
                for a in func.arguments[1:]
            )
            return f"{target}.{java_method}({params})"
        else:
            # No-arg method call (e.g., toUpperCase(), trim(), length())
            return f"{target}.{java_method}()"

    def _generate_collection_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate NexflowRuntime collection function call.

        RFC: Collection Operations Instead of Loops
        Routes collection operations to NexflowRuntime static methods.

        Examples:
        - filter(items, x -> x.active)     => NexflowRuntime.filter(items, x -> x.active())
        - any(items, x -> x.amount > 100)  => NexflowRuntime.any(items, x -> x.amount() > 100L)
        - sum(items, x -> x.amount)        => NexflowRuntime.sum(items, x -> x.amount())
        """
        if assigned_output_fields is None:
            assigned_output_fields = []

        # Generate arguments
        args = []
        for arg in func.arguments:
            args.append(self.generate_expression(arg, use_map, local_vars, assigned_output_fields))

        # Map function name to NexflowRuntime method
        runtime_method = self._map_collection_function(func.name)

        return f"NexflowRuntime.{runtime_method}({', '.join(args)})"

    def _map_collection_function(self, name: str) -> str:
        """Map collection function name to NexflowRuntime method name."""
        # Direct mapping - function names match runtime method names
        return name

    def _generate_voltage_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate Voltage encryption/decryption function call.

        Voltage Format-Preserving Encryption (FPE) functions:
        - encrypt(value, profile) / protect(value, profile) - Encrypt sensitive data
        - decrypt(value, profile) / access(value, profile)  - Decrypt encrypted data
        - mask(value, pattern)                              - Mask data (non-reversible)
        - hash(value)                                       - One-way hash

        All functions route to NexflowRuntime static methods which use
        the Voltage SDK internally.

        Examples in DSL:
            ssn_encrypted = encrypt(input.ssn, "ssn")
            pan_protected = protect(input.pan, "pan")
            ssn_clear = decrypt(encrypted_ssn, "ssn")
            masked_phone = mask(input.phone, "***-***-####")
            hashed_id = hash(input.customer_id)
        """
        if assigned_output_fields is None:
            assigned_output_fields = []

        # Generate arguments
        args = []
        for arg in func.arguments:
            args.append(self.generate_expression(arg, use_map, local_vars, assigned_output_fields))

        # Map function name to NexflowRuntime method
        # encrypt/protect both map to encrypt, decrypt/access both map to decrypt
        voltage_method_map = {
            "encrypt": "encrypt",
            "protect": "encrypt",
            "decrypt": "decrypt",
            "access": "decrypt",
            "mask": "mask",
            "hash": "hash",
        }
        runtime_method = voltage_method_map.get(func.name, func.name)

        return f"NexflowRuntime.{runtime_method}({', '.join(args)})"

    def _generate_date_context_function_call(
        self,
        func: ast.FunctionCall,
        use_map: bool,
        local_vars: List[str],
        assigned_output_fields: Optional[List[str]] = None
    ) -> str:
        """Generate date context function call (v0.7.0+).

        Date context functions provide access to process-level date information:
        - processing_date() - Returns the system time when the record is being processed
        - business_date()   - Returns the business date from calendar context
        - business_date_offset(n) - Returns the business date +/- n days

        These functions return LocalDate or Instant.

        Examples in DSL:
            posting_date = processing_date()
            settlement_date = business_date()
            is_same_day = business_date() == transaction.date
            t_plus_2 = business_date_offset(2)

        Generated Java:
            NexflowRuntime.processingDate(context)
            NexflowRuntime.businessDate(context)
            NexflowRuntime.businessDateOffset(context, 2)

        The context parameter provides access to the process execution context
        which includes the business calendar and system time configuration.
        """
        if assigned_output_fields is None:
            assigned_output_fields = []

        # Map DSL function name to NexflowRuntime method name
        date_method_map = {
            "processing_date": "processingDate",
            "business_date": "businessDate",
            "business_date_offset": "businessDateOffset",
        }
        runtime_method = date_method_map.get(func.name, func.name)

        # Date context functions receive the execution context as first parameter
        # The context is available as 'context' in the generated code
        if func.arguments:
            # Functions with additional arguments (like business_date_offset)
            args = ", ".join(
                self.generate_expression(a, use_map, local_vars, assigned_output_fields)
                for a in func.arguments
            )
            return f"NexflowRuntime.{runtime_method}(context, {args})"
        else:
            # Functions with no arguments (just context)
            return f"NexflowRuntime.{runtime_method}(context)"

    def _map_function_name(self, name: str) -> str:
        """Map DSL function name to Java method."""
        return self.DSL_TO_JAVA_FUNCTIONS.get(name, self.to_camel_case(name))

    def get_expression_imports(self) -> Set[str]:
        """Get required imports for expression generation."""
        return {
            'java.util.Arrays',
            'java.util.Optional',
            'java.util.Objects',
            'java.util.Map',
            'java.math.BigDecimal',
            'java.time.Instant',
            'java.time.LocalDate',
            'com.nexflow.runtime.NexflowRuntime',
        }
