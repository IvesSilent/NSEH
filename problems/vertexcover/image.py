# -*- coding: utf-8 -*-
# Minimum Vertex Cover 可视化

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle


def plot_vertexcover_solution(adjacency_matrix, cover, filename='vertexcover_solution.png'):
    """绘制顶点覆盖结果（红色为覆盖节点）"""
    G = nx.from_numpy_array(adjacency_matrix)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    in_cover = [i for i in range(len(cover)) if cover[i]]
    not_cover = [i for i in range(len(cover)) if not cover[i]]
    nx.draw_networkx_nodes(G, pos, nodelist=not_cover, node_color='lightblue', node_size=200, label='Not in cover')
    nx.draw_networkx_nodes(G, pos, nodelist=in_cover, node_color='red', node_size=260, label='In cover')
    nx.draw_networkx_labels(G, pos, font_size=7)
    plt.title(f'Minimum Vertex Cover (size: {len(in_cover)})')
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_40.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_40.pkl", "rb") as f:
        solutions = pickle.load(f)

    adj = data[0]
    size, cover_list = solutions[0]
    cover = np.zeros(adj.shape[0], dtype=bool)
    cover[list(cover_list)] = True
    plot_vertexcover_solution(adj, cover)
    print("vertexcover_solution.png 已生成")
