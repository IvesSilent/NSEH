# -*- coding: utf-8 -*-
# MaxCut 数据集生成器

import os
import pickle
import numpy as np


def generate_maxcut_instance(n_nodes, edge_density=0.5):
    """
    生成 MaxCut 实例（随机图，带权）
    返回: adjacency_matrix: (n_nodes, n_nodes)
    """
    # 先生成随机连通图
    adj = np.zeros((n_nodes, n_nodes), dtype=float)
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if np.random.random() < edge_density:
                weight = np.random.randint(1, 20)
                adj[i, j] = weight
                adj[j, i] = weight

    # 确保图连通: 生成一个随机生成树
    if not _is_connected(adj, n_nodes):
        # 加边直到连通
        _ensure_connected(adj, n_nodes)

    return adj


def _is_connected(adj, n):
    """检查图是否连通（BFS）"""
    if n <= 1:
        return True
    visited = set()
    stack = [0]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for neighbor in range(n):
                if adj[node, neighbor] > 0 and neighbor not in visited:
                    stack.append(neighbor)
    return len(visited) == n


def _ensure_connected(adj, n):
    """确保图连通"""
    visited = set()
    stack = [0]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for neighbor in range(n):
                if adj[node, neighbor] > 0 and neighbor not in visited:
                    stack.append(neighbor)
    for v in range(n):
        if v not in visited:
            adj[0, v] = np.random.randint(1, 20)
            adj[v, 0] = adj[0, v]
            visited.add(v)


def greedy_random_maxcut(adj, trials=10):
    """
    简单贪心 + 随机重启求解 MaxCut
    返回: (最佳划分, 最佳切割值)
    """
    n = len(adj)
    best_cut = 0
    best_partition = None

    for _ in range(trials):
        # 随机初始划分
        partition = np.random.choice([0, 1], size=n)

        # 局部搜索：逐节点贪心
        improved = True
        while improved:
            improved = False
            for v in range(n):
                current_side = partition[v]
                # 计算切换的收益
                gain = 0
                for u in range(n):
                    if adj[v, u] > 0:
                        if partition[u] == current_side:
                            gain += adj[v, u]
                        else:
                            gain -= adj[v, u]
                if gain > 0:
                    partition[v] = 1 - current_side
                    improved = True

        # 计算切割值
        cut_value = 0
        for i in range(n):
            for j in range(i + 1, n):
                if partition[i] != partition[j]:
                    cut_value += adj[i, j]

        if cut_value > best_cut:
            best_cut = cut_value
            best_partition = partition.copy()

    return best_partition, best_cut


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # --- 训练集：64 个实例，100 个节点 ---
    train_data = []
    train_solutions = []
    for i in range(64):
        adj = generate_maxcut_instance(100, edge_density=0.3)
        best_partition, best_cut = greedy_random_maxcut(adj, trials=20)
        train_data.append(adj)
        train_solutions.append((best_partition.tolist(), best_cut))
        if (i + 1) % 16 == 0:
            print(f"MaxCut 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_maxcut.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_maxcut.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("MaxCut 训练集保存完成")

    # --- 测试集 ---
    test_sizes = [50, 100, 200]
    for size in test_sizes:
        test_data = []
        test_solutions = []
        for i in range(10):
            adj = generate_maxcut_instance(size, edge_density=0.3)
            best_partition, best_cut = greedy_random_maxcut(adj, trials=20)
            test_data.append(adj)
            test_solutions.append((best_partition.tolist(), best_cut))
            print(f"MaxCut{size} 测试实例 {i+1}/10 生成完成")

        with open(os.path.join(datasets_dir, f"test_data_{size}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{size}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"MaxCut{size} 测试集保存完成")

    print("MaxCut 所有数据集生成完成！")
