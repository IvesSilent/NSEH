# -*- coding: utf-8 -*-
# PFSP 可视化：甘特图

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_pfsp_gantt(processing_times, sequence, filename='pfsp_schedule.png'):
    """绘制 PFSP 调度甘特图"""
    num_machines = processing_times.shape[1]
    n_jobs = len(sequence)

    colors = plt.cm.tab20(np.linspace(0, 1, n_jobs))
    job_colors = {job: colors[i] for i, job in enumerate(sequence)}

    fig, ax = plt.subplots(figsize=(14, 6))

    # 计算各作业在各机器上的开始和结束时间
    completion = np.zeros((n_jobs, num_machines))

    for i, job in enumerate(sequence):
        for m in range(num_machines):
            prev_job = completion[i - 1, m] if i > 0 else 0
            prev_machine = completion[i, m - 1] if m > 0 else 0
            start = max(prev_job, prev_machine)
            end = start + processing_times[job, m]
            completion[i, m] = end

            ax.barh(m, end - start, left=start, height=0.6,
                    color=job_colors[job], edgecolor='white',
                    label=f'Job {job}' if m == 0 else "")

    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f'Machine {m + 1}' for m in range(num_machines)])
    ax.set_xlabel('Time')
    ax.set_title(f'PFSP Gantt Chart (Makespan: {completion[-1, -1]:.0f})')
    ax.grid(True, axis='x', alpha=0.3)
    ax.legend(loc='upper right', ncol=min(5, n_jobs))

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()


if __name__ == "__main__":
    test_data_path = 'datasets/test_data_10x5.pkl'
    test_solution_path = 'datasets/test_solution_10x5.pkl'

    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(test_solution_path, 'rb') as f:
        test_solutions = pickle.load(f)

    processing_times = test_data[0]
    best_seq, makespan = test_solutions[0]

    print(f"作业数: {processing_times.shape[0]}, 机器数: {processing_times.shape[1]}")
    print(f"最优序列: {best_seq}")
    print(f"Makespan: {makespan}")

    plot_pfsp_gantt(processing_times, best_seq)
