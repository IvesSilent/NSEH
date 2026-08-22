# -*- coding: utf-8 -*-
# test_eval.py - Bin Packing 测试评估模块

import pickle
import numpy as np
import time
from heuristic import place_item


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 Bin Packing 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_bin_counts = []
    test_times = []

    for instance_idx, (item_sizes, bin_capacity) in enumerate(test_data):
        std_n_bins, _ = test_solutions[instance_idx]

        start_time = time.time()
        remaining = []
        for size in item_sizes:
            bin_idx = place_item(size, np.array(remaining), item_sizes, len(item_sizes))
            bin_idx = int(bin_idx) if bin_idx is not None else -1
            if 0 <= bin_idx < len(remaining) and remaining[bin_idx] >= size:
                remaining[bin_idx] -= size
            else:
                remaining.append(bin_capacity - size)
        elapsed_time = time.time() - start_time

        heuristic_bin_counts.append(len(remaining))
        test_times.append(elapsed_time)

    standard_bin_counts = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_bin_counts) - np.array(standard_bin_counts)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_configs = [(50, 100), (100, 150), (200, 200)]
        for n_items, cap in test_configs:
            test_data_path = f'datasets/test_data_{n_items}x{cap}.pkl'
            test_solution_path = f'datasets/test_solution_{n_items}x{cap}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"BinPacking{n_items}x{cap}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"BinPacking{n_items}x{cap}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
