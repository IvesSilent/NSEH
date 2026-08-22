# -*- coding: utf-8 -*-
# test_eval.py - SMTWT 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_job


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 SMTWT 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_costs = []
    test_times = []

    for instance_idx, (p, d, w) in enumerate(test_data):
        std_cost, _ = test_solutions[instance_idx]
        n = len(p)

        start_time = time.time()
        remaining = list(range(n))
        t = 0.0
        total = 0.0
        while remaining:
            j = select_next_job(np.array(remaining), t, p, d, w)
            j = int(j) if j is not None else remaining[0]
            t += p[j]
            total += w[j] * max(0, t - d[j])
            remaining.remove(j)
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
        test_sizes = [50, 100, 200]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"SMTWT{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"SMTWT{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
