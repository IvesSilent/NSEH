# -*- coding: utf-8 -*-
# train_eval.py - Orienteering 训练评估模块
# 注意：目标为最大化利润，返回 -(利润差距) 保持 ascend=True 框架兼容

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_node"):
    """
    动态评估 Orienteering 启发式算法的训练适应度
    返回标准解利润 - 启发式利润 的平均值（越小越好）
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

    profit_gaps = []

    for instance_idx, (coordinates, distance_matrix, profits, budget) in enumerate(train_data):
        std_profit, _ = train_solutions[instance_idx]
        n = distance_matrix.shape[0]

        visited = np.zeros(n, dtype=bool)
        visited[0] = True
        current = 0
        budget_left = budget
        total_profit = 0.0
        valid = True

        while True:
            nxt = heuristic_function(
                current, visited, profits, distance_matrix, budget_left, total_profit
            )
            if nxt is None:
                break
            nxt = int(nxt)
            if nxt == -1:
                break
            if visited[nxt]:
                valid = False
                break
            dist = distance_matrix[current, nxt]
            if dist + distance_matrix[nxt, 0] > budget_left + 1e-9:
                valid = False
                break
            budget_left -= dist
            total_profit += profits[nxt]
            visited[nxt] = True
            current = nxt

        if valid:
            profit_gaps.append(std_profit - total_profit)
        else:
            profit_gaps.append(float('inf'))

    return np.mean(profit_gaps)


if __name__ == "__main__":
    train_data_path = "datasets/train_data_orienteering.pkl"
    train_solution_path = "datasets/train_solution_orienteering.pkl"

    heuristic_code = """import numpy as np

def select_next_node(current_node, visited, remaining_profits, distance_matrix, budget_left, total_profit):
    best_node = None
    best_ratio = -float('inf')
    for j in np.nonzero(~visited)[0]:
        if j == 0:
            continue
        dist = distance_matrix[current_node, j]
        return_dist = distance_matrix[j, 0]
        if dist + return_dist > budget_left + 1e-9:
            continue
        ratio = remaining_profits[j] / (dist + 1e-10)
        if ratio > best_ratio:
            best_ratio = ratio
            best_node = int(j)
    return best_node if best_node is not None else -1
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_node")
    print(f"Orienteering 训练集评估 objective = {objective}")
