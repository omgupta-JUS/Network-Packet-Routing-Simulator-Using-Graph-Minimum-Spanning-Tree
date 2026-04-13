import sys; sys.path.insert(0, '.')
from core.graph_engine import NetworkGraph

# Test 1: Ring topology + MST
net = NetworkGraph()
net.generate_ring_topology(6)
print('=== Ring Topology (6 nodes) ===')
print('Routers:', net.get_routers())
print('Links:', net.get_links())
print('Connected:', net.is_connected())
mst = net.get_mst_edges('kruskal')
print('MST edges (Kruskal):', mst)
print('MST total weight:', net.get_mst_total_weight())

# Test 2: Shortest path
path, cost = net.compute_shortest_path('R1', 'R4')
print('\nShortest R1->R4:', path, 'cost=', cost)

# Test 3: Link failure
report = net.simulate_link_failure('R1', 'R2')
print('\nFailure R1-R2 disconnected:', report["disconnected_pairs"])

# Test 4: Star topology
net.generate_star_topology(5)
print('\n=== Star Topology (5 nodes) ===')
print('Routers:', net.get_routers())
print('Stats:', net.get_network_stats())

# Test 5: Mesh
net.generate_mesh_topology(4)
mst = net.get_mst_edges('prim')
print('\n=== Mesh Topology (4 nodes) ===')
print('Links count:', len(net.get_links()))
print('MST edges (Prim):', mst)

print('\nAll tests passed!')
