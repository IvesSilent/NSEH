# -*- coding: utf-8 -*-
# Maximum Clique 可视化

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle


def plot_maxclique_solution(adjacency_matrix, clique, filename='maxclique_solution.png'):
    """绘制最大团（红色高亮团内节点与边）"""
    G = nx.from_numpy_array(adjacency_matrix)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_edges(G, pos, alpha=0.2)
    clique_edges = [(u, v) for u, v in G.edges() if u in clique and v in clique]
    nx.draw_networkx_edges(G, pos, edgelist=clique_edges, edge_color='red', width=2.5)
    non_clique = [i for i in range(G.number_of_nodes()) if i not in clique]
    nx.draw_networkx_nodes(G, pos, nodelist=non_clique, node_color='lightblue', node_size=120)
    nx.draw_networkx_nodes(G, pos, nodelist=clique, node_color='red', node_size=260, label='Clique')
    plt.title(f'Maximum Clique (size: {len(clique)})')
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_30.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_30.pkl", "rb") as f:
        solutions = pickle.load(f)

    adj = data[0]
    size, clique = solutions[0]
    plot_maxclique_solution(adj, clique)
    print(f"maxclique_solution.png 已生成 (size={size})")
