# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Services Generator Mixin

Generates Java code for L4 external service declarations.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
Services generate: Service interfaces, wrapper methods with timeout/fallback/retry
Services NEVER generate: Actual service implementations (user provides those)
─────────────────────────────────────────────────────────────────────
"""

import logging
from typing import Set, List, Optional, TYPE_CHECKING

from backend.ast.rules.services import (
    ServiceDecl, ServiceType, ServicesBlock, ServiceParam, Duration
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class ServicesGeneratorMixin:
    """
    Mixin for generating Java service integration code.

    Generates:
    - Service interfaces (user implements these)
    - Service wrapper methods with timeout, fallback, retry
    - Cache setup for cached services
    - Async handling for async services
    """

    def generate_service_interfaces(
        self,
        services: ServicesBlock,
        package: str
    ) -> str:
        """Generate service interfaces that user must implement.

        Args:
            services: ServicesBlock AST node
            package: Java package name

        Returns:
            Java code for service interfaces
        """
        if not services or not services.services:
            return ""

        lines = []

        # Group services by class name
        service_classes = {}
        for service in services.services:
            if service.class_name not in service_classes:
                service_classes[service.class_name] = []
            service_classes[service.class_name].append(service)

        # Generate interface for each service class
        for class_name, class_services in service_classes.items():
            lines.append(f"    /**")
            lines.append(f"     * Service interface for {class_name}.")
            lines.append(f"     * User must provide implementation.")
            lines.append(f"     */")
            lines.append(f"    public interface {class_name} {{")

            for service in class_services:
                return_type = self._map_service_return_type(service.return_type)
                params = self._generate_service_params(service.params)

                if service.is_async():
                    lines.append(f"        CompletableFuture<{return_type}> {service.method_name}({params});")
                else:
                    lines.append(f"        {return_type} {service.method_name}({params});")

            lines.append(f"    }}")
            lines.append("")

        return '\n'.join(lines)

    def generate_service_fields(self, services: ServicesBlock) -> str:
        """Generate private fields for service instances.

        Args:
            services: ServicesBlock AST node

        Returns:
            Java code for service fields
        """
        if not services or not services.services:
            return ""

        lines = []
        service_classes = set(s.class_name for s in services.services)

        for class_name in sorted(service_classes):
            field_name = self._to_field_name(class_name)
            lines.append(f"    private final {class_name} {field_name};")

        # Add cache fields for cached services
        cached_services = services.get_cached_services()
        for service in cached_services:
            cache_name = self._to_field_name(service.name) + "Cache"
            return_type = self._map_service_return_type(service.return_type)
            key_type = self._get_cache_key_type(service)
            lines.append(f"    private final Cache<{key_type}, {return_type}> {cache_name};")

        return '\n'.join(lines)

    def generate_service_constructor_params(self, services: ServicesBlock) -> str:
        """Generate constructor parameters for services.

        Args:
            services: ServicesBlock AST node

        Returns:
            Java constructor parameter list
        """
        if not services or not services.services:
            return ""

        service_classes = set(s.class_name for s in services.services)
        params = []

        for class_name in sorted(service_classes):
            field_name = self._to_field_name(class_name)
            params.append(f"            {class_name} {field_name}")

        return ',\n'.join(params)

    def generate_service_constructor_body(self, services: ServicesBlock) -> str:
        """Generate constructor body for service initialization.

        Args:
            services: ServicesBlock AST node

        Returns:
            Java constructor body
        """
        if not services or not services.services:
            return ""

        lines = []
        service_classes = set(s.class_name for s in services.services)

        for class_name in sorted(service_classes):
            field_name = self._to_field_name(class_name)
            lines.append(f"        this.{field_name} = {field_name};")

        # Initialize caches for cached services
        cached_services = services.get_cached_services()
        for service in cached_services:
            cache_name = self._to_field_name(service.name) + "Cache"
            ttl_ms = service.get_cache_ttl_ms() or 300000  # 5 min default
            ttl_seconds = ttl_ms // 1000
            lines.append(f"        this.{cache_name} = Caffeine.newBuilder()")
            lines.append(f"            .expireAfterWrite({ttl_seconds}, TimeUnit.SECONDS)")
            lines.append(f"            .build();")

        return '\n'.join(lines)

    def generate_service_call_methods(self, services: ServicesBlock) -> str:
        """Generate wrapper methods for calling services.

        Args:
            services: ServicesBlock AST node

        Returns:
            Java code for service call methods
        """
        if not services or not services.services:
            return ""

        lines = []

        for service in services.services:
            lines.append(self._generate_service_call_method(service))
            lines.append("")

        return '\n'.join(lines)

    def _generate_service_call_method(self, service: ServiceDecl) -> str:
        """Generate a single service call wrapper method."""
        method_name = "call" + self._to_java_class_name(service.name)
        return_type = self._map_service_return_type(service.return_type)
        params = self._generate_service_params(service.params)
        param_names = ", ".join(p.name for p in service.params)
        service_field = self._to_field_name(service.class_name)

        lines = []
        lines.append(f"    /**")
        lines.append(f"     * Service call: {service.name}")
        lines.append(f"     * Type: {service.service_type.value}")
        if service.options:
            if service.options.timeout:
                lines.append(f"     * Timeout: {service.options.timeout}")
            if service.options.fallback:
                lines.append(f"     * Fallback: {service.options.fallback}")
            if service.options.retry:
                lines.append(f"     * Retry: {service.options.retry}")
        lines.append(f"     */")
        lines.append(f"    protected {return_type} {method_name}({params}) {{")

        if service.is_cached():
            lines.extend(self._generate_cached_call_body(service, service_field, param_names))
        elif service.is_async():
            lines.extend(self._generate_async_call_body(service, service_field, param_names))
        else:
            lines.extend(self._generate_sync_call_body(service, service_field, param_names))

        lines.append(f"    }}")
        return '\n'.join(lines)

    def _generate_sync_call_body(
        self,
        service: ServiceDecl,
        service_field: str,
        param_names: str
    ) -> List[str]:
        """Generate sync service call body with try/catch and fallback."""
        lines = []
        fallback = self._get_fallback_value(service)
        retry_count = service.get_retry_count()

        lines.append(f"        try {{")

        if retry_count > 0:
            lines.append(f"            int retries = 0;")
            lines.append(f"            while (retries <= {retry_count}) {{")
            lines.append(f"                try {{")
            lines.append(f"                    return {service_field}.{service.method_name}({param_names});")
            lines.append(f"                }} catch (Exception e) {{")
            lines.append(f"                    retries++;")
            lines.append(f"                    if (retries > {retry_count}) throw e;")
            lines.append(f"                    LOG.warn(\"Retry {{}} for {service.name}\", retries);")
            lines.append(f"                }}")
            lines.append(f"            }}")
            lines.append(f"            return {fallback}; // Should not reach here")
        else:
            lines.append(f"            return {service_field}.{service.method_name}({param_names});")

        lines.append(f"        }} catch (Exception e) {{")
        lines.append(f"            LOG.warn(\"{service.name} service failed, using fallback\", e);")
        lines.append(f"            return {fallback};")
        lines.append(f"        }}")

        return lines

    def _generate_async_call_body(
        self,
        service: ServiceDecl,
        service_field: str,
        param_names: str
    ) -> List[str]:
        """Generate async service call body with timeout and fallback."""
        lines = []
        fallback = self._get_fallback_value(service)
        timeout_ms = service.get_timeout_ms() or 1000

        lines.append(f"        try {{")
        lines.append(f"            return {service_field}.{service.method_name}({param_names})")
        lines.append(f"                .orTimeout({timeout_ms}, TimeUnit.MILLISECONDS)")
        lines.append(f"                .exceptionally(ex -> {{")
        lines.append(f"                    LOG.warn(\"{service.name} service failed, using fallback\", ex);")
        lines.append(f"                    return {fallback};")
        lines.append(f"                }})")
        lines.append(f"                .join();")
        lines.append(f"        }} catch (Exception e) {{")
        lines.append(f"            LOG.warn(\"{service.name} async call failed\", e);")
        lines.append(f"            return {fallback};")
        lines.append(f"        }}")

        return lines

    def _generate_cached_call_body(
        self,
        service: ServiceDecl,
        service_field: str,
        param_names: str
    ) -> List[str]:
        """Generate cached service call body."""
        lines = []
        cache_name = self._to_field_name(service.name) + "Cache"
        fallback = self._get_fallback_value(service)

        # Generate cache key
        if len(service.params) == 1:
            cache_key = service.params[0].name
        else:
            # Create composite key
            cache_key = f"String.valueOf({param_names})"

        lines.append(f"        return {cache_name}.get({cache_key}, key -> {{")
        lines.append(f"            try {{")
        lines.append(f"                return {service_field}.{service.method_name}({param_names});")
        lines.append(f"            }} catch (Exception e) {{")
        lines.append(f"                LOG.warn(\"{service.name} service failed for key {{}}\", key, e);")
        lines.append(f"                return {fallback};")
        lines.append(f"            }}")
        lines.append(f"        }});")

        return lines

    def _get_fallback_value(self, service: ServiceDecl) -> str:
        """Get Java fallback value for service."""
        if service.options and service.options.fallback:
            fallback = service.options.fallback
            # Convert AST literal to Java
            from backend.ast.rules.literals import (
                NullLiteral, IntegerLiteral, DecimalLiteral,
                StringLiteral, BooleanLiteral
            )

            if isinstance(fallback, NullLiteral):
                return "null"
            elif isinstance(fallback, IntegerLiteral):
                return str(fallback.value)
            elif isinstance(fallback, DecimalLiteral):
                return f"new BigDecimal(\"{fallback.value}\")"
            elif isinstance(fallback, StringLiteral):
                return f'"{fallback.value}"'
            elif isinstance(fallback, BooleanLiteral):
                return "true" if fallback.value else "false"

        # Default fallback based on return type
        return_type = service.return_type.lower()
        if return_type in ('decimal', 'number', 'bigdecimal'):
            return 'BigDecimal.ZERO'
        elif return_type in ('int', 'integer', 'long'):
            return '0'
        elif return_type in ('boolean', 'bool'):
            return 'false'
        elif return_type in ('string', 'text'):
            return '""'
        else:
            return 'null'

    def _generate_service_params(self, params: List[ServiceParam]) -> str:
        """Generate Java parameter list for service method."""
        java_params = []
        for param in params:
            java_type = self._map_service_param_type(param.param_type)
            java_params.append(f"{java_type} {param.name}")
        return ", ".join(java_params)

    def _map_service_param_type(self, param_type: str) -> str:
        """Map DSL parameter type to Java type."""
        type_map = {
            'text': 'String',
            'string': 'String',
            'number': 'BigDecimal',
            'decimal': 'BigDecimal',
            'integer': 'Integer',
            'boolean': 'Boolean',
            'date': 'LocalDate',
            'timestamp': 'Instant',
            'datetime': 'Instant',
        }
        return type_map.get(param_type.lower(), param_type)

    def _map_service_return_type(self, return_type: str) -> str:
        """Map DSL return type to Java type."""
        type_map = {
            'text': 'String',
            'string': 'String',
            'number': 'BigDecimal',
            'decimal': 'BigDecimal',
            'integer': 'Integer',
            'boolean': 'Boolean',
            'date': 'LocalDate',
            'timestamp': 'Instant',
            'datetime': 'Instant',
        }
        return type_map.get(return_type.lower(), return_type)

    def _get_cache_key_type(self, service: ServiceDecl) -> str:
        """Get cache key type based on service parameters."""
        if len(service.params) == 1:
            return self._map_service_param_type(service.params[0].param_type)
        return "String"  # Composite key as string

    def _to_field_name(self, class_name: str) -> str:
        """Convert class name to field name (camelCase)."""
        if not class_name:
            return "service"
        return class_name[0].lower() + class_name[1:]

    def _to_java_class_name(self, name: str) -> str:
        """Convert DSL name to Java class name (PascalCase)."""
        parts = name.replace('-', '_').split('_')
        return ''.join(part.capitalize() for part in parts)

    def get_services_imports(self, services: ServicesBlock) -> Set[str]:
        """Get required imports for service generation."""
        if not services or not services.services:
            return set()

        imports = set()
        imports.add('java.util.concurrent.TimeUnit')
        imports.add('org.slf4j.Logger')
        imports.add('org.slf4j.LoggerFactory')

        for service in services.services:
            if service.is_async():
                imports.add('java.util.concurrent.CompletableFuture')

            if service.is_cached():
                imports.add('com.github.benmanes.caffeine.cache.Cache')
                imports.add('com.github.benmanes.caffeine.cache.Caffeine')

            # Add type imports
            return_type = self._map_service_return_type(service.return_type)
            if return_type == 'BigDecimal':
                imports.add('java.math.BigDecimal')
            elif return_type == 'LocalDate':
                imports.add('java.time.LocalDate')
            elif return_type == 'Instant':
                imports.add('java.time.Instant')

            for param in service.params:
                param_type = self._map_service_param_type(param.param_type)
                if param_type == 'BigDecimal':
                    imports.add('java.math.BigDecimal')
                elif param_type == 'LocalDate':
                    imports.add('java.time.LocalDate')
                elif param_type == 'Instant':
                    imports.add('java.time.Instant')

        return imports

    def has_services(self, program: 'ast.Program') -> bool:
        """Check if program has service declarations."""
        return program.services is not None and len(program.services.services) > 0
