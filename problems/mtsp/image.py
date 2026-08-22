# -*- coding: utf-8 -*-
# mTSP 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_mtsp_solution(coordinates, routes, filename='mtsp_solution.png'):
    """绘制多旅行商路线图"""
    plt.figure(figsize=(10, 8))
    colors = plt.cm.tab20(np.linspace(0, 1, len(routes)))
    for idx, route in enumerate(routes):
        pts = [coordinates[i] for i in route]
        x = [p[0] for p in pts]
        y = [p[1] for p in pts]
        plt.plot(x, y, '-o', color=colors[idx], linewidth=1.8, markersize=4,
                 label=f'Salesman {idx + 1}', alpha=0.85)
    plt.scatter(*coordinates[0], c='red', s=220, marker='s', label='Depot', zorder=5)
    plt.title('mTSP Solution')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50x3.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50x3.pkl", "rb") as f:
        solutions = pickle.load(f)

    coordinates, D, m = data[0]
    total, routes = solutions[0]
    plot_mtsp_solution(coordinates, routes)
    print(f"mtsp_solution.png 已生成 (total={total:.1f})")
