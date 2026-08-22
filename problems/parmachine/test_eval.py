# -*- coding: utf-8 -*-
# test_eval.py - Parallel Machine 测试评估模块

import pickle
import numpy as np
import time
from heuristic import assign_job


def heuristic_solve_static(test_data_path, test_solution_path):
    """
    静态评估并行机缺省启发式在测试集上的性能
    返回 (objective, elapsed_time)
    """
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    heuristic_makespans = []
    test_times = []

    for instance_idx, (processing_times, num_machines) in enumerate(test_data):
        std_cmax, _ = test_solutions[instance_idx]
        n = len(processing_times)

        start_time = time.time()
        order = list(np.argsort(-processing_times))
        loads = np.zeros(num_machines)
        for j in order:
            mach = assign_job(int(j), loads, processing_times, num_machines)
            mach = int(mach) if mach is not None else 0
            loads[mach] += processing_times[j]
        elapsed_time = time.time() - start_time

        heuristic_makespans.append(float(loads.max()))
        test_times.append(elapsed_time)

    standard_makespans = [sol[0] for sol in test_solutions]
    differences = np.array(heuristic_makespans) - np.array(standard_makespans)
    test_objective = np.mean(differences)
    test_time = np.mean(test_times)

    return test_objective, test_time


if __name__ == "__main__":
    with open("result.txt", "w") as result_file:
        test_sizes = [(50, 4), (100, 8), (200, 8)]
        for n_jobs, m in test_sizes:
            test_data_path = f'datasets/test_data_{n_jobs}x{m}.pkl'
            test_solution_path = f'datasets/test_solution_{n_jobs}x{m}.pkl'
            test_objective, test_time = heuristic_solve_static(test_data_path, test_solution_path)
            print(f"ParMachine{n_jobs}x{m}: Objective = {test_objective:.2f}, time = {test_time:.4f}s")
            result_file.write(f"ParMachine{n_jobs}x{m}: Objective = {test_objective:.2f}, time = {test_time:.4f}s\n")
