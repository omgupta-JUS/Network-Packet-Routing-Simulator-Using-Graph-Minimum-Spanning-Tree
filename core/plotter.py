"""
plotter.py — Visualization Engine for the Network Packet Routing Simulator.

Provides two rendering backends:
  1. PyVis — Interactive HTML-based network graphs (primary)
  2. Matplotlib — Static chart renderings (fallback / export)

The plotter takes a NetworkGraph instance and produces highlighted views of:
  - The full topology
  - MST edges (highlighted in green)
  - Shortest path (highlighted in red/orange)
  - Failed links (dashed gray)

Author: Network Packet Routing Simulator Team
"""

import os
import tempfile
import networkx as nx
from pyvis.network import Network
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ═══════════════════════════════════════════════════════════════════════
# Color Palette
# ═══════════════════════════════════════════════════════════════════════
COLORS = {
    "node_default": "#4FC3F7",       # Light blue
    "node_source": "#66BB6A",        # Green
    "node_target": "#EF5350",        # Red
    "node_intermediate": "#FFA726",  # Orange (on shortest path)
    "edge_default": "#90A4AE",       # Gray-blue
    "edge_mst": "#00E676",           # Bright green
    "edge_shortest": "#FF5252",      # Bright red
    "edge_failed": "#616161",        # Dark gray
    "background": "#263238",         # Dark slate
}


