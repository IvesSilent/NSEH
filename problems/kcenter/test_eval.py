# -*- coding: utf-8 -*-
# test_eval.py - k-Center 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_center


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 k-Center 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_objs = []
    test_times = []

    for instance_idx, (coordinates, distance_matrix, k) in enumerate(test_data):
        std_obj, _ = test_solutions[instance_idx]
        n = distance_matrix.shape[0]

        start_time = time.time()
        centers = [0]
        candidate = list(range(1, n))
        while len(centers) < k and candidate:
            c = select_next_center(np.array(centers), np.array(candidate), distance_matrix, k)
            c = int(c) if c is not None else candidate[0]
            if c not in candidate:
                break
            centers.append(c)
            candidate.remove(c)
        elapsed_time = time.time() - start_time

        if len(centers) == k:
            obj = float(distance_matrix[:, centers].min(axis=1).max())
        else:
            obj = float('inf')
        heuristic_objs.append(obj)
        test_times.append(elapsed_time)

    standard_objs = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_objs) - np.array(standard_objs)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(50, 5), (100, 10), (200, 10)]
        for n_nodes, k in test_sizes:
            test_data_path = f'datasets/test_data_{n_nodes}x{k}.pkl'
            test_solution_path = f'datasets/test_solution_{n_nodes}x{k}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"kCenter{n_nodes}x{k}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"kCenter{n_nodes}x{k}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
