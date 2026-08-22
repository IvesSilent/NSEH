# -*- coding: utf-8 -*-
# Orienteering（定向越野问题）数据集生成器
# 标准解：多起点利润/距离比贪心（带预算约束）
# 每个实例保存为 (coordinates, distance_matrix, profits, budget)
# 目标：最大化总利润 → 评估时取负（ascend=True 框架兼容）

import os
import pickle
import numpy as np


def generate_orienteering_instance(n_nodes, seed=None):
    """
    生成 Orienteering 实例
    - 节点 0 为起点/终点（depot），利润为 0
    - 客户: 坐标随机, 利润 1..100
    - 预算: 约为 depot 到各节点往返的规模（保证有解且非平凡）
    返回: (coordinates, distance_matrix, profits, budget)
    """
    rng = np.random.default_rng(seed)
    coordinates = rng.uniform(0, 100, size=(n_nodes, 2))
    coordinates[0] = [50, 50]
    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distance_matrix = np.sqrt((diff ** 2).sum(-1))
    profits = np.concatenate([[0], rng.integers(1, 101, size=n_nodes - 1)])

    # 预算：约为完整环线（最近邻）长度的 35%~55%，保证只能访问部分节点（非平凡）
    n_full = n_nodes
    visited = np.zeros(n_full, dtype=bool)
    visited[0] = True
    cur = 0
    full_len = 0.0
    for _ in range(n_full - 1):
        cand = np.nonzero(~visited)[0]
        nxt = cand[np.argmin(distance_matrix[cur, cand])]
        full_len += distance_matrix[cur, nxt]
        cur = nxt
        visited[nxt] = True
    full_len += distance_matrix[cur, 0]
    budget = full_len * rng.uniform(0.35, 0.55)

    return coordinates, distance_matrix, profits, budget


def orienteering_greedy(coordinates, distance_matrix, profits, budget, rng=None, start_node=0):
    """
    利润/距离比贪心构建路线
    rng 非 None 时随机打乱节点扫描顺序（产生不同解）
    返回: (总利润, 路线)
    """
    n = distance_matrix.shape[0]
    visited = np.zeros(n, dtype=bool)
    visited[start_node] = True
    route = [start_node]
    current = start_node
    budget_left = budget
    total_profit = 0.0

    # 扫描顺序：随机化打破平局
    scan_order = list(range(1, n))
    if rng is not None:
        rng.shuffle(scan_order)

    while True:
        best_node = None
        best_ratio = -float('inf')
        for j in scan_order:
            if visited[j]:
                continue
            dist = distance_matrix[current, j]
            return_dist = distance_matrix[j, 0]
            if dist + return_dist > budget_left + 1e-9:
                continue
            ratio = profits[j] / (dist + 1e-10)
            if ratio > best_ratio:
                best_ratio = ratio
                best_node = j
        if best_node is None:
            break
        j = best_node
        budget_left -= distance_matrix[current, j]
        total_profit += profits[j]
        visited[j] = True
        current = j
        route.append(j)

    return total_profit, route


def orienteering_local_search(coordinates, distance_matrix, profits, budget, route, max_rounds=20):
    """
    更强的局部搜索：反复尝试
      (1) 插入未访问节点（若预算允许）
      (2) 移除一个低利润节点并插入若干未访问节点（净利润增加）
    直到无法改进。
    """
    n = distance_matrix.shape[0]
    route = list(route)
    improved = True
    rounds = 0
    # 候选限制：利润最高的未访问节点 + 移除候选限制：利润最低的路线节点
    while improved and rounds < max_rounds:
        rounds += 1
        improved = False
        route_len = sum(distance_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
        in_route = set(route)
        unvisited_cands = [j for j in range(1, n) if j not in in_route]
        if len(unvisited_cands) > 30:
            unvisited_cands = sorted(unvisited_cands, key=lambda j: -profits[j])[:30]
        remove_cands = list(range(1, len(route) - 1))
        if len(remove_cands) > 15:
            remove_cands = sorted(remove_cands, key=lambda ri: profits[route[ri]])[:15]
        # 尝试插入单个未访问节点
        best_gain = -float('inf')
        best_ins = None
        for j in unvisited_cands:
            for pos in range(1, len(route)):
                extra = (distance_matrix[route[pos - 1], j] + distance_matrix[j, route[pos]]
                         - distance_matrix[route[pos - 1], route[pos]])
                if route_len + extra <= budget + 1e-9:
                    gain = profits[j]
                    if gain > best_gain:
                        best_gain = gain
                        best_ins = (j, pos, None, 0.0)
        # 尝试移除一个节点并插入一个节点
        for r_idx in remove_cands:
            r = route[r_idx]
            removed_len = (distance_matrix[route[r_idx - 1], r] + distance_matrix[r, route[r_idx + 1]]
                           - distance_matrix[route[r_idx - 1], route[r_idx + 1]])
            new_len = route_len - removed_len
            for j in unvisited_cands:
                if j == r:
                    continue
                for pos in range(1, len(route)):
                    if pos == r_idx or pos == r_idx + 1:
                        continue
                    extra = (distance_matrix[route[pos - 1], j] + distance_matrix[j, route[pos]]
                             - distance_matrix[route[pos - 1], route[pos]])
                    if new_len + extra <= budget + 1e-9:
                        gain = profits[j] - profits[r]
                        if gain > best_gain:
                            best_gain = gain
                            best_ins = (j, pos, r_idx, removed_len)
        if best_ins is not None:
            j, pos, r_idx, removed_len = best_ins
            if r_idx is not None:
                route.pop(r_idx)
                if pos > r_idx:
                    pos -= 1
            route.insert(pos, j)
            improved = True
    return sum(profits[i] for i in route), route


def orienteering_standard_solve(coordinates, distance_matrix, profits, budget, rng=None, restarts=8):
    """标准解：固定从起点出发随机化贪心 + 局部搜索改进取最优（明显强于示例启发式）"""
    best = -float('inf')
    best_route = []
    for _ in range(restarts):
        profit, route = orienteering_greedy(coordinates, distance_matrix, profits, budget, rng, 0)
        profit, route = orienteering_local_search(coordinates, distance_matrix, profits, budget, route)
        if profit > best:
            best = profit
            best_route = route
    return best, best_route


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，100 节点
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_orienteering_instance(100, seed=100 + i)
        coords, D, P, B = inst
        profit, route = orienteering_standard_solve(coords, D, P, B, rng_master)
        train_data.append(inst)
        train_solutions.append((profit, route))
        if (i + 1) % 16 == 0:
            print(f"Orienteering 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_orienteering.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_orienteering.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("Orienteering 训练集保存完成")

    # 测试集：多规模
    test_configs = [50, 100, 200]
    for n_nodes in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_orienteering_instance(n_nodes, seed=1000 + i)
            coords, D, P, B = inst
            profit, route = orienteering_standard_solve(coords, D, P, B, rng_master)
            test_data.append(inst)
            test_solutions.append((profit, route))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"Orienteering{n_nodes} 测试集保存完成")

    print("Orienteering 所有数据集生成完成！")
