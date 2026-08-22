# -*- coding: utf-8 -*-
# test_eval.py - Graph Coloring 测试评估模块

import pickle
import numpy as np
import time
from heuristic import choose_color


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估图着色缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_color_counts = []
    test_times = []

    for instance_idx, adjacency_matrix in enumerate(test_data):
        std_n_colors, _ = test_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        start_time = time.time()
        colors = np.full(n, -1, dtype=int)
        max_color = -1
        for node in range(n):
            c = choose_color(node, adjacency_matrix, colors, max_color + 1)
            c = int(c) if c is not None else max_color + 1
            neighbors = np.nonzero(adjacency_matrix[node] > 0)[0]
            conflict = any(colors[nb] == c for nb in neighbors if colors[nb] >= 0)
            if conflict:
                c = max_color + 1
            colors[node] = c
            if c > max_color:
                max_color = c
        elapsed_time = time.time() - start_time

        heuristic_color_counts.append(max_color + 1)
        test_times.append(elapsed_time)

    standard_color_counts = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_color_counts) - np.array(standard_color_counts)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [30, 60, 100]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"GraphColoring{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"GraphColoring{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
