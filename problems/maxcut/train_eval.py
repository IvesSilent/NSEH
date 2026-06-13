# -*- coding: utf-8 -*-
# train_eval.py - MaxCut 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="assign_node"):
    """
    动态评估 MaxCut 启发式算法的训练适应度
    返回启发式解与贪心随机基线解的平均差距（负值表示更好）
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

    heuristic_cuts = []

    for instance_idx, adjacency_matrix in enumerate(train_data):
        best_partition, best_cut = train_solutions[instance_idx]
        n_nodes = len(adjacency_matrix)

        # 构建型启发式：逐个分配节点
        partition = np.full(n_nodes, -1, dtype=int)  # -1 = 未分配

        # 随机分配第一个节点
        first_node = np.random.randint(0, n_nodes)
        partition[first_node] = np.random.randint(0, 2)

        # 构建顺序（按节点的度降序）
        degrees = np.sum(adjacency_matrix > 0, axis=1)
        order = np.argsort(-degrees)

        for node in order:
            if partition[node] != -1:
                continue
            unassigned = (partition == -1)
            side = heuristic_function(node, unassigned, adjacency_matrix, partition)
            partition[node] = side

        # 计算切割值
        cut_value = 0.0
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if adjacency_matrix[i, j] > 0 and partition[i] != partition[j]:
                    cut_value += adjacency_matrix[i, j]

        heuristic_cuts.append(cut_value)

    # 计算差距（基线 - 启发式解，负值表示启发式更好）
    standard_cuts = [sol[1] for sol in train_solutions]
    differences = np.array(standard_cuts) - np.array(heuristic_cuts)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_maxcut.pkl"
    train_solution_path = "datasets/train_solution_maxcut.pkl"

    heuristic_code = """import numpy as np

def assign_node(node_id, unassigned_nodes, adjacency_matrix, current_partition):
    gain_0 = 0
    gain_1 = 0
    for other_node in range(len(current_partition)):
        if adjacency_matrix[node_id, other_node] > 0:
            if current_partition[other_node] != -1:
                if current_partition[other_node] == 0:
                    gain_1 += adjacency_matrix[node_id, other_node]
                else:
                    gain_0 += adjacency_matrix[node_id, other_node]
    if gain_0 > gain_1:
        return 0
    elif gain_1 > gain_0:
        return 1
    else:
        return 0 if np.random.random() < 0.5 else 1
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "assign_node")
    print(f"MaxCut 训练集评估 objective = {objective}")
