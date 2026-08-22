# -*- coding: utf-8 -*-
# Orienteering 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_orienteering_solution(coordinates, route, profits, filename='orienteering_solution.png'):
    """绘制定向越野路线（节点大小=利润）"""
    plt.figure(figsize=(10, 8))
    x = coordinates[1:, 0]
    y = coordinates[1:, 1]
    sizes = 20 + profits[1:] * 1.5
    plt.scatter(x, y, s=sizes, c='lightblue', edgecolors='blue', alpha=0.7, zorder=2)

    if len(route) > 1:
        pts = [coordinates[i] for i in route]
        rx = [p[0] for p in pts]
        ry = [p[1] for p in pts]
        plt.plot(rx, ry, '-o', color='red', linewidth=2, markersize=5, zorder=3)

    plt.scatter(*coordinates[0], c='red', s=250, marker='s', label='Start/End', zorder=5)
    plt.title(f'Orienteering Solution (profit: {sum(profits[i] for i in route):.0f}, nodes: {len(route)-1})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50.pkl", "rb") as f:
        solutions = pickle.load(f)

    coordinates, D, profits, budget = data[0]
    profit, route = solutions[0]
    plot_orienteering_solution(coordinates, route, profits)
    print(f"orienteering_solution.png 已生成 (profit={profit:.0f})")
