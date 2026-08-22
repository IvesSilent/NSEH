# -*- coding: utf-8 -*-
# problems/jsp/start_evo.py - JSP CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/jsp"
TRAIN_DATA = "train_data_jsp.pkl"
TRAIN_SOLUTION = "train_solution_jsp.pkl"

API_KEY = "sk-YOUR_API_KEY_XXXXXX"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "作业车间调度问题（Job Shop Scheduling）：给定n个作业和m台机器，每个作业由一串工序组成，各工序需按指定顺序在指定机器上加工，目标是最小化所有作业完成的最大完工时间(makespan)。可以通过每次选择一个尚未完成的作业推进其下一道工序来构建调度。",
    "fun_name": "select_next_job",
    "fun_args": ["available_operations", "job_progress", "operation_times", "machine_ready_times", "machine_of_op"],
    "fun_return": ["next_job"],
    "fun_notes": "'available_operations'是可推进下一工序的作业索引数组（未完成作业）。'job_progress'是每个作业已完成的工序数数组。'operation_times'是(n_jobs x n_machines)加工时间矩阵，第k列是该作业第k道工序的时间。'machine_ready_times'是每台机器的最早空闲时间。'machine_of_op'是(n_jobs x n_machines)机器顺序矩阵，第k列是该作业第k道工序使用的机器。返回要推进的作业索引。所有数据均为Numpy数组。"
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
