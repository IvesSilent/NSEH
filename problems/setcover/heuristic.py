# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_set(uncovered_elements, set_membership, set_costs):
    """
    示例启发式：贪心（Greedy）
    选择单位成本覆盖最多未覆盖元素的集合。
    """
    n_sets = set_membership.shape[0]
    best_set = None
    best_ratio = -float('inf')
    for s in range(n_sets):
        covered = 0
        for e in np.nonzero(set_membership[s])[0]:
            if uncovered_elements[e]:
                covered += 1
        if covered > 0:
            ratio = covered / (set_costs[s] + 1e-10)
            if ratio > best_ratio:
                best_ratio = ratio
                best_set = s
    return best_set
