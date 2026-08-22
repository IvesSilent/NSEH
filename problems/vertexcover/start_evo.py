# -*- coding: utf-8 -*-
# problems/vertexcover/start_evo.py - Minimum Vertex Cover CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/vertexcover"
TRAIN_DATA = "train_data_vertexcover.pkl"
TRAIN_SOLUTION = "train_solution_vertexcover.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "最小顶点覆盖问题（Minimum Vertex Cover）：给定一个无向图，需要选出最少数量的节点，使得图中的每条边都至少有一个端点在所选节点集合中。可以通过逐个选择节点加入覆盖集合来构建解，直到所有边都被覆盖。",
    "fun_name": "select_next_vertex",
    "fun_args": ["uncovered_edges", "adjacency_matrix", "current_cover"],
    "fun_return": ["vertex_index"],
    "fun_notes": "'uncovered_edges'是布尔矩阵，uncovered_edges[i,j]=True表示边(i,j)尚未被覆盖。'adjacency_matrix'是无向图邻接矩阵（0/1）。'current_cover'是布尔数组表示当前已选入覆盖的节点。返回下一个要加入覆盖的节点索引（0-based），若无法继续则返回None。所有数据均为Numpy数组。"
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
