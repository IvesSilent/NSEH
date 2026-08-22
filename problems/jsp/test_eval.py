# -*- coding: utf-8 -*-
# test_eval.py - JSP 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_job


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 JSP 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_makespans = []
    test_times = []

    for instance_idx, (machine_matrix, time_matrix) in enumerate(test_data):
        std_makespan = test_solutions[instance_idx]
        n_jobs, n_machines = machine_matrix.shape

        start_time = time.time()
        progress = np.zeros(n_jobs, dtype=int)
        job_completion = np.zeros(n_jobs, dtype=float)
        machine_ready = np.zeros(n_machines, dtype=float)

        remaining = list(range(n_jobs))
        while remaining:
            avail = np.array(remaining)
            job = select_next_job(avail, progress, time_matrix, machine_ready, machine_matrix)
            job = int(job) if job is not None else remaining[0]
            k = progress[job]
            m = machine_matrix[job, k]
            start = max(machine_ready[m], job_completion[job])
            finish = start + time_matrix[job, k]
            machine_ready[m] = finish
            job_completion[job] = finish
            progress[job] += 1
            if progress[job] >= n_machines:
                remaining.remove(job)
        elapsed_time = time.time() - start_time

        heuristic_makespans.append(float(job_completion.max()))
        test_times.append(elapsed_time)

    standard_makespans = np.array(test_solutions, dtype=float)
    differences = np.array(heuristic_makespans) - standard_makespans
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(10, 5), (20, 10), (30, 15)]
        for n_jobs, n_machines in test_sizes:
            test_data_path = f'datasets/test_data_{n_jobs}x{n_machines}.pkl'
            test_solution_path = f'datasets/test_solution_{n_jobs}x{n_machines}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"JSP{n_jobs}x{n_machines}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"JSP{n_jobs}x{n_machines}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
