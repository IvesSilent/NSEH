# -*- coding: utf-8 -*-
# train_eval.py - 0/1 背包 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_item"):
    """
    动态评估 0/1 背包启发式算法的训练适应度
    返回启发式解与 DP 最优解的平均差距（取差值）
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

    heuristic_values = []

    for instance_idx, (weights, values, capacity) in enumerate(train_data):
        optimal_value = train_solutions[instance_idx]
        num_items = len(weights)

        # 构建型启发式：逐个物品决策
        remaining_capacity = capacity
        total_value = 0.0

        for i in range(num_items):
            decision = heuristic_function(i, remaining_capacity, weights, values, num_items)
            if decision == 1 and weights[i] <= remaining_capacity:
                total_value += values[i]
                remaining_capacity -= weights[i]

        heuristic_values.append(total_value)

    # 计算差距（最优解 - 启发式解，正值越小越好）
    differences = np.array(train_solutions) - np.array(heuristic_values)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_knapsack.pkl"
    train_solution_path = "datasets/train_solution_knapsack.pkl"

    heuristic_code = """import numpy as np

def select_item(current_index, remaining_capacity, weights, values, num_items):
    if weights[current_index] > remaining_capacity:
        return 0
    remaining_indices = list(range(current_index, num_items))
    filt_weights = [weights[i] for i in remaining_indices if weights[i] <= remaining_capacity]
    if not filt_weights:
        return 0
    filt_values = [values[i] for i in remaining_indices if weights[i] <= remaining_capacity]
    densities = [filt_values[j] / (filt_weights[j] + 1e-10) for j in range(len(filt_weights))]
    best_idx = np.argmax(densities)
    best_original = [i for i in remaining_indices if weights[i] <= remaining_capacity][best_idx]
    if best_original == current_index:
        return 1
    current_density = values[current_index] / (weights[current_index] + 1e-10)
    avg_density = np.mean(densities)
    return 1 if current_density >= avg_density * 0.8 else 0
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_item")
    print(f"Knapsack 训练集评估 objective = {objective}")
