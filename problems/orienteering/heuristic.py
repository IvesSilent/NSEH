# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_node(current_node, visited, remaining_profits, distance_matrix, budget_left, total_profit):
    """
    示例启发式：利润/距离比贪心
    选择利润/额外距离比最高的未访问节点（需保证能返回仓库不超预算）；否则返回 -1 结束。
    """
    best_node = None
    best_ratio = -float('inf')
    for j in np.nonzero(~visited)[0]:
        if j == 0:
            continue
        dist = distance_matrix[current_node, j]
        return_dist = distance_matrix[j, 0]
        if dist + return_dist > budget_left + 1e-9:
            continue
        ratio = remaining_profits[j] / (dist + 1e-10)
        if ratio > best_ratio:
            best_ratio = ratio
            best_node = int(j)
    return best_node if best_node is not None else -1
