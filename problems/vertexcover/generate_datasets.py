# -*- coding: utf-8 -*-
# Minimum Vertex Cover（最小顶点覆盖）数据集生成器
# 标准解：多起点贪心 + 局部消除（近似）
# 每个实例保存为 (adjacency_matrix,)
#   adjacency_matrix: (n_nodes, n_nodes) 无向图邻接矩阵

import os
import pickle
import numpy as np


def generate_vertexcover_instance(n_nodes, edge_density=0.3, seed=None):
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


def greedy_vc(adjacency_matrix, rng=None):
    """
    单次贪心：每次选覆盖最多未覆盖边的节点（平局随机化）
    返回: (覆盖大小, 覆盖节点列表)
    """
    n = adjacency_matrix.shape[0]
    uncovered = adjacency_matrix.copy().astype(bool)
    cover = np.zeros(n, dtype=bool)
    guard = 0
    while uncovered.any() and guard < n * 2:
        guard += 1
        best_nodes = []
        best_count = -1
        for v in range(n):
            if cover[v]:
                continue
            cnt = int(np.sum(uncovered[v]))
            if cnt > best_count:
                best_count = cnt
                best_nodes = [v]
            elif cnt == best_count and cnt > 0:
                best_nodes.append(v)
        if not best_nodes:
            break
        v = int(rng.choice(best_nodes)) if rng is not None and len(best_nodes) > 1 else best_nodes[0]
        cover[v] = True
        uncovered[v, :] = False
        uncovered[:, v] = False
    return int(cover.sum()), list(np.nonzero(cover)[0])


def vc_standard_solve(adjacency_matrix, rng=None, restarts=30):
    """
    标准解：多起点贪心 + 冗余节点消除
    返回: (覆盖大小, 覆盖节点列表)
    """
    n = adjacency_matrix.shape[0]
    best_size = float('inf')
    best_cover = []

    for trial in range(restarts):
        size, cover_list = greedy_vc(adjacency_matrix, rng)
        # 冗余消除：若移除某节点后仍是覆盖，则移除
        cover_set = set(cover_list)
        changed = True
        while changed:
            changed = False
            for v in list(cover_set):
                test = cover_set - {v}
                is_cover = True
                for i in range(n):
                    for j in range(i + 1, n):
                        if adjacency_matrix[i, j] and (i not in test and j not in test):
                            is_cover = False
                            break
                    if not is_cover:
                        break
                if is_cover:
                    cover_set.remove(v)
                    changed = True
        if len(cover_set) < best_size:
            best_size = len(cover_set)
            best_cover = sorted(cover_set)

    return best_size, best_cover


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，60 节点，边密度 0.3
    train_data = []
    train_solutions = []
    for i in range(64):
        adj = generate_vertexcover_instance(60, 0.3, seed=100 + i)
        size, cover = vc_standard_solve(adj, rng_master)
        train_data.append(adj)
        train_solutions.append((size, cover))
        if (i + 1) % 16 == 0:
            print(f"VertexCover 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_vertexcover.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_vertexcover.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("VertexCover 训练集保存完成")

    # 测试集：多规模
    test_configs = [(40, 0.3), (80, 0.3), (120, 0.25)]
    for n_nodes, density in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            adj = generate_vertexcover_instance(n_nodes, density, seed=1000 + i)
            size, cover = vc_standard_solve(adj, rng_master)
            test_data.append(adj)
            test_solutions.append((size, cover))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"VertexCover{n_nodes} 测试集保存完成")

    print("VertexCover 所有数据集生成完成！")
