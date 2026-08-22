# -*- coding: utf-8 -*-
# Graph Coloring 可视化

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle


def plot_graphcoloring_solution(adjacency_matrix, colors, filename='graphcoloring_solution.png'):
    """绘制图着色结果"""
    G = nx.from_numpy_array(adjacency_matrix)
    cmap = plt.cm.tab10
    node_colors = [cmap(c % 10) for c in colors]
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=200)
    nx.draw_networkx_labels(G, pos, font_size=7)
    plt.title(f'Graph Coloring (colors used: {int(max(colors)) + 1})')
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
    n_colors, colors = solutions[0]
    plot_graphcoloring_solution(adj, colors)
    print("graphcoloring_solution.png 已生成")
