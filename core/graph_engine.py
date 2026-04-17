"""
graph_engine.py - Core Graph Engine for the Network Packet Routing Simulator.

This module provides the NetworkGraph class, which handles:
- Adding/removing routers (nodes) and links (edges)
- Minimum Spanning Tree (Kruskal's /Prim's algorithms )
- Shortest path (Dijkstra)
- Preset topology generation (ring, star, mesh, tree, random)
- Link failure simulation
- Coordinate-based network generation (NEW FEATURE)
"""

import networkx as nx
import random
import math
from typing import Optional


class NetworkGraph:
    """
    Wrapper around a networkx.Graph representing a network of routers.
    connected by weighted links (representing latency, bandwidth cost, etc.).
    """

    def __init__(self):
        """Initialize an empty graph."""
        self.graph = nx.Graph()

    # Node (Router) Management 
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
        """Remove a router and its links.
        Args:
            router_id: Identifier of the router to remove.
        """
        if router_id in self.graph:
            self.graph.remove_node(router_id)

    def get_routers(self) -> list:
        """Return sorted list of routers."""
        return sorted(self.graph.nodes())

    # NEW: Distance-Based Weights 

    def assign_distance_weights(self):
        """
        Assign edge weights based on Euclidean distance between node positions
        """
        for u, v in self.graph.edges:
            x1, y1 = self.graph.nodes[u].get("pos", (0, 0))
            x2, y2 = self.graph.nodes[v].get("pos", (0, 0))

            dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            self.graph[u][v]["weight"] = round(dist, 2)

    # NEW: Coordinate-Based Builder 

    def build_from_coordinates(self, nodes: list, edges: list) -> None:
        """
        Build graph using user-provided coordinates and connections.

        nodes = [(name, x, y)]
        edges = [(u, v)]
        """
        self.graph.clear()

        # Add nodes with positions
        for name, x, y in nodes:
            self.graph.add_node(name, label=name, pos=(float(x), float(y)))

        # Add edges
        for u, v in edges:
            if u in self.graph and v in self.graph:
                self.graph.add_edge(u, v)

        # Compute weights automatically
        self.assign_distance_weights()

    # Edge (Link) Management 
    def add_link(self, router_a: str, router_b: str, weight: float = 1.0, **attrs) -> None:
        """Add a link (edge) between two routers.
        Args:
            router_a: First router ID.
            router_b: Second router ID.
            weight: Cost / latency of the link (must be > 0).
            **attrs: Extra attributes (e.g., bandwidth).
        """
        if router_a not in self.graph:
            self.add_router(router_a)
        if router_b not in self.graph:
            self.add_router(router_b)
        self.graph.add_edge(router_a, router_b, weight=weight, **attrs)

    def remove_link(self, router_a: str, router_b: str) -> None:
        """Remove a link between two routers (simulates link failure).

        Args:
            router_a: First router ID.
            router_b: Second router I

        
        """
        if self.graph.has_edge(router_a, router_b):
            self.graph.remove_edge(router_a, router_b)

    def get_links(self) -> list:
        """Return a list of all links as (router_a, router_b, weight) tuples."""
        return [(u, v, d.get("weight", 1.0)) for u, v, d in self.graph.edges(data=True)]

    # MST (Minimum Spanning Tree) 

    def compute_mst(self, algorithm: str = "kruskal") -> nx.Graph:
        """Compute MST.
        Args:
            algorithm: 'kruskal' or 'prim'. Defaults to 'kruskal'.

        Returns:
            A networkx.Graph representing the MST. Returns an empty graph if
            the original graph has no edges.

        Raises:
            ValueError: If an unsupported algorithm name is given.
          
        """
        if algorithm not in ("kruskal", "prim"):
            raise ValueError("Unsupported MST algorithm")

        if self.graph.number_of_edges() == 0:
            return nx.Graph()

        return nx.minimum_spanning_tree(self.graph, algorithm=algorithm, weight="weight")

    def get_mst_edges(self, algorithm: str = "kruskal") -> list:
        """
        Get the edges of the MST as a list of (u, v, weight) tuples.

        Args:
            algorithm: 'kruskal' or 'prim'.

        Returns:
            List of (router_a, router_b, weight) tuples forming the MST.
        """
        mst = self.compute_mst(algorithm)
        return [(u, v, d.get("weight", 1.0)) for u, v, d in mst.edges(data=True)]

    def get_mst_total_weight(self, algorithm: str = "kruskal") -> float:
        return sum(w for _, _, w in self.get_mst_edges(algorithm))

    # Shortest Path (Dijkstra) 

    def compute_shortest_path(self, source: str, target: str) -> tuple:
        """Compute shortest path using Dijkstra.
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
        """Compute shortest paths from one node to all others.
        Returns:
            A dict mapping each target router to (path, cost).
        """
        results = {}
        for node in self.graph.nodes():
            if node != source:
                results[node] = self.compute_shortest_path(source, node)
        return results

    #  Link Failure Simulation 

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
            return {"error": "No link exists"}

        edge_data = self.graph[router_a][router_b].copy()
        weight = edge_data.get("weight", 1.0)

        self.graph.remove_edge(router_a, router_b)

        new_mst_edges = []
        if self.graph.number_of_edges() > 0:
            new_mst_edges = self.get_mst_edges()

        disconnected = []
        for src in self.graph.nodes():
            for dst in self.graph.nodes():
                if src >= dst:
                    continue
                if not nx.has_path(self.graph, src, dst):
                    disconnected.append((src, dst))

        self.graph.add_edge(router_a, router_b, **edge_data)

        return {
            "removed_edge": (router_a, router_b, weight),
            "new_mst_edges": new_mst_edges,
            "disconnected_pairs": disconnected,
        }

    #  Topology Generators 

    def generate_ring_topology(self, n=6, weight_range=(1, 10)):
        self.graph.clear()
        for i in range(n):
            self.add_router(f"R{i+1}")
        for i in range(n):
            self.add_link(f"R{i+1}", f"R{(i+1) % n + 1}", weight=random.randint(*weight_range))

    def generate_star_topology(self, n=6, weight_range=(1, 10)):
        self.graph.clear()
        self.add_router("R1")
        for i in range(2, n + 1):
            self.add_router(f"R{i}")
            self.add_link("R1", f"R{i}", weight=random.randint(*weight_range))

    def generate_mesh_topology(self, n=5, weight_range=(1, 10)):
        self.graph.clear()
        for i in range(1, n + 1):
            self.add_router(f"R{i}")
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                self.add_link(f"R{i}", f"R{j}", weight=random.randint(*weight_range))

    def generate_tree_topology(self, depth=3, branching=2, weight_range=(1, 10)):
        self.graph.clear()
        counter = [1]

        def build(parent, d):
            if d >= depth:
                return
            for _ in range(branching):
                counter[0] += 1
                child = f"R{counter[0]}"
                self.add_router(child)
                self.add_link(parent, child, weight=random.randint(*weight_range))
                build(child, d + 1)

        self.add_router("R1")
        build("R1", 0)

    def generate_random_topology(self, n=8, edge_probability=0.4, weight_range=(1, 15)):
        self.graph.clear()
        for i in range(1, n + 1):
            self.add_router(f"R{i}")

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                if random.random() < edge_probability:
                    self.add_link(f"R{i}", f"R{j}", weight=random.randint(*weight_range))

    #  Utility Methods 

    def is_connected(self) -> bool:
        if self.graph.number_of_nodes() == 0:
            return True
        return nx.is_connected(self.graph)

    def get_network_stats(self) -> dict:
        stats = {
            "num_routers": self.graph.number_of_nodes(),
            "num_links": self.graph.number_of_edges(),
            "is_connected": self.is_connected(),
            "density": nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0,
        }
        return stats

    def clear(self) -> None:
        self.graph.clear()

    def to_dict(self) -> dict:
        return {
            "nodes": [{"id": n, **self.graph.nodes[n]} for n in self.graph.nodes()],
            "edges": [{"source": u, "target": v, **d} for u, v, d in self.graph.edges(data=True)],
        }

    def from_dict(self, data: dict) -> None:
        self.graph.clear()
        for node in data.get("nodes", []):
            nid = node.pop("id")
            self.graph.add_node(nid, **node)
        for edge in data.get("edges", []):
            src = edge.pop("source")
            tgt = edge.pop("target")
            self.graph.add_edge(src, tgt, **edge)
