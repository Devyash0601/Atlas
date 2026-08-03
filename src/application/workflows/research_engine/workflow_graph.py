"""WorkflowGraph DAG builder with cycle detection and topological ordering."""

from dataclasses import dataclass, field
from typing import Any

from src.application.workflows.research_engine.exceptions import CycleDetectedError


@dataclass
class WorkflowNode:
    """DAG Node representation."""

    node_id: str
    task_type: str
    inputs: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)


class WorkflowGraph:
    """Directed Acyclic Graph (DAG) construction and dependency tracking."""

    def __init__(self) -> None:
        self.nodes: dict[str, WorkflowNode] = {}
        self.edges: dict[str, list[str]] = {}  # node_id -> list of dependent child node_ids

    def add_node(
        self,
        node_id: str,
        task_type: str,
        inputs: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
    ) -> WorkflowNode:
        """Add node to DAG and update edge dependencies."""
        deps = dependencies or []
        node = WorkflowNode(
            node_id=node_id,
            task_type=task_type,
            inputs=inputs or {},
            dependencies=deps,
        )
        self.nodes[node_id] = node

        if node_id not in self.edges:
            self.edges[node_id] = []

        for parent_id in deps:
            if parent_id not in self.edges:
                self.edges[parent_id] = []
            self.edges[parent_id].append(node_id)

        self.detect_cycles()
        return node

    def detect_cycles(self) -> None:
        """Detect cyclic dependencies using depth-first search."""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(curr: str) -> None:
            visited.add(curr)
            rec_stack.add(curr)

            for neighbor in self.edges.get(curr, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    raise CycleDetectedError(
                        f"Cyclic dependency detected involving node '{neighbor}'."
                    )

            rec_stack.remove(curr)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

    def topological_sort(self) -> list[str]:
        """Return topological ordering of node IDs."""
        in_degree = dict.fromkeys(self.nodes, 0)
        for parent in self.edges:
            for child in self.edges[parent]:
                in_degree[child] += 1

        queue = [n for n, deg in in_degree.items() if deg == 0]
        order: list[str] = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in self.edges.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise CycleDetectedError("Cycle detected during topological sorting.")

        return order
