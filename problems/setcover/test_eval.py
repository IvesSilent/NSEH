# -*- coding: utf-8 -*-
# test_eval.py - Set Cover 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_set


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 Set Cover 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_costs = []
    test_times = []

    for instance_idx, (set_membership, set_costs) in enumerate(test_data):
        std_cost, _ = test_solutions[instance_idx]
        n_elements = set_membership.shape[1]

        start_time = time.time()
        uncovered = np.ones(n_elements, dtype=bool)
        total_cost = 0.0
        guard = 0
        while uncovered.any() and guard < n_elements * 2:
            guard += 1
            s = select_next_set(uncovered, set_membership, set_costs)
            s = int(s) if s is not None else -1
            if s < 0:
                break
            total_cost += set_costs[s]
            for e in np.nonzero(set_membership[s])[0]:
                uncovered[e] = False
        elapsed_time = time.time() - start_time

        heuristic_costs.append(total_cost if not uncovered.any() else float('inf'))
        test_times.append(elapsed_time)

    standard_costs = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(100, 50), (200, 100), (300, 150)]
        for n_elements, n_sets in test_sizes:
            test_data_path = f'datasets/test_data_{n_elements}x{n_sets}.pkl'
            test_solution_path = f'datasets/test_solution_{n_elements}x{n_sets}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"SetCover{n_elements}x{n_sets}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"SetCover{n_elements}x{n_sets}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
