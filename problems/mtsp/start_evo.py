# -*- coding: utf-8 -*-
# problems/mtsp/start_evo.py - mTSP CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/mtsp"
TRAIN_DATA = "train_data_mtsp.pkl"
TRAIN_SOLUTION = "train_solution_mtsp.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "多旅行商问题（mTSP）：给定多个旅行商和一个仓库节点，需要为每个旅行商规划一条从仓库出发、访问若干客户节点并返回仓库的环线，所有客户节点必须被恰好一个旅行商访问一次，目标是最小化所有旅行商的总行驶距离。可以通过从当前节点开始逐步选择下一个要访问的客户来构建路线；返回-1表示当前旅行商返回仓库结束路线，换下一个旅行商。",
    "fun_name": "select_next_node",
    "fun_args": ["current_node", "unvisited_nodes", "distance_matrix", "remaining_salesmen"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node'是当前所在节点ID。'unvisited_nodes'是尚未访问的客户节点ID数组。'distance_matrix'是节点间距离矩阵。'remaining_salesmen'是剩余可用的旅行商数量（含当前）。返回下一个要访问的客户节点ID；返回-1表示当前路线结束（返回仓库），换下一个旅行商。所有数据均为Numpy数组。"
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
