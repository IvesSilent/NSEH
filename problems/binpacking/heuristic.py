# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def place_item(item_size, remaining_capacities, item_sizes, num_items):
    """
    示例启发式：Best-Fit（最适合）策略
    将当前物品放入剩余容量最小的箱子；若所有已开箱子都放不下，返回 -1 表示开新箱。
    """
    best_bin = -1
    best_remaining = float('inf')
    for bin_idx, cap in enumerate(remaining_capacities):
        if cap >= item_size and cap - item_size < best_remaining:
            best_remaining = cap - item_size
            best_bin = bin_idx
    return best_bin
