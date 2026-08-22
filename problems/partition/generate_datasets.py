# -*- coding: utf-8 -*-
# Partition（数划分问题）数据集生成器
# 标准解：贪心 + 随机化 + 两两交换局部搜索
# 每个实例保存为 (numbers,)
# 目标：把数字分成两组使两组和之差最小

import os
import pickle
import numpy as np


def generate_partition_instance(n_numbers, seed=None):
    """
    生成数划分实例（数字 10..200）
    返回: numbers: (n_numbers,) float 数组
    """
    rng = np.random.default_rng(seed)
    numbers = rng.integers(10, 201, size=n_numbers).astype(float)
    return numbers


def partition_diff(numbers, assignment):
    """计算两组和的差（绝对值）"""
    sum_a = numbers[assignment == 0].sum()
    sum_b = numbers[assignment == 1].sum()
    return abs(sum_a - sum_b)


def partition_greedy(numbers, order=None, rng=None):
    """贪心：按给定顺序，每个数字给当前和较小的组"""
    n = len(numbers)
    if order is None:
        order = list(np.argsort(-numbers))
    assignment = np.zeros(n, dtype=int)
    sum_a = 0.0
    sum_b = 0.0
    for i in order:
        if sum_a <= sum_b:
            assignment[i] = 0
            sum_a += numbers[i]
        else:
            assignment[i] = 1
            sum_b += numbers[i]
    return assignment, abs(sum_a - sum_b)


def partition_local_search(numbers, assignment):
    """
    局部搜索：
    (1) 单元素移动（从一个组移到另一组）
    (2) 两两交换（跨组交换两个元素）
    直至无法改进。
    """
    n = len(numbers)
    sum_a = numbers[assignment == 0].sum()
    sum_b = numbers[assignment == 1].sum()
    improved = True
    while improved:
        improved = False
        cur_diff = abs(sum_a - sum_b)
        # 单元素移动
        for i in range(n):
            if assignment[i] == 0:
                new_diff = abs((sum_a - numbers[i]) - (sum_b + numbers[i]))
            else:
                new_diff = abs((sum_a + numbers[i]) - (sum_b - numbers[i]))
            if new_diff < cur_diff:
                assignment[i] = 1 - assignment[i]
                if assignment[i] == 0:
                    sum_a += numbers[i]
                    sum_b -= numbers[i]
                else:
                    sum_a -= numbers[i]
                    sum_b += numbers[i]
                improved = True
                cur_diff = new_diff
                break
        if improved:
            continue
        # 两两交换
        group_a = list(np.nonzero(assignment == 0)[0])
        group_b = list(np.nonzero(assignment == 1)[0])
        best_gain = 0
        best_pair = None
        for i in group_a:
            for j in group_b:
                # 交换 i(A) 和 j(B)：diff 变化 = 2*(a_i - b_j)（符号处理）
                gain = abs(sum_a - sum_b) - abs((sum_a - numbers[i] + numbers[j]) - (sum_b - numbers[j] + numbers[i]))
                if gain > best_gain + 1e-9:
                    best_gain = gain
                    best_pair = (i, j)
        if best_pair is not None:
            i, j = best_pair
            assignment[i] = 1
            assignment[j] = 0
            sum_a = sum_a - numbers[i] + numbers[j]
            sum_b = sum_b - numbers[j] + numbers[i]
            improved = True
    return assignment, abs(sum_a - sum_b)


def partition_standard_solve(numbers, rng=None, restarts=30):
    """标准解：贪心（降序）+ 随机化次序 + 局部搜索取最优"""
    best = float('inf')
    best_assignment = None
    assignment, diff = partition_greedy(numbers)
    assignment, diff = partition_local_search(numbers, assignment)
    best = diff
    best_assignment = assignment.copy()
    n = len(numbers)
    for _ in range(restarts):
        order = list(range(n))
        if rng is not None:
            rng.shuffle(order)
        assignment, diff = partition_greedy(numbers, order)
        assignment, diff = partition_local_search(numbers, assignment)
        if diff < best:
            best = diff
            best_assignment = assignment.copy()
    return best, best_assignment


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，100 个数字
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_partition_instance(100, seed=100 + i)
        diff, assignment = partition_standard_solve(inst, rng_master)
        train_data.append(inst)
        train_solutions.append((diff, assignment))
        if (i + 1) % 16 == 0:
            print(f"Partition 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_partition.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_partition.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("Partition 训练集保存完成")

    # 测试集：多规模
    test_configs = [50, 100, 200]
    for n_numbers in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_partition_instance(n_numbers, seed=1000 + i)
            diff, assignment = partition_standard_solve(inst, rng_master)
            test_data.append(inst)
            test_solutions.append((diff, assignment))

        with open(os.path.join(datasets_dir, f"test_data_{n_numbers}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_numbers}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"Partition{n_numbers} 测试集保存完成")

    print("Partition 所有数据集生成完成！")
