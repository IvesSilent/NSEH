# -*- coding: utf-8 -*-
# test_eval.py - CVRP 测试评估模块

import pickle
import numpy as np
import time
from heuristic import find_best_route


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 CVRP 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_distances = []
    test_times = []

    for instance_idx, (coordinates, distance_matrix, demands, capacity) in enumerate(test_data):
        best_routes, best_distance = test_solutions[instance_idx]
        n_customers = len(demands) - 1

        unserved = np.ones(n_customers + 1, dtype=bool)
        unserved[0] = False
        total_distance = 0.0

        start_time = time.time()

        while unserved.any():
            route = [0]
            current_load = 0
            current_node = 0

            while True:
                remaining_demands = unserved.copy()
                next_node = find_best_route(
                    current_node, remaining_demands, capacity,
                    current_load, distance_matrix, demands
                )

                if next_node == -1 or next_node is None:
                    break
                if not unserved[next_node]:
                    break

                node_demand = demands[next_node]
                if current_load + node_demand > capacity:
                    break

                route.append(next_node)
                unserved[next_node] = False
                current_load += node_demand
                current_node = next_node

            route.append(0)
            for i in range(len(route) - 1):
                total_distance += distance_matrix[route[i], route[i + 1]]

        elapsed_time = time.time() - start_time
        heuristic_distances.append(total_distance)
        test_times.append(elapsed_time)

    standard_distances = [sol[1] for sol in test_solutions]
    differences = np.array(heuristic_distances) - np.array(standard_distances)
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
            print(f"CVRP{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"CVRP{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
