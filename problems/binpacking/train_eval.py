# -*- coding: utf-8 -*-
# train_eval.py - Bin Packing 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="place_item"):
    """
    动态评估 Bin Packing 启发式算法的训练适应度
    返回启发式解与 BFD 标准解的平均箱子数差距
    """
    with open(train_data_path, 'rb') as f:
        train_data = pickle.load(f)
    with open(train_solution_path, 'rb') as f:
        train_solutions = pickle.load(f)

    # 动态加载启发式函数
    module_name = "temp_module"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    temp_module = importlib.util.module_from_spec(spec)
    exec(heuristic_algorithm, temp_module.__dict__)
    heuristic_function = getattr(temp_module, fun_name)

    heuristic_bin_counts = []

    for instance_idx, (item_sizes, bin_capacity) in enumerate(train_data):
        std_n_bins, _ = train_solutions[instance_idx]

        # 构建型启发式：按给定顺序逐个放置物品
        remaining = []  # 已开箱子的剩余容量
        for size in item_sizes:
            bin_idx = heuristic_function(size, np.array(remaining), item_sizes, len(item_sizes))
            if bin_idx is None:
                break
            bin_idx = int(bin_idx)
            if 0 <= bin_idx < len(remaining) and remaining[bin_idx] >= size:
                remaining[bin_idx] -= size
            else:
                # 非法/放不下 → 开新箱
                remaining.append(bin_capacity - size)

        heuristic_bin_counts.append(len(remaining))

    standard_bin_counts = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_bin_counts) - np.array(standard_bin_counts)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_binpacking.pkl"
    train_solution_path = "datasets/train_solution_binpacking.pkl"

    heuristic_code = """import numpy as np

def place_item(item_size, remaining_capacities, item_sizes, num_items):
    best_bin = -1
    best_remaining = float('inf')
    for bin_idx, cap in enumerate(remaining_capacities):
        if cap >= item_size and cap - item_size < best_remaining:
            best_remaining = cap - item_size
            best_bin = bin_idx
    return best_bin
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "place_item")
    print(f"BinPacking 训练集评估 objective = {objective}")
