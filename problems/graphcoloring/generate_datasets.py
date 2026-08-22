# -*- coding: utf-8 -*-
# Graph Coloring（图着色）数据集生成器
# 标准解：DSATUR 贪心近似（尽量少用颜色）
# 每个实例保存为 (adjacency_matrix,)

import os
import pickle
import numpy as np


def generate_graphcoloring_instance(n_nodes, edge_density=0.5, seed=None):
    """
    生成无向图（对称邻接矩阵，自环为0）
    返回: adjacency_matrix: (n_nodes, n_nodes)
    """
    rng = np.random.default_rng(seed)
    adj = np.zeros((n_nodes, n_nodes), dtype=int)
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if rng.random() < edge_density:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj


def dsatur_solve(adjacency_matrix):
    """
    DSATUR 贪心着色（标准解近似）
    返回: (使用的颜色数, 颜色分配数组)
    """
    n = adjacency_matrix.shape[0]
    colors = np.full(n, -1, dtype=int)

    def saturation(node):
        return len(set(colors[nb] for nb in np.nonzero(adjacency_matrix[node])[0] if colors[nb] >= 0))

    def degree(node):
        return int(np.sum(adjacency_matrix[node] > 0))

    remaining = set(range(n))
    while remaining:
        # 选饱和度最高、其次度数最高的未着色节点
        node = max(remaining, key=lambda v: (saturation(v), degree(v)))
        forbidden = set(colors[nb] for nb in np.nonzero(adjacency_matrix[node])[0] if colors[nb] >= 0)
        c = 0
        while c in forbidden:
            c += 1
        colors[node] = c
        remaining.remove(node)

    return int(colors.max() + 1), colors


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，60 节点，边密度 0.5
    train_data = []
    train_solutions = []
    for i in range(64):
        adj = generate_graphcoloring_instance(60, 0.5, seed=100 + i)
        n_colors, colors = dsatur_solve(adj)
        train_data.append(adj)
        train_solutions.append((n_colors, colors))
        if (i + 1) % 16 == 0:
            print(f"GraphColoring 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_graphcoloring.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_graphcoloring.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("GraphColoring 训练集保存完成")

    # 测试集：多规模
    test_configs = [(30, 0.5), (60, 0.5), (100, 0.4)]
    for n_nodes, density in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            adj = generate_graphcoloring_instance(n_nodes, density, seed=1000 + i)
            n_colors, colors = dsatur_solve(adj)
            test_data.append(adj)
            test_solutions.append((n_colors, colors))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"GraphColoring{n_nodes} 测试集保存完成")

    print("GraphColoring 所有数据集生成完成！")
