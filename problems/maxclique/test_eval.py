# -*- coding: utf-8 -*-
# test_eval.py - Maximum Clique 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_vertex


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估最大团缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    size_gaps = []
    test_times = []

    for instance_idx, adjacency_matrix in enumerate(test_data):
        std_size, _ = test_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        start_time = time.time()
        clique = set()
        candidates = np.ones(n, dtype=bool)
        while candidates.any():
            v = select_next_vertex(np.array(sorted(clique)) if clique else np.array([]),
                                   np.nonzero(candidates)[0], adjacency_matrix)
            v = int(v) if v is not None else -1
            if v < 0 or not candidates[v]:
                break
            if not all(adjacency_matrix[v, u] for u in clique):
                break
            clique.add(v)
            for u in range(n):
                if candidates[u] and not all(adjacency_matrix[u, c] for c in clique):
                    candidates[u] = False
        elapsed_time = time.time() - start_time

        size_gaps.append(std_size - len(clique))
        test_times.append(elapsed_time)

    test_objective = np.mean(size_gaps)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [30, 60, 100]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"MaxClique{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"MaxClique{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
