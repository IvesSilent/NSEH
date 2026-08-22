# -*- coding: utf-8 -*-
# problems/setcover/start_evo.py - Set Cover CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/setcover"
TRAIN_DATA = "train_data_setcover.pkl"
TRAIN_SOLUTION = "train_solution_setcover.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "集合覆盖问题（Set Cover）：给定一个包含所有元素的全集和若干集合，每个集合覆盖其中一部分元素并有一个选取成本，目标是用最小的总成本选出一些集合，使得所有元素都被至少一个所选集合覆盖。可以通过逐个选择集合来构建解，直到所有元素都被覆盖。",
    "fun_name": "select_next_set",
    "fun_args": ["uncovered_elements", "set_membership", "set_costs"],
    "fun_return": ["set_index"],
    "fun_notes": "'uncovered_elements'是布尔数组，True表示该元素尚未被覆盖。'set_membership'是(n_sets x n_elements)的0/1矩阵，set_membership[s,e]=1表示集合s包含元素e。'set_costs'是每个集合的选取成本数组。返回下一个要选取的集合索引（0-based），若无法继续则返回None。所有数据均为Numpy数组。"
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
