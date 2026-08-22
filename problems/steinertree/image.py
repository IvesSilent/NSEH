# -*- coding: utf-8 -*-
# Steiner Tree 可视化

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle


def plot_steinertree_solution(adjacency_matrix, terminals, tree_nodes, filename='steinertree_solution.png'):
    """绘制斯坦纳树（红=终端，黄=斯坦纳点，粗边=所选边）"""
    G = nx.from_numpy_array(adjacency_matrix)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, weight=None)

    # 未选边
    nx.draw_networkx_edges(G, pos, alpha=0.15)

    # 所选边（树中节点的边）
    tree_set = set(tree_nodes)
    selected_edges = [(u, v) for u, v in G.edges() if u in tree_set and v in tree_set]
    nx.draw_networkx_edges(G, pos, edgelist=selected_edges, edge_color='red', width=2)

    normal_nodes = [i for i in range(G.number_of_nodes()) if i not in tree_set and i not in terminals]
    steiner_nodes = [i for i in tree_set if i not in terminals]
    terminal_nodes = list(terminals)

    nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_color='lightgray', node_size=60)
    nx.draw_networkx_nodes(G, pos, nodelist=steiner_nodes, node_color='gold', node_size=120, label='Steiner nodes')
    nx.draw_networkx_nodes(G, pos, nodelist=terminal_nodes, node_color='red', node_size=200, label='Terminals')

    plt.title('Steiner Tree Solution')
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50x8.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50x8.pkl", "rb") as f:
        solutions = pickle.load(f)

    adj, terminals = data[0]
    cost, tree = solutions[0]
    plot_steinertree_solution(adj, terminals, tree)
    print(f"steinertree_solution.png 已生成 (cost={cost:.0f})")
