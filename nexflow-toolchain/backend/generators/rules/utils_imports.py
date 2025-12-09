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
