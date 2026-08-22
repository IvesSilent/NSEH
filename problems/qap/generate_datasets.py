# -*- coding: utf-8 -*-
# QAP（二次分配问题）数据集生成器
# 标准解：贪心（按流量降序分配）+ 多起点 + 成对交换局部搜索
# 每个实例保存为 (flow_matrix, distance_matrix)

import os
import pickle
import numpy as np


def generate_qap_instance(n, seed=None):
    """
    生成 QAP 实例（n 设施 × n 位置）
    - flow_matrix: 设施间流量 0..20
    - distance_matrix: 位置间距离 1..30
    返回: (flow_matrix, distance_matrix)
    """
    rng = np.random.default_rng(seed)
    flow = rng.integers(0, 21, size=(n, n)).astype(float)
    flow = (flow + flow.T) / 2
    np.fill_diagonal(flow, 0)
    dist = rng.integers(1, 31, size=(n, n)).astype(float)
    dist = (dist + dist.T) / 2
    np.fill_diagonal(dist, 0)
    return flow, dist


def qap_cost(flow, dist, assignment):
    """计算给定分配（设施→位置）的总成本"""
    n = len(assignment)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += flow[i, j] * dist[assignment[i], assignment[j]]
    return total


def qap_greedy(flow, dist, order=None, rng=None):
    """按设施顺序贪心分配（每个设施选最小增量位置）"""
    n = flow.shape[0]
    if order is None:
        # 默认按总流量降序
        order = list(np.argsort(-flow.sum(axis=1)))
    assignment = np.full(n, -1, dtype=int)
    available = list(range(n))
    for f in order:
        best_pos = None
        best_cost = float('inf')
        for pos in available:
            cost = 0.0
            for other, assigned_pos in enumerate(assignment):
                if assigned_pos >= 0:
                    cost += flow[f, other] * dist[pos, assigned_pos]
                    cost += flow[other, f] * dist[assigned_pos, pos]
            if cost < best_cost:
                best_cost = cost
                best_pos = pos
        assignment[f] = best_pos
        available.remove(best_pos)
    return assignment, qap_cost(flow, dist, assignment)


def qap_local_search(flow, dist, assignment):
    """成对交换局部搜索：交换两个设施的位置若降低成本"""
    n = len(assignment)
    cur_cost = qap_cost(flow, dist, assignment)
    improved = True
    while improved:
        improved = False
        for i in range(n):
            for j in range(i + 1, n):
                # 计算交换 i,j 的增量
                delta = 0.0
                for k in range(n):
                    if k == i or k == j:
                        continue
                    pi, pj, pk = assignment[i], assignment[j], assignment[k]
                    delta += (flow[i, k] - flow[j, k]) * (dist[pj, pk] - dist[pi, pk])
                    delta += (flow[k, i] - flow[k, j]) * (dist[pk, pj] - dist[pk, pi])
                # 对角项
                delta += (flow[i, j] + flow[j, i]) * (dist[pj, pi] - dist[pi, pj]) * 0.5 * 2
                if cur_cost + delta < cur_cost - 1e-9:
                    assignment[i], assignment[j] = assignment[j], assignment[i]
                    cur_cost += delta
                    improved = True
        # 简化：上面 delta 计算可能不准，用全量重算兜底
        new_cost = qap_cost(flow, dist, assignment)
        if new_cost < cur_cost - 1e-9:
            cur_cost = new_cost
            improved = True
    return assignment, cur_cost


def qap_standard_solve(flow, dist, rng=None, restarts=20):
    """标准解：多起点贪心 + 局部搜索取最优"""
    n = flow.shape[0]
    best = float('inf')
    best_assignment = None
    # 默认顺序
    assignment, cost = qap_greedy(flow, dist)
    assignment, cost = qap_local_search(flow, dist, assignment)
    best = cost
    best_assignment = assignment.copy()
    # 随机顺序
    for _ in range(restarts):
        order = list(range(n))
        if rng is not None:
            rng.shuffle(order)
        assignment, cost = qap_greedy(flow, dist, order)
        assignment, cost = qap_local_search(flow, dist, assignment)
        if cost < best:
            best = cost
            best_assignment = assignment.copy()
    return best, best_assignment


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，12 设施
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_qap_instance(12, seed=100 + i)
        cost, assignment = qap_standard_solve(*inst, rng_master)
        train_data.append(inst)
        train_solutions.append((cost, assignment))
        if (i + 1) % 16 == 0:
            print(f"QAP 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_qap.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_qap.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("QAP 训练集保存完成")

    # 测试集：多规模
    test_configs = [8, 12, 16]
    for n in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_qap_instance(n, seed=1000 + i)
            cost, assignment = qap_standard_solve(*inst, rng_master)
            test_data.append(inst)
            test_solutions.append((cost, assignment))

        with open(os.path.join(datasets_dir, f"test_data_{n}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"QAP{n} 测试集保存完成")

    print("QAP 所有数据集生成完成！")
