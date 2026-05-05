# -*- coding: utf-8 -*-
# problems/knapsack/start_evo.py - 0/1 背包 CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/knapsack"
TRAIN_DATA = "train_data_knapsack.pkl"
TRAIN_SOLUTION = "train_solution_knapsack.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "0/1背包问题：给定一组物品，每个物品有重量和价值，在背包容量限制内选择物品使总价值最大。需要通过逐个物品决策来构建解，每个物品选择拿(1)或不拿(0)。",
    "fun_name": "select_item",
    "fun_args": ["current_index", "remaining_capacity", "weights", "values", "num_items"],
    "fun_return": ["take_item"],
    "fun_notes": "'current_index'是当前考虑的物品索引。'remaining_capacity'是背包剩余容量。'weights'和'values'是所有物品的重量和价值数组。'num_items'是物品总数。返回1表示拿该物品，0表示不拿。所有数据均为Numpy数组。"
}

ASCEND = True  # 差距越小越好

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
