"""
Nexflow Language Server Driver

Main LSP server that orchestrates language modules.
Routes requests to appropriate modules based on file extension.
"""

import logging
from typing import Optional, List

from pygls.lsp.server import LanguageServer
from lsprotocol import types

from .registry import ModuleRegistry
from .modules.base import LanguageModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("nexflow-lsp")


class NexflowLanguageServer(LanguageServer):
    """
    Main Language Server for Nexflow DSLs.

    Orchestrates multiple language modules, routing LSP requests
    to the appropriate module based on file extension.

    Usage:
        server = NexflowLanguageServer()
        server.register_module(ProcModule())
        server.register_module(SchemaModule())
        server.start_io()
    """

    def __init__(self, name: str = "nexflow-lsp", version: str = "0.1.0"):
        super().__init__(name, version)
        self.registry = ModuleRegistry()
        self._document_diagnostics: dict = {}  # Cache diagnostics per document

        logger.info(f"Initializing {name} v{version}")

    def register_module(self, module: LanguageModule) -> None:
        """
        Register a language module with the server.

        Args:
            module: LanguageModule instance to register
        """
        self.registry.register(module)
        logger.info(f"Registered: {module.display_name}")

    def get_module(self, uri: str) -> Optional[LanguageModule]:
        """
        Get the appropriate module for a document URI.

        Args:
            uri: Document URI (e.g., 'file:///path/to/file.proc')

        Returns:
            LanguageModule or None if no module handles this file type
        """
        return self.registry.get_by_uri(uri)

    def get_all_trigger_characters(self) -> List[str]:
        """Get combined trigger characters from all modules."""
        chars = set()
        for module in self.registry:
            chars.update(module.trigger_characters)
        return list(chars)


# Create the server instance
server = NexflowLanguageServer()


# =============================================================================
# Document Synchronization
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: NexflowLanguageServer, params: types.DidOpenTextDocumentParams):
    """Handle document open - validate and publish diagnostics."""
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.diagnostics:
        doc = ls.workspace.get_text_document(uri)
        diagnostics = module.get_diagnostics(uri, doc.source)

        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=doc.version,
                diagnostics=diagnostics
            )
        )
        logger.debug(f"Published {len(diagnostics)} diagnostics for {uri}")


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: NexflowLanguageServer, params: types.DidChangeTextDocumentParams):
    """Handle document change - re-validate and publish diagnostics."""
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.diagnostics:
        doc = ls.workspace.get_text_document(uri)
        diagnostics = module.get_diagnostics(uri, doc.source)

        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=doc.version,
                diagnostics=diagnostics
            )
        )


@server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: NexflowLanguageServer, params: types.DidCloseTextDocumentParams):
    """Handle document close - clear diagnostics."""
    uri = params.text_document.uri

    # Clear diagnostics for closed document
    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=uri,
            diagnostics=[]
        )
    )
    logger.debug(f"Cleared diagnostics for {uri}")


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: NexflowLanguageServer, params: types.DidSaveTextDocumentParams):
    """Handle document save - re-validate."""
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.diagnostics:
        doc = ls.workspace.get_text_document(uri)
        diagnostics = module.get_diagnostics(uri, doc.source)

        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=doc.version,
                diagnostics=diagnostics
            )
        )


# =============================================================================
# Completion
# =============================================================================

@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(
        trigger_characters=[" ", "\n"],
        resolve_provider=False
    )
)
def completions(
    ls: NexflowLanguageServer,
    params: types.CompletionParams
) -> types.CompletionList:
    """
    Handle completion request.

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.completion:
        doc = ls.workspace.get_text_document(uri)
        trigger_char = None
        if params.context:
            trigger_char = params.context.trigger_character

        items = module.get_completions(
            uri,
            doc.source,
            params.position,
            trigger_char
        )
        return types.CompletionList(is_incomplete=False, items=items)

    return types.CompletionList(is_incomplete=False, items=[])


# =============================================================================
# Hover
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(
    ls: NexflowLanguageServer,
    params: types.HoverParams
) -> Optional[types.Hover]:
    """
    Handle hover request.

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.hover:
        doc = ls.workspace.get_text_document(uri)
        return module.get_hover(uri, doc.source, params.position)

    return None


# =============================================================================
# Document Symbols
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(
    ls: NexflowLanguageServer,
    params: types.DocumentSymbolParams
) -> List[types.DocumentSymbol]:
    """
    Handle document symbol request (outline view).

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.symbols:
        doc = ls.workspace.get_text_document(uri)
        return module.get_symbols(uri, doc.source)

    return []


# =============================================================================
# Go to Definition
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_DEFINITION)
def definition(
    ls: NexflowLanguageServer,
    params: types.DefinitionParams
) -> Optional[types.Location]:
    """
    Handle go-to-definition request.

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.definition:
        doc = ls.workspace.get_text_document(uri)
        return module.get_definition(uri, doc.source, params.position)

    return None


# =============================================================================
# Find References
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_REFERENCES)
def references(
    ls: NexflowLanguageServer,
    params: types.ReferenceParams
) -> List[types.Location]:
    """
    Handle find-references request.

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.references:
        doc = ls.workspace.get_text_document(uri)
        return module.get_references(
            uri,
            doc.source,
            params.position,
            params.context.include_declaration
        )

    return []


# =============================================================================
# Formatting
# =============================================================================

@server.feature(types.TEXT_DOCUMENT_FORMATTING)
def formatting(
    ls: NexflowLanguageServer,
    params: types.DocumentFormattingParams
) -> List[types.TextEdit]:
    """
    Handle document formatting request.

    Routes to appropriate module based on file extension.
    """
    uri = params.text_document.uri
    module = ls.get_module(uri)

    if module and module.capabilities.formatting:
        doc = ls.workspace.get_text_document(uri)
        return module.format_document(uri, doc.source, params.options)

    return []
