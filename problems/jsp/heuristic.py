# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def select_next_job(available_operations, job_progress, operation_times, machine_ready_times, machine_of_op):
    """
    示例启发式：SPT（最短加工时间优先）
    选择下一工序加工时间最短的可开工作业。
    """
    best_job = None
    best_time = float('inf')
    for job in available_operations:
        k = int(job_progress[job])
        t = operation_times[job, k]
        if t < best_time:
            best_time = t
            best_job = job
    return best_job
