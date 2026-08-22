# -*- coding: utf-8 -*-
# train_eval.py - k-Center 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_center"):
    """
    动态评估 k-Center 启发式算法的训练适应度
    返回启发式解与标准解的平均最大覆盖距离差距
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

    heuristic_objs = []

    for instance_idx, (coordinates, distance_matrix, k) in enumerate(train_data):
        std_obj, _ = train_solutions[instance_idx]
        n = distance_matrix.shape[0]

        # 第一个中心固定为 0
        centers = [0]
        candidate = list(range(1, n))
        valid = True
        while len(centers) < k and candidate:
            c = heuristic_function(np.array(centers), np.array(candidate), distance_matrix, k)
            if c is None:
                valid = False
                break
            c = int(c)
            if c not in candidate:
                valid = False
                break
            centers.append(c)
            candidate.remove(c)

        if valid and len(centers) == k:
            obj = float(distance_matrix[:, centers].min(axis=1).max())
            heuristic_objs.append(obj)
        else:
            heuristic_objs.append(float('inf'))

    standard_objs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_objs) - np.array(standard_objs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_kcenter.pkl"
    train_solution_path = "datasets/train_solution_kcenter.pkl"

    heuristic_code = """import numpy as np

def select_next_center(selected_centers, candidate_nodes, distance_matrix, k):
    best_node = None
    best_dist = -1.0
    for v in candidate_nodes:
        v = int(v)
        d = distance_matrix[selected_centers, v].min()
        if d > best_dist:
            best_dist = d
            best_node = v
    return best_node
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_center")
    print(f"kCenter 训练集评估 objective = {objective}")
