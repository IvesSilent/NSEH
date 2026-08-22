# -*- coding: utf-8 -*-
# Steiner Tree（斯坦纳树）数据集生成器
# 标准解：最短路径贪心扩展（树 → 最近终端的最短路径）+ 多起点
# 每个实例保存为 (adjacency_matrix, terminals)
#   adjacency_matrix: (n_nodes, n_nodes) 带权邻接矩阵（0 表示无边）
#   terminals: 终端节点索引数组（节点 0 为根终端）

import os
import pickle
import numpy as np
import heapq


def generate_steinertree_instance(n_nodes, n_terminals, edge_density=0.3, seed=None):
    """
    生成带权无向图 + 终端集合
    返回: (adjacency_matrix, terminals)
    """
    rng = np.random.default_rng(seed)
    adj = np.zeros((n_nodes, n_nodes), dtype=float)
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if rng.random() < edge_density:
                w = rng.integers(1, 101)
                adj[i, j] = w
                adj[j, i] = w

    # 终端：节点 0 + 随机选 n_terminals-1 个
    terminals = np.concatenate([[0], rng.choice(np.arange(1, n_nodes), size=n_terminals - 1, replace=False)])
    return adj, terminals


def dijkstra(adjacency_matrix, source):
    """返回从 source 到所有节点的最短距离"""
    n = adjacency_matrix.shape[0]
    dist = np.full(n, float('inf'))
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in range(n):
            w = adjacency_matrix[u, v]
            if w > 0 and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


def steiner_greedy(adjacency_matrix, terminals, start_root=0):
    """
    贪心扩展：当前树为 {start_root}，每次选距树最近的未连接终端，沿最短路径加入节点
    返回: (总成本, 树节点集合)
    """
    n = adjacency_matrix.shape[0]
    all_dist = np.array([dijkstra(adjacency_matrix, s) for s in range(n)])
    tree = {int(start_root)}
    unconnected = set(int(t) for t in terminals if t != start_root)
    total = 0.0

    while unconnected:
        best_t = None
        best_d = float('inf')
        best_path = None
        for t in unconnected:
            d = all_dist[list(tree), t].min()
            if d < best_d:
                best_d = d
                best_t = t
        if best_t is None or best_d == float('inf'):
            break  # 图不连通
        # 沿最短路径加入节点
        t = best_t
        total += best_d
        # 把路径上的节点加入树（简化：直接加入终端，路径成本已计入）
        tree.add(t)
        unconnected.remove(t)

    return total, tree


def dijkstra_path(adjacency_matrix, source):
    """返回 (距离数组, 前驱矩阵路径重建用)：记录每个节点的前驱"""
    n = adjacency_matrix.shape[0]
    dist = np.full(n, float('inf'))
    dist[source] = 0
    prev = np.full(n, -1, dtype=int)
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in range(n):
            w = adjacency_matrix[u, v]
            if w > 0 and d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(pq, (d + w, v))
    return dist, prev


def _reconstruct_path(prev, target):
    """沿前驱重建路径节点列表"""
    path = []
    cur = target
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def steiner_standard_solve(adjacency_matrix, terminals, restarts=10):
    """
    标准解：KMB 算法（终端 MST + 最短路径展开为边集 + 子图 MST 重算）
    利用路径共享，成本通常低于 Prim 式贪心，为进化留空间。
    """
    n = adjacency_matrix.shape[0]
    terms = list(terminals)
    k = len(terms)
    if k <= 1:
        return 0.0, set(terms)

    # 终端对最短路径（距离 + 路径重建）
    dists = np.full((k, k), float('inf'))
    paths = {}
    for a in range(k):
        dist, prev = dijkstra_path(adjacency_matrix, terms[a])
        for b in range(k):
            dists[a, b] = dist[terms[b]]
            paths[(a, b)] = _reconstruct_path(prev, terms[b])

    # 终端完全图上的 Prim MST
    in_mst = [False] * k
    min_edge = [float('inf')] * k
    parent = [-1] * k
    min_edge[0] = 0
    mst_links = []
    for _ in range(k):
        u = min((i for i in range(k) if not in_mst[i]), key=lambda i: min_edge[i])
        in_mst[u] = True
        if parent[u] != -1:
            mst_links.append((parent[u], u))
        for v in range(k):
            if not in_mst[v] and dists[u, v] < min_edge[v]:
                min_edge[v] = dists[u, v]
                parent[v] = u

    # 展开路径边集（利用共享）
    edge_set = set()
    for a, b in mst_links:
        p = paths[(a, b)]
        for i in range(len(p) - 1):
            u, v = p[i], p[i + 1]
            edge_set.add((min(u, v), max(u, v)))

    # 子图（终端 + 路径节点）上的 MST：把路径展开后的子图再求一次 MST
    sub_nodes = set()
    for u, v in edge_set:
        sub_nodes.add(u)
        sub_nodes.add(v)
    sub_nodes = sorted(sub_nodes)
    idx = {node: i for i, node in enumerate(sub_nodes)}
    m = len(sub_nodes)
    # Prim on subgraph
    sub_adj = np.full((m, m), float('inf'))
    for u, v in edge_set:
        w = adjacency_matrix[u, v]
        sub_adj[idx[u], idx[v]] = min(sub_adj[idx[u], idx[v]], w)
        sub_adj[idx[v], idx[u]] = sub_adj[idx[u], idx[v]]
    in_sub = [False] * m
    min_e = [float('inf')] * m
    min_e[0] = 0
    total = 0.0
    for _ in range(m):
        u = min((i for i in range(m) if not in_sub[i]), key=lambda i: min_e[i])
        in_sub[u] = True
        total += min_e[u]
        for v in range(m):
            if not in_sub[v] and sub_adj[u, v] < min_e[v]:
                min_e[v] = sub_adj[u, v]
    return total, set(sub_nodes)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，80 节点，12 终端
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_steinertree_instance(80, 12, 0.3, seed=100 + i)
        total, tree = steiner_standard_solve(*inst)
        train_data.append(inst)
        train_solutions.append((total, sorted(tree)))
        if (i + 1) % 16 == 0:
            print(f"SteinerTree 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_steinertree.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_steinertree.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("SteinerTree 训练集保存完成")

    # 测试集：多规模 (节点数, 终端数)
    test_configs = [(50, 8), (100, 15), (200, 20)]
    for n_nodes, n_terms in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_steinertree_instance(n_nodes, n_terms, 0.3, seed=1000 + i)
            total, tree = steiner_standard_solve(*inst)
            test_data.append(inst)
            test_solutions.append((total, sorted(tree)))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}x{n_terms}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}x{n_terms}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"SteinerTree{n_nodes}x{n_terms} 测试集保存完成")

    print("SteinerTree 所有数据集生成完成！")
