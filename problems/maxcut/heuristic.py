# -*- coding: utf-8 -*-
# MaxCut 缺省启发式：贪心分配（每次选择使切割值增量最大的侧）
import numpy as np

def assign_node(node_id, unassigned_nodes, adjacency_matrix, current_partition):
    """
    MaxCut 缺省启发式：选择使切割值最大化的分配侧
    返回 0 或 1（分配到哪一侧）
    """
    # 计算分配到侧 0 的切割收益
    gain_0 = 0
    gain_1 = 0

    for other_node in range(len(current_partition)):
        if adjacency_matrix[node_id, other_node] > 0:
            if current_partition[other_node] != -1:  # 已分配
                if current_partition[other_node] == 0:
                    gain_1 += adjacency_matrix[node_id, other_node]
                else:
                    gain_0 += adjacency_matrix[node_id, other_node]

    if gain_0 > gain_1:
        return 0
    elif gain_1 > gain_0:
        return 1
    else:
        # 相等时随机选择
        return 0 if np.random.random() < 0.5 else 1
