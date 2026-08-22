# -*- coding: utf-8 -*-
# problems/smtwt/start_evo.py - SMTWT CLI 启动脚本

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.evolution import EvolutionFramework
from core.generator import generator
import os

PROBLEM_PATH = "problems/smtwt"
TRAIN_DATA = "train_data_smtwt.pkl"
TRAIN_SOLUTION = "train_solution_smtwt.pkl"

API_KEY = "***"
BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-v4-flash"

POPULATION_CAPACITY = 7
NUM_GENERATIONS = 5
NUM_MUTATION = 3
NUM_HYBRIDIZATION = 3
NUM_REFLECTION = 3

FUNCTION_CONFIG = {
    "problem": "单机加权延误调度问题（1||ΣwT）：给定一批作业在一台机器上加工，每个作业有加工时间、截止日期和权重，机器一次只能加工一个作业，目标是最小化所有作业的加权总延误（每个作业延误 = 权重 × max(0, 完工时间 - 截止日期)）。可以通过从当前时刻开始逐个选择下一个要加工的作业来构建调度序列。",
    "fun_name": "select_next_job",
    "fun_args": ["unscheduled_jobs", "current_time", "processing_times", "due_dates", "weights"],
    "fun_return": ["next_job"],
    "fun_notes": "'unscheduled_jobs'是尚未加工的作业索引数组。'current_time'是当前时刻（标量）。'processing_times'是各作业加工时间数组。'due_dates'是各作业截止日期数组。'weights'是各作业权重数组。返回下一个要加工的作业索引。所有数据均为Numpy数组。"
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
