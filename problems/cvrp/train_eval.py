# -*- coding: utf-8 -*-
# train_eval.py - CVRP 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="find_best_route"):
    """
    动态评估 CVRP 启发式算法的训练适应度
    返回启发式解与 Clarke-Wright 标准解的平均差距
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
    for instance_idx, (coordinates, distance_matrix, demands, capacity) in enumerate(train_data):
        best_routes, best_distance = train_solutions[instance_idx]
        n_customers = len(demands) - 1

        # 构建型启发式：逐条路线构建
        unserved = np.ones(n_customers + 1, dtype=bool)
        unserved[0] = False  # depot 已服务
        total_distance = 0.0
        routes = []

        while unserved.any():
            route = [0]
            current_load = 0
            current_node = 0

            while True:
                remaining_demands = unserved.copy()
                next_node = heuristic_function(
                    current_node, remaining_demands, capacity,
                    current_load, distance_matrix, demands
                )

                if next_node == -1 or next_node is None:
                    break

                if not unserved[next_node]:
                    break

                node_demand = demands[next_node]
                if current_load + node_demand > capacity:
                    break

                route.append(next_node)
                unserved[next_node] = False
                current_load += node_demand
                current_node = next_node

            # 返回仓库
            route.append(0)
            routes.append(route)
            # 计算路线距离
            for i in range(len(route) - 1):
                total_distance += distance_matrix[route[i], route[i + 1]]

        heuristic_distances.append(total_distance)

    # 计算差距
    standard_distances = [sol[1] for sol in train_solutions]
    differences = np.array(heuristic_distances) - np.array(standard_distances)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_cvrp.pkl"
    train_solution_path = "datasets/train_solution_cvrp.pkl"

    heuristic_code = """import numpy as np

def find_best_route(current_node, remaining_demands, vehicle_capacity, current_load, distance_matrix, demand_list):
    best_node = None
    best_ratio = float('inf')
    for node in range(len(remaining_demands)):
        if remaining_demands[node] > 0:
            node_demand = demand_list[node]
            if current_load + node_demand <= vehicle_capacity:
                dist = distance_matrix[current_node, node]
                ratio = dist / (node_demand + 1e-10)
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_node = node
    if best_node is None:
        return -1
    return best_node
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "find_best_route")
    print(f"CVRP 训练集评估 objective = {objective}")
