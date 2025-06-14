# -*- coding: utf-8 -*-
# prompt_template.py
from core.llm_interface import llm_interface
import re
import numpy as np


# prompt_template 提示词模版生成
class prompt_template():
    def __init__(self, problem, fun_name, fun_args, fun_return, fun_notes):
        self.problem = problem
        fun_requirement = (f"用Python实现一个名为{fun_name}的函数。\n"
                           f"该函数应接受{len(fun_args)}个输入：")
        amount_args = len(fun_args)
        for arg in fun_args:
            fun_requirement += f"'{arg}'"
            amount_args -= 1
            if amount_args >= 1:
                fun_requirement += ", "

        fun_requirement += f"；\n函数应返回{len(fun_return)}个输出："
        amount_return = len(fun_return)
        for val in fun_return:
            fun_requirement += f"'{val}'"
            amount_return -= 1
            if amount_args >= 1:
                fun_requirement += ", "
        fun_requirement += f"。\n{fun_notes}\n"

        # 启发式输出要求
        output_requirement = ("你需要分别提供以下三个部分：\n"
                              " - 该启发式的思想概念，用大括号包裹\n"
                              " - 该启发式的策略关键词，用+连接，用大括号包裹\n"
                              " - 该启发式的python代码，写在代码块里\n"
                              "请按如下格式给出回复：\n"
                              "{ 这里写思想概念 }\n{ 这里写策略关键词 }\n```python\n这里写代码实现```\n")

        self.output_requirement = output_requirement

        self.fun_requirement = fun_requirement
        # 进化策略
        self.strategy_MUT = "请你设计一个与现有的这些启发式算法尽可能不同的新启发式算法。\n"
        self.strategy_HYB = "请你综合现有的这些启发式算法的关键思想，设计一个新的启发式算法。\n"
        self.strategy_OPT = ("请你对现有的这个启发式进行优化，"
                             "使用包括但不限于调整其参数值、对其进行复杂度层面的优化或精简其结构等方式，得到一个新的启发式算法。\n")

        # 分析提示词
        self.analyze = ("\n请你梳理所有信息，进行一个长度在200字内的分析。\n"
                        "你可以将构思新启发式需要纳入考量的条件列举出来，并分析该如何进行设计构思或改进，以得到新的启发式。\n"
                        "不要进行任何代码实现，只给出修改的目标，并构思如何设计新启发式。")

    def prompt_initial_single(self):
        prompt = f"设计一个解决以下问题的启发式算法：\n{self.problem}\n"
        prompt += self.output_requirement
        prompt += f"注意：{self.fun_requirement}\n不要提供额外解释。"
        return prompt

    def prompt_evolve(self, strategy, parent_heuristics, positive_features, negative_features):
        prompt_group = []
        condition_prompt = f"你需要协助我设计一个用于解决如下问题的启发式：{self.problem}\n"

        condition_prompt += f"\n### 已有启发式\n我这里有如下{len(parent_heuristics)}个启发式：\n"
        for i in range(len(parent_heuristics)):
            condition_prompt += (f"\n#### 启发式_{i + 1}\n"
                                 f"思想概念：{parent_heuristics[i]['concept']}\n"
                                 f"策略关键词：{parent_heuristics[i]['feature']}\n"
                                 f"代码如下\n```python{parent_heuristics[i]['algorithm']}```\n")

        if positive_features or negative_features:
            condition_prompt += "\n### 研究经验"
            if positive_features:
                condition_prompt += "在我之前的研究过程中，有以下思想特征组合的启发式效果较好：\n"
                for feature in positive_features:
                    condition_prompt += f" - {feature}\n"
            if negative_features:
                condition_prompt += "在我之前的研究过程中，有以下思想特征组合的启发式效果较差：\n"
                for feature in positive_features:
                    condition_prompt += f" - {feature}\n"

        condition_prompt += "\n### 优化策略\n"

        if strategy == 'MUTATION':  # 突变策略
            condition_prompt += self.strategy_MUT
        elif strategy == 'HYBRIDIZATION':  # 杂交策略
            condition_prompt += self.strategy_HYB
        else:  # 优化策略
            condition_prompt += self.strategy_OPT

        condition_prompt += self.analyze

        result_prompt = f"接下来，你需要根据你上述思考完成这个新的启发式。\n"
        result_prompt += self.output_requirement
        result_prompt += f"注意，{self.fun_requirement}\n不要提供额外解释"

        return [condition_prompt, result_prompt]

    def altprompt_get(self):
        # 读取可自定义的提示词模版
        return self.fun_requirement, self.strategy_MUT, self.strategy_HYB, self.strategy_OPT, self.analyze

    def altprompt_set(self, fun_requirement, strategy_MUT, strategy_HYB, strategy_OPT, analyze):
        # 写入可自定义的提示词模版
        self.fun_requirement = fun_requirement
        self.strategy_MUT = strategy_MUT
        self.strategy_HYB = strategy_HYB
        self.strategy_OPT = strategy_OPT
        self.analyze = analyze


