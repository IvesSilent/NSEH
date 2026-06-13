# -*- coding: utf-8 -*-
# CVRP 数据集生成器

import os
import pickle
import numpy as np

def generate_cvrp_instance(n_customers, capacity=100, space=(0, 100)):
    """
    生成一个 CVRP 实例
    返回: (coordinates, distance_matrix, demands, capacity)
    - 索引 0 为仓库 (depot)
    - 索引 1..n_customers 为客户节点
    """
    # 仓库在中心
    depot = np.array([[50.0, 50.0]])
    # 随机生成客户坐标
    customers = np.random.uniform(space[0], space[1], size=(n_customers, 2))
    coordinates = np.vstack([depot, customers])

    # 计算距离矩阵
    diff = coordinates[:, np.newaxis, :] - coordinates[np.newaxis, :, :]
    distance_matrix = np.sqrt(np.sum(diff ** 2, axis=2))

    # 随机生成客户需求 (1-30 单位)
    demands = np.random.randint(1, 31, size=n_customers)
    # 确保所有需求都不超过容量
    demands = np.minimum(demands, capacity // 2)
    # 前面补 0（仓库需求为 0）
    full_demands = np.concatenate([[0], demands])

    return coordinates, distance_matrix, full_demands, capacity


def clarke_wright_solve(distance_matrix, demands, capacity):
    """
    使用 Clarke-Wright 节约算法求解 CVRP
    返回路由列表和总距离
    """
    n = len(demands)
    if n <= 1:
        return [0, 0], 0.0

    # 初始解：每个客户单独一条路线 depot -> customer -> depot
    routes = [[0, i, 0] for i in range(1, n)]

    # 计算节约值
    savings = []
    for i in range(1, n):
        for j in range(i + 1, n):
            saving = distance_matrix[0, i] + distance_matrix[0, j] - distance_matrix[i, j]
            savings.append((saving, i, j))

    # 按节约值降序排序
    savings.sort(key=lambda x: x[0], reverse=True)

    # 合并路线
    for saving, i, j in savings:
        # 找到包含 i 的路线和包含 j 的路线
        route_i = None
        route_j = None
        for r in routes:
            if i in r:
                route_i = r
            if j in r:
                route_j = r

        if route_i is None or route_j is None or route_i is route_j:
            continue

        # 检查 i 在终点（末尾倒数第二个），j 在起点（正数第二个）
        if route_i[-2] == i and route_j[1] == j:
            # 计算合并后的总需求
            demand_i = sum(demands[node] for node in route_i if node != 0)
            demand_j = sum(demands[node] for node in route_j if node != 0)
            if demand_i + demand_j <= capacity:
                # 合并：route_i ... -> i -> j -> ... route_j
                new_route = route_i[:-1] + route_j[1:]
                routes.remove(route_i)
                routes.remove(route_j)
                routes.append(new_route)

    # 计算总距离
    total_distance = 0.0
    for route in routes:
        for idx in range(len(route) - 1):
            total_distance += distance_matrix[route[idx], route[idx + 1]]

    return routes, total_distance


if __name__ == "__main__":
    # 创建目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # --- 训练集：64 个实例，100 个客户节点 ---
    train_data = []
    train_solutions = []
    for i in range(64):
        coord, dist_mat, demands, capacity = generate_cvrp_instance(100, capacity=200)
        routes, total_dist = clarke_wright_solve(dist_mat, demands, capacity)
        train_data.append((coord, dist_mat, demands, capacity))
        train_solutions.append((routes, total_dist))
        if (i + 1) % 16 == 0:
            print(f"CVRP 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_cvrp.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_cvrp.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("CVRP 训练集保存完成")

    # --- 测试集 ---
    test_sizes = [50, 100, 200]
    for size in test_sizes:
        test_data = []
        test_solutions = []
        for i in range(10):
            coord, dist_mat, demands, capacity = generate_cvrp_instance(size, capacity=300 if size > 100 else 200)
            routes, total_dist = clarke_wright_solve(dist_mat, demands, capacity)
            test_data.append((coord, dist_mat, demands, capacity))
            test_solutions.append((routes, total_dist))
            print(f"CVRP{size} 测试实例 {i+1}/10 生成完成")

        with open(os.path.join(datasets_dir, f"test_data_{size}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{size}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"CVRP{size} 测试集保存完成")

    print("CVRP 所有数据集生成完成！")
