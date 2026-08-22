# -*- coding: utf-8 -*-
# test_eval.py - QAP 测试评估模块

import pickle
import numpy as np
import time
from heuristic import assign_facility


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 QAP 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_costs = []
    test_times = []

    for instance_idx, (flow_matrix, distance_matrix) in enumerate(test_data):
        std_cost, _ = test_solutions[instance_idx]
        n = flow_matrix.shape[0]

        start_time = time.time()
        order = list(np.argsort(-flow_matrix.sum(axis=1)))
        assignment = np.full(n, -1, dtype=int)
        available = list(range(n))
        for f in order:
            pos = assign_facility(int(f), np.array(available), flow_matrix, distance_matrix, assignment)
            pos = int(pos) if pos is not None else available[0]
            assignment[f] = pos
            available.remove(pos)
        total = 0.0
        for i in range(n):
            for j in range(n):
                total += flow_matrix[i, j] * distance_matrix[assignment[i], assignment[j]]
        elapsed_time = time.time() - start_time

        heuristic_costs.append(total)
        test_times.append(elapsed_time)

    standard_costs = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [8, 12, 16]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"QAP{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"QAP{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
