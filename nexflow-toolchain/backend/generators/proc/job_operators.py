# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Job Operators Mixin (Backward Compatibility)

This module re-exports JobOperatorsMixin from the modular operators package.
The implementation has been refactored into focused sub-modules:

- operators/basic_operators.py: transform, enrich, route, aggregate
- operators/window_join_operators.py: window, join, merge
- operators/advanced_operators.py: validate_input, evaluate, lookup, parallel
- operators/sql_operators.py: sql_transform (Flink/Spark SQL)
- operators/dispatcher.py: main _wire_operator() dispatcher
"""

from backend.generators.proc.operators import JobOperatorsMixin

__all__ = ['JobOperatorsMixin']
