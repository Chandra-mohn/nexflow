"""
Module Registry

Manages registration and lookup of language modules.
Supports dynamic loading and extension-based routing.
"""

from typing import Dict, List, Optional
from pathlib import Path
import logging

from .modules.base import LanguageModule

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """
    Registry for language modules.

    Handles:
    - Module registration by language_id
    - Extension-to-module mapping
    - Module lookup by file URI or extension

    Usage:
        registry = ModuleRegistry()
        registry.register(ProcModule())
        registry.register(SchemaModule())

        module = registry.get_by_uri("file:///path/to/file.proc")
        # Returns ProcModule instance
    """

    def __init__(self):
        self._modules: Dict[str, LanguageModule] = {}
        self._extension_map: Dict[str, str] = {}  # ext -> language_id
        self._registered_order: List[str] = []  # Track registration order

    def register(self, module: LanguageModule) -> None:
        """
        Register a language module.

        Args:
            module: LanguageModule instance to register

        Raises:
            ValueError: If module with same language_id already registered
            ValueError: If extension already mapped to another module
        """
        lang_id = module.language_id

        # Check for duplicate language_id
        if lang_id in self._modules:
            raise ValueError(
                f"Module with language_id '{lang_id}' already registered"
            )

        # Check for extension conflicts
        for ext in module.file_extensions:
            if ext in self._extension_map:
                existing_id = self._extension_map[ext]
                raise ValueError(
                    f"Extension '{ext}' already mapped to module '{existing_id}'"
                )

        # Register module
        self._modules[lang_id] = module
        self._registered_order.append(lang_id)

        # Map extensions to language_id
        for ext in module.file_extensions:
            # Normalize extension (ensure leading dot)
            normalized_ext = ext if ext.startswith(".") else f".{ext}"
            self._extension_map[normalized_ext] = lang_id

        logger.info(
            f"Registered module: {module.display_name} "
            f"(extensions: {module.file_extensions})"
        )

    def unregister(self, language_id: str) -> Optional[LanguageModule]:
        """
        Unregister a module by language_id.

        Args:
            language_id: ID of module to remove

        Returns:
            The removed module, or None if not found
        """
        module = self._modules.pop(language_id, None)
        if module:
            # Remove extension mappings
            for ext in module.file_extensions:
                normalized_ext = ext if ext.startswith(".") else f".{ext}"
                self._extension_map.pop(normalized_ext, None)

            # Remove from order tracking
            if language_id in self._registered_order:
                self._registered_order.remove(language_id)

            logger.info(f"Unregistered module: {module.display_name}")

        return module

    def get_by_language_id(self, language_id: str) -> Optional[LanguageModule]:
        """
        Get module by its language_id.

        Args:
            language_id: e.g., 'procdsl', 'schemadsl'

        Returns:
            LanguageModule or None
        """
        return self._modules.get(language_id)

    def get_by_extension(self, extension: str) -> Optional[LanguageModule]:
        """
        Get module by file extension.

        Args:
            extension: e.g., '.proc', '.schema', 'proc'

        Returns:
            LanguageModule or None
        """
        # Normalize extension
        normalized_ext = extension if extension.startswith(".") else f".{extension}"
        lang_id = self._extension_map.get(normalized_ext)
        return self._modules.get(lang_id) if lang_id else None

    def get_by_uri(self, uri: str) -> Optional[LanguageModule]:
        """
        Get module for a document URI.

        Args:
            uri: Document URI, e.g., 'file:///path/to/file.proc'

        Returns:
            LanguageModule or None
        """
        # Extract extension from URI
        path = uri.replace("file://", "")
        ext = Path(path).suffix
        return self.get_by_extension(ext)

    def get_all(self) -> List[LanguageModule]:
        """
        Get all registered modules in registration order.

        Returns:
            List of LanguageModule instances
        """
        return [self._modules[lang_id] for lang_id in self._registered_order]

    def get_supported_extensions(self) -> List[str]:
        """
        Get all supported file extensions.

        Returns:
            List of extensions (e.g., ['.proc', '.schema', '.xform', '.rules'])
        """
        return list(self._extension_map.keys())

    def get_language_ids(self) -> List[str]:
        """
        Get all registered language IDs.

        Returns:
            List of language IDs
        """
        return list(self._registered_order)

    def is_supported(self, uri_or_extension: str) -> bool:
        """
        Check if a file or extension is supported.

        Args:
            uri_or_extension: File URI or extension

        Returns:
            True if supported by a registered module
        """
        if uri_or_extension.startswith("file://") or "/" in uri_or_extension:
            return self.get_by_uri(uri_or_extension) is not None
        return self.get_by_extension(uri_or_extension) is not None

    def __len__(self) -> int:
        """Number of registered modules."""
        return len(self._modules)

    def __contains__(self, language_id: str) -> bool:
        """Check if language_id is registered."""
        return language_id in self._modules

    def __iter__(self):
        """Iterate over registered modules."""
        return iter(self.get_all())

    def __repr__(self) -> str:
        modules = ", ".join(self._registered_order)
        return f"<ModuleRegistry modules=[{modules}]>"
