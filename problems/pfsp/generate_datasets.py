# -*- coding: utf-8 -*-
# PFSP (Permutation Flow Shop Scheduling) 数据集生成器

import os
import pickle
import numpy as np


def generate_pfsp_instance(n_jobs, n_machines):
    """
    生成 Flow Shop 调度实例（Taillard 风格）
    返回: processing_times: (n_jobs, n_machines) 加工时间矩阵
    """
    processing_times = np.random.randint(1, 100, size=(n_jobs, n_machines))
    return processing_times


def neh_solve(processing_times):
    """
    NEH 启发式算法求解 PFSP
    返回: (最佳序列, makespan)
    """
    n_jobs, n_machines = processing_times.shape

    # 按总加工时间降序排列作为初始顺序
    total_times = np.sum(processing_times, axis=1)
    sorted_jobs = np.argsort(-total_times)

    def calculate_makespan(sequence):
        """计算给定序列的 makespan"""
        n = len(sequence)
        completion = np.zeros((n, n_machines), dtype=float)
        for i in range(n):
            for m in range(n_machines):
                prev_job = completion[i - 1, m] if i > 0 else 0
                prev_machine = completion[i, m - 1] if m > 0 else 0
                completion[i, m] = max(prev_job, prev_machine) + processing_times[sequence[i], m]
        return completion[-1, -1]

    # NEH 插入法
    best_seq = [sorted_jobs[0]]
    for job in sorted_jobs[1:]:
        best_makespan = float('inf')
        best_pos = 0
        for pos in range(len(best_seq) + 1):
            candidate = best_seq[:pos] + [job] + best_seq[pos:]
            ms = calculate_makespan(candidate)
            if ms < best_makespan:
                best_makespan = ms
                best_pos = pos
        best_seq = best_seq[:best_pos] + [job] + best_seq[best_pos:]

    return best_seq, calculate_makespan(best_seq)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    # 训练集：64 个实例，20 jobs x 5 machines (构建型启发式)
    train_data = []
    train_solutions = []
    for i in range(64):
        proc_times = generate_pfsp_instance(20, 5)
        best_seq, makespan = neh_solve(proc_times)
        train_data.append(proc_times)
        train_solutions.append((best_seq, makespan))
        if (i + 1) % 16 == 0:
            print(f"PFSP 训练实例 {i+1}/64 生成完成")

    with open(os.path.join(datasets_dir, "train_data_pfsp.pkl"), "wb") as f:
        pickle.dump(train_data, f)
    with open(os.path.join(datasets_dir, "train_solution_pfsp.pkl"), "wb") as f:
        pickle.dump(train_solutions, f)
    print("PFSP 训练集保存完成")

    # 测试集：多规模
    test_configs = [(10, 5), (20, 5), (50, 10)]
    for n_jobs, n_machines in test_configs:
        test_data = []
        test_solutions = []
        for i in range(10):
            proc_times = generate_pfsp_instance(n_jobs, n_machines)
            best_seq, makespan = neh_solve(proc_times)
            test_data.append(proc_times)
            test_solutions.append((best_seq, makespan))
            print(f"PFSP{n_jobs}x{n_machines} 测试实例 {i+1}/10 生成完成")

        with open(os.path.join(datasets_dir, f"test_data_{n_jobs}x{n_machines}.pkl"), "wb") as f:
            pickle.dump(test_data, f)
        with open(os.path.join(datasets_dir, f"test_solution_{n_jobs}x{n_machines}.pkl"), "wb") as f:
            pickle.dump(test_solutions, f)
        print(f"PFSP{n_jobs}x{n_machines} 测试集保存完成")

    print("PFSP 所有数据集生成完成！")
