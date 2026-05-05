# -*- coding: utf-8 -*-
# train_eval.py - PFSP 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_job"):
    """
    动态评估 PFSP 启发式算法的训练适应度
    返回启发式解与 NEH 标准解的平均差距
    """
    with open(train_data_path, 'rb') as f:
        train_data = pickle.load(f)
    with open(train_solution_path, 'rb') as f:
        train_solutions = pickle.load(f)

    # 动态加载启发式函数
    module_name = "temp_module"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    temp_module = importlib.util.module_from_spec(spec)
    exec(heuristic_algorithm, temp_module.__dict__)
    heuristic_function = getattr(temp_module, fun_name)

    heuristic_makespans = []

    for instance_idx, processing_times in enumerate(train_data):
        best_seq, best_makespan = train_solutions[instance_idx]
        n_jobs, num_machines = processing_times.shape

        # 构建型启发式：逐个选择作业
        current_schedule = []
        unscheduled = list(range(n_jobs))

        while unscheduled:
            next_job = heuristic_function(np.array(unscheduled), current_schedule, processing_times, num_machines)
            if next_job is None:
                break
            current_schedule.append(next_job)
            unscheduled.remove(next_job)

        # 计算 final makespan
        if current_schedule:
            n = len(current_schedule)
            completion = np.zeros((n, num_machines))
            for i in range(n):
                for m in range(num_machines):
                    prev_job = completion[i - 1, m] if i > 0 else 0
                    prev_machine = completion[i, m - 1] if m > 0 else 0
                    completion[i, m] = max(prev_job, prev_machine) + processing_times[current_schedule[i], m]
            makespan = completion[-1, -1]
        else:
            makespan = float('inf')

        heuristic_makespans.append(makespan)

    standard_makespans = [sol[1] for sol in train_solutions]
    differences = np.array(heuristic_makespans) - np.array(standard_makespans)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_pfsp.pkl"
    train_solution_path = "datasets/train_solution_pfsp.pkl"

    heuristic_code = """import numpy as np

def select_next_job(unscheduled_jobs, current_schedule, processing_times, num_machines):
    if len(unscheduled_jobs) == 0:
        return None
    if len(current_schedule) == 0:
        total_times = np.sum(processing_times[unscheduled_jobs], axis=1)
        return unscheduled_jobs[np.argmin(total_times)]
    best_job = None
    best_makespan = float('inf')
    for job in unscheduled_jobs:
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
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_job")
    print(f"PFSP 训练集评估 objective = {objective}")
