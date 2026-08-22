# -*- coding: utf-8 -*-
# train_eval.py - SMTWT 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_job"):
    """
    动态评估 SMTWT 启发式算法的训练适应度
    返回启发式解与标准解的平均 ΣwT 差距
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

    for instance_idx, (p, d, w) in enumerate(train_data):
        std_cost, _ = train_solutions[instance_idx]
        n = len(p)

        remaining = list(range(n))
        t = 0.0
        total = 0.0
        valid = True
        while remaining:
            j = heuristic_function(np.array(remaining), t, p, d, w)
            if j is None:
                valid = False
                break
            j = int(j)
            if j not in remaining:
                valid = False
                break
            t += p[j]
            total += w[j] * max(0, t - d[j])
            remaining.remove(j)

        heuristic_costs.append(total if valid else float('inf'))

    standard_costs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_costs) - np.array(standard_costs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_smtwt.pkl"
    train_solution_path = "datasets/train_solution_smtwt.pkl"

    heuristic_code = """import numpy as np

def select_next_job(unscheduled_jobs, current_time, processing_times, due_dates, weights):
    best_job = None
    best_ratio = float('inf')
    for j in unscheduled_jobs:
        j = int(j)
        ratio = processing_times[j] / (weights[j] + 1e-10)
        if ratio < best_ratio:
            best_ratio = ratio
            best_job = j
    return best_job
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_job")
    print(f"SMTWT 训练集评估 objective = {objective}")
