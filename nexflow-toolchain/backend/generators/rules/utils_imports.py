# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules Generator Import Utilities

Import set utilities for L4 Rules code generation.
"""

from typing import Set


def get_common_imports() -> Set[str]:
    """Get commonly needed imports for rule generation."""
    return {
        'java.util.Arrays',
        'java.math.BigDecimal',
    }


def get_logging_imports() -> Set[str]:
    """Get imports for logging."""
    return {
        'org.slf4j.Logger',
        'org.slf4j.LoggerFactory',
    }


def get_collection_imports() -> Set[str]:
    """Get imports for collections."""
    return {
        'java.util.List',
        'java.util.ArrayList',
        'java.util.Map',
        'java.util.HashMap',
        'java.util.Set',
        'java.util.HashSet',
        'java.util.Optional',
    }


def get_time_imports() -> Set[str]:
    """Get imports for date/time types."""
    return {
        'java.time.LocalDate',
        'java.time.Instant',
    }


def get_concurrent_imports() -> Set[str]:
    """Get imports for concurrent utilities."""
    return {
        'java.util.concurrent.CompletableFuture',
        'java.util.concurrent.ExecutorService',
        'java.util.concurrent.Executors',
    }


def get_runtime_imports(package_prefix: str = None) -> Set[str]:
    """Get static imports for NexflowRuntime built-in functions.

    Args:
        package_prefix: Package prefix for the project (e.g., 'nexflow.flink')
                       If None, uses a placeholder that must be replaced.

    Returns:
        Set containing static import statement for NexflowRuntime
    """
    if package_prefix:
        return {f"static {package_prefix}.runtime.NexflowRuntime.*"}
    return {"static nexflow.runtime.NexflowRuntime.*"}
