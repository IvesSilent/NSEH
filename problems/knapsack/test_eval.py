# -*- coding: utf-8 -*-
# test_eval.py - 0/1 背包 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_item


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 0/1 背包缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_values_list = []
    test_times = []

    for instance_idx, (weights, values, capacity) in enumerate(test_data):
        optimal_value = test_solutions[instance_idx]
        num_items = len(weights)
        total_value = 0.0
        remaining_capacity = capacity

        start_time = time.time()
        for i in range(num_items):
            decision = select_item(i, remaining_capacity, weights, values, num_items)
            if decision == 1 and weights[i] <= remaining_capacity:
                total_value += values[i]
                remaining_capacity -= weights[i]
        elapsed_time = time.time() - start_time

        heuristic_values_list.append(total_value)
        test_times.append(elapsed_time)

    # 计算差距（最优 - 启发式）
    differences = np.array(test_solutions) - np.array(heuristic_values_list)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [50, 100, 150]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"Knapsack{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"Knapsack{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
