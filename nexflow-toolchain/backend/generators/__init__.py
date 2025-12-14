# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Nexflow Generators Module
# Code generators for Flink, Spark, and other targets

from typing import Optional, Dict, Type

from backend.generators.base import (
    BaseGenerator,
    GeneratorConfig,
    GeneratedFile,
    GenerationResult,
)
from backend.generators.voltage import (
    VoltageProfile,
    VoltageProfilesConfig,
)
from backend.generators.pom_generator import (
    generate_pom,
    write_pom,
)
from backend.generators.schema_generator import SchemaGenerator
from backend.generators.flow import FlowGenerator
from backend.generators.transform import TransformGenerator
from backend.generators.rules import RulesGenerator
from backend.generators.scaffold_generator import ScaffoldGenerator
from backend.generators.runtime import RuntimeGenerator

# Generator registry - maps DSL type to generator class
GENERATORS: Dict[str, Type[BaseGenerator]] = {
    'schema': SchemaGenerator,
    'flow': FlowGenerator,
    'transform': TransformGenerator,
    'rules': RulesGenerator,
    'scaffold': ScaffoldGenerator,
}


def get_generator(lang: str, config: GeneratorConfig) -> Optional[BaseGenerator]:
    """
    Factory function to get a generator instance for a DSL type.

    Args:
        lang: DSL type ('schema', 'flow', 'transform', 'rules')
        config: Generator configuration

    Returns:
        Generator instance or None if not found
    """
    generator_class = GENERATORS.get(lang)
    if generator_class:
        return generator_class(config)
    return None


__all__ = [
    'BaseGenerator',
    'GeneratorConfig',
    'GeneratedFile',
    'GenerationResult',
    'SchemaGenerator',
    'FlowGenerator',
    'TransformGenerator',
    'RulesGenerator',
    'ScaffoldGenerator',
    'RuntimeGenerator',
    'VoltageProfile',
    'VoltageProfilesConfig',
    'GENERATORS',
    'get_generator',
    'generate_pom',
    'write_pom',
]
