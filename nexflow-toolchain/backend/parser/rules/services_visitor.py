# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Services Visitor Mixin for Rules Parser

Handles parsing of services block for external service declarations.
"""


from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesServicesVisitorMixin:
    """Mixin for services block visitor methods."""

    def visitServicesBlock(self, ctx: RulesDSLParser.ServicesBlockContext) -> ast.ServicesBlock:
        """Parse services { } block."""
        services = []
        for service_ctx in ctx.serviceDecl():
            services.append(self.visitServiceDecl(service_ctx))

        return ast.ServicesBlock(
            services=services,
            location=self._get_location(ctx)
        )

    def visitServiceDecl(self, ctx: RulesDSLParser.ServiceDeclContext) -> ast.ServiceDecl:
        """Parse single service declaration."""
        name = self._get_text(ctx.serviceName())
        service_type_ctx = ctx.serviceType()
        service_type, cache_duration = self._parse_service_type(service_type_ctx)

        class_name = self._get_text(ctx.serviceClassName())
        method_name = self._get_text(ctx.serviceMethodName())
        return_type = self._get_text(ctx.serviceReturnType())

        # Parse parameters
        params = []
        param_list_ctx = ctx.serviceParamList()
        if param_list_ctx:
            for param_ctx in param_list_ctx.serviceParam():
                params.append(self.visitServiceParam(param_ctx))

        # Parse options
        options = None
        options_ctx = ctx.serviceOptions()
        if options_ctx:
            options = self.visitServiceOptions(options_ctx)

        return ast.ServiceDecl(
            name=name,
            service_type=service_type,
            class_name=class_name,
            method_name=method_name,
            params=params,
            return_type=return_type,
            cache_duration=cache_duration,
            options=options,
            location=self._get_location(ctx)
        )

    def _parse_service_type(self, ctx: RulesDSLParser.ServiceTypeContext) -> tuple:
        """Parse service type (sync, async, cached).

        Returns:
            Tuple of (ServiceType, Optional[Duration])
        """
        text = self._get_text(ctx)
        cache_duration = None

        if text.startswith('cached'):
            service_type = ast.ServiceType.CACHED
            # Parse cache duration
            duration_ctx = ctx.duration()
            if duration_ctx:
                cache_duration = self.visitDuration(duration_ctx)
        elif text == 'async':
            service_type = ast.ServiceType.ASYNC
        else:
            service_type = ast.ServiceType.SYNC

        return service_type, cache_duration

    def visitServiceParam(self, ctx: RulesDSLParser.ServiceParamContext) -> ast.ServiceParam:
        """Parse service parameter."""
        name = ctx.IDENTIFIER().getText()
        param_type = self._get_text(ctx.paramType())

        return ast.ServiceParam(
            name=name,
            param_type=param_type,
            location=self._get_location(ctx)
        )

    def visitServiceOptions(self, ctx: RulesDSLParser.ServiceOptionsContext) -> ast.ServiceOptions:
        """Parse service options (timeout, fallback, retry)."""
        timeout = None
        fallback = None
        retry = None

        for option_ctx in ctx.serviceOption():
            if option_ctx.TIMEOUT():
                timeout = self.visitDuration(option_ctx.duration())
            elif option_ctx.FALLBACK():
                fallback = self.visitLiteral(option_ctx.literal())
            elif option_ctx.RETRY():
                retry = int(option_ctx.INTEGER().getText())

        return ast.ServiceOptions(
            timeout=timeout,
            fallback=fallback,
            retry=retry,
            location=self._get_location(ctx)
        )

    def visitDuration(self, ctx: RulesDSLParser.DurationContext) -> ast.Duration:
        """Parse duration value (e.g., 500ms, 5m)."""
        value = int(ctx.INTEGER().getText())
        unit_ctx = ctx.durationUnit()
        unit_text = self._get_text(unit_ctx)

        unit_map = {
            'ms': ast.DurationUnit.MILLISECONDS,
            's': ast.DurationUnit.SECONDS,
            'm': ast.DurationUnit.MINUTES,
            'h': ast.DurationUnit.HOURS,
        }
        unit = unit_map.get(unit_text, ast.DurationUnit.MILLISECONDS)

        return ast.Duration(
            value=value,
            unit=unit,
            location=self._get_location(ctx)
        )
