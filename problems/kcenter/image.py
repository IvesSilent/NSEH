# -*- coding: utf-8 -*-
# k-Center 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_kcenter_solution(coordinates, centers, distance_matrix, filename='kcenter_solution.png'):
    """绘制 k-Center 结果（红色星=中心，节点按最近中心着色）"""
    n = coordinates.shape[0]
    assign = distance_matrix[:, centers].argmin(axis=1)
    colors = plt.cm.tab20(np.linspace(0, 1, len(centers)))
    plt.figure(figsize=(10, 8))
    for c_idx in range(len(centers)):
        members = np.nonzero(assign == c_idx)[0]
        plt.scatter(coordinates[members, 0], coordinates[members, 1],
                    c=[colors[c_idx]], s=60, alpha=0.7, edgecolors='none')
    centers_arr = np.array(centers)
    plt.scatter(coordinates[centers_arr, 0], coordinates[centers_arr, 1],
                c='red', s=280, marker='*', edgecolors='black', zorder=5, label='Centers')
    plt.title(f'k-Center Solution (k={len(centers)})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50x5.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50x5.pkl", "rb") as f:
        solutions = pickle.load(f)

    coordinates, D, k = data[0]
    obj, centers = solutions[0]
    plot_kcenter_solution(coordinates, centers, D)
    print(f"kcenter_solution.png 已生成 (objective={obj:.1f})")
