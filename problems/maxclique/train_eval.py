# -*- coding: utf-8 -*-
# train_eval.py - Maximum Clique 训练评估模块
# 目标为最大化团大小 → objective = 标准解大小 - 启发式大小（越小越好）

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_vertex"):
    """
    动态评估最大团启发式算法的训练适应度
    返回标准解团大小 - 启发式团大小 的平均值
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

    size_gaps = []

    for instance_idx, adjacency_matrix in enumerate(train_data):
        std_size, _ = train_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        clique = set()
        candidates = np.ones(n, dtype=bool)
        valid = True

        while candidates.any():
            v = heuristic_function(np.array(sorted(clique)) if clique else np.array([]),
                                   np.nonzero(candidates)[0], adjacency_matrix)
            if v is None:
                break
            v = int(v)
            if not candidates[v]:
                valid = False
                break
            # 校验与当前团全相邻
            if not all(adjacency_matrix[v, u] for u in clique):
                valid = False
                break
            clique.add(v)
            # 更新候选：与 clique 全相邻
            for u in range(n):
                if candidates[u] and not all(adjacency_matrix[u, c] for c in clique):
                    candidates[u] = False

        if valid:
            size_gaps.append(std_size - len(clique))
        else:
            size_gaps.append(float('inf'))

    return np.mean(size_gaps)


if __name__ == "__main__":
    train_data_path = "datasets/train_data_maxclique.pkl"
    train_solution_path = "datasets/train_solution_maxclique.pkl"

    heuristic_code = """import numpy as np

def select_next_vertex(current_clique, candidate_vertices, adjacency_matrix):
    best_vertex = None
    best_degree = -1
    for v in candidate_vertices:
        v = int(v)
        deg = int(adjacency_matrix[v].sum())
        if deg > best_degree:
            best_degree = deg
            best_vertex = v
    return best_vertex
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_vertex")
    print(f"MaxClique 训练集评估 objective = {objective}")
