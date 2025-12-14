# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Metadata Visitor Mixin for Transform Parser

Handles parsing of metadata, versioning, compatibility, and caching declarations.
"""

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformMetadataVisitorMixin:
    """Mixin for metadata visitor methods."""

    def visitTransformMetadata(self, ctx: TransformDSLParser.TransformMetadataContext) -> ast.TransformMetadata:
        version = None
        description = None
        previous_version = None
        compatibility = None

        if ctx.versionDecl():
            version = ctx.versionDecl().VERSION_NUMBER().getText()

        if ctx.descriptionDecl():
            description = self._strip_quotes(ctx.descriptionDecl().STRING().getText())

        if ctx.previousVersionDecl():
            previous_version = ctx.previousVersionDecl().VERSION_NUMBER().getText()

        if ctx.compatibilityDecl():
            compatibility = self.visitCompatibilityDecl(ctx.compatibilityDecl())

        return ast.TransformMetadata(
            version=version,
            description=description,
            previous_version=previous_version,
            compatibility=compatibility,
            location=self._get_location(ctx)
        )

    def visitCompatibilityDecl(self, ctx: TransformDSLParser.CompatibilityDeclContext) -> ast.CompatibilityMode:
        mode_ctx = ctx.compatibilityMode()
        mode_text = self._get_text(mode_ctx).lower()
        mode_map = {
            'backward': ast.CompatibilityMode.BACKWARD,
            'forward': ast.CompatibilityMode.FORWARD,
            'full': ast.CompatibilityMode.FULL,
            'none': ast.CompatibilityMode.NONE,
        }
        return mode_map.get(mode_text, ast.CompatibilityMode.BACKWARD)

    def visitCacheDecl(self, ctx: TransformDSLParser.CacheDeclContext) -> ast.CacheDecl:
        ttl = None
        key_fields = None

        if ctx.cacheTtl():
            ttl = self.visitDuration(ctx.cacheTtl().duration())

        if ctx.cacheKey():
            key_fields = self._get_field_array(ctx.cacheKey().fieldArray())

        return ast.CacheDecl(
            ttl=ttl,
            key_fields=key_fields,
            location=self._get_location(ctx)
        )

    def visitUseBlock(self, ctx: TransformDSLParser.UseBlockContext) -> ast.UseBlock:
        transforms = [ident.getText() for ident in ctx.IDENTIFIER()]
        return ast.UseBlock(
            transforms=transforms,
            location=self._get_location(ctx)
        )
