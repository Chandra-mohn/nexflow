"""
Transform AST Metadata Types

Metadata and cache configuration dataclasses.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation, Duration
from .enums import CompatibilityMode


@dataclass
class TransformMetadata:
    """Transform metadata (version, description, etc.)."""
    version: Optional[str] = None
    description: Optional[str] = None
    previous_version: Optional[str] = None
    compatibility: Optional[CompatibilityMode] = None
    location: Optional[SourceLocation] = None


@dataclass
class CacheDecl:
    """Cache configuration."""
    ttl: Optional[Duration] = None
    key_fields: Optional[List[str]] = None
    location: Optional[SourceLocation] = None
