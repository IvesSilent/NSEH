# -*- coding: utf-8 -*-
# train_eval.py - Graph Coloring 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="choose_color"):
    """
    动态评估图着色启发式算法的训练适应度
    返回启发式解与 DSATUR 标准解的平均颜色数差距
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

    heuristic_color_counts = []

    for instance_idx, adjacency_matrix in enumerate(train_data):
        std_n_colors, _ = train_solutions[instance_idx]
        n = adjacency_matrix.shape[0]

        # 按节点 ID 顺序逐个着色（构建型）
        colors = np.full(n, -1, dtype=int)
        max_color = -1
        for node in range(n):
            c = heuristic_function(node, adjacency_matrix, colors, max_color + 1)
            if c is None:
                break
            c = int(c)
            # 校验：不允许与已着色邻居冲突
            neighbors = np.nonzero(adjacency_matrix[node] > 0)[0]
            conflict = any(colors[nb] == c for nb in neighbors if colors[nb] >= 0)
            if conflict:
                # 冲突则强制使用新颜色
                c = max_color + 1
            colors[node] = c
            if c > max_color:
                max_color = c

        heuristic_color_counts.append(max_color + 1)

    standard_color_counts = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_color_counts) - np.array(standard_color_counts)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_graphcoloring.pkl"
    train_solution_path = "datasets/train_solution_graphcoloring.pkl"

    heuristic_code = """import numpy as np

def choose_color(node_id, adjacency_matrix, current_colors, num_colors_used):
    neighbors = np.nonzero(adjacency_matrix[node_id] > 0)[0]
    forbidden = set(current_colors[n] for n in neighbors if current_colors[n] >= 0)
    for c in range(int(num_colors_used) + 1):
        if c not in forbidden:
            return c
    return int(num_colors_used)
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "choose_color")
    print(f"GraphColoring 训练集评估 objective = {objective}")
