# -*- coding: utf-8 -*-
# train_eval.py - Minimum Vertex Cover 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_vertex"):
    """
    动态评估顶点覆盖启发式算法的训练适应度
    返回启发式解与标准解的平均覆盖大小差距
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

    heuristic_sizes = []

    for instance_idx, adjacency_matrix in enumerate(train_data):
        std_size, _ = train_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        uncovered = adjacency_matrix.copy().astype(bool)
        cover = np.zeros(n, dtype=bool)
        valid = True
        guard = 0
        while uncovered.any() and guard < n * 2:
            guard += 1
            v = heuristic_function(uncovered, adjacency_matrix, cover)
            if v is None:
                valid = False
                break
            v = int(v)
            if not (0 <= v < n) or cover[v]:
                valid = False
                break
            cover[v] = True
            uncovered[v, :] = False
            uncovered[:, v] = False

        if not valid or uncovered.any():
            heuristic_sizes.append(float('inf'))
        else:
            heuristic_sizes.append(int(cover.sum()))

    standard_sizes = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_sizes) - np.array(standard_sizes)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_vertexcover.pkl"
    train_solution_path = "datasets/train_solution_vertexcover.pkl"

    heuristic_code = """import numpy as np

def select_next_vertex(uncovered_edges, adjacency_matrix, current_cover):
    n = adjacency_matrix.shape[0]
    best_vertex = None
    best_count = -1
    for v in range(n):
        if current_cover[v]:
            continue
        cnt = 0
        for u in np.nonzero(adjacency_matrix[v])[0]:
            if uncovered_edges[v, u]:
                cnt += 1
        if cnt > best_count:
            best_count = cnt
            best_vertex = v
    return best_vertex
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_vertex")
    print(f"VertexCover 训练集评估 objective = {objective}")
