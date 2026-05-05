# -*- coding: utf-8 -*-
# test_eval.py - MaxCut 测试评估模块

import pickle
import numpy as np
import time
from heuristic import assign_node


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 MaxCut 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_cuts = []
    test_times = []

    for instance_idx, adjacency_matrix in enumerate(test_data):
        best_partition_list, best_cut = test_solutions[instance_idx]
        best_partition = np.array(best_partition_list)
        n_nodes = len(adjacency_matrix)

        start_time = time.time()

        # 构建型启发式
        partition = np.full(n_nodes, -1, dtype=int)
        first_node = np.random.randint(0, n_nodes)
        partition[first_node] = np.random.randint(0, 2)

        degrees = np.sum(adjacency_matrix > 0, axis=1)
        order = np.argsort(-degrees)

        for node in order:
            if partition[node] != -1:
                continue
            unassigned = (partition == -1)
            side = assign_node(node, unassigned, adjacency_matrix, partition)
            partition[node] = side

        cut_value = 0.0
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if adjacency_matrix[i, j] > 0 and partition[i] != partition[j]:
                    cut_value += adjacency_matrix[i, j]

        elapsed_time = time.time() - start_time
        heuristic_cuts.append(cut_value)
        test_times.append(elapsed_time)

    standard_cuts = [sol[1] for sol in test_solutions]
    differences = np.array(standard_cuts) - np.array(heuristic_cuts)
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
            print(f"MaxCut{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"MaxCut{size}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
