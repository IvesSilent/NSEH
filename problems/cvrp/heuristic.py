# -*- coding: utf-8 -*-
# CVRP 缺省启发式：基于容量约束的最近邻算法
import numpy as np

def find_best_route(current_node, remaining_demands, vehicle_capacity, current_load, distance_matrix, demand_list):
    """
    CVRP 缺省启发式：选择最近的、容量允许的客户节点
    """
    best_node = None
    best_distance = float('inf')

    for node in range(len(remaining_demands)):
        if remaining_demands[node] > 0:  # 还有需求
            node_demand = demand_list[node]
            if current_load + node_demand <= vehicle_capacity:  # 容量允许
                dist = distance_matrix[current_node, node]
                # 用距离和需求密度的组合进行选择
                ratio = dist / (node_demand + 1e-10)
                if ratio < best_distance:
                    best_distance = ratio
                    best_node = node

    # 如果所有节点都不满足容量约束，返回 -1 表示需要返回仓库
    if best_node is None:
        return -1

    return best_node
