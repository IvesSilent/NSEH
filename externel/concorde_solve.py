import os
import pickle
import numpy as np
from concorde.tsp import TSPSolver


def concorde_solve(data_path, output_path):
    """
    使用pyconcorde求解TSP问题，并保存结果。
    """
    # 加载数据集
    with open(data_path, 'rb') as f:
        data = pickle.load(f)

    # 求解每个实例并保存结果
    solutions = []
    for coordinates, distance_matrix in data:

        # 提取坐标信息
        xs = coordinates[:, 0]  # 提取所有节点的 x 坐标
        ys = coordinates[:, 1]  # 提取所有节点的 y 坐标

        xs = np.round(xs * 100000).astype(int)
        ys = np.round(ys * 100000).astype(int)
        # print("开始创建求解器")
        # breakpoint()

        # 使用坐标创建 TSPSolver 实例
        solver = TSPSolver.from_data(xs, ys, norm="EUC_2D", name="TSP")
        # print("求解器创建成功！")
        # breakpoint()

        solution = solver.solve()
        # print("问题解决！")
        # breakpoint()

        tour = solution.tour
        tour_length = solution.optimal_value / 100000

        # print(f"tour_length = {tour_length}")
        # breakpoint()

        solutions.append((tour, tour_length))



    # 保存结果
    with open(output_path, 'wb') as f:
        pickle.dump(solutions, f)


if __name__ == "__main__":
    # 设置数据集路径和输出路径
    train_data_path = '../problems/tsp/datasets/train_data_tsp.pkl'
    train_solution_path = '../problems/tsp/datasets/train_data_solution.pkl'

    test_sizes = [10, 20, 50, 100, 200]
    test_data_paths = []
    test_solution_paths = []

    for size in test_sizes:
        test_data_paths.append(f'problems/tsp/datasets/test_data_{size}.pkl')
        test_solution_paths.append(f'problems/tsp/datasets/test_solution_{size}.pkl')

    # 处理训练数据集
    concorde_solve(train_data_path, train_solution_path)

    # 处理测试数据集
    for data_path, solution_path in zip(test_data_paths, test_solution_paths):
        concorde_solve(data_path, solution_path)

    print("Concorde求解完成，结果已保存！")
