# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_job(unscheduled_jobs, current_time, processing_times, due_dates, weights):
    """
    示例启发式：WSPT（加权最短处理时间优先，按 p/w 升序）
    优先选择单位权重处理时间最小的作业。
    """
    best_job = None
    best_ratio = float('inf')
    for j in unscheduled_jobs:
        j = int(j)
        ratio = processing_times[j] / (weights[j] + 1e-10)
        if ratio < best_ratio:
            best_ratio = ratio
            best_job = j
    return best_job
