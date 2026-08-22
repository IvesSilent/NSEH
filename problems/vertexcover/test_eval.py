# -*- coding: utf-8 -*-
# test_eval.py - Minimum Vertex Cover 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_vertex


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估顶点覆盖缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_sizes = []
    test_times = []

    for instance_idx, adjacency_matrix in enumerate(test_data):
        std_size, _ = test_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        start_time = time.time()
        uncovered = adjacency_matrix.copy().astype(bool)
        cover = np.zeros(n, dtype=bool)
        guard = 0
        while uncovered.any() and guard < n * 2:
            guard += 1
            v = select_next_vertex(uncovered, adjacency_matrix, cover)
            v = int(v) if v is not None else -1
            if v < 0 or cover[v]:
                break
            cover[v] = True
            uncovered[v, :] = False
            uncovered[:, v] = False
        elapsed_time = time.time() - start_time

        heuristic_sizes.append(int(cover.sum()) if not uncovered.any() else float('inf'))
        test_times.append(elapsed_time)

    standard_sizes = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_sizes) - np.array(standard_sizes)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [40, 80, 120]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"VertexCover{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"VertexCover{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
