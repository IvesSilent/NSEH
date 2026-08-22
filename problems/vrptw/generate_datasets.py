# -*- coding: utf-8 -*-
# VRPTW（带时间窗车辆路径问题）数据集生成器
# 标准解：时间窗可行贪心（EDD 优先）+ 多起点随机化
# 每个实例保存为 (coordinates, distance_matrix, demands, capacity, time_windows, service_times)

import os
import pickle
import numpy as np


def generate_vrptw_instance(n_customers, seed=None):
    """
    生成 VRPTW 实例
    - 节点 0 为仓库（demand=0, time window [0, H]）
    - 客户: 坐标随机, demand 1..10, 时间窗以随机中心±宽度, 服务时间 1..10
    返回: (coordinates, distance_matrix, demands, capacity, time_windows, service_times)
    """
    rng = np.random.default_rng(seed)
    n = n_customers + 1
    coordinates = rng.uniform(0, 100, size=(n, 2))
    coordinates[0] = [50, 50]

    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distance_matrix = np.sqrt((diff ** 2).sum(-1))

    demands = np.concatenate([[0], rng.integers(1, 11, size=n_customers)])
    capacity = 50

    # 时间窗：ready ~ due（保证至少能从仓库出发单独服务）
    service_times = np.concatenate([[0], rng.integers(1, 11, size=n_customers)])
    time_windows = np.zeros((n, 2))
    for j in range(1, n):
        d0 = distance_matrix[0, j]
        ready = rng.integers(0, max(1, int(300 - d0 * 2)))
        due = ready + rng.integers(20, 80)
        # 保证可行性：due 至少 ≥ 仓库直达 + 服务时间 + 余量
        due = max(due, int(d0 + service_times[j] + 15))
        time_windows[j] = [ready, due]
    time_windows[0] = [0, 1000]

    return coordinates, distance_matrix, demands, capacity, time_windows, service_times


def vrptw_greedy(coordinates, distance_matrix, demands, capacity, time_windows, service_times, rng=None, strategy='edd'):
    """
    时间窗可行贪心（numpy 向量化），支持多种策略：
      'edd'    : 最早开始时间优先（+距离微调）
      'dist'   : 距离优先
      'slack'  : 时间窗松弛度优先（due - arrival 最小）
      'random' : 随机扰动扫描次序
    返回 (总距离, 是否全部服务)
    """
    n = distance_matrix.shape[0]
    unserved = np.ones(n, dtype=bool)
    unserved[0] = False
    total = 0.0
    route_count = 0

    while unserved.any() and route_count < n:
        route_count += 1
        current = 0
        current_time = 0.0
        current_load = 0
        served_any = False
        while True:
            cand = np.nonzero(unserved)[0]
            if len(cand) == 0:
                break
            load_ok = (current_load + demands[cand]) <= capacity
            arrival = current_time + distance_matrix[current, cand]
            tw_ok = arrival <= time_windows[cand, 1]
            feasible_mask = load_ok & tw_ok
            feasible = cand[feasible_mask]
            if len(feasible) == 0:
                break
            if strategy == 'dist':
                key = distance_matrix[current, feasible]
            elif strategy == 'slack':
                key = time_windows[feasible, 1] - arrival[feasible_mask]
            elif strategy == 'random':
                key = np.random.random(len(feasible)) if rng is None else rng.random(len(feasible))
            else:  # edd
                start = np.maximum(arrival[feasible_mask], time_windows[feasible, 0])
                key = start + distance_matrix[current, feasible] * 0.1
            j = int(feasible[np.argmin(key)])
            arrival_j = current_time + distance_matrix[current, j]
            current_time = max(arrival_j, time_windows[j, 0]) + service_times[j]
            current_load += demands[j]
            total += distance_matrix[current, j]
            current = j
            unserved[j] = False
            served_any = True
        total += distance_matrix[current, 0]
        if not served_any:
            break  # 本轮未服务任何客户，无法继续

    return total, not unserved.any()


def vrptw_standard_solve(coordinates, distance_matrix, demands, capacity, time_windows, service_times, rng=None, restarts=8):
    """标准解：多策略 + 随机化贪心取最优（保证可行性）"""
    best = float('inf')
    for strategy in ['edd', 'dist', 'slack']:
        total, served = vrptw_greedy(coordinates, distance_matrix, demands, capacity, time_windows, service_times, rng, strategy)
        if served:
            best = min(best, total)
    for _ in range(restarts):
        total, served = vrptw_greedy(coordinates, distance_matrix, demands, capacity, time_windows, service_times, rng, 'random')
        if served:
            best = min(best, total)
    return best if best != float('inf') else vrptw_greedy(coordinates, distance_matrix, demands, capacity, time_windows, service_times, rng, 'edd')[0], None


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，50 客户
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_vrptw_instance(50, seed=100 + i)
        total, _ = vrptw_standard_solve(*inst, rng_master)
        train_data.append(inst)
        train_solutions.append(total)
        if (i + 1) % 16 == 0:
            print(f"VRPTW 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_vrptw.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_vrptw.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("VRPTW 训练集保存完成")

    # 测试集：多规模
    test_configs = [50, 100, 200]
    for n_customers in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_vrptw_instance(n_customers, seed=1000 + i)
            total, _ = vrptw_standard_solve(*inst, rng_master)
            test_data.append(inst)
            test_solutions.append(total)

        with open(os.path.join(datasets_dir, f"test_data_{n_customers}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_customers}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"VRPTW{n_customers} 测试集保存完成")

    print("VRPTW 所有数据集生成完成！")
