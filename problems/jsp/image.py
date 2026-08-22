# -*- coding: utf-8 -*-
# JSP 可视化（甘特图）

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_jsp_solution(machine_matrix, time_matrix, schedule, filename='jsp_solution.png'):
    """
    绘制 JSP 甘特图
    schedule: 按工序推进顺序记录 (job, machine, start, end) 的列表
    """
    plt.figure(figsize=(12, 6))
    colors = plt.cm.tab20(np.linspace(0, 1, machine_matrix.shape[0]))

    for job, machine, start, end in schedule:
        plt.barh(machine, end - start, left=start, height=0.6,
                 color=colors[job], edgecolor='black', linewidth=0.5,
                 label=f'Job {job}' if start == 0 and machine == machine_matrix[job, 0] else None)

    plt.xlabel('Time')
    plt.ylabel('Machine')
    plt.title('Job Shop Schedule (Gantt Chart)')
    plt.yticks(range(machine_matrix.shape[1]))
    plt.grid(axis='x', alpha=0.3)
    plt.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


def build_schedule(machine_matrix, time_matrix):
    """用 SPT 规则构建调度记录，返回 (schedule, makespan)"""
    n_jobs, n_machines = machine_matrix.shape
    progress = np.zeros(n_jobs, dtype=int)
    job_completion = np.zeros(n_jobs, dtype=float)
    machine_ready = np.zeros(n_machines, dtype=float)
    schedule = []
    remaining = list(range(n_jobs))
    while remaining:
        job = min(remaining, key=lambda j: time_matrix[j, progress[j]])
        k = progress[job]
        m = machine_matrix[job, k]
        start = max(machine_ready[m], job_completion[job])
        finish = start + time_matrix[job, k]
        schedule.append((job, m, start, finish))
        machine_ready[m] = finish
        job_completion[job] = finish
        progress[job] += 1
        if progress[job] >= n_machines:
            remaining.remove(job)
    return schedule, float(job_completion.max())


if __name__ == "__main__":
    with open("datasets/test_data_10x5.pkl", "rb") as f:
        data = pickle.load(f)
    machine_matrix, time_matrix = data[0]
    schedule, mk = build_schedule(machine_matrix, time_matrix)
    plot_jsp_solution(machine_matrix, time_matrix, schedule)
    print(f"jsp_solution.png 已生成 (makespan={mk:.0f})")
