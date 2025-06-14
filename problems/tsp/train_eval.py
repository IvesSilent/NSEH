# -*coding=utf-8*-
# train_eval.py 问题情景自定义的评估模块
# 适用于优化训练过程中的适应度计算

import pickle
import numpy as np
import importlib.util

def heuristic_solve_dynamic(train_data_path,train_solution_path,heuristic_algorithm,fun_name = "select_next_node"):
    """
        使用动态启发式方法求解TSP问题，用于优化训练

        参数:
            train_data_path (str): 训练数据路径
            train_solution_path (str): 训练数据标准解路径
            heuristic_algorithm (str): 需要评估的启发式

        返回:
            objective (float): 启发式解和Concorde解的平均差距
    """

    # 读取数据和标准解
    # 此处动态加载数据的原因（重要）：
    #   对于每个问题情景，单独实现其train_eval.py，问题不同加载的数据及其类型也不同
    #   这里只是将文件名传入，在每次评估时单独读取数据
    with open(train_data_path, 'rb') as f:
        train_data = pickle.load(f)
    with open(train_solution_path, 'rb') as f:
        train_solution = [solution[1] for solution in pickle.load(f)]

    # 加载动态的启发式函
    # 创建一个临时模块
    module_name = "temp_module"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    temp_module = importlib.util.module_from_spec(spec)

    # 将代码字符串执行到临时模块中
    exec(heuristic_algorithm, temp_module.__dict__)

    # 动态加载函数
    heuristic_function = getattr(temp_module, fun_name)
    # 将启发式内的函数加载为 heuristic_function


    heuristic_solutions = []

    for coordinates, distance_matrix in train_data:

        # 使用 heuristic_algorithm 的方法求解
        num_nodes = len(coordinates)
        unvisited_nodes = np.arange(num_nodes)
        current_node = 0
        tour_length = 0

        while len(unvisited_nodes) > 1:
            next_node = heuristic_function(current_node, None, unvisited_nodes, distance_matrix)
            tour_length += distance_matrix[current_node, next_node]
            unvisited_nodes = np.delete(unvisited_nodes, np.where(unvisited_nodes == next_node))
            current_node = next_node

        # 添加返回起点的距离
        tour_length += distance_matrix[current_node, 0]
        # 加入启发式解序列
        heuristic_solutions.append(tour_length)

    differences = np.array(heuristic_solutions) - np.array(train_solution)
    objective = np.mean(differences)

    # 返回计算所得的 objective 值
    return objective


if __name__ == "__main__":

    train_data_path = "datasets/train_data_tsp.pkl"
    train_solution_path = "datasets/train_data_solution.pkl"
    fun_name = "select_next_node"
    heuristic_algorithm_str = "import numpy as np\n\ndef select_next_node(current_node, destination_node, unvisited_nodes, distance_matrix):\n    min_distance = float('inf')\n    next_node = None\n    \n    for node in unvisited_nodes:\n        if distance_matrix[current_node, node] < min_distance:\n            min_distance = distance_matrix[current_node, node]\n            next_node = node\n    \n    return next_node"


    objective = heuristic_solve_dynamic(train_data_path,train_solution_path,heuristic_algorithm_str,fun_name)
    print(f"objective = {objective}")