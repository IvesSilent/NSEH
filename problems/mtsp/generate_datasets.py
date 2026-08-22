# -*- coding: utf-8 -*-
# mTSP（多旅行商问题）数据集生成器
# 标准解：多起点最近邻贪心（每个旅行商独立构建环线）
# 每个实例保存为 (coordinates, distance_matrix, num_salesmen)

import os
import pickle
import numpy as np


def generate_mtsp_instance(n_nodes, num_salesmen, seed=None):
    """
    生成 mTSP 实例（节点坐标 0~100 正方形区域，节点 0 为仓库）
    返回: (coordinates, distance_matrix, num_salesmen)
    """
    rng = np.random.default_rng(seed)
    coordinates = rng.uniform(0, 100, size=(n_nodes, 2))
    coordinates[0] = [50, 50]  # depot 居中
    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distance_matrix = np.sqrt((diff ** 2).sum(-1))
    return coordinates, distance_matrix, num_salesmen


def mtsp_nearest_neighbor(coordinates, distance_matrix, num_salesmen, rng=None, start_nodes=None):
    """
    多起点最近邻贪心构建 mTSP 解
    返回: (总距离, 各旅行商路线列表)
    """
    n = distance_matrix.shape[0]
    unvisited = set(range(1, n))
    total = 0.0
    routes = []

    for s in range(num_salesmen):
        if not unvisited:
            break
        if start_nodes is not None and start_nodes[s] in unvisited:
            current = start_nodes[s]
            unvisited.remove(current)
            route = [0, current]
            total += distance_matrix[0, current]
        else:
            current = 0
            route = [0]
        # 最近邻扩展
        while unvisited:
            best = min(unvisited, key=lambda j: distance_matrix[current, j])
            total += distance_matrix[current, best]
            current = best
            route.append(best)
            unvisited.remove(best)
        total += distance_matrix[current, 0]
        route.append(0)
        routes.append(route)

    return total, routes


def mtsp_standard_solve(coordinates, distance_matrix, num_salesmen, rng=None, restarts=30):
    """标准解：多起点随机化（不同起点组合）取最优"""
    n = distance_matrix.shape[0]
    best = float('inf')
    best_routes = []
    for trial in range(restarts):
        if rng is None:
            starts = None
        else:
            # 随机为每个旅行商指定一个起始客户（不重复）
            nodes = list(range(1, n))
            rng.shuffle(nodes)
            starts = nodes[:num_salesmen]
        total, routes = mtsp_nearest_neighbor(coordinates, distance_matrix, num_salesmen, rng, starts)
        if total < best:
            best = total
            best_routes = routes
    return best, best_routes


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    rng_master = np.random.default_rng(777)

    # 训练集：64 个实例，100 节点，3 个旅行商
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_mtsp_instance(100, 3, seed=100 + i)
        coords, D, m = inst
        total, routes = mtsp_standard_solve(coords, D, m, rng_master)
        train_data.append(inst)
        train_solutions.append((total, routes))
        if (i + 1) % 16 == 0:
            print(f"mTSP 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_mtsp.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_mtsp.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("mTSP 训练集保存完成")

    # 测试集：多规模 (节点数, 旅行商数)
    test_configs = [(50, 3), (100, 4), (200, 5)]
    for n_nodes, m in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_mtsp_instance(n_nodes, m, seed=1000 + i)
            coords, D, m_ = inst
            total, routes = mtsp_standard_solve(coords, D, m_, rng_master)
            test_data.append(inst)
            test_solutions.append((total, routes))

        with open(os.path.join(datasets_dir, f"test_data_{n_nodes}x{m}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_nodes}x{m}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"mTSP{n_nodes}x{m} 测试集保存完成")

    print("mTSP 所有数据集生成完成！")
