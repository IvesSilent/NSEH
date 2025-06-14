import numpy as np
import matplotlib.pyplot as plt
import pickle

# 读取测试数据
test_data_path = 'datasets/test_data_100.pkl'
with open(test_data_path, 'rb') as f:
    test_data = pickle.load(f)

# 提取第一个TSP10实例的坐标和距离矩阵
coordinates = test_data[0][0]
distance_matrix = test_data[0][1]


# 启发式算法：贪心算法
def select_next_node(current_node, unvisited_nodes, distance_matrix):
    # 计算当前节点到所有未访问节点的距离
    distances = [distance_matrix[current_node][i] for i in unvisited_nodes if i != current_node]
    # 选择距离最小的节点
    next_node_id = np.argmin(distances)
    next_node = unvisited_nodes[next_node_id]
    return next_node


# 求解TSP问题
def solve_tsp(coordinates, distance_matrix):
    num_nodes = len(coordinates)
    visited_nodes = [0]  # 从第一个节点开始
    unvisited_nodes = list(range(1, num_nodes))

    current_node = 0
    while unvisited_nodes:
        next_node = select_next_node(current_node, unvisited_nodes, distance_matrix)
        visited_nodes.append(next_node)
        unvisited_nodes.remove(next_node)
        current_node = next_node

    # 添加返回起点的路径
    visited_nodes.append(0)
    return visited_nodes


# 求解第一个TSP10实例
solution = solve_tsp(coordinates, distance_matrix)


# 绘制路径图
def plot_tsp_solution(coordinates, solution, filename='tsp_solution_100.png'):
    x = [coordinates[i][0] for i in solution]
    y = [coordinates[i][1] for i in solution]

    plt.figure(figsize=(6, 6))
    plt.plot(x, y, 'b-o', markersize=8, linewidth=2)
    plt.title('TSP Solution')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.savefig(filename)
    plt.show()


# 绘制并保存路径图
plot_tsp_solution(coordinates, solution)