# 启发式提取函
def get_heuristic(heuristic_string):
    # 提取大括号中的内容
    bracket_contents = re.findall(r'\{(.*?)\}', heuristic_string, re.DOTALL)
    # 提取代码块内容
    code_block = re.search(r'```python(.*?)```', heuristic_string, re.DOTALL)
    algorithm = code_block.group(1).strip() if code_block else ""
    # 构造heuristic字典
    heuristic = {
        'concept': bracket_contents[0].strip(),
        'feature': bracket_contents[1].strip(),
        'algorithm': algorithm,
        'objective': np.inf
    }
    return heuristic


if __name__ == "__main__":

    # 优化策略
    strategies = ['MUTATION', 'HYBRIDIZATION', 'OPTIMIZATION']

    # 种群
    population_0 = {'heuristics': [],
                    'memory': {
                        'positive_features': [],
                        'negative_features': []
                    }}

    # print(f"初始化prompt:\n{initial_prompt}")

    # 设置api_key和base_url
    # api_key = "YOUR_api_key" # 替换为你的api_key

    api_key = "sk-adc490f6203a4c6ab9ae9faf985897c2"  # 替换为你的api_key
    base_url = "https://api.deepseek.com/v1"
    llm_model = "deepseek-chat"
    # llm_model = "deepseek-reasoner"

    if_stream = False
    message_list = []
    interface_example = llm_interface(api_key, base_url, llm_model, if_stream)

    # 初始化问题及启发式条件
    problem = ("TSP问题,即给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
               "可以通过从当前节点开始逐步选择下一个节点来解决此任务。")
    fun_name = "select_next_node"
    fun_args = ["current_node", "destination_node", "univisited_nodes", "distance_matrix"]
    fun_return = ["next_node"]
    fun_notes = ("'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix'是节点的距离矩阵。"
                 "所有数据均为Numpy数组。")

    # 初始化prompt模版
    prompt_template = prompt_template(problem, fun_name, fun_args, fun_return, fun_notes)

    #############
    ### 初始化 ###
    #############

    # 初始化的消息记录
    message_list_0 = message_list

    # 用于生成初始启发式的单个提示词
    initial_prompt = prompt_template.prompt_initial_single()

    # 将initial_prompt加入消息记录
    message_list_0.append({"role": "user", "content": initial_prompt})

    # 得到初始启发式的字符串回复
    heuristic_string = interface_example.send_message(message_list_0)

    # 将初始启发式加入种群
    population_0['heuristics'].append(get_heuristic(heuristic_string))

    ###############
    ### 进化策略 ####
    ###############
    population_1 = population_0
    # 启发式进化的信息记录
    message_list_1 = message_list

    # # 用于进化的提示词组
    # evol_prompt = prompt_template.prompt_evolve(strategies[0],population_0['heuristics'],
    #                                               population_0['memory']['positive_features'],
    #                                               population_0['memory']['negative_features'])
    #
    # message_list_1.append({"role": "user", "content": evol_prompt[0]})
    #
    # print(f"\nUser：\n{evol_prompt[0]}")
    #
    # response = interface_example.send_message(message_list_1)
    # print(f"\nAssistant：\n{response}")
    #
    # message_list_1.append({"role": "assistant", "content": response})
    # message_list_1.append({"role": "user", "content": evol_prompt[1]})
    #
    # print(f"\nUser：\n{evol_prompt[1]}")
    #
    # heuristic_string = interface_example.send_message(message_list_1)
    # print(f"\nAssistant：\n{heuristic_string}")
    #
    # # 将初始启发式加入种群
    # population_1['heuristics'].append(get_heuristic(heuristic_string))

    k1 = 5  # 突变常数，重复5次
    for i in range(k1):
        # 启发式进化的信息记录
        message_list_1 = message_list

        # 用于进化的提示词组
        evol_prompt = prompt_template.prompt_evolve(strategies[0], population_1['heuristics'],
                                                    population_1['memory']['positive_features'],
                                                    population_1['memory']['negative_features'])

        message_list_1.append({"role": "user", "content": evol_prompt[0]})

        print(f"\nUser：\n{evol_prompt[0]}")
        print("------------------------------------------------------------------------------------------")

        response = interface_example.send_message(message_list_1)
        print(f"\nAssistant：\n{response}")
        print("------------------------------------------------------------------------------------------")

        message_list_1.append({"role": "assistant", "content": response})
        message_list_1.append({"role": "user", "content": evol_prompt[1]})

        print(f"\nUser：\n{evol_prompt[1]}")
        print("------------------------------------------------------------------------------------------")

        heuristic_string = interface_example.send_message(message_list_1)
        print(f"\nAssistant：\n{heuristic_string}")
        print("------------------------------------------------------------------------------------------")

        # 将初始启发式加入种群
        population_1['heuristics'].append(get_heuristic(heuristic_string))

    print(f"\n\n\npopulation_1 = {population_1}")
