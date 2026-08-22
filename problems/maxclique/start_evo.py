# -*- coding: utf-8 -*-
# problems/maxclique/start_evo.py - Maximum Clique CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/maxclique"
TRAIN_DATA = "train_data_maxclique.pkl"
TRAIN_SOLUTION = "train_solution_maxclique.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "最大团问题（Maximum Clique）：给定一个无向图，需要找出一组节点，使得这组节点中任意两个节点之间都有边相连（构成一个团），目标是在所有这样的节点组中找到规模最大的一个。可以通过从空团开始，逐个选择与当前团所有节点都相邻的候选节点加入来构建解；当没有可加入的候选节点时结束。",
    "fun_name": "select_next_vertex",
    "fun_args": ["current_clique", "candidate_vertices", "adjacency_matrix"],
    "fun_return": ["vertex_index"],
    "fun_notes": "'current_clique'是当前团中的节点索引数组（可能为空）。'candidate_vertices'是候选节点索引数组（与当前团全相邻的未选节点）。'adjacency_matrix'是无向图邻接矩阵（0/1）。返回下一个要加入团的节点索引；若无候选节点则返回None。所有数据均为Numpy数组。"
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
