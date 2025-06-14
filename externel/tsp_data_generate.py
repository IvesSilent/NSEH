import os
import pickle
import numpy as np
from scipy.spatial.distance import pdist, squareform

# 创建保存数据的目录
os.makedirs("../problems/tsp/datasets", exist_ok=True)

# 生成TSP实例的函数
def generate_tsp_instance(num_nodes, space=(0, 1)):
    # 随机生成点的坐标
    coordinates = np.random.uniform(space[0], space[1], size=(num_nodes, 2))
    # 计算距离矩阵
    distance_matrix = squareform(pdist(coordinates, metric='euclidean'))
    return coordinates, distance_matrix

# 生成训练数据
train_data = []
for _ in range(64):
    coordinates, distance_matrix = generate_tsp_instance(100)
    train_data.append((coordinates, distance_matrix))

# 保存训练数据
with open("../problems/tsp/datasets/train_data_tsp.pkl", "wb") as f:
    pickle.dump(train_data, f)

# 生成测试数据
test_sizes = [10, 20, 50, 100, 200]
for size in test_sizes:
    test_data = []
    for _ in range(100):
        coordinates, distance_matrix = generate_tsp_instance(size)
        test_data.append((coordinates, distance_matrix))
    # 保存测试数据
    with open(f"problems/tsp/datasets/test_data_{size}.pkl", "wb") as f:
        pickle.dump(test_data, f)

print("数据生成完成！")