"""
app.py — Main Streamlit Application for the Network Packet Routing Simulator.

This is the entry point. Run with:
    streamlit run app.py

Features:
  - Sidebar controls for building & modifying the network
  - Preset topology generators (ring, star, mesh, tree, random)
  - MST computation and visualization (Kruskal / Prim)
  - Shortest path computation and visualization (Dijkstra)
  - Link failure simulation with impact analysis
  - Interactive PyVis graph + Matplotlib static export
  - Network statistics dashboard
  - JSON import/export of topologies

Author: Network Packet Routing Simulator Team
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os

from core.graph_engine import NetworkGraph
from core.plotter import GraphPlotter

# ═══════════════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Network Packet Routing Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
# Custom CSS for Premium Look
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 30%, #1E88E5 60%, #42A5F5 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(13, 71, 161, 0.3);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
        font-weight: 300;
    }

    /* Stat card styling */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
    }
    .stat-card .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #42A5F5;
        line-height: 1;
    }
    .stat-card .stat-label {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.6);
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Algorithm result banner */
    .algo-result {
        background: linear-gradient(135deg, #1B5E20, #2E7D32);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #69F0AE;
    }
    .algo-result.warning {
        background: linear-gradient(135deg, #E65100, #F57C00);
        border-left-color: #FFD54F;
    }
    .algo-result h4 {
        color: white;
        margin: 0 0 0.3rem 0;
    }
    .algo-result p {
        color: rgba(255,255,255,0.9);
        margin: 0;
    }

    /* Edge table */
    .edge-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
    }
    .edge-table th {
        background: #1565C0;
        color: white;
        padding: 0.6rem 0.8rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .edge-table td {
        padding: 0.5rem 0.8rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        font-size: 0.85rem;
    }

    /* Section divider */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(66,165,245,0.4), transparent);
        margin: 1.5rem 0;
    }
    
    /* Sidebar section headers */
    .sidebar-section {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid #42A5F5;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# Session State Initialization
# ═══════════════════════════════════════════════════════════════════════
if "net" not in st.session_state:
    st.session_state.net = NetworkGraph()
if "mst_edges" not in st.session_state:
    st.session_state.mst_edges = []
if "shortest_path" not in st.session_state:
    st.session_state.shortest_path = []
if "shortest_cost" not in st.session_state:
    st.session_state.shortest_cost = 0
if "failed_edges" not in st.session_state:
    st.session_state.failed_edges = []
if "show_mst" not in st.session_state:
    st.session_state.show_mst = False
if "show_sp" not in st.session_state:
    st.session_state.show_sp = False
if "failure_report" not in st.session_state:
    st.session_state.failure_report = None

net: NetworkGraph = st.session_state.net

# ═══════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🌐 Network Packet Routing Simulator</h1>
    <p>Interactive visualization of graph topologies, MST, and shortest-path routing</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# Sidebar — Controls
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Network Controls")

    # ── Preset Topologies ──────────────────────────────────────────────
    st.markdown('<div class="sidebar-section"><b>📐 Preset Topologies</b></div>', unsafe_allow_html=True)
    topo_col1, topo_col2 = st.columns(2)
    with topo_col1:
        preset = st.selectbox("Topology", ["Ring", "Star", "Mesh", "Tree", "Random"], label_visibility="collapsed")
    with topo_col2:
        n_nodes = st.number_input("Nodes", min_value=3, max_value=20, value=6, step=1)

    if st.button("🔄 Generate Topology", use_container_width=True, type="primary"):
        if preset == "Ring":
            net.generate_ring_topology(n_nodes)
        elif preset == "Star":
            net.generate_star_topology(n_nodes)
        elif preset == "Mesh":
            net.generate_mesh_topology(n_nodes)
        elif preset == "Tree":
            net.generate_tree_topology(depth=3, branching=2)
        elif preset == "Random":
            net.generate_random_topology(n_nodes)
        # Reset highlights
        st.session_state.mst_edges = []
        st.session_state.shortest_path = []
        st.session_state.shortest_cost = 0
        st.session_state.failed_edges = []
        st.session_state.show_mst = False
        st.session_state.show_sp = False
        st.session_state.failure_report = None
        st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    # ── Custom Coordinate-Based Input ──────────────────────────────────
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section"><b>📍 Custom Coordinate Network</b></div>', unsafe_allow_html=True)

    node_input = st.text_area(
        "Nodes (format: name x y)",
        placeholder="A 10 20\nB 40 50\nC 70 10",
        key="custom_nodes"
    )

    edge_input = st.text_area(
        "Edges (format: A B)",
        placeholder="A B\nB C\nA C",
        key="custom_edges"
    )

    def parse_nodes(text):
        nodes = []
        for line in text.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) == 3:
                name, x, y = parts
                nodes.append((name, float(x), float(y)))
        return nodes

    def parse_edges(text):
        edges = []
        for line in text.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) == 2:
                edges.append((parts[0], parts[1]))
        return edges

    if st.button("📍 Generate Custom Network", use_container_width=True):
        try:
            nodes = parse_nodes(node_input)
            edges = parse_edges(edge_input)

            if not nodes:
                st.warning("Please enter valid node data.")
            else:
                net.build_from_coordinates(nodes, edges)

                # Reset previous results
                st.session_state.mst_edges = []
                st.session_state.shortest_path = []
                st.session_state.shortest_cost = 0
                st.session_state.failed_edges = []
                st.session_state.show_mst = False
                st.session_state.show_sp = False
                st.session_state.failure_report = None

                st.success("✅ Custom network generated!")
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
        





    # ── Manual Node/Edge Addition ──────────────────────────────────────
    st.markdown('<div class="sidebar-section"><b>➕ Add Router</b></div>', unsafe_allow_html=True)
    new_router = st.text_input("Router ID (e.g., R7)", key="new_router_input")
    if st.button("Add Router", use_container_width=True):
        if new_router.strip():
            net.add_router(new_router.strip())
            st.success(f"✅ Router '{new_router.strip()}' added!")
            st.rerun()

    st.markdown('<div class="sidebar-section"><b>🔗 Add Link</b></div>', unsafe_allow_html=True)
    routers = net.get_routers()
    if len(routers) >= 2:
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            link_a = st.selectbox("From", routers, key="link_from")
        with link_col2:
            link_b = st.selectbox("To", [r for r in routers if r != link_a] if routers else [], key="link_to")
        link_weight = st.slider("Weight (Latency)", min_value=1, max_value=50, value=5)
        if st.button("Add Link", use_container_width=True):
            net.add_link(link_a, link_b, weight=link_weight)
            st.success(f"✅ Link {link_a} ↔ {link_b} (w={link_weight}) added!")
            st.rerun()
    else:
        st.info("Add at least 2 routers to create links.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Remove Router / Link ───────────────────────────────────────────
    st.markdown('<div class="sidebar-section"><b>🗑️ Remove Elements</b></div>', unsafe_allow_html=True)
    if routers:
        rm_router = st.selectbox("Remove Router", routers, key="rm_router")
        if st.button("Remove Router", use_container_width=True):
            net.remove_router(rm_router)
            st.session_state.mst_edges = []
            st.session_state.shortest_path = []
            st.rerun()

    links = net.get_links()
    if links:
        link_options = [f"{u} ↔ {v} (w={w})" for u, v, w in links]
        rm_link_idx = st.selectbox("Remove Link", range(len(links)), format_func=lambda i: link_options[i], key="rm_link")
        if st.button("Remove Link", use_container_width=True):
            u, v, _ = links[rm_link_idx]
            net.remove_link(u, v)
            st.session_state.mst_edges = []
            st.session_state.shortest_path = []
            st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Clear All ──────────────────────────────────────────────────────
    if st.button("🧹 Clear Entire Network", use_container_width=True):
        net.clear()
        st.session_state.mst_edges = []
        st.session_state.shortest_path = []
        st.session_state.shortest_cost = 0
        st.session_state.failed_edges = []
        st.session_state.show_mst = False
        st.session_state.show_sp = False
        st.session_state.failure_report = None
        st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── JSON Import / Export ───────────────────────────────────────────
    st.markdown('<div class="sidebar-section"><b>💾 Import / Export</b></div>', unsafe_allow_html=True)
    if st.button("📥 Export as JSON", use_container_width=True):
        data = net.to_dict()
        st.download_button(
            "Download JSON",
            data=json.dumps(data, indent=2),
            file_name="network_topology.json",
            mime="application/json",
            use_container_width=True,
        )
    uploaded = st.file_uploader("📤 Import JSON", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            net.from_dict(data)
            st.success("Topology loaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# Main Content Area
# ═══════════════════════════════════════════════════════════════════════

if net.graph.number_of_nodes() == 0:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;">
        <h2 style="color: #42A5F5;">Welcome to the Simulator!</h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">
            Use the sidebar to generate a preset topology or manually build your network.
        </p>
        <p style="font-size: 3rem; margin-top: 1rem;">🌐🔗📡</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Network Stats Row ──────────────────────────────────────────────────
stats = net.get_network_stats()
stat_cols = st.columns(5)
stat_items = [
    ("🖥️", str(stats["num_routers"]), "Routers"),
    ("🔗", str(stats["num_links"]), "Links"),
    ("📊", f"{stats.get('avg_degree', 0):.1f}", "Avg Degree"),
    ("🔌", "Yes" if stats["is_connected"] else "No", "Connected"),
    ("🧮", f"{stats.get('density', 0):.2f}", "Density"),
]
for col, (icon, value, label) in zip(stat_cols, stat_items):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:1.5rem;">{icon}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Algorithm Controls ─────────────────────────────────────────────────
algo_col1, algo_col2, algo_col3 = st.columns(3)

with algo_col1:
    st.markdown("### 🌲 Minimum Spanning Tree")
    mst_algo = st.radio("Algorithm", ["Kruskal", "Prim"], horizontal=True, key="mst_algo_radio")
    if st.button("Compute MST", use_container_width=True, type="primary"):
        try:
            mst_edges = net.get_mst_edges(algorithm=mst_algo.lower())
            st.session_state.mst_edges = mst_edges
            st.session_state.show_mst = True
            total_w = net.get_mst_total_weight(algorithm=mst_algo.lower())
            st.markdown(f"""
            <div class="algo-result">
                <h4>🌲 MST Computed ({mst_algo})</h4>
                <p>Edges: {len(mst_edges)} &nbsp;|&nbsp; Total Weight: {total_w}</p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"MST computation failed: {e}")

