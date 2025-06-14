import pickle
import numpy as np

# with open("externel/instance_data_20.pkl", "rb") as f:
#     data = pickle.load(f)
# with open("problems/tsp/datasets/test_data_10.pkl", "rb") as f:
#     data = pickle.load(f)

# print(f"\ndata:\n{data}")
# breakpoint()

with open("../problems/tsp/datasets/train_data_solution.pkl", "rb") as f:
    data = pickle.load(f)
# print("Now loading file: train_data_solution.pkl")
# print(f"Data type: {type(data)}")
# print(f"Data length: {len(data)}")
# breakpoint()

# test_sizes = [10, 20, 50, 100, 200]
# for size in test_sizes:
#     with open(f"problems/tsp/datasets/test_solution_{size}.pkl", "rb") as f:
#         data = pickle.load(f)
#     print(f"Now loading file: test_solution_{size}.pkl")
#     print(f"Data type: {type(data)}")
#     print(f"Data length: {len(data)}")
#     breakpoint()


for i in range(50):
    print(f"length_{i+1} = {data[i][1]}")

print("\n!END!")
# print(f"Data type: {type(data)}")
# print(f"Data length: {len(data)}")
breakpoint()

unvisited_nodes,distance_matrix = data[0]

print(f"len(unvisited_nodes) = {len(unvisited_nodes)}")
print(f"len(distance_matrix) = {len(distance_matrix)}")
breakpoint()

print(f"unvisited_nodes = {unvisited_nodes}")

# print(f"First few items of data:\n{data[:5]}")
breakpoint()

# 将列表转换为 NumPy 数组
data_array = np.array(data)
print(f"data_array.shape:\n{data_array.shape}")

# print(data.shape)  # 例如输出 (10,2) 表示10个城市的坐标
