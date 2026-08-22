# -*- coding: utf-8 -*-
# Bin Packing（一维装箱）数据集生成器
# 标准解：Best-Fit Decreasing (BFD) 近似
# 每个实例保存为 (item_sizes, bin_capacity)

import os
import pickle
import numpy as np


def generate_binpacking_instance(n_items, bin_capacity=100):
    """
    生成一维装箱实例
    返回: (item_sizes, bin_capacity)
    item_sizes: (n_items,) 物品大小数组（10..capacity/2 随机，避免平凡情形）
    """
    item_sizes = np.random.randint(10, bin_capacity // 2 + 1, size=n_items)
    return item_sizes, bin_capacity


def bfd_solve(item_sizes, bin_capacity):
    """
    Best-Fit Decreasing 近似求解
    返回: (总箱子数, 每个箱子的剩余容量列表)
    """
    sizes = sorted(item_sizes, reverse=True)
    remaining = []  # 已开箱子的剩余容量
    for size in sizes:
        best_idx = -1
        best_left = float('inf')
        for i, cap in enumerate(remaining):
            if cap >= size and cap - size < best_left:
                best_left = cap - size
                best_idx = i
        if best_idx == -1:
            remaining.append(bin_capacity - size)
        else:
            remaining[best_idx] -= size
    return len(remaining), remaining


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    np.random.seed(42)

    # 训练集：64 个实例，100 物品，容量 100（构建型启发式）
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_binpacking_instance(100, 100)
        item_sizes, cap = inst
        n_bins, remaining = bfd_solve(item_sizes, cap)
        train_data.append(inst)
        train_solutions.append((n_bins, remaining))
        if (i + 1) % 16 == 0:
            print(f"BinPacking 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_binpacking.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_binpacking.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("BinPacking 训练集保存完成")

    # 测试集：多规模
    test_configs = [(50, 100), (100, 150), (200, 200)]
    for n_items, cap in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_binpacking_instance(n_items, cap)
            item_sizes, cap_i = inst
            n_bins, remaining = bfd_solve(item_sizes, cap_i)
            test_data.append(inst)
            test_solutions.append((n_bins, remaining))

        with open(os.path.join(datasets_dir, f"test_data_{n_items}x{cap}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_items}x{cap}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"BinPacking{n_items}x{cap} 测试集保存完成")

    print("BinPacking 所有数据集生成完成！")
