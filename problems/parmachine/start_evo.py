# -*- coding: utf-8 -*-
# problems/parmachine/start_evo.py - Parallel Machine CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/parmachine"
TRAIN_DATA = "train_data_parmachine.pkl"
TRAIN_SOLUTION = "train_solution_parmachine.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "并行机调度问题（P||Cmax）：给定n个独立作业和m台相同的并行机器，每个作业有加工时间，可以将每个作业分配给任意一台机器加工（每台机器同一时间只能加工一个作业），目标是最小化所有机器的最晚完工时间(makespan)。可以通过按某个顺序逐个将作业分配给一台机器来构建解。",
    "fun_name": "assign_job",
    "fun_args": ["job_id", "machine_loads", "processing_times", "num_machines"],
    "fun_return": ["machine_index"],
    "fun_notes": "'job_id'是当前要分配的作业索引。'machine_loads'是每台机器当前累计负载数组。'processing_times'是所有作业的加工时间数组。'num_machines'是机器数量。返回该作业要分配到的机器索引（0-based）。所有数据均为Numpy数组。"
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
