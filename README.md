#  Network Packet Routing Simulator

An interactive, web-based tool that visualizes network topologies, computes **Minimum Spanning Trees (MST)**, and simulates **dynamic packet routing** using Dijkstra's algorithm — built with Python, Streamlit, NetworkX, and PyVis.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?logo=streamlit&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-3.4+-orange?logo=python&logoColor=white)

---

##  Features

| Feature | Description |
|---------|-------------|
| **Preset Topologies** | Generate Ring, Star, Mesh, Tree, and Random network layouts instantly |
| **Custom Networks** | Manually add/remove routers (nodes) and links (edges) with custom weights |
| **MST Computation** | Kruskal's and Prim's algorithms with visual highlighting |
| **Shortest Path** | Dijkstra's algorithm to find minimum-cost routes between any two routers |
| **Link Failure Sim** | Simulate a link going down and analyze its impact on connectivity |
| **Interactive Graphs** | Drag, zoom, hover for details with PyVis HTML rendering |
| **Static Export** | Matplotlib-based graph rendering for reports and documentation |
| **JSON Import/Export** | Save and load entire network topologies |
| **Network Stats** | Real-time dashboard showing routers, links, density, connectivity |

---

##  Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/Network-Packet-Routing-Simulator-Using-Graph-Minimum-Spanning-Tree.git
cd Network-Packet-Routing-Simulator-Using-Graph-Minimum-Spanning-Tree

# Install dependencies
pip install -r requirements.txt
```

---

##  Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your default browser.

---

##  Project Architecture

```
├── app.py                  # Main Streamlit UI application
├── core/
│   ├── __init__.py         # Package exports
│   ├── graph_engine.py     # NetworkGraph class — algorithms & topology generators
│   └── plotter.py          # GraphPlotter — PyVis & Matplotlib visualization
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── WEEKLY_REPORT.md        # Mandatory progress reports
```

---

##  Algorithms Implemented

### 1. Minimum Spanning Tree (MST)
   - **Kruskal's Algorithm**: Sorts all edges by weight and greedily builds the MST by picking the smallest edge that doesn't create a cycle (Union-Find approach).
   - **Prim's Algorithm**: Starts from an arbitrary node and grows the tree by always adding the cheapest edge connecting the tree to a new vertex (priority queue approach).
   - **Time Complexity**: O(E log E) for Kruskal's, O(E log V) for Prim's.

### 2. Shortest Path (Dijkstra)
   - Finds the minimum-cost path from a source to a destination node.
   - Uses a priority queue (min-heap) to greedily expand the nearest unvisited node.
   - **Time Complexity**: O((V + E) log V) with a binary heap.

### 3. Link Failure Simulation
   - Temporarily removes an edge, recomputes the MST, and checks for disconnected node pairs.
   - Demonstrates network resilience and fault tolerance.

---

##  Topology Types

| Topology | Visual | Description |
|----------|--------|-------------|
| **Ring** | ⭕ | Each router connects to exactly 2 neighbors in a circle |
| **Star** | ⭐ | One central hub connects to all others |
| **Mesh** | 🔗 | Every router connects to every other (full mesh) |
| **Tree** | 🌳 | Hierarchical structure with a root and branching |
| **Random** | 🎲 | Erdős–Rényi random graph (guaranteed connected) |

---

##  Usage Guide

1. **Generate a Topology**: Use the sidebar dropdown to pick a preset (Ring, Star, Mesh, Tree, Random) and hit "Generate Topology."
2. **Customize**: Add/remove routers and links manually using the sidebar controls.
3. **Compute MST**: Select Kruskal or Prim and click "Compute MST" — MST edges light up in **green**.
4. **Find Shortest Path**: Pick a source and destination, then click "Find Shortest Path" — the route lights up in **red**.
5. **Simulate Failure**: Select a link and click "Simulate Failure" to see which node pairs become disconnected.
6. **Toggle Renderer**: Switch between interactive PyVis and static Matplotlib views.
7. **Export/Import**: Save your topology as JSON or load a previously saved one.

---

##  Testing

Run the unit tests to verify algorithm correctness:

```bash
python -m pytest tests/ -v
```

---

##  Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Web Framework | Streamlit |
| Graph Library | NetworkX |
| Interactive Viz | PyVis |
| Static Viz | Matplotlib |
| Package Manager | pip |

---

##  Team

| Member | Role |
|--------|------|
| *Om Gupta* | *[Role/Contribution]* |
| *Tirunagari Bhuvan* | *[Role/Contribution]* |
| *Gyan Vardhan Chauhan* | *[Role/Contribution]* |
| *Nitesh* | *[Role/Contribution]* |
---

##  License

This project is developed as an academic project. See the project documentation for details.

---

<p align="center">
  <b>Built with ❤️ using Streamlit, NetworkX, and PyVis</b>
</p>
