# -*- coding: utf-8 -*-
# problems/orienteering/start_evo.py - Orienteering CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/orienteering"
TRAIN_DATA = "train_data_orienteering.pkl"
TRAIN_SOLUTION = "train_solution_orienteering.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "定向越野问题（Orienteering）：给定一个起点/终点和一组客户节点，每个客户有访问利润，旅行者有一条总距离预算，需要规划一条从起点出发、在预算内访问若干客户并返回起点的路线，目标是在预算约束内最大化访问客户的总利润。可以通过从当前节点开始逐步选择下一个要访问的客户来构建路线；若剩余预算不足以访问任何客户并返回起点，则返回-1表示结束路线返回起点。",
    "fun_name": "select_next_node",
    "fun_args": ["current_node", "visited", "remaining_profits", "distance_matrix", "budget_left", "total_profit"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node'是当前所在节点ID。'visited'是布尔数组表示已访问节点。'remaining_profits'是各节点利润数组。'distance_matrix'是距离矩阵。'budget_left'是剩余预算（标量）。'total_profit'是当前累计利润（标量）。返回下一个要访问的客户节点ID；若无法再访问任何客户（预算不足）则返回-1表示返回起点结束。所有数据均为Numpy数组。"
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
