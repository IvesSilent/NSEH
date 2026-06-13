# -*- coding: utf-8 -*-
# PFSP 缺省启发式：基于总加工时间的贪心算法
import numpy as np

def select_next_job(unscheduled_jobs, current_schedule, processing_times, num_machines):
    """
    PFSP 缺省启发式：选择能使完工时间增加最小的作业
    """
    if len(unscheduled_jobs) == 0:
        return None

    if len(current_schedule) == 0:
        # 第一个作业：选择总加工时间最小的
        total_times = np.sum(processing_times[unscheduled_jobs], axis=1)
        return unscheduled_jobs[np.argmin(total_times)]

    best_job = None
    best_makespan = float('inf')

    for job in unscheduled_jobs:
        # 模拟将 job 插入到当前调度末尾
        test_schedule = list(current_schedule) + [job]
        n_jobs = len(test_schedule)
        completion = np.zeros((n_jobs, num_machines))
        for i in range(n_jobs):
            for m in range(num_machines):
                prev_job = completion[i - 1, m] if i > 0 else 0
                prev_machine = completion[i, m - 1] if m > 0 else 0
                completion[i, m] = max(prev_job, prev_machine) + processing_times[test_schedule[i], m]
        makespan = completion[-1, -1]

        if makespan < best_makespan:
            best_makespan = makespan
            best_job = job

    return best_job
