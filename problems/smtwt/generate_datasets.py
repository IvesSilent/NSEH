# -*- coding: utf-8 -*-
# SMTWT（单机加权延误调度 1||ΣwT）数据集生成器
# 标准解：多规则贪心（WSPT/EDD/MS）+ 局部交换改进
# 每个实例保存为 (processing_times, due_dates, weights)

import os
import pickle
import numpy as np


def generate_smtwt_instance(n_jobs, seed=None):
    """
    生成单机加权延误实例
    - processing_times: 1..50
    - due_dates: 按处理时间和紧度生成（混合宽松/紧凑）
    - weights: 1..10
    返回: (processing_times, due_dates, weights)
    """
    rng = np.random.default_rng(seed)
    p = rng.integers(1, 51, size=n_jobs)
    w = rng.integers(1, 11, size=n_jobs)
    # 紧度因子 0.3~1.2 混合
    tightness = rng.uniform(0.3, 1.2, size=n_jobs)
    d = (p * tightness * n_jobs * 0.5).astype(int) + rng.integers(0, 20, size=n_jobs)
    d = np.maximum(d, p)
    return p.astype(float), d.astype(float), w.astype(float)


def smtwt_evaluate(sequence, p, d, w):
    """计算序列的 ΣwT"""
    t = 0.0
    total = 0.0
    for j in sequence:
        t += p[j]
        total += w[j] * max(0, t - d[j])
    return total


def smtwt_greedy(p, d, w, rule='wspt', rng=None):
    """按规则贪心构建序列（每次选最优先的作业）"""
    n = len(p)
    remaining = list(range(n))
    seq = []
    t = 0.0
    while remaining:
        if rule == 'wspt':
            j = min(remaining, key=lambda x: p[x] / (w[x] + 1e-10))
        elif rule == 'edd':
            j = min(remaining, key=lambda x: d[x])
        elif rule == 'ms':
            # Modified Due Date: max(d, t+p)
            j = min(remaining, key=lambda x: max(d[x], t + p[x]))
        elif rule == 'random':
            j = int(rng.choice(remaining)) if rng is not None else remaining[0]
        else:
            j = remaining[0]
        seq.append(j)
        t += p[j]
        remaining.remove(j)
    return seq


def smtwt_local_search(seq, p, d, w, max_passes=3):
    """局部搜索：相邻交换改进（直至无改进）"""
    n = len(seq)
    cur_cost = smtwt_evaluate(seq, p, d, w)
    improved = True
    passes = 0
    while improved and passes < max_passes:
        passes += 1
        improved = False
        for i in range(n - 1):
            seq[i], seq[i + 1] = seq[i + 1], seq[i]
            new_cost = smtwt_evaluate(seq, p, d, w)
            if new_cost < cur_cost:
                cur_cost = new_cost
                improved = True
            else:
                seq[i], seq[i + 1] = seq[i + 1], seq[i]
    return seq, cur_cost


def smtwt_standard_solve(p, d, w, rng=None, restarts=8):
    """标准解：多规则 + 随机化贪心 + 相邻交换局部搜索取最优"""
    best = float('inf')
    best_seq = None
    rules = ['wspt', 'edd', 'ms']
    for rule in rules:
        seq = smtwt_greedy(p, d, w, rule)
        seq, cost = smtwt_local_search(seq, p, d, w)
        if cost < best:
            best = cost
            best_seq = seq
    for _ in range(restarts):
        seq = smtwt_greedy(p, d, w, 'random', rng)
        seq, cost = smtwt_local_search(seq, p, d, w)
        if cost < best:
            best = cost
            best_seq = seq
    return best, best_seq


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，50 作业
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_smtwt_instance(50, seed=100 + i)
        cost, seq = smtwt_standard_solve(*inst, rng_master)
        train_data.append(inst)
        train_solutions.append((cost, seq))
        if (i + 1) % 16 == 0:
            print(f"SMTWT 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_smtwt.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_smtwt.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("SMTWT 训练集保存完成")

    # 测试集：多规模
    test_configs = [50, 100, 200]
    for n_jobs in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_smtwt_instance(n_jobs, seed=1000 + i)
            cost, seq = smtwt_standard_solve(*inst, rng_master)
            test_data.append(inst)
            test_solutions.append((cost, seq))

        with open(os.path.join(datasets_dir, f"test_data_{n_jobs}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_jobs}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"SMTWT{n_jobs} 测试集保存完成")

    print("SMTWT 所有数据集生成完成！")