with algo_col2:
    st.markdown("### ⚡ Shortest Path (Dijkstra)")
    if len(routers) >= 2:
        sp_src = st.selectbox("Source", routers, key="sp_src")
        sp_dst = st.selectbox("Destination", [r for r in routers if r != sp_src], key="sp_dst")
        if st.button("Find Shortest Path", use_container_width=True, type="primary"):
            path, cost = net.compute_shortest_path(sp_src, sp_dst)
            if path:
                st.session_state.shortest_path = path
                st.session_state.shortest_cost = cost
                st.session_state.show_sp = True
                st.markdown(f"""
                <div class="algo-result">
                    <h4>⚡ Path Found!</h4>
                    <p>Route: {' → '.join(path)}<br>Total Cost: {cost}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="algo-result warning">
                    <h4>❌ No Path Found</h4>
                    <p>{sp_src} and {sp_dst} are not connected.</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Need at least 2 routers.")

with algo_col3:
    st.markdown("### 💥 Link Failure Simulation")
    if links:
        fail_options = [f"{u} ↔ {v} (w={w})" for u, v, w in links]
        fail_idx = st.selectbox("Link to Fail", range(len(links)), format_func=lambda i: fail_options[i], key="fail_link")
        if st.button("Simulate Failure", use_container_width=True, type="primary"):
            u, v, w = links[fail_idx]
            report = net.simulate_link_failure(u, v)
            st.session_state.failure_report = report
            st.session_state.failed_edges = [(u, v)]

            if report.get("disconnected_pairs"):
                st.markdown(f"""
                <div class="algo-result warning">
                    <h4>💥 Link {u} ↔ {v} Failed!</h4>
                    <p>⚠️ {len(report['disconnected_pairs'])} pair(s) became disconnected!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="algo-result">
                    <h4>💥 Link {u} ↔ {v} Failed!</h4>
                    <p>✅ Network remains fully connected. MST was recalculated.</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No links to simulate failure on.")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Visualization Toggle ───────────────────────────────────────────────
viz_col1, viz_col2 = st.columns([3, 1])
with viz_col1:
    st.markdown("### 🗺️ Network Topology Visualization")
with viz_col2:
    viz_mode = st.radio("Renderer", ["Interactive (PyVis)", "Static (Matplotlib)"], horizontal=True, label_visibility="collapsed")

# Prepare highlight data
display_mst = st.session_state.mst_edges if st.session_state.show_mst else None
display_sp = st.session_state.shortest_path if st.session_state.show_sp else None
display_failed = st.session_state.failed_edges if st.session_state.failed_edges else None

plotter = GraphPlotter(net)

if "PyVis" in viz_mode:
    html_path = plotter.render_pyvis(
        mst_edges=display_mst,
        shortest_path=display_sp,
        failed_edges=display_failed,
        height="650px",
    )
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=680, scrolling=False)
    # Clean up temp file
    try:
        os.unlink(html_path)
    except Exception:
        pass
