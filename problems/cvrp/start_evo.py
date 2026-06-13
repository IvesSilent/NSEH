# -*- coding: utf-8 -*-
# problems/cvrp/start_evo.py - CVRP CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

# 配置参数
PROBLEM_PATH = "problems/cvrp"
TRAIN_DATA = "train_data_cvrp.pkl"
TRAIN_SOLUTION = "train_solution_cvrp.pkl"

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
    "problem": "CVRP（容量受限车辆路径问题）：给定一个仓库和多个客户节点，每辆车有容量限制，需要为所有客户配送货物，目标是最小化总行驶距离。可以通过从当前节点开始逐步选择下一个要服务的客户来构建路线。",
    "fun_name": "find_best_route",
    "fun_args": ["current_node", "remaining_demands", "vehicle_capacity", "current_load", "distance_matrix", "demand_list"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node'和'next_node'是节点ID。'remaining_demands'是布尔数组表示未服务节点。'vehicle_capacity'和'current_load'是标量。'distance_matrix'是距离矩阵。'demand_list'是各节点需求量。如果无合适节点则返回-1表示返回仓库。所有数据均为Numpy数组。"
}

ASCEND = True

EVOLUTION_CONFIG = {
    "population_capacity": POPULATION_CAPACITY,
    "num_generations": NUM_GENERATIONS,
    "num_mutation": NUM_MUTATION,
    "num_hybridization": NUM_HYBRIDIZATION,
    "num_reflection": NUM_REFLECTION,
    "save_dir": "result",
    "ascend": ASCEND
}

if __name__ == "__main__":
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"

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

    evo = EvolutionFramework(
        problem_path=PROBLEM_PATH,
        generator=gen,
        **EVOLUTION_CONFIG
    )

    evo.run()
