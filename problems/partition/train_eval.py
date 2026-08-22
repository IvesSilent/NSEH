# -*- coding: utf-8 -*-
# train_eval.py - Partition 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="assign_number"):
    """
    动态评估数划分启发式算法的训练适应度
    返回启发式解与标准解的平均差值差距
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

    heuristic_diffs = []

    for instance_idx, numbers in enumerate(train_data):
        std_diff, _ = train_solutions[instance_idx]
        n = len(numbers)

        # 按降序逐个分配
        order = list(np.argsort(-numbers))
        sum_a = 0.0
        sum_b = 0.0
        valid = True
        for i in order:
            g = heuristic_function(int(i), sum_a, sum_b, numbers)
            if g is None:
                valid = False
                break
            g = int(g)
            if g == 0:
                sum_a += numbers[i]
            elif g == 1:
                sum_b += numbers[i]
            else:
                valid = False
                break

        heuristic_diffs.append(abs(sum_a - sum_b) if valid else float('inf'))

    standard_diffs = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_diffs) - np.array(standard_diffs)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_partition.pkl"
    train_solution_path = "datasets/train_solution_partition.pkl"

    heuristic_code = """import numpy as np

def assign_number(number_id, sum_a, sum_b, numbers):
    return 0 if sum_a <= sum_b else 1
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "assign_number")
    print(f"Partition 训练集评估 objective = {objective}")
