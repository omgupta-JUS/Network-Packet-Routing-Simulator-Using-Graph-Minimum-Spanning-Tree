import os

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = """    # ── Preset Topologies ──────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Preset Topologies</div>', unsafe_allow_html=True)
    topo_col1, topo_col2 = st.columns(2)
    with topo_col1:
        preset = st.selectbox("Topology", ["Ring", "Star", "Mesh", "Tree", "Random"], label_visibility="collapsed")
    with topo_col2:
        n_nodes = st.number_input("Nodes", min_value=3, max_value=20, value=6, step=1)

    if st.button("Generate Topology", use_container_width=True, type="primary"):
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
    st.markdown('<div class="sidebar-section">Custom Coordinate Network</div>', unsafe_allow_html=True)

    node_input = st.text_area(
        "Nodes (format: name x y)",
        placeholder="A 10 20\\nB 40 50\\nC 70 10",
        key="custom_nodes"
    )

    edge_input = st.text_area(
        "Edges (format: A B)",
        placeholder="A B\\nB C\\nA C",
        key="custom_edges"
    )

    def parse_nodes(text):
        nodes = []
        for line in text.strip().split("\\n"):
            parts = line.strip().split()
            if len(parts) == 3:
                name, x, y = parts
                nodes.append((name, float(x), float(y)))
        return nodes

    def parse_edges(text):
        edges = []
        for line in text.strip().split("\\n"):
            parts = line.strip().split()
            if len(parts) == 2:
                edges.append((parts[0], parts[1]))
        return edges

    if st.button("Generate Custom Network", use_container_width=True):
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

                st.success("Custom network generated.")
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")"""

new_block = """    # ── Topology Generation Modes ─────────────────────────────────────
    gen_mode = st.radio("Generation Mode", ["Preset Topologies", "Custom Coordinate Network"])
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    if gen_mode == "Preset Topologies":
        st.markdown('<div class="sidebar-section">Preset Topologies</div>', unsafe_allow_html=True)
        topo_col1, topo_col2 = st.columns(2)
        with topo_col1:
            preset = st.selectbox("Topology", ["Ring", "Star", "Mesh", "Tree", "Random"], label_visibility="collapsed")
        with topo_col2:
            n_nodes = st.number_input("Nodes", min_value=3, max_value=20, value=6, step=1)

        if st.button("Generate Topology", use_container_width=True, type="primary"):
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

    else:
        st.markdown('<div class="sidebar-section">Custom Coordinate Network</div>', unsafe_allow_html=True)
        node_input = st.text_area(
            "Nodes (format: name x y)",
            placeholder="A 10 20\\nB 40 50\\nC 70 10",
            key="custom_nodes"
        )

        edge_input = st.text_area(
            "Edges (format: A B)",
            placeholder="A B\\nB C\\nA C",
            key="custom_edges"
        )

        def parse_nodes(text):
            nodes = []
            for line in text.strip().split("\\n"):
                parts = line.strip().split()
                if len(parts) == 3:
                    name, x, y = parts
                    nodes.append((name, float(x), float(y)))
            return nodes

        def parse_edges(text):
            edges = []
            for line in text.strip().split("\\n"):
                parts = line.strip().split()
                if len(parts) == 2:
                    edges.append((parts[0], parts[1]))
            return edges

        if st.button("Generate Custom Network", use_container_width=True):
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
                    st.success("Custom network generated.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Replaced successfully")
else:
    print("Could not find the block to replace!")
