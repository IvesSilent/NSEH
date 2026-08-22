# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def choose_color(node_id, adjacency_matrix, current_colors, num_colors_used):
    """
    示例启发式：贪心（Greedy）
    选择当前节点可用的最小颜色编号；若已有颜色都冲突，返回 num_colors_used（开新颜色）。
    """
    neighbors = np.nonzero(adjacency_matrix[node_id] > 0)[0]
    forbidden = set(current_colors[n] for n in neighbors if current_colors[n] >= 0)
    for c in range(int(num_colors_used) + 1):
        if c not in forbidden:
            return c
    return int(num_colors_used)
