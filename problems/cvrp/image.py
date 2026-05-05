# -*- coding: utf-8 -*-
# CVRP 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_cvrp_solution(coordinates, routes, demands, filename='cvrp_solution.png'):
    """绘制 CVRP 路线图"""
    depot = coordinates[0]
    plt.figure(figsize=(10, 8))

    # 绘制仓库
    plt.scatter(depot[0], depot[1], c='red', s=200, marker='s', label='Depot', zorder=5)

    colors = plt.cm.tab20(np.linspace(0, 1, len(routes)))
    for idx, route in enumerate(routes):
        if len(route) <= 2:
            continue
        route_coords = [coordinates[i] for i in route]
        x = [c[0] for c in route_coords]
        y = [c[1] for c in route_coords]
        plt.plot(x, y, '-o', color=colors[idx], linewidth=2, markersize=5,
                 label=f'Route {idx + 1}', alpha=0.8)

    # 标记客户需求
    for i in range(1, len(coordinates)):
        plt.annotate(f'{demands[i]}', coordinates[i], fontsize=7,
                     xytext=(3, 3), textcoords='offset points')

    plt.title('CVRP Solution')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()


if __name__ == "__main__":
    # 读取测试数据
    test_data_path = 'datasets/test_data_50.pkl'
    test_solution_path = 'datasets/test_solution_50.pkl'

    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    coordinates, distance_matrix, demands, capacity = test_data[0]
    routes, total_dist = test_solutions[0]

    print(f"实例信息: {len(coordinates) - 1} 个客户, 容量 {capacity}")
    print(f"路线数: {len(routes)}")
    print(f"总距离: {total_dist:.2f}")
    for i, route in enumerate(routes):
        print(f"路线 {i + 1}: {route}")

    plot_cvrp_solution(coordinates, routes, demands)
