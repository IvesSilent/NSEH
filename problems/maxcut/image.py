# -*- coding: utf-8 -*-
# MaxCut 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle
import networkx as nx


def plot_maxcut_solution(adjacency_matrix, partition, filename='maxcut_solution.png'):
    """绘制 MaxCut 图划分（使用 networkx）"""
    n = len(adjacency_matrix)
    G = nx.Graph()

    for i in range(n):
        G.add_node(i, partition=partition[i])

    for i in range(n):
        for j in range(i + 1, n):
            if adjacency_matrix[i, j] > 0:
                G.add_edge(i, j, weight=adjacency_matrix[i, j])

    pos = nx.spring_layout(G, seed=42, k=2 / np.sqrt(n))

    # 颜色：侧 0 和侧 1
    node_colors = ['#3fb950' if partition[i] == 0 else '#f0883e' for i in range(n)]

    # 边颜色：切边显示
    edge_colors = []
    edge_widths = []
    cut_edges_weight = 0
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        if partition[u] != partition[v]:
            edge_colors.append('#f85149')
            edge_widths.append(weight / 5 + 0.5)
            cut_edges_weight += weight
        else:
            edge_colors.append('#30363d')
            edge_widths.append(weight / 10 + 0.2)

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, node_color=node_colors, edge_color=edge_colors,
            width=edge_widths, node_size=100, with_labels=False,
            alpha=0.8)

    # Side legends
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#3fb950', markersize=12, label='Side 0'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f0883e', markersize=12, label='Side 1'),
        plt.Line2D([0], [0], color='#f85149', linewidth=2, label=f'Cut Edge (Weight: {cut_edges_weight:.0f})'),
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    plt.title(f'MaxCut Solution (Cut Value: {cut_edges_weight:.0f})')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()


if __name__ == "__main__":
    test_data_path = 'datasets/test_data_50.pkl'
    test_solution_path = 'datasets/test_solution_50.pkl'

    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    adjacency_matrix = test_data[0]
    best_partition_list, best_cut = test_solutions[0]

    print(f"节点数: {len(adjacency_matrix)}")
    print(f"基准切割值: {best_cut}")

    partition = np.array(best_partition_list)
    plot_maxcut_solution(adjacency_matrix, partition)
