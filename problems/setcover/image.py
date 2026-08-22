# -*- coding: utf-8 -*-
# Set Cover 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_setcover_solution(set_membership, set_costs, selected, filename='setcover_solution.png'):
    """绘制集合覆盖方案（矩阵热力图：行为集合，列为元素）"""
    plt.figure(figsize=(12, 6))
    selected_mask = np.zeros(set_membership.shape[0], dtype=bool)
    selected_mask[list(selected)] = True

    # 按选择状态着色
    display = set_membership.astype(float)
    display[selected_mask] += 1.0  # 已选集合 = 2，未选 = 0/1

    plt.imshow(display, aspect='auto', cmap='coolwarm', interpolation='nearest')
    plt.colorbar(label='0/1 = unselected, 2 = selected')
    plt.xlabel('Element Index')
    plt.ylabel('Set Index')
    plt.title(f'Set Cover Solution (selected: {len(selected)} sets, cost: {sum(set_costs[s] for s in selected):.0f})')
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_100x50.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_100x50.pkl", "rb") as f:
        solutions = pickle.load(f)

    membership, costs = data[0]
    cost, selected = solutions[0]
    plot_setcover_solution(membership, costs, selected)
    print("setcover_solution.png 已生成")
