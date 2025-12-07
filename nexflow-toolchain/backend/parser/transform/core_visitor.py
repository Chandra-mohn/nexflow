"""
Core Visitor Mixin for Transform Parser

Handles parsing of top-level elements: program, transform definitions,
and transform block definitions.
"""

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformCoreVisitorMixin:
    """Mixin for core transform visitor methods."""

    def visitProgram(self, ctx: TransformDSLParser.ProgramContext) -> ast.Program:
        transforms = []
        transform_blocks = []

        for child in ctx.getChildren():
            if isinstance(child, TransformDSLParser.TransformDefContext):
                transforms.append(self.visitTransformDef(child))
            elif isinstance(child, TransformDSLParser.TransformBlockDefContext):
                transform_blocks.append(self.visitTransformBlockDef(child))

        return ast.Program(
            transforms=transforms,
            transform_blocks=transform_blocks,
            location=self._get_location(ctx)
        )

    def visitTransformDef(self, ctx: TransformDSLParser.TransformDefContext) -> ast.TransformDef:
        name = self._get_text(ctx.transformName())

        metadata = None
        if ctx.transformMetadata():
            metadata = self.visitTransformMetadata(ctx.transformMetadata())

        pure = None
        if ctx.purityDecl():
            pure = True

        cache = None
        if ctx.cacheDecl():
            cache = self.visitCacheDecl(ctx.cacheDecl())

        input_spec = None
        if ctx.inputSpec():
            input_spec = self.visitInputSpec(ctx.inputSpec())

        output_spec = None
        if ctx.outputSpec():
            output_spec = self.visitOutputSpec(ctx.outputSpec())

        validate_input = None
        if ctx.validateInputBlock():
            validate_input = self.visitValidateInputBlock(ctx.validateInputBlock())

        apply = None
        if ctx.applyBlock():
            apply = self.visitApplyBlock(ctx.applyBlock())

        validate_output = None
        if ctx.validateOutputBlock():
            validate_output = self.visitValidateOutputBlock(ctx.validateOutputBlock())

        on_error = None
        if ctx.onErrorBlock():
            on_error = self.visitOnErrorBlock(ctx.onErrorBlock())

        return ast.TransformDef(
            name=name,
            metadata=metadata,
            pure=pure,
            cache=cache,
            input=input_spec,
            output=output_spec,
            validate_input=validate_input,
            apply=apply,
            validate_output=validate_output,
            on_error=on_error,
            location=self._get_location(ctx)
        )

    def visitTransformBlockDef(self, ctx: TransformDSLParser.TransformBlockDefContext) -> ast.TransformBlockDef:
        name = self._get_text(ctx.transformName())

        metadata = None
        if ctx.transformMetadata():
            metadata = self.visitTransformMetadata(ctx.transformMetadata())

        use = None
        if ctx.useBlock():
            use = self.visitUseBlock(ctx.useBlock())

        input_spec = None
        if ctx.inputSpec():
            input_spec = self.visitInputSpec(ctx.inputSpec())

        output_spec = None
        if ctx.outputSpec():
            output_spec = self.visitOutputSpec(ctx.outputSpec())

        validate_input = None
        if ctx.validateInputBlock():
            validate_input = self.visitValidateInputBlock(ctx.validateInputBlock())

        invariant = None
        if ctx.invariantBlock():
            invariant = self.visitInvariantBlock(ctx.invariantBlock())

        mappings = None
        if ctx.mappingsBlock():
            mappings = self.visitMappingsBlock(ctx.mappingsBlock())

        compose = None
        if ctx.composeBlock():
            compose = self.visitComposeBlock(ctx.composeBlock())

        validate_output = None
        if ctx.validateOutputBlock():
            validate_output = self.visitValidateOutputBlock(ctx.validateOutputBlock())

        on_change = None
        if ctx.onChangeBlock():
            on_change = self.visitOnChangeBlock(ctx.onChangeBlock())

        on_error = None
        if ctx.onErrorBlock():
            on_error = self.visitOnErrorBlock(ctx.onErrorBlock())

        return ast.TransformBlockDef(
            name=name,
            metadata=metadata,
            use=use,
            input=input_spec,
            output=output_spec,
            validate_input=validate_input,
            invariant=invariant,
            mappings=mappings,
            compose=compose,
            validate_output=validate_output,
            on_change=on_change,
            on_error=on_error,
            location=self._get_location(ctx)
        )
