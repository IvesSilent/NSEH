# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def assign_facility(facility_id, available_positions, flow_matrix, distance_matrix, current_assignment):
    """
    示例启发式：最小增量贪心
    选择使当前总成本增量最小的位置。
    """
    best_pos = None
    best_cost = float('inf')
    for pos in available_positions:
        pos = int(pos)
        cost = 0.0
        for other, assigned_pos in enumerate(current_assignment):
            if assigned_pos >= 0:
                cost += flow_matrix[facility_id, other] * distance_matrix[pos, assigned_pos]
                cost += flow_matrix[other, facility_id] * distance_matrix[assigned_pos, pos]
        if cost < best_cost:
            best_cost = cost
            best_pos = pos
    return best_pos
