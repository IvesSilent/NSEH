# -*- coding: utf-8 -*-
# problems/partition/start_evo.py - Partition CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/partition"
TRAIN_DATA = "train_data_partition.pkl"
TRAIN_SOLUTION = "train_solution_partition.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "数划分问题（Number Partitioning）：给定一组数字，需要将它们分成两组（组A和组B），使得两组数字之和的差尽可能小（理想为0）。可以通过按顺序逐个决定每个数字放入哪一组来构建解。",
    "fun_name": "assign_number",
    "fun_args": ["number_id", "sum_a", "sum_b", "numbers"],
    "fun_return": ["group"],
    "fun_notes": "'number_id'是当前要分配的数字索引。'sum_a'和'sum_b'是两组当前的累计和（标量）。'numbers'是所有数字数组。返回0表示放入组A，返回1表示放入组B。所有数据均为Numpy数组。"
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
