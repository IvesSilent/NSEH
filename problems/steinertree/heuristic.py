# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_terminal(current_tree, unconnected_terminals, adjacency_matrix, distances):
    """
    示例启发式：最近终端贪心（类似 Prim 扩展）
    选择距离当前树最近的未连接终端。
    """
    best_terminal = None
    best_dist = float('inf')
    tree_nodes = np.nonzero(current_tree)[0]
    for t in unconnected_terminals:
        # 树到终端的最短距离（取树中节点到终端的最小距离）
        d = distances[tree_nodes, t].min() if len(tree_nodes) > 0 else distances[t].max()
        if d < best_dist:
            best_dist = d
            best_terminal = int(t)
    return best_terminal