class GraphPlotter:
    """Render a NetworkGraph using PyVis or Matplotlib."""

    def __init__(self, net_graph):
        """
        Args:
            net_graph: A NetworkGraph instance from graph_engine.
        """
        self.net_graph = net_graph

    # ─── PyVis Interactive Rendering ────────────────────────────────────

    def render_pyvis(
        self,
        mst_edges: list = None,
        shortest_path: list = None,
        failed_edges: list = None,
        height: str = "600px",
        width: str = "100%",
    ) -> str:
        """
        Render the network as an interactive PyVis HTML graph.

        Args:
            mst_edges: List of (u, v) tuples to highlight as MST edges.
            shortest_path: Ordered list of node IDs forming the shortest path.
            failed_edges: List of (u, v) tuples to mark as failed.
            height: CSS height of the canvas.
            width: CSS width of the canvas.

        Returns:
            Path to the generated HTML file.
        """
        G = self.net_graph.graph

        net = Network(
            height=height,
            width=width,
            bgcolor=COLORS["background"],
            font_color="#ECEFF1",
            directed=False,
            notebook=False,
        )

        # Build sets for fast lookup
        mst_set = set()
        if mst_edges:
            for u, v, *_ in mst_edges:
                mst_set.add((u, v))
                mst_set.add((v, u))

        sp_set = set()
        sp_nodes = set()
        if shortest_path and len(shortest_path) >= 2:
            sp_nodes = set(shortest_path)
            for i in range(len(shortest_path) - 1):
                sp_set.add((shortest_path[i], shortest_path[i + 1]))
                sp_set.add((shortest_path[i + 1], shortest_path[i]))

        failed_set = set()
        if failed_edges:
            for u, v in failed_edges:
                failed_set.add((u, v))
                failed_set.add((v, u))

        # ── Add Nodes ──
        for node in G.nodes():
            color = COLORS["node_default"]
            size = 25
            border_width = 2
            border_color = "#FFFFFF"

            if shortest_path:
                if node == shortest_path[0]:
                    color = COLORS["node_source"]
                    size = 35
                    border_width = 4
                    border_color = "#FFFFFF"
                elif node == shortest_path[-1]:
                    color = COLORS["node_target"]
                    size = 35
                    border_width = 4
                    border_color = "#FFFFFF"
                elif node in sp_nodes:
                    color = COLORS["node_intermediate"]
                    size = 30

            label = G.nodes[node].get("label", node)
            net.add_node(
                node,
                label=label,
                color={
                    "background": color,
                    "border": border_color,
                    "highlight": {"background": "#FFD54F", "border": "#FFC107"},
                },
                size=size,
                borderWidth=border_width,
                font={"size": 14, "face": "Segoe UI, Arial"},
                shadow=True,
            )

        # ── Add Edges ──
        for u, v, data in G.edges(data=True):
            weight = data.get("weight", 1)
            color = COLORS["edge_default"]
            edge_width = 2
            dashes = False
            title = f"{u} ↔ {v}  |  Weight: {weight}"

            if (u, v) in failed_set:
                color = COLORS["edge_failed"]
                dashes = True
                edge_width = 3
                title += "  ❌ FAILED"
            elif (u, v) in sp_set:
                color = COLORS["edge_shortest"]
                edge_width = 5
                title += "  ⚡ Shortest Path"
            elif (u, v) in mst_set:
                color = COLORS["edge_mst"]
                edge_width = 4
                title += "  🌲 MST"

            net.add_edge(
                u, v,
                value=edge_width,
                color=color,
                title=title,
                label=str(weight),
                font={"size": 12, "color": "#B0BEC5", "align": "top"},
                dashes=dashes,
                smooth={"type": "continuous"},
            )

        # Physics settings for a nice layout
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 150,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "stabilization": {
              "enabled": true,
              "iterations": 200
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "zoomView": true,
            "dragView": true
          },
          "edges": {
            "font": {
              "strokeWidth": 0
            }
          }
        }
        """)

        # Save to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
        net.save_graph(tmp.name)
        tmp.close()
        return tmp.name

    # ─── Matplotlib Static Rendering ────────────────────────────────────

    def render_matplotlib(
        self,
        mst_edges: list = None,
        shortest_path: list = None,
        failed_edges: list = None,
        figsize: tuple = (12, 8),
    ):
        """
        Render the network as a static Matplotlib figure.

        Returns:
            A matplotlib Figure object.
        """
        G = self.net_graph.graph
        fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["background"])
        ax.set_facecolor(COLORS["background"])

        if G.number_of_nodes() == 0:
            ax.text(0.5, 0.5, "No routers in the network",
                    ha="center", va="center", fontsize=16, color="white",
                    transform=ax.transAxes)
            ax.axis("off")
            return fig

        pos = nx.spring_layout(G, seed=42, k=2)

        # Build lookup sets
        mst_set = set()
        if mst_edges:
            for u, v, *_ in mst_edges:
                mst_set.add((u, v))
                mst_set.add((v, u))

        sp_set = set()
        sp_nodes = set()
        if shortest_path and len(shortest_path) >= 2:
            sp_nodes = set(shortest_path)
            for i in range(len(shortest_path) - 1):
                sp_set.add((shortest_path[i], shortest_path[i + 1]))
                sp_set.add((shortest_path[i + 1], shortest_path[i]))

        failed_set = set()
        if failed_edges:
            for u, v in failed_edges:
                failed_set.add((u, v))
                failed_set.add((v, u))

        # Categorize edges
        default_edges = []
        mst_draw_edges = []
        sp_draw_edges = []
        failed_draw_edges = []

        for u, v in G.edges():
            if (u, v) in failed_set:
                failed_draw_edges.append((u, v))
            elif (u, v) in sp_set:
                sp_draw_edges.append((u, v))
            elif (u, v) in mst_set:
                mst_draw_edges.append((u, v))
            else:
                default_edges.append((u, v))

        # Draw edges layer by layer
        nx.draw_networkx_edges(G, pos, edgelist=default_edges, edge_color=COLORS["edge_default"],
                               width=1.5, alpha=0.5, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=mst_draw_edges, edge_color=COLORS["edge_mst"],
                               width=3.0, alpha=0.9, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=sp_draw_edges, edge_color=COLORS["edge_shortest"],
                               width=4.0, alpha=1.0, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=failed_draw_edges, edge_color=COLORS["edge_failed"],
                               width=2.0, style="dashed", alpha=0.7, ax=ax)

        # Node colors
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            if shortest_path and node == shortest_path[0]:
                node_colors.append(COLORS["node_source"])
                node_sizes.append(700)
            elif shortest_path and node == shortest_path[-1]:
                node_colors.append(COLORS["node_target"])
                node_sizes.append(700)
            elif node in sp_nodes:
                node_colors.append(COLORS["node_intermediate"])
                node_sizes.append(500)
            else:
                node_colors.append(COLORS["node_default"])
                node_sizes.append(400)

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                               edgecolors="white", linewidths=2, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="white",
                                font_weight="bold", ax=ax)

        # Edge weight labels
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                      font_size=8, font_color="#CFD8DC", ax=ax)

        # Legend
        legend_items = [
            mpatches.Patch(color=COLORS["edge_default"], label="Network Link"),
        ]
        if mst_draw_edges:
            legend_items.append(mpatches.Patch(color=COLORS["edge_mst"], label="MST Edge"))
        if sp_draw_edges:
            legend_items.append(mpatches.Patch(color=COLORS["edge_shortest"], label="Shortest Path"))
        if failed_draw_edges:
            legend_items.append(mpatches.Patch(color=COLORS["edge_failed"], label="Failed Link"))

        ax.legend(handles=legend_items, loc="upper left", fontsize=9,
                  facecolor="#37474F", edgecolor="#546E7A", labelcolor="white")

        ax.axis("off")
        ax.set_title("Network Topology", fontsize=16, color="white", pad=20)
        fig.tight_layout()
        return fig
