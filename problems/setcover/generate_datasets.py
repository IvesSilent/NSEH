# -*- coding: utf-8 -*-
# Set Cover（集合覆盖）数据集生成器
# 标准解：贪心近似（每步选单位成本覆盖最多未覆盖元素的集合）
# 每个实例保存为 (set_membership, set_costs)
#   set_membership: (n_sets, n_elements) 0/1 矩阵
#   set_costs: (n_sets,) 每个集合的选取成本

import os
import pickle
import numpy as np


def generate_setcover_instance(n_elements, n_sets, density=0.2, seed=None):
    """
    生成集合覆盖实例（确保并集覆盖全部元素）
    返回: (set_membership, set_costs)
    """
    rng = np.random.default_rng(seed)
    membership = (rng.random((n_sets, n_elements)) < density).astype(int)
    # 保证每个元素至少被一个集合覆盖
    for e in range(n_elements):
        if membership[:, e].sum() == 0:
            membership[rng.integers(0, n_sets), e] = 1
    costs = rng.integers(1, 20, size=n_sets).astype(float)
    return membership, costs


def greedy_solve(set_membership, set_costs, rng=None, restarts=20):
    """
    多起点随机化贪心 + 冗余集合消除（标准解近似）
    返回: (总成本, 所选集合索引列表)
    """
    n_sets = set_membership.shape[0]
    n_elements = set_membership.shape[1]
    best_cost = float('inf')
    best_selected = []

    for trial in range(restarts):
        if rng is None:
            order = list(range(n_sets))  # 第一次确定性贪心
        else:
            order = list(range(n_sets))
            rng.shuffle(order)

        uncovered = np.ones(n_elements, dtype=bool)
        selected = []
        total_cost = 0.0
        guard = 0
        while uncovered.any() and guard < n_elements * 2:
            guard += 1
            best_set = -1
            best_ratio = -float('inf')
            for s in order:
                covered = 0
                for e in np.nonzero(set_membership[s])[0]:
                    if uncovered[e]:
                        covered += 1
                if covered > 0:
                    ratio = covered / (set_costs[s] + 1e-10)
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_set = s
            if best_set == -1:
                break
            selected.append(best_set)
            total_cost += set_costs[best_set]
            for e in np.nonzero(set_membership[best_set])[0]:
                uncovered[e] = False

        if not uncovered.any():
            # 冗余集合消除：若移除某集合仍全覆盖，则移除
            changed = True
            while changed:
                changed = False
                for s in selected[:]:
                    test_uncovered = np.zeros(n_elements, dtype=bool)
                    for t in selected:
                        if t != s:
                            for e in np.nonzero(set_membership[t])[0]:
                                test_uncovered[e] = True
                    if test_uncovered.all():
                        selected.remove(s)
                        total_cost -= set_costs[s]
                        changed = True
            if total_cost < best_cost:
                best_cost = total_cost
                best_selected = selected[:]

    return best_cost, best_selected


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，100 元素，50 集合
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_setcover_instance(100, 50, 0.2, seed=100 + i)
        cost, selected = greedy_solve(*inst, rng=np.random.default_rng(seed=2000 + i))
        train_data.append(inst)
        train_solutions.append((cost, selected))
        if (i + 1) % 16 == 0:
            print(f"SetCover 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_setcover.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_setcover.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("SetCover 训练集保存完成")

    # 测试集：多规模 (元素数, 集合数)
    test_configs = [(100, 50), (200, 100), (300, 150)]
    for n_elements, n_sets in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_setcover_instance(n_elements, n_sets, 0.2, seed=1000 + i)
            cost, selected = greedy_solve(*inst, rng=np.random.default_rng(seed=2000 + i))
            test_data.append(inst)
            test_solutions.append((cost, selected))

        with open(os.path.join(datasets_dir, f"test_data_{n_elements}x{n_sets}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_elements}x{n_sets}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"SetCover{n_elements}x{n_sets} 测试集保存完成")

    print("SetCover 所有数据集生成完成！")
