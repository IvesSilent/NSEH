# -*- coding: utf-8 -*-
# generator.py

from core.prompt_template import prompt_template
from core.llm_interface import llm_interface
import re
import numpy as np
import importlib.util
import os
import time
import pickle

# 启发式生成器类
class  generator():
    def __init__(self,
                 api_key,base_url,llm_model,if_stream,
                 problem_path,train_data_name,train_solution_name,
                 problem,fun_name,fun_args,fun_return,fun_notes):

        self.problem_path = problem_path
        self.train_data_name = train_data_name
        self.train_solution_name = train_solution_name
        self.fun_name = fun_name

        self.interface = llm_interface(api_key, base_url, llm_model, if_stream)
        self.prompt_template = prompt_template(problem, fun_name, fun_args, fun_return, fun_notes)


    # 启发式提取函
    def get_heuristic(self,heuristic_string):
        # 提取大括号中的内容
        bracket_contents = re.findall(r'\{(.*?)\}', heuristic_string, re.DOTALL)
        # 提取代码块内容
        code_block = re.search(r'```python(.*?)```', heuristic_string, re.DOTALL)
        algorithm = code_block.group(1).strip() if code_block else ""

        # # 过滤 concept 中的【思想概念】标题
        # concept = re.sub(r'^【思想概念】\s*', '', bracket_contents[0].strip(), flags=re.MULTILINE)
        # # 过滤 feature 中的【策略关键词】标题
        # feature = re.sub(r'^【策略关键词】\s*', '', bracket_contents[1].strip(), flags=re.MULTILINE)

        # 构造heuristic字典
        heuristic = {
            'concept': bracket_contents[0].strip(),
            'feature': bracket_contents[1].strip(),
            # 'concept': concept,
            # 'feature': feature,
            'algorithm': algorithm,
            'objective': np.inf
        }
        # print(f"\n\n\n从self.get_heuristic()输出前，algorithm_str = \n{heuristic['algorithm']}")

        # print(f"构造启发式\n"
        #       f"\nconcept = {heuristic['concept']}"
        #       f"\nfeature = {heuristic['feature']}"
        #       f"\nalgorithm = {heuristic['algorithm']}"
        #       f"\nobjective = {heuristic['objective']}\n\n")

        return heuristic

    # 启发式适应度评估函
    def eval_heuristic(self, algorithm):

        eval_start_time = time.time()

        # 获取 heuristic_solve_dynamic 函数

        eval_module_path = os.path.join(self.problem_path, "train_eval")
        module_name = eval_module_path.replace("/", ".").replace("\\", ".")
        module = importlib.import_module(module_name)
        heuristic_solve_dynamic = getattr(module, "heuristic_solve_dynamic")

        # 数据调用部分迁移
        problem_path = os.path.join(os.path.dirname(__file__), '..', self.problem_path)
        train_data_path = os.path.join(problem_path, "datasets", self.train_data_name)
        train_solution_path = os.path.join(problem_path, "datasets", self.train_solution_name)

        try:
            # 尝试调用 heuristic_solve_dynamic
            objective = heuristic_solve_dynamic(train_data_path, train_solution_path, algorithm, self.fun_name)

        except Exception as e:
            # 如果出现异常，为 objective 赋异常值
            # print(f"Error occurred while running heuristic_solve_dynamic: {e}")
            objective = float('inf')  # 或者其他你定义的异常值

        # print(f"\n\n本次评估耗时:{time.time() - eval_start_time}s\n\n")

        return objective

    # 启发式生成函
    def heuristic_generator(self,heuristic_string):
        # 启发式提取
        heuristic = self.get_heuristic(heuristic_string)


        algorithm_str = heuristic['algorithm']

        # print(f"\n\n\n传入self.eval_heuristic()前，algorithm_str = \n{algorithm_str}")

        # 启发式评估
        objective = self.eval_heuristic(algorithm_str)

        heuristic['objective'] = objective

        return heuristic

    # 生成初始启发式
    def initial_heuristic(self):
        # 初始化的消息记录
        message_list = []

        # 用于生成初始启发式的单个提示词
        initial_prompt = self.prompt_template.prompt_initial_single()

        # 将initial_prompt加入消息记录
        message_list.append({"role": "user", "content": initial_prompt})

        heuristic_string = self.interface.send_message(message_list)
        heuristic = self.heuristic_generator(heuristic_string)

        return heuristic

    def evol_heuristic(self,strategy,parent_heuristics,memory):
        message_list = []

        # print(f"memory = {memory}")
        # breakpoint()
        positive_features = memory['positive_features']
        negative_features = memory['negative_features']

        evol_prompt = self.prompt_template.prompt_evolve(strategy, parent_heuristics,positive_features,negative_features)
        message_list.append({"role": "user", "content": evol_prompt[0]})
        response = self.interface.send_message(message_list)
        message_list.append({"role": "assistant", "content": response})
        message_list.append({"role": "user", "content": evol_prompt[1]})
        heuristic_string = self.interface.send_message(message_list)
        heuristic = self.heuristic_generator(heuristic_string)

        return heuristic


