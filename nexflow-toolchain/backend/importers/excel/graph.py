"""
Relationship graph builder for entity hierarchy resolution.

Builds a directed graph of entity relationships to:
- Resolve parent-child composition hierarchies (unlimited depth)
- Detect circular references
- Determine entity generation order (topological sort)
- Track cross-domain dependencies
"""

from dataclasses import dataclass, field
from typing import Optional
import logging

from .models import ServiceDomain, Entity

logger = logging.getLogger(__name__)


class GraphError(Exception):
    """Error in relationship graph building."""


@dataclass
class EntityNode:
    """Node in the entity relationship graph."""
    entity: Entity
    parent: Optional["EntityNode"] = None
    children: list["EntityNode"] = field(default_factory=list)
    depth: int = 0


@dataclass
class DomainGraph:
    """Complete graph of entities and relationships for a domain."""
    domain: ServiceDomain
    nodes: dict[str, EntityNode] = field(default_factory=dict)
    root_entities: list[str] = field(default_factory=list)
    generation_order: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class GraphBuilder:
    """Build entity relationship graph from ServiceDomain."""

    def __init__(self, domain: ServiceDomain):
        self.domain = domain
        self.warnings: list[str] = []

    def build(self) -> DomainGraph:
        """Build the complete entity graph."""
        graph = DomainGraph(domain=self.domain)

        # Create nodes for all entities
        for entity_name, entity in self.domain.entities.items():
            graph.nodes[entity_name] = EntityNode(entity=entity)

        # Build parent-child relationships
        self._build_hierarchy(graph)

        # Find root entities (no parent)
        self._find_roots(graph)

        # Calculate depth for each entity
        self._calculate_depths(graph)

        # Topological sort for generation order
        self._compute_generation_order(graph)

        # Detect circular references
        self._detect_cycles(graph)

        graph.warnings = self.warnings
        return graph

    def _build_hierarchy(self, graph: DomainGraph):
        """Build parent-child relationships from Relationships data."""
        for rel in self.domain.relationships:
            if not rel.is_composition():
                continue  # Only handle composition relationships

            parent_node = graph.nodes.get(rel.parent_entity)
            child_node = graph.nodes.get(rel.child_entity)

            if not parent_node:
                self.warnings.append(
                    f"Relationship '{rel.name}': Parent entity '{rel.parent_entity}' not found"
                )
                continue

            if not child_node:
                self.warnings.append(
                    f"Relationship '{rel.name}': Child entity '{rel.child_entity}' not found"
                )
                continue

            # Establish parent-child link
            child_node.parent = parent_node
            parent_node.children.append(child_node)

            logger.debug(f"Linked {rel.parent_entity} -> {rel.child_entity}")

    def _find_roots(self, graph: DomainGraph):
        """Identify root entities (no parent in composition hierarchy)."""
        for entity_name, node in graph.nodes.items():
            if node.parent is None:
                graph.root_entities.append(entity_name)
                logger.debug(f"Root entity: {entity_name}")

    def _calculate_depths(self, graph: DomainGraph):
        """Calculate depth of each entity in the hierarchy."""
        def set_depth(node: EntityNode, depth: int):
            node.depth = depth
            for child in node.children:
                set_depth(child, depth + 1)

        for root_name in graph.root_entities:
            root_node = graph.nodes[root_name]
            set_depth(root_node, 0)

    def _compute_generation_order(self, graph: DomainGraph):
        """
        Compute topological order for schema generation.

        Children must be generated before parents (so parent can reference child type).
        """
        visited: set[str] = set()
        order: list[str] = []

        def visit(entity_name: str):
            if entity_name in visited:
                return
            visited.add(entity_name)

            node = graph.nodes.get(entity_name)
            if node:
                # Visit children first (depth-first)
                for child in node.children:
                    visit(child.entity.entity_name)

            order.append(entity_name)

        # Start from roots
        for root in graph.root_entities:
            visit(root)

        # Add any orphaned entities not in hierarchy
        for entity_name in graph.nodes:
            if entity_name not in visited:
                order.append(entity_name)

        graph.generation_order = order
        logger.info(f"Generation order: {order}")

    def _detect_cycles(self, graph: DomainGraph):
        """Detect circular composition references."""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(entity_name: str) -> bool:
            visited.add(entity_name)
            rec_stack.add(entity_name)

            node = graph.nodes.get(entity_name)
            if node:
                for child in node.children:
                    child_name = child.entity.entity_name
                    if child_name not in visited:
                        if has_cycle(child_name):
                            return True
                    elif child_name in rec_stack:
                        self.warnings.append(
                            f"CIRCULAR_COMPOSITION: Cycle detected involving '{entity_name}' -> '{child_name}'"
                        )
                        return True

            rec_stack.remove(entity_name)
            return False

        for entity_name in graph.nodes:
            if entity_name not in visited:
                has_cycle(entity_name)


class CrossDomainResolver:
    """Resolve shortcut entity references across multiple domains."""

    def __init__(self):
        self.domains: dict[str, DomainGraph] = {}
        self.entity_to_domain: dict[str, str] = {}
        self.unresolved: list[tuple[str, str]] = []  # (domain, entity)

    def add_domain(self, graph: DomainGraph):
        """Add a domain graph for cross-reference resolution."""
        domain_name = graph.domain.name
        self.domains[domain_name] = graph

        # Index managed entities by name
        for entity_name in graph.domain.managed_entities:
            entity = graph.domain.entities.get(entity_name)
            if entity:
                schema_name = entity.get_schema_name()
                self.entity_to_domain[schema_name] = domain_name
                self.entity_to_domain[entity_name] = domain_name

    def resolve_shortcuts(self) -> dict[str, dict[str, str]]:
        """
        Resolve all shortcut entity references.

        Returns:
            Dict mapping domain -> entity -> source_domain
        """
        resolutions: dict[str, dict[str, str]] = {}

        for domain_name, graph in self.domains.items():
            resolutions[domain_name] = {}

            for entity_name in graph.domain.external_references:
                entity = graph.domain.entities.get(entity_name)
                if not entity:
                    continue

                schema_name = entity.get_schema_name()

                # Try to find source domain
                source_domain = self.entity_to_domain.get(schema_name)
                if not source_domain:
                    source_domain = self.entity_to_domain.get(entity_name)

                if source_domain:
                    resolutions[domain_name][entity_name] = source_domain
                    logger.info(f"Resolved shortcut: {domain_name}/{entity_name} -> {source_domain}")
                else:
                    self.unresolved.append((domain_name, entity_name))
                    logger.warning(f"Unresolved shortcut: {domain_name}/{entity_name}")

        return resolutions

    def get_dependencies(self) -> dict[str, dict[str, list[str]]]:
        """
        Get cross-domain dependency manifest.

        Returns:
            Dict mapping domain -> depends_on -> [entities]
        """
        resolutions = self.resolve_shortcuts()
        dependencies: dict[str, dict[str, list[str]]] = {}

        for domain_name, entity_sources in resolutions.items():
            dependencies[domain_name] = {"depends_on": {}}

            for entity_name, source_domain in entity_sources.items():
                if source_domain not in dependencies[domain_name]["depends_on"]:
                    dependencies[domain_name]["depends_on"][source_domain] = []
                dependencies[domain_name]["depends_on"][source_domain].append(entity_name)

        return dependencies
