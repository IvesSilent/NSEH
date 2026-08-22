# -*- coding: utf-8 -*-
# Bin Packing 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_binpacking_solution(item_sizes, bin_assignments, bin_capacity=100, filename='binpacking_solution.png'):
    """绘制装箱方案（每个箱子内物品大小堆叠条形图）"""
    n_bins = len(bin_assignments)
    plt.figure(figsize=(12, 6))

    for bin_idx, sizes in enumerate(bin_assignments):
        bottom = 0
        for s in sizes:
            plt.bar(bin_idx, s, bottom=bottom, width=0.6, color=plt.cm.viridis(s / bin_capacity), edgecolor='black', linewidth=0.5)
            bottom += s
        plt.text(bin_idx, bin_capacity + 2, f'{bottom:.0f}', ha='center', fontsize=9)

    plt.axhline(y=bin_capacity, color='red', linestyle='--', linewidth=1, label='Bin Capacity')
    plt.xlabel('Bin Index')
    plt.ylabel('Used Capacity')
    plt.title('Bin Packing Solution')
    plt.xticks(range(n_bins))
    plt.ylim(0, bin_capacity * 1.15)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50x100.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50x100.pkl", "rb") as f:
        solutions = pickle.load(f)

    item_sizes, bin_capacity = data[0]
    # 简单 First-Fit 重建分配（仅用于可视化演示）
    remaining = []
    bins = []
    for s in item_sizes:
        placed = False
        for i, cap in enumerate(remaining):
            if cap >= s:
                remaining[i] -= s
                bins[i].append(s)
                placed = True
                break
        if not placed:
            remaining.append(bin_capacity - s)
            bins.append([s])

    plot_binpacking_solution(item_sizes, bins, bin_capacity)
    print("binpacking_solution.png 已生成")
