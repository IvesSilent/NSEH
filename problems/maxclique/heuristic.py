# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_vertex(current_clique, candidate_vertices, adjacency_matrix):
    """
    示例启发式：度数优先贪心
    从候选节点中选择与当前团全相邻、且度数最高的节点加入。
    """
    best_vertex = None
    best_degree = -1
    for v in candidate_vertices:
        v = int(v)
        deg = int(adjacency_matrix[v].sum())
        if deg > best_degree:
            best_degree = deg
            best_vertex = v
    return best_vertex
