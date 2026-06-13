# -*- coding: utf-8 -*-
# test_eval.py - PFSP 测试评估模块

import pickle
import numpy as np
import time
from heuristic import select_next_job


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估 PFSP 缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_makespans = []
    test_times = []

    for instance_idx, processing_times in enumerate(test_data):
        best_seq, best_makespan = test_solutions[instance_idx]
        n_jobs, num_machines = processing_times.shape
        current_schedule = []
        unscheduled = list(range(n_jobs))

        start_time = time.time()
        while unscheduled:
            next_job = select_next_job(np.array(unscheduled), current_schedule, processing_times, num_machines)
            if next_job is None:
                break
            current_schedule.append(next_job)
            unscheduled.remove(next_job)

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

        elapsed_time = time.time() - start_time
        heuristic_makespans.append(makespan)
        test_times.append(elapsed_time)

    standard_makespans = [sol[1] for sol in test_solutions]
    differences = np.array(heuristic_makespans) - np.array(standard_makespans)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_configs = [(10, 5), (20, 5), (50, 10)]
        for n_jobs, n_machines in test_configs:
            test_data_path = f'datasets/test_data_{n_jobs}x{n_machines}.pkl'
            test_solution_path = f'datasets/test_solution_{n_jobs}x{n_machines}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"PFSP{n_jobs}x{n_machines}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"PFSP{n_jobs}x{n_machines}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
