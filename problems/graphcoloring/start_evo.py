# -*- coding: utf-8 -*-
# problems/graphcoloring/start_evo.py - Graph Coloring CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/graphcoloring"
TRAIN_DATA = "train_data_graphcoloring.pkl"
TRAIN_SOLUTION = "train_solution_graphcoloring.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "图着色问题（Graph Coloring）：给定一个无向图，需要为每个节点分配一种颜色，使得任意相邻（有边相连）的两个节点颜色不同，目标是最小化使用的颜色总数。可以通过按顺序逐个为节点选择颜色来构建解；如果已有颜色都与邻居冲突，可以启用一种新颜色。",
    "fun_name": "choose_color",
    "fun_args": ["node_id", "adjacency_matrix", "current_colors", "num_colors_used"],
    "fun_return": ["color"],
    "fun_notes": "'node_id'是当前需要着色的节点索引。'adjacency_matrix'是无向图邻接矩阵（0/1）。'current_colors'是当前部分着色数组（-1=未着色，>=0=颜色编号）。'num_colors_used'是当前已使用的颜色种类数。返回该节点应使用的颜色编号（0到num_colors_used均可，num_colors_used表示开新颜色）。所有数据均为Numpy数组。"
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
