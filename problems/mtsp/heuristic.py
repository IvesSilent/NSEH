# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_node(current_node, unvisited_nodes, distance_matrix, remaining_salesmen):
    """
    示例启发式：最近邻（Nearest Neighbor）
    选择距当前节点最近的未访问节点；若无合适节点则返回 -1 结束当前旅行商路线。
    """
    if len(unvisited_nodes) == 0:
        return -1
    distances = [distance_matrix[current_node][i] for i in unvisited_nodes]
    return int(unvisited_nodes[np.argmin(distances)])
