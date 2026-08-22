# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_customer(current_node, current_time, remaining_demands, vehicle_capacity,
                         current_load, distance_matrix, demand_list, time_windows, service_times):
    """
    示例启发式：时间窗紧迫度优先（EDD + 距离修正）
    选择能在时间窗内到达、且截止时间最早的可行客户；无可行客户则返回 -1 回仓库。
    """
    best_node = None
    best_key = float('inf')
    for j in np.nonzero(remaining_demands)[0]:
        node_demand = demand_list[j]
        if current_load + node_demand > vehicle_capacity:
            continue
        arrival = current_time + distance_matrix[current_node, j]
        ready, due = time_windows[j]
        if arrival > due:
            continue  # 超窗不可行
        # 到达越早越优先；考虑服务后最早开始时间
        start = max(arrival, ready)
        key = start + distance_matrix[current_node, j] * 0.1
        if key < best_key:
            best_key = key
            best_node = int(j)
    return best_node if best_node is not None else -1
