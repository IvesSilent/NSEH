# -*- coding: utf-8 -*-
# train_eval.py - Set Cover 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_set"):
    """
    动态评估 Set Cover 启发式算法的训练适应度
    返回启发式解与贪心标准解的平均成本差距
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

    for instance_idx, (set_membership, set_costs) in enumerate(train_data):
        std_cost, _ = train_solutions[instance_idx]
        n_elements = set_membership.shape[1]
        n_sets = set_membership.shape[0]

        uncovered = np.ones(n_elements, dtype=bool)
        total_cost = 0.0
        guard = 0
        valid = True
        while uncovered.any() and guard < n_elements * 2:
            guard += 1
            s = heuristic_function(uncovered, set_membership, set_costs)
            if s is None:
                valid = False
                break
            s = int(s)
            if not (0 <= s < n_sets):
                valid = False
                break
            total_cost += set_costs[s]
            for e in np.nonzero(set_membership[s])[0]:
                uncovered[e] = False

        if not valid or uncovered.any():
            heuristic_costs.append(float('inf'))
        else:
            heuristic_costs.append(total_cost)

    standard_costs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_setcover.pkl"
    train_solution_path = "datasets/train_solution_setcover.pkl"

    heuristic_code = """import numpy as np

def select_next_set(uncovered_elements, set_membership, set_costs):
    n_sets = set_membership.shape[0]
    best_set = None
    best_ratio = -float('inf')
    for s in range(n_sets):
        covered = 0
        for e in np.nonzero(set_membership[s])[0]:
            if uncovered_elements[e]:
                covered += 1
        if covered > 0:
            ratio = covered / (set_costs[s] + 1e-10)
            if ratio > best_ratio:
                best_ratio = ratio
                best_set = s
    return best_set
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_set")
    print(f"SetCover 训练集评估 objective = {objective}")
