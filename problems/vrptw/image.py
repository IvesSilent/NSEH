# -*- coding: utf-8 -*-
# VRPTW 可视化

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_vrptw_solution(coordinates, routes, time_windows, filename='vrptw_solution.png'):
    """绘制 VRPTW 路线图（附时间窗标注）"""
    plt.figure(figsize=(10, 8))
    colors = plt.cm.tab20(np.linspace(0, 1, len(routes)))
    for idx, route in enumerate(routes):
        if len(route) <= 2:
            continue
        pts = [coordinates[i] for i in route]
        x = [p[0] for p in pts]
        y = [p[1] for p in pts]
        plt.plot(x, y, '-o', color=colors[idx], linewidth=1.8, markersize=4,
                 label=f'Route {idx + 1}', alpha=0.85)
    plt.scatter(*coordinates[0], c='red', s=220, marker='s', label='Depot', zorder=5)
    plt.title('VRPTW Solution')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


def build_routes(coordinates, distance_matrix, demands, capacity, time_windows, service_times):
    """用缺省启发式构建路线（演示用）"""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from heuristic import select_next_customer
    n = distance_matrix.shape[0]
    unserved = np.ones(n, dtype=bool)
    unserved[0] = False
    routes = []
    while unserved.any():
        route = [0]
        current = 0
        current_time = 0.0
        current_load = 0
        while True:
            nxt = select_next_customer(current, current_time, unserved.copy(), capacity,
                                       current_load, distance_matrix, demands, time_windows, service_times)
            nxt = int(nxt) if nxt is not None else -1
            if nxt == -1:
                break
            arrival = current_time + distance_matrix[current, nxt]
            start = max(arrival, time_windows[nxt, 0])
            current_time = start + service_times[nxt]
            current_load += demands[nxt]
            current = nxt
            unserved[nxt] = False
            route.append(nxt)
        route.append(0)
        routes.append(route)
    return routes


if __name__ == "__main__":
    with open("datasets/test_data_50.pkl", "rb") as f:
        data = pickle.load(f)
    coordinates, D, demands, cap, tw, st = data[0]
    routes = build_routes(coordinates, D, demands, cap, tw, st)
    plot_vrptw_solution(coordinates, routes, tw)
    print(f"vrptw_solution.png 已生成 (routes={len(routes)})")
