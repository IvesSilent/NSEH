# -*- coding: utf-8 -*-
# problems/vrptw/start_evo.py - VRPTW CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/vrptw"
TRAIN_DATA = "train_data_vrptw.pkl"
TRAIN_SOLUTION = "train_solution_vrptw.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "带时间窗的车辆路径问题（VRPTW）：给定一个仓库和多个客户节点，每个客户有需求量、服务时间和服务时间窗[最早开始,最晚开始]，车辆有容量限制，目标是在满足所有客户时间窗和车辆容量约束的前提下，用最少的车辆和最短的总行驶距离服务所有客户。可以通过从当前节点开始逐步选择下一个要服务的客户来构建路线；若车辆装不下或无法在时间窗内到达，则返回-1表示返回仓库。",
    "fun_name": "select_next_customer",
    "fun_args": ["current_node", "current_time", "remaining_demands", "vehicle_capacity", "current_load", "distance_matrix", "demand_list", "time_windows", "service_times"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node'是当前节点ID。'current_time'是当前路线已用时间。'remaining_demands'是布尔数组表示未服务节点。'vehicle_capacity'和'current_load'是标量。'distance_matrix'是距离矩阵。'demand_list'是各节点需求量。'time_windows'是(n,2)数组，每行[最早开始,最晚开始]。'service_times'是各节点服务时间。返回下一个要服务的客户节点ID；若无可行客户则返回-1表示返回仓库。所有数据均为Numpy数组。"
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
        api_key=***
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
