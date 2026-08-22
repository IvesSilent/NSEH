# -*- coding: utf-8 -*-
# QAP 可视化（分配热力图）

import numpy as np
import matplotlib.pyplot as plt
import pickle


def plot_qap_solution(flow_matrix, distance_matrix, assignment, filename='qap_solution.png'):
    """绘制设施-位置分配热力图"""
    n = len(assignment)
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(flow_matrix, cmap='Blues', aspect='auto')
    plt.colorbar(label='Flow')
    plt.title('Flow Matrix (facilities)')
    plt.xlabel('Facility')
    plt.ylabel('Facility')

    plt.subplot(1, 2, 2)
    perm = np.argsort(assignment)
    plt.imshow(distance_matrix, cmap='Oranges', aspect='auto')
    plt.colorbar(label='Distance')
    plt.title('Distance Matrix (positions)')
    plt.xlabel('Position')
    plt.ylabel('Position')
    # 标注设施→位置映射
    for f in range(n):
        plt.annotate(f'F{f}', (assignment[f], f), ha='center', va='center',
                     color='red', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()


if __name__ == "__main__":
    with open("datasets/test_data_8.pkl", "rb") as f:
        data = pickle.load(f)
    with open("datasets/test_solution_8.pkl", "rb") as f:
        solutions = pickle.load(f)

    flow, dist = data[0]
    cost, assignment = solutions[0]
    plot_qap_solution(flow, dist, assignment)
    print(f"qap_solution.png 已生成 (cost={cost:.0f})")
