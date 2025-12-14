# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Init Command Implementation

Initializes a new Nexflow project.
"""

from pathlib import Path

from ..project import create_default_config
from .types import InitResult


def init_project(name: str, force: bool) -> InitResult:
    """
    Initialize a new Nexflow project.
    """
    result = InitResult(success=True)
    cwd = Path.cwd()

    # Check if nexflow.toml already exists
    config_file = cwd / "nexflow.toml"
    if config_file.exists() and not force:
        result.success = False
        result.message = "nexflow.toml already exists. Use --force to overwrite."
        return result

    # Create config file
    config_content = create_default_config(name)
    config_file.write_text(config_content)
    result.created.append("nexflow.toml")

    # Create directory structure
    dirs_to_create = [
        "src/flow",
        "src/schema",
        "src/transform",
        "src/rules",
        "generated",
    ]

    for dir_path in dirs_to_create:
        full_path = cwd / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True)
            result.created.append(f"{dir_path}/")

    # Create .gitignore for generated files
    gitignore = cwd / "generated" / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Generated files - do not commit\n*\n!.gitignore\n")

    return result
