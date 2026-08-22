# -*- coding: utf-8 -*-
# Maximum Clique（最大团问题）数据集生成器
# 标准解：多起点度数贪心 + 局部改进（近似）
# 每个实例保存为 (adjacency_matrix,)

import os
import pickle
import numpy as np


def generate_maxclique_instance(n_nodes, edge_density=0.5, seed=None):
    """
    生成无向图（无自环）
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


def clique_greedy(adjacency_matrix, rng=None, start=None):
    """
    单次贪心：从 start（或度数最高节点）开始，每次选与当前团全相邻且度数最高的候选
    返回: (团大小, 团节点列表)
    """
    n = adjacency_matrix.shape[0]
    if start is None:
        start = int(np.argmax(adjacency_matrix.sum(axis=1)))
    clique = {int(start)}
    candidates = [v for v in range(n) if v != start and adjacency_matrix[start, v]]

    while candidates:
        # 候选 = 与当前团所有节点相邻
        best = None
        best_deg = -1
        for v in candidates:
            if all(adjacency_matrix[v, u] for u in clique):
                deg = int(adjacency_matrix[v].sum())
                if deg > best_deg:
                    best_deg = deg
                    best = v
        if best is None:
            break
        clique.add(best)
        candidates.remove(best)

    return len(clique), sorted(clique)


def maxclique_standard_solve(adjacency_matrix, rng=None, restarts=30):
    """标准解：多起点贪心取最大团"""
    n = adjacency_matrix.shape[0]
    best = 0
    best_clique = []
    starts = [int(np.argmax(adjacency_matrix.sum(axis=1)))]
    if rng is not None:
        nodes = list(range(n))
        rng.shuffle(nodes)
        starts += nodes[:restarts - 1]
    for s in starts[:restarts]:
        size, clique = clique_greedy(adjacency_matrix, rng, s)
        if size > best:
            best = size
            best_clique = clique
    return best, best_clique


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，60 节点，密度 0.5
    train_data = []
    train_solutions = []
    for i in range(64):
        adj = generate_maxclique_instance(60, 0.5, seed=100 + i)
        size, clique = maxclique_standard_solve(adj, rng_master)
        train_data.append(adj)
        train_solutions.append((size, clique))
        if (i + 1) % 16 == 0:
            print(f"MaxClique 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_maxclique.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_maxclique.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("MaxClique 训练集保存完成")

    # 测试集：多规模
    test_configs = [(30, 0.5), (60, 0.5), (100, 0.5)]
    for n_nodes, density in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            adj = generate_maxclique_instance(n_nodes, density, seed=1000 + i)
            size, clique = maxclique_standard_solve(adj, rng_master)
            test_data.append(adj)
            test_solutions.append((size, clique))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"MaxClique{n_nodes} 测试集保存完成")

    print("MaxClique 所有数据集生成完成！")
