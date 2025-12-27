# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Comparison Functions Generator Mixin

Generates comparison and null-handling functions for NexflowRuntime.java:
- coalesce(), nvl()
- between() for various types
- equals() with null safety
"""


class ComparisonFunctionsMixin:
    """Mixin for generating comparison runtime functions.

    The implementation is inherited from RuntimeGenerator for now.
    Future refactoring can move the full implementation here.
    """
    pass  # Implementation inherited from RuntimeGenerator
