# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Import Statement AST Type

Represents an import statement in any DSL file (L1-L4).
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class ImportStatement:
    """Import statement for cross-file dependencies.

    Syntax examples:
        import ../shared/Currency.schema
        import ./local/Types.schema
        import /absolute/path/Common.schema

    Attributes:
        path: Raw import path as written in DSL (e.g., ../shared/Currency.schema)
        resolved_path: Absolute resolved path (populated by ImportResolver)
        source_file: The file containing this import statement
        line: Line number in source file
        column: Column number in source file
    """
    path: str
    resolved_path: Optional[Path] = None
    source_file: Optional[Path] = None
    line: int = 0
    column: int = 0

    def __post_init__(self):
        # Normalize path separators
        self.path = self.path.replace('\\', '/')

    @property
    def is_relative(self) -> bool:
        """Check if this is a relative import (starts with . or ..)."""
        return self.path.startswith('.') or self.path.startswith('..')

    @property
    def is_absolute(self) -> bool:
        """Check if this is an absolute import (starts with /)."""
        return self.path.startswith('/')

    @property
    def extension(self) -> Optional[str]:
        """Get the file extension from the import path."""
        if '.' in self.path.split('/')[-1]:
            return '.' + self.path.rsplit('.', 1)[-1]
        return None

    @property
    def dsl_type(self) -> Optional[str]:
        """Infer DSL type from extension."""
        ext_map = {
            '.schema': 'schema',
            '.transform': 'transform',
            '.flow': 'flow',
            '.rules': 'rules',
        }
        ext = self.extension
        return ext_map.get(ext) if ext else None
