# -*- coding: utf-8 -*-
# test_eval.py - Orienteering 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_node


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 Orienteering 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    profit_gaps = []
    test_times = []

    for instance_idx, (coordinates, distance_matrix, profits, budget) in enumerate(test_data):
        std_profit, _ = test_solutions[instance_idx]
        n = distance_matrix.shape[0]

        start_time = time.time()
        visited = np.zeros(n, dtype=bool)
        visited[0] = True
        current = 0
        budget_left = budget
        total_profit = 0.0
        while True:
            nxt = select_next_node(current, visited, profits, distance_matrix, budget_left, total_profit)
            nxt = int(nxt) if nxt is not None else -1
            if nxt == -1:
                break
            if visited[nxt]:
                break
            dist = distance_matrix[current, nxt]
            if dist + distance_matrix[nxt, 0] > budget_left + 1e-9:
                break
            budget_left -= dist
            total_profit += profits[nxt]
            visited[nxt] = True
            current = nxt
        elapsed_time = time.time() - start_time

        profit_gaps.append(std_profit - total_profit)
        test_times.append(elapsed_time)

    test_objective = np.mean(profit_gaps)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [50, 100, 200]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"Orienteering{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"Orienteering{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
