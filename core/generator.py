# -*- coding: utf-8 -*-
# generator.py

from core.prompt_template import prompt_template, get_heuristic
from core.llm_interface import llm_interface
import re
import numpy as np
import importlib.util
import os
import time
import pickle

class generator():
    def __init__(self,
                 api_key, base_url, llm_model, if_stream,
                 problem_path, train_data_name, train_solution_name,
                 problem, fun_name, fun_args, fun_return, fun_notes):

        self.problem_path = problem_path
        self.train_data_name = train_data_name
        self.train_solution_name = train_solution_name
        self.fun_name = fun_name

        self.interface = llm_interface(api_key, base_url, llm_model, if_stream)
        self.prompt_template = prompt_template(problem, fun_name, fun_args, fun_return, fun_notes)

    def get_heuristic(self, heuristic_string):
        """使用 prompt_template 中的标准化解析"""
        return get_heuristic(heuristic_string)

    def eval_heuristic(self, algorithm):
        eval_start_time = time.time()

        eval_module_path = os.path.join(self.problem_path, "train_eval")
        module_name = eval_module_path.replace("/", ".").replace("\\", ".")
        module = importlib.import_module(module_name)
        heuristic_solve_dynamic = getattr(module, "heuristic_solve_dynamic")

        problem_path = os.path.join(os.path.dirname(__file__), '..', self.problem_path)
        train_data_path = os.path.join(problem_path, "datasets", self.train_data_name)
        train_solution_path = os.path.join(problem_path, "datasets", self.train_solution_name)

        try:
            objective = heuristic_solve_dynamic(train_data_path, train_solution_path, algorithm, self.fun_name)
        except Exception as e:
            objective = float('inf')

        return objective

    def heuristic_generator(self, heuristic_string):
        heuristic = self.get_heuristic(heuristic_string)
        algorithm_str = heuristic['algorithm']
        objective = self.eval_heuristic(algorithm_str)
        heuristic['objective'] = objective
        return heuristic

    def initial_heuristic(self):
        message_list = []
        initial_prompt = self.prompt_template.prompt_initial_single()
        message_list.append({"role": "user", "content": initial_prompt})
        heuristic_string = self.interface.send_message(message_list)
        heuristic = self.heuristic_generator(heuristic_string)
        return heuristic

    def evol_heuristic(self, strategy, parent_heuristics, memory):
        message_list = []
        positive_features = memory.get('positive_features', [])
        negative_features = memory.get('negative_features', [])

        evol_prompt = self.prompt_template.prompt_evolve(
            strategy, parent_heuristics, positive_features, negative_features
        )
        message_list.append({"role": "user", "content": evol_prompt[0]})
        response = self.interface.send_message(message_list)
        message_list.append({"role": "assistant", "content": response})
        message_list.append({"role": "user", "content": evol_prompt[1]})
        heuristic_string = self.interface.send_message(message_list)
        heuristic = self.heuristic_generator(heuristic_string)
        return heuristic


if __name__ == "__main__":
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"

    problem_path = "problems/tsp"
    train_data = "train_data_tsp.pkl"
    train_solution = "train_data_solution.pkl"

    problem = ("TSP问题,即给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
               "可以通过从当前节点开始逐步选择下一个节点来解决此任务。")
    fun_name = "select_next_node"
    fun_args = ["current_node", "destination_node", "univisited_nodes", "distance_matrix"]
    fun_return = ["next_node"]
    fun_notes = ("'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix'是节点的距离矩阵。"
                 "所有数据均为Numpy数组。")

    api_key = "sk-YOUR_API_KEY_XXXXXX"
    base_url = "https://api.deepseek.com/v1"
    llm_model = "deepseek-chat"
    if_stream = False
    ascend = True
    population_capacity = 5
    num_mutation = 3
    num_hybridization = 3
    num_generation = 4
    num_reflection = 3

    gen = generator(api_key, base_url, llm_model, if_stream,
                    problem_path, train_data, train_solution,
                    problem, fun_name, fun_args, fun_return, fun_notes)

    population = {
        'heuristics': [],
        'memory': {
            'positive_features': [],
            'negative_features': []
        }
    }

    strategies = ['MUTATION', 'HYBRIDIZATION', 'OPTIMIZATION']

    # Phase_0
    print("\n##########################\n### Phase_0 - 种群初始化 ###\n##########################\n")
    population_0 = dict(population)
    start_time = time.time()
    new_heuristic = gen.initial_heuristic()
    population_0['heuristics'].append(new_heuristic)
    elapsed_time = time.time() - start_time
    print(f"初始启发式已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

    num_heuristic = len(population_0['heuristics'])
    while num_heuristic < population_capacity:
        start_time = time.time()
        new_heuristic = gen.evol_heuristic(strategies[0], population_0['heuristics'], population_0['memory'])
        elapsed_time = time.time() - start_time
        print(f"启发式_{num_heuristic + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")
        if new_heuristic['objective'] != np.inf:
            population_0['heuristics'].append(new_heuristic)
            num_heuristic += 1
        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_0['memory']['negative_features'].append(new_heuristic['feature'])

    print("初始化完成，对population_0进行排序")
    population_0['heuristics'].sort(key=lambda x: x['objective'], reverse=not ascend)
    print("排序完成\n\n")

    # Phase_1
    print("\n########################\n### Phase_1 - 种群进化 ###\n########################\n")
    population_1 = dict(population_0)

    print(" - * Phase_1.1 - Mutation突变 *  - \n")
    for i in range(num_mutation):
        start_time = time.time()
        new_heuristic = gen.evol_heuristic(strategies[0], population_1['heuristics'], population_1['memory'])
        elapsed_time = time.time() - start_time
        print(f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")
        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)
        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    # 杂交阶段
    print(" - * Phase_1.2 - Hybridization 杂交 *  - \n")
    heuristic_list = []
    selected_heuristics = population_1['heuristics'][:num_hybridization]
    for i in range(num_hybridization):
        for j in range(i + 1, num_hybridization):
            heuristic_list.append([selected_heuristics[i], selected_heuristics[j]])

    for pair in heuristic_list:
        start_time = time.time()
        new_heuristic = gen.evol_heuristic(strategies[1], pair, population_1['memory'])
        elapsed_time = time.time() - start_time
        print(f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")
        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)
        else:
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    # 优化阶段
    print(" - * Phase_1.3 - Optimization 优化 *  - \n")
    for h in population_1['heuristics'][:population_capacity]:
        start_time = time.time()
        new_heuristic = gen.evol_heuristic(strategies[2], h, population_1['memory'])
        elapsed_time = time.time() - start_time
        print(f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")
        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)
        else:
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    # Phase_2 筛选
    print("\n##########################\n### Phase_2 - 筛选启发式 ###\n##########################\n")
    survivor = population_1['heuristics'][:population_capacity]
    good_list = population_1['heuristics'][:num_reflection]
    bad_list = population_1['heuristics'][-num_reflection:]

    for heuristic in good_list:
        population_1['memory']['positive_features'].append(heuristic['feature'])
    for heuristic in bad_list:
        population_1['memory']['negative_features'].append(heuristic['feature'])

    population_1['heuristics'] = survivor
    print(f"单次迭代进化已完成，population_1如下\n{population_1}")
