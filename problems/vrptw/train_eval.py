# -*- coding: utf-8 -*-
# train_eval.py - VRPTW 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_customer"):
    """
    动态评估 VRPTW 启发式算法的训练适应度
    返回启发式解与标准解的平均总距离差距（不可行解计 inf）
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

    for instance_idx, (coordinates, distance_matrix, demands, capacity, time_windows, service_times) in enumerate(train_data):
        std_total = train_solutions[instance_idx]
        n = distance_matrix.shape[0]

        unserved = np.ones(n, dtype=bool)
        unserved[0] = False
        total = 0.0
        valid = True

        while unserved.any() and valid:
            current = 0
            current_time = 0.0
            current_load = 0
            while True:
                remaining = unserved.copy()
                nxt = heuristic_function(
                    current, current_time, remaining, capacity,
                    current_load, distance_matrix, demands, time_windows, service_times
                )
                if nxt is None:
                    break
                nxt = int(nxt)
                if nxt == -1:
                    break
                if not unserved[nxt]:
                    valid = False
                    break
                node_demand = demands[nxt]
                if current_load + node_demand > capacity:
                    valid = False
                    break
                arrival = current_time + distance_matrix[current, nxt]
                ready, due = time_windows[nxt]
                if arrival > due:
                    valid = False
                    break
                start = max(arrival, ready)
                current_time = start + service_times[nxt]
                current_load += node_demand
                total += distance_matrix[current, nxt]
                current = nxt
                unserved[nxt] = False
            total += distance_matrix[current, 0]

        if unserved.any():
            valid = False

        heuristic_distances.append(total if valid else float('inf'))

    standard_totals = np.array(train_solutions, dtype=float)
    differences = np.array(heuristic_distances) - standard_totals
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_vrptw.pkl"
    train_solution_path = "datasets/train_solution_vrptw.pkl"

    heuristic_code = """import numpy as np

def select_next_customer(current_node, current_time, remaining_demands, vehicle_capacity,
                         current_load, distance_matrix, demand_list, time_windows, service_times):
    best_node = None
    best_key = float('inf')
    for j in np.nonzero(remaining_demands)[0]:
        node_demand = demand_list[j]
        if current_load + node_demand > vehicle_capacity:
            continue
        arrival = current_time + distance_matrix[current_node, j]
        ready, due = time_windows[j]
        if arrival > due:
            continue
        start = max(arrival, ready)
        key = start + distance_matrix[current_node, j] * 0.1
        if key < best_key:
            best_key = key
            best_node = int(j)
    return best_node if best_node is not None else -1
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_customer")
    print(f"VRPTW 训练集评估 objective = {objective}")
