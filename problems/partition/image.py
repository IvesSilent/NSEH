# -*- coding: utf-8 -*-
# Partition 可视化（两组堆积条形图）

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_partition_solution(numbers, assignment, filename='partition_solution.png'):
    """绘制两组分配（堆积条形图）"""
    group_a = numbers[assignment == 0]
    group_b = numbers[assignment == 1]
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.bar(range(len(group_a)), np.sort(group_a)[::-1], color='steelblue')
    plt.title(f'Group A (sum={group_a.sum():.0f})')
    plt.subplot(1, 2, 2)
    plt.bar(range(len(group_b)), np.sort(group_b)[::-1], color='coral')
    plt.title(f'Group B (sum={group_b.sum():.0f})')
    plt.suptitle(f'Partition Solution (diff={abs(group_a.sum() - group_b.sum()):.0f})')
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50.pkl", "rb") as f:
        solutions = pickle.load(f)

    numbers = data[0]
    diff, assignment = solutions[0]
    plot_partition_solution(numbers, assignment)
    print(f"partition_solution.png 已生成 (diff={diff:.0f})")
