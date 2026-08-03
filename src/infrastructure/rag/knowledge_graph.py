"""KnowledgeGraph storing nodes (Paper, Section, Claim, Figure, Table, Equation) and typed edges."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    """Knowledge Graph Node."""

    node_id: str
    kind: str  # Paper, Section, Figure, Table, Equation, Claim, Reference, Chunk
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Knowledge Graph Edge."""

    source_id: str
    target_id: str
    relation: str  # contains, supports, references, derived_from, mentions, contradicts, extends


class KnowledgeGraph:
    """In-memory and persistent Knowledge Graph representation."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_node(
        self, node_id: str, kind: str, metadata: dict[str, Any] | None = None
    ) -> GraphNode:
        """Add node to graph."""
        node = GraphNode(node_id=node_id, kind=kind, metadata=metadata or {})
        self.nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, relation: str) -> GraphEdge:
        """Add directed edge to graph."""
        edge = GraphEdge(source_id=source_id, target_id=target_id, relation=relation)
        self.edges.append(edge)
        return edge

    def get_related_nodes(self, node_id: str, relation: str | None = None) -> list[GraphNode]:
        """Find related target nodes from source node."""
        targets: list[GraphNode] = []
        for e in self.edges:
            if e.source_id == node_id and (relation is None or e.relation == relation):
                if e.target_id in self.nodes:
                    targets.append(self.nodes[e.target_id])
        return targets

    def count_nodes(self) -> int:
        """Return count of graph nodes."""
        return len(self.nodes)

    def count_edges(self) -> int:
        """Return count of graph edges."""
        return len(self.edges)
