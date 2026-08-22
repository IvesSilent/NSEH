# -*- coding: utf-8 -*-
# Parallel Machine Scheduling（并行机调度 P||Cmax）数据集生成器
# 标准解：LPT + 随机化次序 + 局部交换改进
# 每个实例保存为 (processing_times, num_machines)

import os
import pickle
import numpy as np


def generate_parmachine_instance(n_jobs, num_machines, seed=None):
    """
    生成并行机实例（相同机器，目标最小化 makespan）
    返回: (processing_times, num_machines)
    """
    rng = np.random.default_rng(seed)
    p = rng.integers(1, 100, size=n_jobs).astype(float)
    return p, num_machines


def parmachine_evaluate(assignment, p, m):
    """计算 makespan"""
    loads = np.zeros(m)
    for j, mach in enumerate(assignment):
        loads[mach] += p[j]
    return loads.max()


def parmachine_greedy(p, m, order=None, rule='minload', rng=None):
    """
    按给定作业顺序 + 选机器规则 构建分配
    返回: (assignment, makespan)
    """
    n = len(p)
    if order is None:
        if rule == 'lpt':
            order = list(np.argsort(-p))
        elif rule == 'random':
            order = list(range(n))
            if rng is not None:
                rng.shuffle(order)
        else:
            order = list(range(n))
    loads = np.zeros(m)
    assignment = [-1] * n
    for j in order:
        if rule == 'minload':
            mach = int(np.argmin(loads))
        elif rule == 'lpt_mach':
            mach = int(np.argmin(loads))
        else:
            mach = int(np.argmin(loads))
        assignment[j] = mach
        loads[mach] += p[j]
    return assignment, loads.max()


def parmachine_local_search(assignment, p, m):
    """
    局部搜索（强化版）：
      (1) 任意作业迁移到其他机器（若降低 makespan）
      (2) 跨机器两两交换（若降低 makespan）
    反复直至无改进。
    """
    n = len(p)
    improved = True
    while improved:
        improved = False
        loads = np.zeros(m)
        for j, mach in enumerate(assignment):
            loads[mach] += p[j]
        cmax = loads.max()
        # (1) 单作业迁移
        for j in range(n):
            src = assignment[j]
            for dst in range(m):
                if dst == src:
                    continue
                new_cmax = max(cmax, loads[dst] + p[j])
                # 迁移后 src 负载下降，若新 makespan 更小则接受
                if loads[src] - p[j] <= new_cmax and new_cmax < cmax:
                    assignment[j] = dst
                    loads[src] -= p[j]
                    loads[dst] += p[j]
                    improved = True
                    break
            if improved:
                break
        if improved:
            continue
        # (2) 跨机器交换
        for j in range(n):
            for k in range(j + 1, n):
                if assignment[j] == assignment[k]:
                    continue
                src_j, src_k = assignment[j], assignment[k]
                new_loads = loads.copy()
                new_loads[src_j] = new_loads[src_j] - p[j] + p[k]
                new_loads[src_k] = new_loads[src_k] - p[k] + p[j]
                new_cmax = new_loads.max()
                if new_cmax < cmax - 1e-9:
                    assignment[j], assignment[k] = assignment[k], assignment[j]
                    loads = new_loads
                    cmax = new_cmax
                    improved = True
                    break
            if improved:
                break
    return assignment, loads.max()


def parmachine_standard_solve(p, m, rng=None, restarts=20):
    """标准解：LPT + 随机次序 + 局部搜索取最优"""
    best = float('inf')
    best_assignment = None
    # LPT
    assignment, cmax = parmachine_greedy(p, m, rule='lpt')
    assignment, cmax = parmachine_local_search(assignment, p, m)
    best = cmax
    best_assignment = assignment[:]
    # 随机化
    for _ in range(restarts):
        assignment, cmax = parmachine_greedy(p, m, rule='random', rng=rng)
        assignment, cmax = parmachine_local_search(assignment, p, m)
        if cmax < best:
            best = cmax
            best_assignment = assignment[:]
    return best, best_assignment


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，100 作业，4 机器
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_parmachine_instance(100, 4, seed=100 + i)
        cost, assignment = parmachine_standard_solve(*inst, rng_master)
        train_data.append(inst)
        train_solutions.append((cost, assignment))
        if (i + 1) % 16 == 0:
            print(f"ParMachine 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_parmachine.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_parmachine.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("ParMachine 训练集保存完成")

    # 测试集：多规模 (作业数, 机器数)
    test_configs = [(50, 4), (100, 8), (200, 8)]
    for n_jobs, m in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_parmachine_instance(n_jobs, m, seed=1000 + i)
            cost, assignment = parmachine_standard_solve(*inst, rng_master)
            test_data.append(inst)
            test_solutions.append((cost, assignment))

        with open(os.path.join(datasets_dir, f"test_data_{n_jobs}x{m}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_jobs}x{m}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"ParMachine{n_jobs}x{m} 测试集保存完成")

    print("ParMachine 所有数据集生成完成！")
