# -*- coding: utf-8 -*-
# Job Shop Scheduling（作业车间调度）数据集生成器
# 标准解：SPT 优先规则贪心（非延迟调度近似）
# 每个实例保存为 (machine_matrix, time_matrix)
#   machine_matrix: (n_jobs, n_machines) 每行是该 job 的机器访问顺序（permutation）
#   time_matrix:    (n_jobs, n_machines) 对应工序的加工时间

import os
import pickle
import numpy as np


def generate_jsp_instance(n_jobs, n_machines, seed=None):
    """
    生成 JSP 实例（Taillard 风格）
    返回: (machine_matrix, time_matrix)
    """
    rng = np.random.default_rng(seed)
    machine_matrix = np.array([rng.permutation(n_machines) for _ in range(n_jobs)])
    time_matrix = rng.integers(1, 100, size=(n_jobs, n_machines))
    return machine_matrix, time_matrix


def schedule_by_rule(machine_matrix, time_matrix, rule='spt', rng=None):
    """按指定规则贪心调度，返回 makespan"""
    n_jobs, n_machines = machine_matrix.shape
    progress = np.zeros(n_jobs, dtype=int)
    job_completion = np.zeros(n_jobs, dtype=float)
    machine_ready = np.zeros(n_machines, dtype=float)

    remaining = list(range(n_jobs))
    while remaining:
        if rule == 'spt':
            best_job = min(remaining, key=lambda j: time_matrix[j, progress[j]])
        elif rule == 'mwkr':
            # Most Work Remaining：剩余总加工时间最大
            best_job = max(remaining, key=lambda j: np.sum(time_matrix[j, progress[j]:]))
        elif rule == 'lpt':
            best_job = max(remaining, key=lambda j: time_matrix[j, progress[j]])
        elif rule == 'random':
            best_job = int(rng.choice(remaining))
        else:
            best_job = remaining[0]
        k = progress[best_job]
        m = machine_matrix[best_job, k]
        start = max(machine_ready[m], job_completion[best_job])
        finish = start + time_matrix[best_job, k]
        machine_ready[m] = finish
        job_completion[best_job] = finish
        progress[best_job] += 1
        if progress[best_job] >= n_machines:
            remaining.remove(best_job)

    return float(job_completion.max())


def jsp_standard_solve(machine_matrix, time_matrix, rng=None):
    """
    标准解：多规则 + 随机重启取最优（比单一 SPT 更强，给进化留空间）
    返回: makespan
    """
    best = float('inf')
    for rule in ['spt', 'mwkr', 'lpt']:
        best = min(best, schedule_by_rule(machine_matrix, time_matrix, rule))
    if rng is not None:
        for _ in range(20):
            best = min(best, schedule_by_rule(machine_matrix, time_matrix, 'random', rng))
    return best


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，10 jobs x 5 machines
    train_data = []
    train_solutions = []
    for i in range(64):
        inst = generate_jsp_instance(10, 5, seed=100 + i)
        mk = jsp_standard_solve(*inst, rng=np.random.default_rng(seed=5000 + i))
        train_data.append(inst)
        train_solutions.append(mk)
        if (i + 1) % 16 == 0:
            print(f"JSP 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_jsp.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_jsp.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("JSP 训练集保存完成")

    # 测试集：多规模
    test_configs = [(10, 5), (20, 10), (30, 15)]
    for n_jobs, n_machines in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            inst = generate_jsp_instance(n_jobs, n_machines, seed=1000 + i)
            mk = jsp_standard_solve(*inst, rng=np.random.default_rng(seed=5000 + i))
            test_data.append(inst)
            test_solutions.append(mk)

        with open(os.path.join(datasets_dir, f"test_data_{n_jobs}x{n_machines}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_jobs}x{n_machines}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"JSP{n_jobs}x{n_machines} 测试集保存完成")

    print("JSP 所有数据集生成完成！")
