# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Services Module

AST types for external service declarations in L4 Rules DSL.

Service declarations allow rules to call external services (ML models, databases, APIs)
with automatic handling of timeout, fallback, retry, and caching.

Example DSL:
    services {
        ml_fraud: async MLFraudService.predict(transaction: Transaction) -> decimal
            timeout: 500ms
            fallback: 0.0
            retry: 3

        bureau: cached(5m) BureauService.lookup(customer_id: string) -> BureauData
            timeout: 1s
            fallback: null
    }
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union
from enum import Enum

from .common import SourceLocation
from .literals import Literal


class ServiceType(Enum):
    """Service invocation type."""
    SYNC = "sync"
    ASYNC = "async"
    CACHED = "cached"


class DurationUnit(Enum):
    """Time duration units."""
    MILLISECONDS = "ms"
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"


@dataclass
class Duration:
    """Time duration with unit."""
    value: int
    unit: DurationUnit
    location: Optional[SourceLocation] = None

    def to_milliseconds(self) -> int:
        """Convert duration to milliseconds."""
        multipliers = {
            DurationUnit.MILLISECONDS: 1,
            DurationUnit.SECONDS: 1000,
            DurationUnit.MINUTES: 60_000,
            DurationUnit.HOURS: 3_600_000,
        }
        return self.value * multipliers[self.unit]

    def __str__(self) -> str:
        return f"{self.value}{self.unit.value}"


@dataclass
class ServiceParam:
    """Service method parameter declaration."""
    name: str
    param_type: str  # Type name (can be BaseType or custom type)
    location: Optional[SourceLocation] = None


@dataclass
class ServiceOptions:
    """Service invocation options (timeout, fallback, retry)."""
    timeout: Optional[Duration] = None
    fallback: Optional[Literal] = None
    retry: Optional[int] = None
    location: Optional[SourceLocation] = None


@dataclass
class ServiceDecl:
    """
    External service declaration.

    Declares an external service method with invocation semantics.

    Attributes:
        name: Local name for the service call (e.g., 'ml_fraud')
        service_type: How to invoke (SYNC, ASYNC, CACHED)
        class_name: Service class/interface name (e.g., 'MLFraudService')
        method_name: Method to call (e.g., 'predict')
        params: Method parameters
        return_type: Return type name
        cache_duration: For CACHED type, how long to cache results
        options: Timeout, fallback, retry configuration
        location: Source location for error reporting
    """
    name: str
    service_type: ServiceType
    class_name: str
    method_name: str
    params: List[ServiceParam] = field(default_factory=list)
    return_type: str = "Object"
    cache_duration: Optional[Duration] = None  # Only for CACHED type
    options: Optional[ServiceOptions] = None
    location: Optional[SourceLocation] = None

    def is_async(self) -> bool:
        """Check if this is an async service."""
        return self.service_type == ServiceType.ASYNC

    def is_cached(self) -> bool:
        """Check if this is a cached service."""
        return self.service_type == ServiceType.CACHED

    def get_timeout_ms(self) -> Optional[int]:
        """Get timeout in milliseconds, or None if not specified."""
        if self.options and self.options.timeout:
            return self.options.timeout.to_milliseconds()
        return None

    def get_retry_count(self) -> int:
        """Get retry count, defaulting to 0 if not specified."""
        if self.options and self.options.retry is not None:
            return self.options.retry
        return 0

    def get_cache_ttl_ms(self) -> Optional[int]:
        """Get cache TTL in milliseconds for cached services."""
        if self.cache_duration:
            return self.cache_duration.to_milliseconds()
        return None


@dataclass
class ServicesBlock:
    """
    Container for service declarations.

    Example:
        services {
            service1: sync ...
            service2: async ...
        }
    """
    services: List[ServiceDecl] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    def get_service(self, name: str) -> Optional[ServiceDecl]:
        """Get a service by its local name."""
        for service in self.services:
            if service.name == name:
                return service
        return None

    def get_async_services(self) -> List[ServiceDecl]:
        """Get all async services."""
        return [s for s in self.services if s.is_async()]

    def get_cached_services(self) -> List[ServiceDecl]:
        """Get all cached services."""
        return [s for s in self.services if s.is_cached()]

    def get_service_classes(self) -> List[str]:
        """Get unique service class names."""
        return list(set(s.class_name for s in self.services))
