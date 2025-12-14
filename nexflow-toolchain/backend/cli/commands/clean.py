# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Clean Command Implementation

Removes generated files.
"""

import shutil

from ..project import Project
from .types import CleanResult


def clean_project(project: Project, clean_all: bool) -> CleanResult:
    """
    Remove generated files.
    """
    result = CleanResult(success=False)

    # Remove generated directory
    if project.output_dir.exists():
        shutil.rmtree(project.output_dir)
        result.removed_count += 1
        result.success = True

    # Remove cache if requested
    if clean_all:
        cache_dir = project.root_dir / ".nexflow-cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            result.removed_count += 1
            result.success = True

    return result
