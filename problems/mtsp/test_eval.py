# -*- coding: utf-8 -*-
# test_eval.py - mTSP 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_node


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 mTSP 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_distances = []
    test_times = []

    for instance_idx, (coordinates, distance_matrix, num_salesmen) in enumerate(test_data):
        std_total, _ = test_solutions[instance_idx]
        n = distance_matrix.shape[0]

        start_time = time.time()
        unvisited = np.ones(n, dtype=bool)
        unvisited[0] = False
        total = 0.0
        for s in range(num_salesmen):
            current = 0
            while unvisited.any():
                nxt = select_next_node(current, np.nonzero(unvisited)[0], distance_matrix, num_salesmen - s)
                nxt = int(nxt) if nxt is not None else -1
                if nxt == -1:
                    break
                if not unvisited[nxt]:
                    break
                total += distance_matrix[current, nxt]
                current = nxt
                unvisited[nxt] = False
            total += distance_matrix[current, 0]
            if not unvisited.any():
                break
        elapsed_time = time.time() - start_time

        heuristic_distances.append(total if not unvisited.any() else float('inf'))
        test_times.append(elapsed_time)

    standard_totals = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_distances) - np.array(standard_totals)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(50, 3), (100, 4), (200, 5)]
        for n_nodes, m in test_sizes:
            test_data_path = f'datasets/test_data_{n_nodes}x{m}.pkl'
            test_solution_path = f'datasets/test_solution_{n_nodes}x{m}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"mTSP{n_nodes}x{m}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"mTSP{n_nodes}x{m}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