else:
    fig = plotter.render_matplotlib(
        mst_edges=display_mst,
        shortest_path=display_sp,
        failed_edges=display_failed,
    )
    st.pyplot(fig)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Edge Table & Path Details ──────────────────────────────────────────
detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.markdown("### 📋 Edge Table")
    if links:
        table_html = '<table class="edge-table"><tr><th>#</th><th>From</th><th>To</th><th>Weight</th></tr>'
        for i, (u, v, w) in enumerate(links, 1):
            table_html += f"<tr><td>{i}</td><td>{u}</td><td>{v}</td><td>{w}</td></tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No links in the network.")

with detail_col2:
    if st.session_state.show_mst and st.session_state.mst_edges:
        st.markdown("### 🌲 MST Edges")
        mst_table = '<table class="edge-table"><tr><th>#</th><th>From</th><th>To</th><th>Weight</th></tr>'
        for i, (u, v, w) in enumerate(st.session_state.mst_edges, 1):
            mst_table += f"<tr><td>{i}</td><td>{u}</td><td>{v}</td><td>{w}</td></tr>"
        mst_table += "</table>"
        st.markdown(mst_table, unsafe_allow_html=True)
        st.markdown(f"**Total MST Weight:** {sum(w for _,_,w in st.session_state.mst_edges)}")

    if st.session_state.show_sp and st.session_state.shortest_path:
        st.markdown("### ⚡ Shortest Path Details")
        path = st.session_state.shortest_path
        st.markdown(f"**Route:** {' → '.join(path)}")
        st.markdown(f"**Hops:** {len(path) - 1}")
        st.markdown(f"**Total Cost:** {st.session_state.shortest_cost}")

    if st.session_state.failure_report:
        report = st.session_state.failure_report
        st.markdown("### 💥 Failure Impact Report")
        u, v, w = report["removed_edge"]
        st.markdown(f"**Failed Link:** {u} ↔ {v} (weight: {w})")
        if report["disconnected_pairs"]:
            st.warning(f"**Disconnected pairs:** {len(report['disconnected_pairs'])}")
            for a, b in report["disconnected_pairs"][:10]:
                st.markdown(f"  - {a} ↔ {b}")
        else:
            st.success("Network remains fully connected after failure.")

# ── Footer ─────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:1rem; color: rgba(255,255,255,0.4); font-size:0.8rem;">
    Network Packet Routing Simulator &nbsp;|&nbsp; Built with Streamlit + NetworkX + PyVis &nbsp;|&nbsp; 2026
</div>
""", unsafe_allow_html=True)
