# -*- coding: utf-8 -*-
# k-Center（k 中心问题）数据集生成器
# 标准解：最远点贪心 + 局部交换改进
# 每个实例保存为 (coordinates, distance_matrix, k)

import os
import pickle
import numpy as np


def generate_kcenter_instance(n_nodes, k, seed=None):
    """
    生成 k-Center 实例
    返回: (coordinates, distance_matrix, k)
    """
    rng = np.random.default_rng(seed)
    coordinates = rng.uniform(0, 100, size=(n_nodes, 2))
    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distance_matrix = np.sqrt((diff ** 2).sum(-1))
    return coordinates, distance_matrix, k


def kcenter_objective(distance_matrix, centers):
    """最大覆盖距离（所有节点到最近中心的距离最大值）"""
    return float(distance_matrix[:, centers].min(axis=1).max())


def kcenter_greedy(distance_matrix, k, start=0, rng=None):
    """最远点贪心：第一个中心为 start，后续选距最近中心最远的节点"""
    n = distance_matrix.shape[0]
    centers = [start]
    remaining = list(range(n))
    remaining.remove(start)
    while len(centers) < k and remaining:
        best = max(remaining, key=lambda v: distance_matrix[centers, v].min())
        centers.append(best)
        remaining.remove(best)
    return centers


def kcenter_local_search(distance_matrix, k, centers):
    """局部搜索：尝试替换中心（若降低最大覆盖距离）"""
    n = distance_matrix.shape[0]
    improved = True
    while improved:
        improved = False
        cur_obj = kcenter_objective(distance_matrix, centers)
        for idx in range(len(centers)):
            for cand in range(n):
                if cand in centers:
                    continue
                new_centers = centers[:idx] + [cand] + centers[idx + 1:]
                new_obj = kcenter_objective(distance_matrix, new_centers)
                if new_obj < cur_obj:
                    centers = new_centers
                    cur_obj = new_obj
                    improved = True
                    break
            if improved:
                break
    return centers, cur_obj


def kcenter_standard_solve(distance_matrix, k, rng=None, restarts=15):
    """标准解：多起点最远点贪心 + 局部搜索取最优"""
    n = distance_matrix.shape[0]
    best = float('inf')
    best_centers = None
    starts = list(range(n))
    if rng is not None:
        rng.shuffle(starts)
    for start in starts[:restarts]:
        centers = kcenter_greedy(distance_matrix, k, start)
        centers, obj = kcenter_local_search(distance_matrix, k, centers)
        if obj < best:
            best = obj
            best_centers = centers
    return best, best_centers


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，100 节点，k=8
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_kcenter_instance(100, 8, seed=100 + i)
        coords, D, k = inst
        obj, centers = kcenter_standard_solve(D, k, rng_master)
        train_data.append(inst)
        train_solutions.append((obj, centers))
        if (i + 1) % 16 == 0:
            print(f"kCenter 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_kcenter.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_kcenter.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("kCenter 训练集保存完成")

    # 测试集：多规模 (节点数, k)
    test_configs = [(50, 5), (100, 10), (200, 10)]
    for n_nodes, k in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_kcenter_instance(n_nodes, k, seed=1000 + i)
            coords, D, k_ = inst
            obj, centers = kcenter_standard_solve(D, k_, rng_master)
            test_data.append(inst)
            test_solutions.append((obj, centers))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}x{k}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}x{k}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"kCenter{n_nodes}x{k} 测试集保存完成")

    print("kCenter 所有数据集生成完成！")
