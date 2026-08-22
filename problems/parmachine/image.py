# -*- coding: utf-8 -*-
# Parallel Machine 可视化（机器负载条形图）

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_parmachine_solution(p, assignment, num_machines, filename='parmachine_solution.png'):
    """绘制各机器负载甘特图"""
    plt.figure(figsize=(12, max(4, num_machines * 0.8)))
    colors = plt.cm.tab20(np.linspace(0, 1, len(p)))
    for mach in range(num_machines):
        jobs = [j for j, m in enumerate(assignment) if m == mach]
        t = 0.0
        for j in jobs:
            plt.barh(mach, p[j], left=t, height=0.6, color=colors[j], edgecolor='black', linewidth=0.3)
            t += p[j]
    plt.xlabel('Time')
    plt.ylabel('Machine')
    plt.title('Parallel Machine Schedule')
    plt.yticks(range(num_machines))
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50x4.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50x4.pkl", "rb") as f:
        solutions = pickle.load(f)

    p, m = data[0]
    cmax, assignment = solutions[0]
    plot_parmachine_solution(p, assignment, m)
    print(f"parmachine_solution.png 已生成 (makespan={cmax:.0f})")
