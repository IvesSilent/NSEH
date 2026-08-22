# -*- coding: utf-8 -*-
# train_eval.py - Parallel Machine 训练评估模块

import pickle
import numpy as np
import importlib.util


def heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_algorithm, fun_name="assign_job"):
    """
    动态评估并行机启发式算法的训练适应度
    返回启发式解与标准解的平均 makespan 差距
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

    for instance_idx, (processing_times, num_machines) in enumerate(train_data):
        std_cmax, _ = train_solutions[instance_idx]
        n = len(processing_times)

        # 评估器按 LPT 顺序逐个分配
        order = list(np.argsort(-processing_times))
        loads = np.zeros(num_machines)
        valid = True
        for j in order:
            mach = heuristic_function(int(j), loads, processing_times, num_machines)
            if mach is None:
                valid = False
                break
            mach = int(mach)
            if not (0 <= mach < num_machines):
                valid = False
                break
            loads[mach] += processing_times[j]

        heuristic_makespans.append(float(loads.max()) if valid else float('inf'))

    standard_makespans = [sol[0] for sol in train_solutions]
    differences = np.array(heuristic_makespans) - np.array(standard_makespans)
    objective = np.mean(differences)

    return objective


if __name__ == "__main__":
    train_data_path = "datasets/train_data_parmachine.pkl"
    train_solution_path = "datasets/train_solution_parmachine.pkl"

    heuristic_code = """import numpy as np

def assign_job(job_id, machine_loads, processing_times, num_machines):
    return int(np.argmin(machine_loads))
"""

    objective = heuristic_solve_dynamic(train_data_path, train_solution_path, heuristic_code, "assign_job")
    print(f"ParMachine 训练集评估 objective = {objective}")
