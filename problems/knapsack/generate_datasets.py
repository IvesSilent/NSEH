# -*- coding: utf-8 -*-
# 0/1 背包问题 数据集生成器

import os
import pickle
import numpy as np


def generate_knapsack_instance(n_items, max_weight=200, max_value=100):
    """
    生成 0/1 背包实例（控制容量大小以保证 DP 可解）
    返回: (weights, values, capacity)
    """
    weights = np.random.randint(1, max_weight, size=n_items)
    values = np.random.randint(1, max_value, size=n_items)
    # 容量设为总重量的 20%-35%（适中，保证 DP 在合理时间内）
    capacity = int(np.random.uniform(0.2, 0.35) * weights.sum())
    return weights, values, capacity


def dp_knapsack(weights, values, capacity):
    """
    动态规划求解 0/1 背包问题（精确最优解）
    返回最佳总价值
    """
    n = len(weights)
    dp = np.zeros(capacity + 1, dtype=int)
    for i in range(n):
        w, v = weights[i], values[i]
        if w > capacity:
            continue
        for c in range(capacity, w - 1, -1):
            new_val = dp[c - w] + v
            if new_val > dp[c]:
                dp[c] = new_val
    return dp[capacity]


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，150 个物品（用较小容量保证 DP 可解）
    train_data = []
    train_solutions = []
    for i in range(64):
        weights, values, capacity = generate_knapsack_instance(150, max_weight=150, max_value=80)
        best_value = dp_knapsack(weights, values, capacity)
        train_data.append((weights, values, capacity))
        train_solutions.append(best_value)
        if (i + 1) % 8 == 0:
            print(f"Knapsack 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_knapsack.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_knapsack.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("Knapsack 训练集保存完成")

    # 测试集：多规模
    test_configs = [50, 100, 150]
    for size in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            weights, values, capacity = generate_knapsack_instance(size, max_weight=150, max_value=80)
            best_value = dp_knapsack(weights, values, capacity)
            test_data.append((weights, values, capacity))
            test_solutions.append(best_value)
            print(f"Knapsack{size} 测试实例 {i+1}/10 生成完成")

        with open(os.path.join(datasets_dir, f"test_data_{size}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{size}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"Knapsack{size} 测试集保存完成")

    print("Knapsack 所有数据集生成完成！")
