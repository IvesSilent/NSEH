# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_vertex(uncovered_edges, adjacency_matrix, current_cover):
    """
    示例启发式：贪心（Greedy）
    选择覆盖最多未覆盖边的节点（度数优先）。
    """
    n = adjacency_matrix.shape[0]
    best_vertex = None
    best_count = -1
    for v in range(n):
        if current_cover[v]:
            continue
        cnt = 0
        for u in np.nonzero(adjacency_matrix[v])[0]:
            if uncovered_edges[v, u]:
                cnt += 1
        if cnt > best_count:
            best_count = cnt
            best_vertex = v
    return best_vertex
