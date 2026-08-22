# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_center(selected_centers, candidate_nodes, distance_matrix, k):
    """
    示例启发式：最远点贪心（Farthest-First）
    选择距最近已选中心最远的候选节点。
    """
    best_node = None
    best_dist = -1.0
    for v in candidate_nodes:
        v = int(v)
        d = distance_matrix[selected_centers, v].min()
        if d > best_dist:
            best_dist = d
            best_node = v
    return best_node
