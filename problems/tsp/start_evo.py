# problems/tsp/start_evo.py

import sys
from pathlib import Path

# 获取项目根目录路径（假设start_evo.py在problems/tsp目录下）
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))  # 将项目根目录加入模块搜索路径

from core.evolution import EvolutionFramework
from core.generator import generator
import os
# 配置参数
PROBLEM_PATH = "problems/tsp"
TRAIN_DATA = "train_data_tsp.pkl"
TRAIN_SOLUTION = "train_data_solution.pkl"

# LLM配置
API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

# 进化参数
POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

# 函数参数配置
FUNCTION_CONFIG = {
    "problem": "TSP问题即，给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。可以通过从当前节点开始逐步选择下一个节点来解决此任务。",
    "fun_name": "select_next_node",
    "fun_args": ["current_node", "destination_node", "unvisited_nodes", "distance_matrix"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix是节点的距离矩阵。所有数据均为Numpy数组。"
}

ASCEND = True # 是否生序排列

# 进化参数
EVOLUTION_CONFIG = {
    "population_capacity": POPULATION_CAPACITY,
    "num_generations": NUM_GENERATIONS,
    "num_mutation": NUM_MUTATION,
    "num_hybridization": NUM_HYBRIDIZATION,
    "num_reflection": NUM_REFLECTION,
    "save_dir": "result",
    "ascend":ASCEND # 是否升序排列
}

if __name__ == "__main__":
    # 防止joblib警告
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # 设置为你的核心数

    # 问题及启发式函描述
    problem = ("TSP问题,即给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
               "可以通过从当前节点开始逐步选择下一个节点来解决此任务。")
    fun_name = "select_next_node"
    fun_args = ["current_node", "destination_node", "univisited_nodes", "distance_matrix"]
    fun_return = ["next_node"]
    fun_notes = ("'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix'是节点的距离矩阵。"
                 "所有数据均为Numpy数组。")


    # 初始化生成器
    gen = generator(
        api_key=API_KEY,
        base_url=BASE_URL,
        llm_model=LLM_MODEL,
        if_stream=False,
        problem_path=PROBLEM_PATH,
        train_data_name=TRAIN_DATA,
        train_solution_name=TRAIN_SOLUTION,
        **FUNCTION_CONFIG
    )
    #
    # print(f"EVOLUTION_CONFIG = {EVOLUTION_CONFIG}")
    # breakpoint()

    # 初始化进化框架
    evo = EvolutionFramework(
        problem_path=PROBLEM_PATH,
        generator=gen,
        **EVOLUTION_CONFIG
    )


    # 启动进化流程
    evo.run()