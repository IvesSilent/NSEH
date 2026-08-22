# -*- coding: utf-8 -*-
# problems/steinertree/start_evo.py - Steiner Tree CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/steinertree"
TRAIN_DATA = "train_data_steinertree.pkl"
TRAIN_SOLUTION = "train_solution_steinertree.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "斯坦纳树问题（Steiner Tree）：给定一个带权无向图和一组必须连通的终端节点，需要选择一组边和中间节点（斯坦纳点），使得所有终端节点连通，目标是最小化所选边的总权重。可以通过从根终端出发，每次选择一个未连接的终端并将其连接到当前树（沿最短路径）来构建解。",
    "fun_name": "select_next_terminal",
    "fun_args": ["current_tree", "unconnected_terminals", "adjacency_matrix", "distances"],
    "fun_return": ["terminal_index"],
    "fun_notes": "'current_tree'是布尔数组，True表示该节点已在当前树中。'unconnected_terminals'是尚未连接的终端节点索引数组。'adjacency_matrix'是带权邻接矩阵（0表示无边）。'distances'是(n x n)全源最短路径距离矩阵。返回下一个要连接的终端节点索引；若无法连接则返回None。所有数据均为Numpy数组。"
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
