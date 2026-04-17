import re
import os

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. CSS Block
new_css = """<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: var(--secondary-background-color);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-color);
    }
    .main-header p {
        opacity: 0.8;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        color: var(--text-color);
    }

    .stat-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
    }
    .stat-card .stat-value {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.2;
        color: var(--text-color);
    }
    .stat-card .stat-label {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-color);
    }

    .algo-result {
        background: var(--secondary-background-color);
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6; 
    }
    .algo-result.warning {
        border-left-color: #ef4444; 
    }
    .algo-result h4 {
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-color);
    }
    .algo-result p {
        opacity: 0.9;
        margin: 0;
        font-size: 0.9rem;
        color: var(--text-color);
    }

    .edge-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .edge-table th {
        background: rgba(128, 128, 128, 0.1);
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: left;
        color: var(--text-color);
    }
    .edge-table td {
        padding: 0.75rem 1rem;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        font-size: 0.85rem;
        color: var(--text-color);
    }

    .section-divider {
        border: none;
        height: 1px;
        background: rgba(128, 128, 128, 0.2);
        margin: 1.5rem 0;
    }
    
    .sidebar-section {
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 0;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        color: var(--text-color);
        opacity: 0.9;
    }
</style>"""

code = re.sub(r'<style>.*?</style>', new_css, code, flags=re.DOTALL)

replacements = [
    ('page_icon="🌐",', 'layout="wide",'),
    ('layout="wide",\n    layout="wide",', 'layout="wide",'), # cleanup
    ('<h1>🌐 Network Packet Routing Simulator</h1>', '<h1>Network Packet Routing Simulator</h1>'),
    ('st.markdown("## ⚙️ Network Controls")', 'st.markdown("## Network Controls")'),
    ('<div class="sidebar-section"><b>📐 Preset Topologies</b></div>', '<div class="sidebar-section">Preset Topologies</div>'),
    ('st.button("🔄 Generate Topology"', 'st.button("Generate Topology"'),
    ('<div class="sidebar-section"><b>📍 Custom Coordinate Network</b></div>', '<div class="sidebar-section">Custom Coordinate Network</div>'),
    ('st.button("📍 Generate Custom Network"', 'st.button("Generate Custom Network"'),
    ('st.success("✅ Custom network generated!")', 'st.success("Custom network generated.")'),
    ('<div class="sidebar-section"><b>➕ Add Router</b></div>', '<div class="sidebar-section">Add Router</div>'),
    ('st.success(f"✅ Router \'{new_router.strip()}\' added!")', 'st.success(f"Router \'{new_router.strip()}\' added.")'),
    ('<div class="sidebar-section"><b>🔗 Add Link</b></div>', '<div class="sidebar-section">Add Link</div>'),
    ('st.success(f"✅ Link {link_a} ↔ {link_b} (w={link_weight}) added!")', 'st.success(f"Link {link_a} ↔ {link_b} (w={link_weight}) added.")'),
    ('<div class="sidebar-section"><b>🗑️ Remove Elements</b></div>', '<div class="sidebar-section">Remove Elements</div>'),
    ('st.button("🧹 Clear Entire Network"', 'st.button("Clear Entire Network"'),
    ('<div class="sidebar-section"><b>💾 Import / Export</b></div>', '<div class="sidebar-section">Import / Export</div>'),
    ('st.button("📥 Export as JSON"', 'st.button("Export as JSON"'),
    ('st.file_uploader("📤 Import JSON"', 'st.file_uploader("Import JSON"'),
    ('<h2 style="color: #42A5F5;">Welcome to the Simulator!</h2>', '<h2>Welcome to the Simulator</h2>'),
    ('<p style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">', '<p style="opacity: 0.7; font-size: 1.1rem;">'),
    ('<p style="font-size: 3rem; margin-top: 1rem;">🌐🔗📡</p>', ''),
    ('st.markdown("### 🌲 Minimum Spanning Tree")', 'st.markdown("### Minimum Spanning Tree")'),
    ('<h4>🌲 MST Computed ({mst_algo})</h4>', '<h4>MST Computed ({mst_algo})</h4>'),
    ('st.markdown("### ⚡ Shortest Path (Dijkstra)")', 'st.markdown("### Shortest Path (Dijkstra)")'),
    ('<h4>⚡ Path Found!</h4>', '<h4>Path Found</h4>'),
    ('<h4>❌ No Path Found</h4>', '<h4>No Path Found</h4>'),
    ('st.markdown("### 💥 Link Failure Simulation")', 'st.markdown("### Link Failure Simulation")'),
    ('<h4>💥 Link {u} ↔ {v} Failed!</h4>', '<h4>Link {u} ↔ {v} Failed</h4>'),
    ('<p>⚠️ {len(report[\'disconnected_pairs\'])} pair(s) became disconnected!</p>', '<p>{len(report[\'disconnected_pairs\'])} pair(s) became disconnected.</p>'),
    ('<p>✅ Network remains fully connected. MST was recalculated.</p>', '<p>Network remains fully connected. MST was recalculated.</p>'),
    ('st.markdown("### 🗺️ Network Topology Visualization")', 'st.markdown("### Network Topology Visualization")'),
    ('st.markdown("### 📋 Edge Table")', 'st.markdown("### Edge Table")'),
    ('st.markdown("### 🌲 MST Edges")', 'st.markdown("### MST Edges")'),
    ('st.markdown("### ⚡ Shortest Path Details")', 'st.markdown("### Shortest Path Details")'),
    ('st.markdown("### 💥 Failure Impact Report")', 'st.markdown("### Failure Impact Report")')
]

for old, new in replacements:
    code = code.replace(old, new)

# specifically rework the stats cards
old_stats = """stat_items = [
    ("🖥️", str(stats["num_routers"]), "Routers"),
    ("🔗", str(stats["num_links"]), "Links"),
    ("📊", f"{stats.get('avg_degree', 0):.1f}", "Avg Degree"),
    ("🔌", "Yes" if stats["is_connected"] else "No", "Connected"),
    ("🧮", f"{stats.get('density', 0):.2f}", "Density"),
]
for col, (icon, value, label) in zip(stat_cols, stat_items):
    with col:
        st.markdown(f\"\"\"
        <div class="stat-card">
            <div style="font-size:1.5rem;">{icon}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        \"\"\", unsafe_allow_html=True)"""

new_stats = """stat_items = [
    (str(stats["num_routers"]), "Routers"),
    (str(stats["num_links"]), "Links"),
    (f"{stats.get('avg_degree', 0):.1f}", "Avg Degree"),
    ("Yes" if stats["is_connected"] else "No", "Connected"),
    (f"{stats.get('density', 0):.2f}", "Density"),
]
for col, (value, label) in zip(stat_cols, stat_items):
    with col:
        st.markdown(f\"\"\"
        <div class="stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        \"\"\", unsafe_allow_html=True)"""

code = code.replace(old_stats, new_stats)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
