# -*- coding: utf-8 -*-
# problems/maxcut/start_evo.py - MaxCut CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/maxcut"
TRAIN_DATA = "train_data_maxcut.pkl"
TRAIN_SOLUTION = "train_solution_maxcut.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "MaxCut问题：给定一个无向带权图，需要将节点分成两组（用0和1标记），使得连接不同组的边的权重之和最大。可以通过逐个分配节点到某一侧来构建划分。",
    "fun_name": "assign_node",
    "fun_args": ["node_id", "unassigned_nodes", "adjacency_matrix", "current_partition"],
    "fun_return": ["side"],
    "fun_notes": "'node_id'是当前需要分配的节点索引。'unassigned_nodes'是布尔数组表示尚未分配的节点。'adjacency_matrix'是带权邻接矩阵。'current_partition'是当前部分分配（-1=未分配, 0/1=已分配侧）。返回0或1表示分配到哪一侧。所有数据均为Numpy数组。"
}

ASCEND = True  # 差值越小越好（基线 - 启发式）

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
