# -*- coding: utf-8 -*-
# train_eval.py - Steiner Tree 训练评估模块

import pickle
import numpy as np
import heapq
import importlib.util


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


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_terminal"):
    """
    动态评估 Steiner Tree 启发式算法的训练适应度
    返回启发式解与标准解的平均总成本差距
    """
    with open(train_data_path, 'rb') as f:
        train_data = pickle.load(f)
    with open(train_solution_path, 'rb') as f:
        train_solutions = pickle.load(f)

    # 动态加载启发式函数
    module_name = "temp_module"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    temp_module = importlib.util.module_from_spec(spec)
    exec(heuristic_algorithm, temp_module.__dict__)
    heuristic_function = getattr(temp_module, fun_name)

    heuristic_costs = []

    for instance_idx, (adjacency_matrix, terminals) in enumerate(train_data):
        std_cost, _ = train_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        all_dist = np.array([_dijkstra(adjacency_matrix, s) for s in range(n)])
        tree = np.zeros(n, dtype=bool)
        root = int(terminals[0])
        tree[root] = True
        unconnected = set(int(t) for t in terminals if t != root)
        total = 0.0
        valid = True

        while unconnected:
            t = heuristic_function(tree, np.array(sorted(unconnected)), adjacency_matrix, all_dist)
            if t is None:
                valid = False
                break
            t = int(t)
            if t not in unconnected:
                valid = False
                break
            d = all_dist[tree, t].min() if tree.any() else float('inf')
            if d == float('inf'):
                valid = False
                break
            total += d
            tree[t] = True
            unconnected.remove(t)

        heuristic_costs.append(total if valid else float('inf'))

    standard_costs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_steinertree.pkl"
    train_solution_path = "datasets/train_solution_steinertree.pkl"

    heuristic_code = """import numpy as np

def select_next_terminal(current_tree, unconnected_terminals, adjacency_matrix, distances):
    best_terminal = None
    best_dist = float('inf')
    tree_nodes = np.nonzero(current_tree)[0]
    for t in unconnected_terminals:
        d = distances[tree_nodes, t].min() if len(tree_nodes) > 0 else distances[t].max()
        if d < best_dist:
            best_dist = d
            best_terminal = int(t)
    return best_terminal
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_terminal")
    print(f"SteinerTree 训练集评估 objective = {objective}")
