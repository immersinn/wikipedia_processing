"""
Build some example small-world networks to test code for partitioning
Wiki link data.
"""

import networkx as nx

seed = 8675309

# 30, 3, 0.1
num_nodes = 30
k_nearnest_neighbors = 3
prob_adding_new_edge = 0.1
nsw_G = nx.newman_watts_strogatz_graph(num_nodes,
                                       k_nearnest_neighbors,
                                       prob_adding_new_edge,
                                       seed=seed)

# 30, 3, 0.1
num_nodes = 30
k_nearnest_neighbors = 3
prob_adding_new_edge = 0.1
ws_G = nx.watts_strogatz_graph(num_nodes,
                               k_nearnest_neighbors,
                               prob_adding_new_edge,
                               seed=seed)

# 100, 5
num_nodes = 100
new_edges_to_add = 5
ba_G = nx.barabasi_albert_graph(num_nodes,
                                new_edges_to_add,
                                seed=seed)

# 100, 0.15
num_nodes = 100
prob_fr_edge_creation = 0.15
er_G = nx.erdos_renyi_graph(num_nodes,
                            prob_fr_edge_creation,
                            seed=seed)

# Spectral analysis
spec = nx.spectrum.adjacency_spectrum(er_G)
