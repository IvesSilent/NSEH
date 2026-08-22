# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def assign_job(job_id, machine_loads, processing_times, num_machines):
    """
    示例启发式：最小负载优先（List Scheduling）
    将作业分配给当前负载最小的机器。
    """
    return int(np.argmin(machine_loads))
