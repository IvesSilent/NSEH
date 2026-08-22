# -*- coding: utf-8 -*-
# train_eval.py - mTSP 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_node"):
    """
    动态评估 mTSP 启发式算法的训练适应度
    返回启发式解与标准解的平均总距离差距
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

    heuristic_distances = []

    for instance_idx, (coordinates, distance_matrix, num_salesmen) in enumerate(train_data):
        std_total, _ = train_solutions[instance_idx]
        n = distance_matrix.shape[0]

        unvisited = np.ones(n, dtype=bool)
        unvisited[0] = False
        total = 0.0
        valid = True

        for s in range(num_salesmen):
            current = 0
            while unvisited.any():
                nxt = heuristic_function(
                    current, np.nonzero(unvisited)[0], distance_matrix, num_salesmen - s
                )
                if nxt is None:
                    break
                nxt = int(nxt)
                if nxt == -1:
                    break
                if not unvisited[nxt]:
                    valid = False
                    break
                total += distance_matrix[current, nxt]
                current = nxt
                unvisited[nxt] = False
            total += distance_matrix[current, 0]
            if not valid:
                break
            if not unvisited.any():
                break

        if unvisited.any():
            valid = False

        heuristic_distances.append(total if valid else float('inf'))

    standard_totals = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_distances) - np.array(standard_totals)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_mtsp.pkl"
    train_solution_path = "datasets/train_solution_mtsp.pkl"

    heuristic_code = """import numpy as np

def select_next_node(current_node, unvisited_nodes, distance_matrix, remaining_salesmen):
    if len(unvisited_nodes) == 0:
        return -1
    distances = [distance_matrix[current_node][i] for i in unvisited_nodes]
    return int(unvisited_nodes[np.argmin(distances)])
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_node")
    print(f"mTSP 训练集评估 objective = {objective}")
