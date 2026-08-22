# -*- coding: utf-8 -*-
# train_eval.py - QAP 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="assign_facility"):
    """
    动态评估 QAP 启发式算法的训练适应度
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

    for instance_idx, (flow_matrix, distance_matrix) in enumerate(train_data):
        std_cost, _ = train_solutions[instance_idx]
        n = flow_matrix.shape[0]

        # 按总流量降序分配
        order = list(np.argsort(-flow_matrix.sum(axis=1)))
        assignment = np.full(n, -1, dtype=int)
        available = list(range(n))
        valid = True
        for f in order:
            pos = heuristic_function(int(f), np.array(available), flow_matrix, distance_matrix, assignment)
            if pos is None:
                valid = False
                break
            pos = int(pos)
            if pos not in available:
                valid = False
                break
            assignment[f] = pos
            available.remove(pos)

        if valid:
            total = 0.0
            for i in range(n):
                for j in range(n):
                    total += flow_matrix[i, j] * distance_matrix[assignment[i], assignment[j]]
            heuristic_costs.append(total)
        else:
            heuristic_costs.append(float('inf'))

    standard_costs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_qap.pkl"
    train_solution_path = "datasets/train_solution_qap.pkl"

    heuristic_code = """import numpy as np

def assign_facility(facility_id, available_positions, flow_matrix, distance_matrix, current_assignment):
    best_pos = None
    best_cost = float('inf')
    for pos in available_positions:
        pos = int(pos)
        cost = 0.0
        for other, assigned_pos in enumerate(current_assignment):
            if assigned_pos >= 0:
                cost += flow_matrix[facility_id, other] * distance_matrix[pos, assigned_pos]
                cost += flow_matrix[other, facility_id] * distance_matrix[assigned_pos, pos]
        if cost < best_cost:
            best_cost = cost
            best_pos = pos
    return best_pos
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "assign_facility")
    print(f"QAP 训练集评估 objective = {objective}")
