# -*- coding: utf-8 -*-
# problems/kcenter/start_evo.py - k-Center CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/kcenter"
TRAIN_DATA = "train_data_kcenter.pkl"
TRAIN_SOLUTION = "train_solution_kcenter.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "k中心问题（k-Center）：给定一组节点和它们之间的距离，需要选出k个节点作为服务中心，使得所有节点到其最近中心的距离中的最大值（最大覆盖距离）最小。可以通过从第一个中心开始，逐个选择下一个中心来构建解。",
    "fun_name": "select_next_center",
    "fun_args": ["selected_centers", "candidate_nodes", "distance_matrix", "k"],
    "fun_return": ["center_index"],
    "fun_notes": "'selected_centers'是已选中心节点索引数组。'candidate_nodes'是候选节点索引数组（尚未被选为中心）。'distance_matrix'是节点间距离矩阵。'k'是需要选择的总中心数。返回下一个要选为中心节点的索引；若无法继续则返回None。所有数据均为Numpy数组。"
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
