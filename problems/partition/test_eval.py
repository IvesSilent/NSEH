# -*- coding: utf-8 -*-
# test_eval.py - Partition 测试评估模块

import pickle
import numpy as np
import time
from heuristic import assign_number


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估数划分缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_diffs = []
    test_times = []

    for instance_idx, numbers in enumerate(test_data):
        std_diff, _ = test_solutions[instance_idx]
        n = len(numbers)

        start_time = time.time()
        order = list(np.argsort(-numbers))
        sum_a = 0.0
        sum_b = 0.0
        for i in order:
            g = assign_number(int(i), sum_a, sum_b, numbers)
            g = int(g) if g is not None else 0
            if g == 0:
                sum_a += numbers[i]
            else:
                sum_b += numbers[i]
        elapsed_time = time.time() - start_time

        heuristic_diffs.append(abs(sum_a - sum_b))
        test_times.append(elapsed_time)

    standard_diffs = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_diffs) - np.array(standard_diffs)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [50, 100, 200]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"Partition{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"Partition{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