if __name__ == "__main__":

    # 防止joblib警告
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # 设置为你的核心数

    # 参数列表

    # 问题情景路径
    problem_path = "problems/tsp"
    train_data = "train_data_tsp.pkl"
    train_solution = "train_data_solution.pkl"

    # 问题及启发式函描述
    problem = ("TSP问题,即给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
               "可以通过从当前节点开始逐步选择下一个节点来解决此任务。")
    fun_name = "select_next_node"
    fun_args = ["current_node", "destination_node", "univisited_nodes", "distance_matrix"]
    fun_return = ["next_node"]
    fun_notes = ("'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix'是节点的距离矩阵。"
                 "所有数据均为Numpy数组。")

    # LLM配置
    api_key = "sk-YOUR_API_KEY_XXXXXX"  # 替换为你的api_key
    base_url = "https://api.deepseek.com/v1"
    llm_model = "deepseek-chat"

    if_stream = False
    ascend = True # 是否为升序，对于tsp问题 objective 较小的优先，因此是True

    # 进化常数
    population_capacity = 5
    num_mutation = 3
    num_hybridization = 3
    num_generation = 4
    num_reflection = 3

    generator = generator(api_key,base_url,llm_model,if_stream,
                 problem_path,train_data,train_solution,
                 problem,fun_name,fun_args,fun_return,fun_notes)



    # 初始化原始种群
    population = {'heuristics': [],
                    'memory': {
                        'positive_features': [],
                        'negative_features': []
                    }}

    strategies = ['MUTATION', 'HYBRIDIZATION', 'OPTIMIZATION']

    ##########################
    ### Phase_0 - 种群初始化 ###
    ##########################

    population_0 = population
    print("\n##########################\n### Phase_0 - 种群初始化 ###\n##########################\n")

    # print(f"开始生成初始化启发式")
    start_time = time.time()  # 开始计时
    new_heuristic = generator.initial_heuristic()
    population_0['heuristics'].append(new_heuristic)
    elapsed_time = time.time() - start_time
    print(
        f"初始启发式已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

    num_heuristic = len(population_0['heuristics'])

    while num_heuristic < population_capacity:

        start_time = time.time()  # 开始计时
        new_heuristic = generator.evol_heuristic(strategies[0], population_0['heuristics'], population_0['memory'])
        elapsed_time = time.time() - start_time
        print(
            f"启发式_{num_heuristic + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

        if new_heuristic['objective'] != np.inf:
            population_0['heuristics'].append(new_heuristic)
            num_heuristic += 1

        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_0['memory']['negative_features'].append(new_heuristic['feature'])

        # num_heuristic = len(population_0['heuristics'])

    print("初始化完成，对population_0进行排序")
    population_0['heuristics'].sort(key=lambda x: x['objective'], reverse=not ascend)
    print("排序完成\n\n")
    # for i in range(population_capacity-1):
    #
    #     # print(f"开始生成启发式_{i + 1}")
    #     start_time = time.time()  # 开始计时
    #
    #     new_heuristic = generator.evol_heuristic( strategies[0], population_0['heuristics'], population_0['memory'] )
    #     population_0['heuristics'].append(new_heuristic)
    #
    #     elapsed_time = time.time() - start_time
    #     print(f"启发式_{i + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")


    ########################
    ### Phase_1 - 种群进化 ###
    ########################

    print("\n########################\n### Phase_1 - 种群进化 ###\n########################\n")

    # 继承负面特征记忆，清空正面特征记忆
    population_1 = population_0

    # Phase_1.1 - Mutation 突变
    print(" - * Phase_1.1 - Mutation突变 *  - \n")

    for i in range(num_mutation):

        start_time = time.time()  # 开始计时
        new_heuristic = generator.evol_heuristic(strategies[0], population_0['heuristics'], population_1['memory'])
        elapsed_time = time.time() - start_time
        print(
            f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)

        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    # Phase_1.2 - Hybridization 杂交
    print(" - * Phase_1.2 - Hybridization 杂交 *  - \n")

    # 初始化进行杂交的启发式对 列表
    heuristic_list = []

    # 提取population_0['heuristics']中前num_hybridization个启发式
    selected_heuristics = population_0['heuristics'][:num_hybridization]

    # 两两组合
    for i in range(num_hybridization):
        for j in range(i + 1, num_hybridization):
            heuristic_pair = [selected_heuristics[i], selected_heuristics[j]]
            heuristic_list.append(heuristic_pair)

    list_len = len(heuristic_list)

    for i in range(list_len):
        start_time = time.time()  # 开始计时
        new_heuristic = generator.evol_heuristic(strategies[1], heuristic_list[i], population_1['memory'])
        elapsed_time = time.time() - start_time
        print(
            f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)

        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    # Phase_1.3 - Optimization 优化
    print(" - * Phase_1.3 - Optimization 优化 *  - \n")

    list_len = len(population_0['heuristics'])

    for i in range(list_len):
        start_time = time.time()  # 开始计时
        new_heuristic = generator.evol_heuristic(strategies[2], population_0['heuristics'][i], population_1['memory'])
        elapsed_time = time.time() - start_time
        print(
            f"启发式_{len(population_1['heuristics']) + 1} 已生成\n\t - feature = {new_heuristic['feature']}\n\t - objective = {new_heuristic['objective']}\n\t - time = {elapsed_time}\n")

        if new_heuristic['objective'] != np.inf:
            population_1['heuristics'].append(new_heuristic)

        else:
            print(f"该启发式不适用于本情形，弃用。\n")
            population_1['memory']['negative_features'].append(new_heuristic['feature'])

    ##########################
    ### Phase_2 - 筛选启发式 ###
    ##########################

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
