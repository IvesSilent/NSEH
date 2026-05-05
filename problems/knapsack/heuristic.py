# -*- coding: utf-8 -*-
# 0/1 背包 缺省启发式：基于价值密度的贪心算法
import numpy as np

def select_item(current_index, remaining_capacity, weights, values, num_items):
    """
    0/1 背包缺省启发式：选择剩余物品中价值密度最大的物品
    返回 1 (拿) 或 0 (不拿)
    """
    # 如果当前物品装不下，直接跳过
    if weights[current_index] > remaining_capacity:
        return 0

    # 计算剩余物品中价值密度最大的
    remaining_indices = list(range(current_index, num_items))
    remaining_weights = np.array([weights[i] for i in remaining_indices if weights[i] <= remaining_capacity])
    remaining_values = np.array([values[i] for i in remaining_indices if weights[i] <= remaining_capacity])

    if len(remaining_weights) == 0:
        return 0

    # 价值密度最大优先
    densities = remaining_values / (remaining_weights + 1e-10)
    best_idx_in_remaining = np.argmax(densities)
    best_original_idx = [i for i in remaining_indices if weights[i] <= remaining_capacity][best_idx_in_remaining]

    if best_original_idx == current_index:
        return 1
    else:
        # 如果当前物品的价值密度≥平均密度，拿；否则不拿
        avg_density = np.mean(densities)
        current_density = values[current_index] / (weights[current_index] + 1e-10)
        return 1 if current_density >= avg_density * 0.8 else 0
