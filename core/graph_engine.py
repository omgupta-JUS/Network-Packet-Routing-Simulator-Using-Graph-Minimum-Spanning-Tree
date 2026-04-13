"""
graph_engine.py — Core Graph Engine for the Network Packet Routing Simulator.

This module provides the NetworkGraph class, which encapsulates all graph
operations including:
  - Adding / removing routers (nodes) and links (edges)
  - Computing Minimum Spanning Trees using Kruskal's and Prim's algorithms
  - Computing shortest paths using Dijkstra's algorithm
  - Generating preset network topologies (ring, star, mesh, tree, random)
  - Simulating link failures and dynamic re-routing

Author: Network Packet Routing Simulator Team
"""

import networkx as nx
import random
from typing import Optional


class NetworkGraph:
    """
    A wrapper around a networkx.Graph that models a network of routers
    connected by weighted links (representing latency, bandwidth cost, etc.).
    """

    def __init__(self):
        """Initialize an empty undirected weighted graph."""
        self.graph = nx.Graph()

    # ─── Node (Router) Management ───────────────────────────────────────

    def add_router(self, router_id: str, label: str = "", **attrs) -> None:
        """
        Add a router (node) to the network.

        Args:
            router_id: Unique identifier for the router (e.g., "R1").
            label: Human-readable label. Defaults to the router_id.
            **attrs: Extra attributes such as x/y coordinates.
        """
        if not label:
            label = router_id
        self.graph.add_node(router_id, label=label, **attrs)

    def remove_router(self, router_id: str) -> None:
        """
        Remove a router and all its connected links from the network.

        Args:
            router_id: Identifier of the router to remove.
        """
        if router_id in self.graph:
            self.graph.remove_node(router_id)

    def get_routers(self) -> list:
        """Return a sorted list of all router IDs."""
        return sorted(self.graph.nodes())

    # ─── Edge (Link) Management ─────────────────────────────────────────

    def add_link(self, router_a: str, router_b: str, weight: float = 1.0, **attrs) -> None:
        """
        Add a bidirectional link (edge) between two routers.

        Args:
            router_a: First router ID.
            router_b: Second router ID.
            weight: Cost / latency of the link (must be > 0).
            **attrs: Extra attributes (e.g., bandwidth).
        """
        # Auto-create routers if they don't exist yet
        if router_a not in self.graph:
            self.add_router(router_a)
        if router_b not in self.graph:
            self.add_router(router_b)
        self.graph.add_edge(router_a, router_b, weight=weight, **attrs)

    def remove_link(self, router_a: str, router_b: str) -> None:
        """
        Remove the link between two routers (simulates link failure).

        Args:
            router_a: First router ID.
            router_b: Second router ID.
        """
        if self.graph.has_edge(router_a, router_b):
            self.graph.remove_edge(router_a, router_b)

    def get_links(self) -> list:
        """Return a list of all links as (router_a, router_b, weight) tuples."""
        return [
            (u, v, d.get("weight", 1.0))
            for u, v, d in self.graph.edges(data=True)
        ]

    # ─── Algorithm: Minimum Spanning Tree ───────────────────────────────

    def compute_mst(self, algorithm: str = "kruskal") -> nx.Graph:
        """
        Compute the Minimum Spanning Tree of the current network.

        Args:
            algorithm: 'kruskal' or 'prim'. Defaults to 'kruskal'.

        Returns:
            A networkx.Graph representing the MST. Returns an empty graph if
            the original graph has no edges.

        Raises:
            ValueError: If an unsupported algorithm name is given.
        """
        if algorithm not in ("kruskal", "prim"):
            raise ValueError(f"Unsupported MST algorithm: '{algorithm}'. Use 'kruskal' or 'prim'.")

        if self.graph.number_of_edges() == 0:
            return nx.Graph()

        # NetworkX's minimum_spanning_tree supports both algorithms
        mst = nx.minimum_spanning_tree(self.graph, algorithm=algorithm, weight="weight")
        return mst

    def get_mst_edges(self, algorithm: str = "kruskal") -> list:
        """
        Get the edges of the MST as a list of (u, v, weight) tuples.

        Args:
            algorithm: 'kruskal' or 'prim'.

        Returns:
            List of (router_a, router_b, weight) tuples forming the MST.
        """
        mst = self.compute_mst(algorithm)
        return [
            (u, v, d.get("weight", 1.0))
            for u, v, d in mst.edges(data=True)
        ]

    def get_mst_total_weight(self, algorithm: str = "kruskal") -> float:
        """Return the total weight (cost) of the MST."""
        return sum(w for _, _, w in self.get_mst_edges(algorithm))

    # ─── Algorithm: Shortest Path (Dijkstra) ────────────────────────────

    def compute_shortest_path(self, source: str, target: str) -> tuple:
        """
        Compute the shortest (minimum-cost) path between two routers
        using Dijkstra's algorithm.

        Args:
            source: Source router ID.
            target: Destination router ID.

        Returns:
            A tuple (path, total_cost) where:
              - path is an ordered list of router IDs from source to target.
              - total_cost is the sum of edge weights along the path.
            Returns ([], float('inf')) if no path exists.
        """
        if source not in self.graph or target not in self.graph:
            return ([], float("inf"))

        try:
            path = nx.dijkstra_path(self.graph, source, target, weight="weight")
            cost = nx.dijkstra_path_length(self.graph, source, target, weight="weight")
            return (path, cost)
        except nx.NetworkXNoPath:
            return ([], float("inf"))

    def compute_all_shortest_paths(self, source: str) -> dict:
        """
        Compute shortest paths from a single source to ALL other routers.

        Args:
            source: The source router ID.

        Returns:
            A dict mapping each target router to (path, cost).
        """
        results = {}
        for node in self.graph.nodes():
            if node == source:
                continue
            results[node] = self.compute_shortest_path(source, node)
        return results

    # ─── Link Failure Simulation ────────────────────────────────────────

    def simulate_link_failure(self, router_a: str, router_b: str) -> dict:
        """
        Simulate a link failure between two routers and return the impact.

        This temporarily removes the link, recomputes all-pairs shortest paths,
        and then restores the link.

        Args:
            router_a: First router ID.
            router_b: Second router ID.

        Returns:
            A dict with keys:
              - 'removed_edge': (router_a, router_b, weight)
              - 'new_mst_edges': MST edges after failure
              - 'disconnected_pairs': list of (src, dst) pairs that became unreachable
        """
        if not self.graph.has_edge(router_a, router_b):
            return {"error": f"No link exists between {router_a} and {router_b}"}

        # Save edge data
        edge_data = self.graph[router_a][router_b].copy()
        weight = edge_data.get("weight", 1.0)

        # Remove the link
        self.graph.remove_edge(router_a, router_b)

        # Analyze impact
        new_mst_edges = []
        if self.graph.number_of_edges() > 0:
            try:
                new_mst_edges = self.get_mst_edges()
            except Exception:
                pass

        disconnected = []
        for src in self.graph.nodes():
            for dst in self.graph.nodes():
                if src >= dst:
                    continue
                if not nx.has_path(self.graph, src, dst):
                    disconnected.append((src, dst))

        # Restore the link
        self.graph.add_edge(router_a, router_b, **edge_data)

        return {
            "removed_edge": (router_a, router_b, weight),
            "new_mst_edges": new_mst_edges,
            "disconnected_pairs": disconnected,
        }

    # ─── Preset Topology Generators ─────────────────────────────────────

    def generate_ring_topology(self, n: int = 6, weight_range: tuple = (1, 10)) -> None:
        """
        Generate a ring topology with n routers.
        Each router is connected to its neighbors in a circle.
        """
        self.graph.clear()
        for i in range(n):
            self.add_router(f"R{i+1}")
        for i in range(n):
            w = random.randint(*weight_range)
            self.add_link(f"R{i+1}", f"R{(i+1) % n + 1}", weight=w)

    def generate_star_topology(self, n: int = 6, weight_range: tuple = (1, 10)) -> None:
        """
        Generate a star topology with 1 hub (R1) and n-1 spokes.
        """
        self.graph.clear()
        hub = "R1"
        self.add_router(hub)
        for i in range(2, n + 1):
            self.add_router(f"R{i}")
            w = random.randint(*weight_range)
            self.add_link(hub, f"R{i}", weight=w)

    def generate_mesh_topology(self, n: int = 5, weight_range: tuple = (1, 10)) -> None:
        """
        Generate a full mesh topology where every router connects to every other router.
        """
        self.graph.clear()
        for i in range(1, n + 1):
            self.add_router(f"R{i}")
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                w = random.randint(*weight_range)
                self.add_link(f"R{i}", f"R{j}", weight=w)

    def generate_tree_topology(self, depth: int = 3, branching: int = 2, weight_range: tuple = (1, 10)) -> None:
        """
        Generate a tree topology with the given depth and branching factor.
        """
        self.graph.clear()
        counter = [1]  # mutable counter

        def _build_tree(parent: str, current_depth: int):
            if current_depth >= depth:
                return
            for _ in range(branching):
                counter[0] += 1
                child = f"R{counter[0]}"
                self.add_router(child)
                w = random.randint(*weight_range)
                self.add_link(parent, child, weight=w)
                _build_tree(child, current_depth + 1)

        root = "R1"
        self.add_router(root)
        _build_tree(root, 0)

    def generate_random_topology(self, n: int = 8, edge_probability: float = 0.4,
                                  weight_range: tuple = (1, 15)) -> None:
        """
        Generate a random Erdős–Rényi graph and ensure it is connected.
        """
        self.graph.clear()
        for i in range(1, n + 1):
            self.add_router(f"R{i}")

        # Add random edges
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                if random.random() < edge_probability:
                    w = random.randint(*weight_range)
                    self.add_link(f"R{i}", f"R{j}", weight=w)

        # Ensure connectivity: connect each component to the main one
        components = list(nx.connected_components(self.graph))
        if len(components) > 1:
            main_component = components[0]
            for comp in components[1:]:
                a = random.choice(list(main_component))
                b = random.choice(list(comp))
                w = random.randint(*weight_range)
                self.add_link(a, b, weight=w)
                main_component = main_component.union(comp)

    # ─── Utility Methods ────────────────────────────────────────────────

    def is_connected(self) -> bool:
        """Check if the entire network is connected."""
        if self.graph.number_of_nodes() == 0:
            return True
        return nx.is_connected(self.graph)

    def get_network_stats(self) -> dict:
        """
        Return basic statistics about the current network topology.
        """
        stats = {
            "num_routers": self.graph.number_of_nodes(),
            "num_links": self.graph.number_of_edges(),
            "is_connected": self.is_connected(),
            "density": nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0,
        }
        if self.graph.number_of_nodes() > 0:
            degrees = dict(self.graph.degree())
            stats["avg_degree"] = sum(degrees.values()) / len(degrees)
            stats["max_degree"] = max(degrees.values()) if degrees else 0
            stats["min_degree"] = min(degrees.values()) if degrees else 0
        return stats

    def clear(self) -> None:
        """Remove all routers and links."""
        self.graph.clear()

    def to_dict(self) -> dict:
        """
        Serialize the network graph to a dictionary for JSON export.
        """
        return {
            "nodes": [
                {"id": n, **self.graph.nodes[n]}
                for n in self.graph.nodes()
            ],
            "edges": [
                {"source": u, "target": v, **d}
                for u, v, d in self.graph.edges(data=True)
            ],
        }

    def from_dict(self, data: dict) -> None:
        """
        Load a network graph from a dictionary (JSON import).
        """
        self.graph.clear()
        for node in data.get("nodes", []):
            nid = node.pop("id")
            self.graph.add_node(nid, **node)
        for edge in data.get("edges", []):
            src = edge.pop("source")
            tgt = edge.pop("target")
            self.graph.add_edge(src, tgt, **edge)
