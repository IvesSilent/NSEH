# -*- coding: utf-8 -*-
# problems/pfsp/start_evo.py - PFSP CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/pfsp"
TRAIN_DATA = "train_data_pfsp.pkl"
TRAIN_SOLUTION = "train_solution_pfsp.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "PFSP（置换流水车间调度问题）：给定n个作业和m台机器，每个作业需按相同顺序在所有机器上加工，目标是最小化最大完工时间(makespan)。可以通过逐个选择未调度的作业来构建调度序列。",
    "fun_name": "select_next_job",
    "fun_args": ["unscheduled_jobs", "current_schedule", "processing_times", "num_machines"],
    "fun_return": ["next_job"],
    "fun_notes": "'unscheduled_jobs'是未调度作业的索引数组。'current_schedule'是当前已调度的作业序列列表。'processing_times'是(n_jobs x num_machines)的加工时间矩阵。'num_machines'是机器数。返回要调度的下一个作业的索引。所有数据均为Numpy数组。"
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
