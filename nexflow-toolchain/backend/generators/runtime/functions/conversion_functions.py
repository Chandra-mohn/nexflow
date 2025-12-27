# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Conversion Functions Generator Mixin

Generates type conversion functions for NexflowRuntime.java:
- toString(), toInteger(), toDecimal(), toBoolean()
- parseDate(), parseTimestamp()
- formatDate(), formatNumber()
"""


class ConversionFunctionsMixin:
    """Mixin for generating conversion runtime functions.

    The implementation is inherited from RuntimeGenerator for now.
    Future refactoring can move the full implementation here.
    """
    pass  # Implementation inherited from RuntimeGenerator
