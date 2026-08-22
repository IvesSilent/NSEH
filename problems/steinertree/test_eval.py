# -*- coding: utf-8 -*-
# test_eval.py - Steiner Tree 测试评估模块

import pickle
import numpy as np
import heapq
import time
from heuristic import select_next_terminal


def _dijkstra(adjacency_matrix, source):
    n = adjacency_matrix.shape[0]
    dist = np.full(n, float('inf'))
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in range(n):
            w = adjacency_matrix[u, v]
            if w > 0 and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 Steiner Tree 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_costs = []
    test_times = []

    for instance_idx, (adjacency_matrix, terminals) in enumerate(test_data):
        std_cost, _ = test_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        start_time = time.time()
        all_dist = np.array([_dijkstra(adjacency_matrix, s) for s in range(n)])
        tree = np.zeros(n, dtype=bool)
        root = int(terminals[0])
        tree[root] = True
        unconnected = set(int(t) for t in terminals if t != root)
        total = 0.0
        while unconnected:
            t = select_next_terminal(tree, np.array(sorted(unconnected)), adjacency_matrix, all_dist)
            t = int(t) if t is not None else -1
            if t < 0 or t not in unconnected:
                break
            d = all_dist[tree, t].min() if tree.any() else float('inf')
            if d == float('inf'):
                break
            total += d
            tree[t] = True
            unconnected.remove(t)
        elapsed_time = time.time() - start_time

        heuristic_costs.append(total if not unconnected else float('inf'))
        test_times.append(elapsed_time)

    standard_costs = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(50, 8), (100, 15), (200, 20)]
        for n_nodes, n_terms in test_sizes:
            test_data_path = f'datasets/test_data_{n_nodes}x{n_terms}.pkl'
            test_solution_path = f'datasets/test_solution_{n_nodes}x{n_terms}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"SteinerTree{n_nodes}x{n_terms}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"SteinerTree{n_nodes}x{n_terms}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
