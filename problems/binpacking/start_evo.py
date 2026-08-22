# -*- coding: utf-8 -*-
# problems/binpacking/start_evo.py - Bin Packing CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/binpacking"
TRAIN_DATA = "train_data_binpacking.pkl"
TRAIN_SOLUTION = "train_solution_binpacking.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "一维装箱问题（Bin Packing）：给定一组物品，每个物品有大小，以及无限多个容量相同的箱子，目标是用最少的箱子装下所有物品。可以通过按顺序逐个决定每个物品放入哪个已开箱子来构建解；如果所有已开箱子都放不下，则返回-1表示开一个新箱子。",
    "fun_name": "place_item",
    "fun_args": ["item_size", "remaining_capacities", "item_sizes", "num_items"],
    "fun_return": ["bin_index"],
    "fun_notes": "'item_size'是当前要放置的物品大小（标量）。'remaining_capacities'是已开箱子的剩余容量数组。'item_sizes'是所有物品大小数组。'num_items'是物品总数。返回要放入的箱子索引（0-based），若所有已开箱子都放不下则返回-1表示开新箱。所有数据均为Numpy数组。"
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
