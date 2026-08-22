# -*- coding: utf-8 -*-
# train_eval.py - JSP 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="select_next_job"):
    """
    动态评估 JSP 启发式算法的训练适应度
    返回启发式解与 SPT 标准解的平均 makespan 差距
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

    for instance_idx, (machine_matrix, time_matrix) in enumerate(train_data):
        std_makespan = train_solutions[instance_idx]
        n_jobs, n_machines = machine_matrix.shape

        progress = np.zeros(n_jobs, dtype=int)
        job_completion = np.zeros(n_jobs, dtype=float)
        machine_ready = np.zeros(n_machines, dtype=float)

        remaining = list(range(n_jobs))
        valid = True
        while remaining:
            avail = np.array(remaining)
            job = heuristic_function(
                avail, progress, time_matrix, machine_ready, machine_matrix
            )
            if job is None:
                valid = False
                break
            job = int(job)
            if job not in remaining:
                valid = False
                break
            k = progress[job]
            m = machine_matrix[job, k]
            start = max(machine_ready[m], job_completion[job])
            finish = start + time_matrix[job, k]
            machine_ready[m] = finish
            job_completion[job] = finish
            progress[job] += 1
            if progress[job] >= n_machines:
                remaining.remove(job)

        heuristic_makespans.append(float(job_completion.max()) if valid else float('inf'))

    standard_makespans = np.array(train_solutions, dtype=float)
    differences = np.array(heuristic_makespans) - standard_makespans
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_jsp.pkl"
    train_solution_path = "datasets/train_solution_jsp.pkl"

    heuristic_code = """import numpy as np

def select_next_job(available_operations, job_progress, operation_times, machine_ready_times, machine_of_op):
    best_job = None
    best_time = float('inf')
    for job in available_operations:
        k = int(job_progress[job])
        t = operation_times[job, k]
        if t < best_time:
            best_time = t
            best_job = job
    return best_job
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "select_next_job")
    print(f"JSP 训练集评估 objective = {objective}")
