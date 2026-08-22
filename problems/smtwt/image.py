# -*- coding: utf-8 -*-
# SMTWT 可视化（甘特图 + 延误标注）

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_smtwt_solution(p, d, w, sequence, filename='smtwt_solution.png'):
    """绘制单机调度甘特图"""
    plt.figure(figsize=(12, 4))
    t = 0.0
    colors = plt.cm.tab20(np.linspace(0, 1, len(sequence)))
    for k, j in enumerate(sequence):
        plt.barh(0, p[j], left=t, height=0.5, color=colors[k], edgecolor='black', linewidth=0.5)
        # 标记延误
        tardiness = max(0, t + p[j] - d[j])
        if tardiness > 0:
            plt.text(t + p[j] / 2, 0.35, f'{tardiness:.0f}', ha='center', fontsize=7, color='red')
        t += p[j]
    plt.xlabel('Time')
    plt.title('Single Machine Schedule (red = tardiness)')
    plt.yticks([])
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_50.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_50.pkl", "rb") as f:
        solutions = pickle.load(f)

    p, d, w = data[0]
    cost, seq = solutions[0]
    plot_smtwt_solution(p, d, w, seq)
    print(f"smtwt_solution.png 已生成 (cost={cost:.0f})")
