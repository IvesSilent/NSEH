# -*- coding: utf-8 -*-
# 0/1 背包 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_knapsack_solution(weights, values, selected_indices, capacity, filename='knapsack_solution.png'):
    """绘制背包问题解的可视化"""
    n = len(weights)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 左侧：物品选择状态
    colors = ['#3fb950' if i in selected_indices else '#f85149' for i in range(n)]
    ax1.bar(range(n), values, color=colors, alpha=0.7, label='Value')
    ax1.bar(range(n), [-w for w in weights], color=colors, alpha=0.4, label='Weight (neg)')
    ax1.axhline(y=0, color='white', linewidth=0.5)
    ax1.set_xlabel('Item Index')
    ax1.set_ylabel('Value / Weight')
    ax1.set_title(f'Knapsack Selection (Capacity: {capacity})')
    ax1.legend()

    # 右侧：价值密度排序
    densities = values / (weights + 1e-10)
    sorted_idx = np.argsort(-densities)
    sorted_colors = ['#3fb950' if i in selected_indices else '#f85149' for i in sorted_idx]
    ax2.bar(range(n), densities[sorted_idx], color=sorted_colors, alpha=0.7)
    ax2.set_xlabel('Items (sorted by density)')
    ax2.set_ylabel('Value Density')
    ax2.set_title('Items Ranked by Value/Weight Ratio')
    ax2.axhline(y=np.mean(densities), color='#f0883e', linestyle='--', label='Avg Density')
    ax2.legend()

    total_value = sum(values[i] for i in selected_indices)
    total_weight = sum(weights[i] for i in selected_indices)
    fig.suptitle(f'Knapsack Solution: Value={total_value}, Weight={total_weight}/{capacity}', fontsize=14)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()


if __name__ == "__main__":
    test_data_path = 'datasets/test_data_50.pkl'
    test_solution_path = 'datasets/test_solution_50.pkl'

    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    weights, values, capacity = test_data[0]
    optimal_value = test_solutions[0]

    # 用贪心找选择方案
    num_items = len(weights)
    ratios = values / (weights + 1e-10)
    sorted_by_density = np.argsort(-ratios)
    remaining = capacity
    selected = []
    for idx in sorted_by_density:
        if weights[idx] <= remaining:
            selected.append(idx)
            remaining -= weights[idx]

    print(f"物品数: {num_items}, 容量: {capacity}")
    print(f"选择物品数: {len(selected)}")
    print(f"总价值: {sum(values[i] for i in selected)}")
    print(f"最优价值: {optimal_value}")

    plot_knapsack_solution(weights, values, selected, capacity)
