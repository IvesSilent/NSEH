# -*- coding: utf-8 -*-
# test_eval.py - VRPTW 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_customer


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 VRPTW 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_distances = []
    test_times = []

    for instance_idx, (coordinates, distance_matrix, demands, capacity, time_windows, service_times) in enumerate(test_data):
        std_total = test_solutions[instance_idx]
        n = distance_matrix.shape[0]

        start_time = time.time()
        unserved = np.ones(n, dtype=bool)
        unserved[0] = False
        total = 0.0
        while unserved.any():
            current = 0
            current_time = 0.0
            current_load = 0
            while True:
                remaining = unserved.copy()
                nxt = select_next_customer(
                    current, current_time, remaining, capacity,
                    current_load, distance_matrix, demands, time_windows, service_times
                )
                nxt = int(nxt) if nxt is not None else -1
                if nxt == -1:
                    break
                if not unserved[nxt]:
                    break
                node_demand = demands[nxt]
                if current_load + node_demand > capacity:
                    break
                arrival = current_time + distance_matrix[current, nxt]
                if arrival > time_windows[nxt, 1]:
                    break
                start = max(arrival, time_windows[nxt, 0])
                current_time = start + service_times[nxt]
                current_load += node_demand
                total += distance_matrix[current, nxt]
                current = nxt
                unserved[nxt] = False
            total += distance_matrix[current, 0]
        elapsed_time = time.time() - start_time

        heuristic_distances.append(total if not unserved.any() else float('inf'))
        test_times.append(elapsed_time)

    standard_totals = np.array(test_solutions, dtype=float)
    differences = np.array(heuristic_distances) - standard_totals
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
            print(f"VRPTW{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"VRPTW{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
