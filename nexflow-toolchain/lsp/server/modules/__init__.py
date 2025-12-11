"""
Nexflow LSP Language Modules

Each module implements support for one DSL layer:
- proc_module: L1 ProcDSL (Process Orchestration)
- schema_module: L2 SchemaDSL (Data Schemas)
- transform_module: L3 TransformDSL (Transformations)
- rules_module: L4 RulesDSL (Decision Logic)
"""

from .base import LanguageModule, ModuleCapabilities

__all__ = ["LanguageModule", "ModuleCapabilities"]
