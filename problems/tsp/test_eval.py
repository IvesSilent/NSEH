# -*coding=utf-8*-
# test_eval.py 问题情景自定义的评估模块
# 适用于训练结束后的单独评估计时

import pickle
import numpy as np
from heuristic import select_next_node
import time




def heuristic_solve_static(test_data_path,test_solution_path):
    """
        使用 heuristic.py 里的静态启发式方法求解TSP问题，用于评估

        参数:
            test_data_path (str): 测试数据路径
            test_solution_path (str): 测试数据标准解路径

        返回:
            objective (float): 启发式解和Concorde解的平均差距
            elapsed_time (float): 启发式算法的运行时间（秒）
    """
    # 读取数据和标准解
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        concorde_solutions = [solution[1] for solution in pickle.load(f)]

    # 使用启发式方法求解测试数据
    heuristic_solutions = []
    test_times = []

    for coordinates, distance_matrix in test_data:

        # 使用 heuristic.py 中的方法求解
        num_nodes = len(coordinates)
        unvisited_nodes = np.arange(num_nodes)
        current_node = 0
        tour_length = 0

        start_time = time.time()  # 开始计时

        while len(unvisited_nodes) > 1:
            next_node = select_next_node(current_node, None, unvisited_nodes, distance_matrix)
            tour_length += distance_matrix[current_node, next_node]
            unvisited_nodes = np.delete(unvisited_nodes, np.where(unvisited_nodes == next_node))
            current_node = next_node

        # 添加返回起点的距离
        tour_length += distance_matrix[current_node, 0]
        elapsed_time = time.time() - start_time  # 结束计时

        # 加入启发式解列表和时间列表
        heuristic_solutions.append(tour_length)
        test_times.append(elapsed_time)

    differences = np.array(heuristic_solutions) - np.array(concorde_solutions)
    test_objective = np.mean(differences)

    # # 计算相对差距百分比（启发式解与标准解的差距占标准解的百分比）
    # relative_differences = (np.array(heuristic_solutions) - np.array(concorde_solutions)) / np.array(concorde_solutions)
    # test_objective = np.mean(relative_differences) * 100  # 转换为百分比形式

    # 计算测试数据的平均差距
    # test_objective = calculate_objective(test_heuristic_solutions, test_concorde_solutions)
    test_time = np.mean(test_times)

    return test_objective, test_time




if __name__ == "__main__":

    with open("result.txt", "w") as result_file:

        # 处理测试数据
        test_sizes = [10, 20, 50, 100, 200]
        for size in test_sizes:
            test_data_path = f'datasets/test_data_{size}.pkl'
            test_solution_path = f'datasets/test_solution_{size}.pkl'
            test_objective,test_time = heuristic_solve_static(test_data_path,test_solution_path)

            print(
                    f"在TSP{size}的测试数据集上，启发式解和 Concorde 解的平均差距为：{test_objective}，耗时{test_time}s")

            # print(
            #     f"在TSP{size}的测试数据集上，启发式解和 Concorde 解的相对差距百分比为：{test_objective}（%），耗时{test_time}s")



            result_file.write(f"TSP{size}: Objective = {test_objective}, time = {test_time}s\n")