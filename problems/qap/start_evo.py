# -*- coding: utf-8 -*-
# problems/qap/start_evo.py - QAP CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/qap"
TRAIN_DATA = "train_data_qap.pkl"
TRAIN_SOLUTION = "train_solution_qap.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "二次分配问题（QAP）：给定n个设施和n个位置，设施之间有物流流量矩阵，位置之间有距离矩阵，需要将每个设施分配到唯一一个位置，使所有设施对的流量×距离之和最小。可以通过按某个顺序逐个为设施选择位置来构建解（考虑与已分配设施的交互成本）。",
    "fun_name": "assign_facility",
    "fun_args": ["facility_id", "available_positions", "flow_matrix", "distance_matrix", "current_assignment"],
    "fun_return": ["position_index"],
    "fun_notes": "'facility_id'是当前要分配的设施索引。'available_positions'是尚未占用的位置索引数组。'flow_matrix'是设施间流量矩阵。'distance_matrix'是位置间距离矩阵。'current_assignment'是当前部分分配数组（-1=未分配，>=0=设施占用的位置）。返回该设施应分配的位置索引。所有数据均为Numpy数组。"
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
