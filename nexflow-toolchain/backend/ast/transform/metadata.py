# Nexflow DSL Toolchain
# Author: Chandra Mohn

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


@dataclass
class LookupRef:
    """Reference to a lookup table/service."""
    name: str
    lookup_source: str  # The lookup service/table name
    location: Optional[SourceLocation] = None


@dataclass
class LookupsBlock:
    """Block of lookup references for enrichment.

    Example DSL:
        lookups:
            customer: customer_profile_lookup
            account: account_lookup
            rates: exchange_rate_lookup
        end
    """
    lookups: List[LookupRef]
    location: Optional[SourceLocation] = None


@dataclass
class ParamDecl:
    """Transform parameter declaration.

    Example DSL:
        threshold: decimal required
        mode: string optional, default: "standard"
    """
    name: str
    param_type: str  # "string", "integer", "decimal", "boolean"
    required: bool = True
    default_value: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class ParamsBlock:
    """Block of transform parameters.

    Example DSL:
        params:
            threshold: decimal required
            mode: string optional, default: "standard"
            multiplier: decimal required, default: 1.0
        end
    """
    params: List[ParamDecl]
    location: Optional[SourceLocation] = None
