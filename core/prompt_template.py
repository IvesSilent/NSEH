# -*- coding: utf-8 -*-
# prompt_template.py

import re
import numpy as np

from core.tag_memory import format_for_prompt, classify_tag


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

        # 启发式输出要求 — 新增 tags 格式
        self.output_requirement = (
            "你需要分别提供以下四个部分：\n"
            " - 该启发式的思想概念，用大括号包裹\n"
            " - 该启发式的策略标签，每个标签用方括号包裹，多个标签用+连接，用大括号包裹\n"
            "   例如：{ [贪婪搜索] + [随机抖动] + [最近邻] }\n"
            " - 该启发式的python代码，写在代码块里\n"
            "请按如下格式给出回复：\n"
            "{ 这里写思想概念 }\n"
            "{ [标签1] + [标签2] + [标签3] }\n"
            "```python\n这里写代码实现```\n"
        )

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
            # If feature is a string (legacy), keep display; if list of tags, join
            feat_display = parent_heuristics[i].get('feature', '')
            if isinstance(feat_display, list):
                feat_display = ' + '.join(feat_display)

            condition_prompt += (f"\n#### 启发式_{i + 1}\n"
                                 f"思想概念：{parent_heuristics[i]['concept']}\n"
                                 f"策略标签：{feat_display}\n"
                                 f"代码如下\n```python{parent_heuristics[i]['algorithm']}```\n")

        if positive_features or negative_features:
            condition_prompt += "\n### 研究经验"
            # 使用分层记忆格式化
            if positive_features:
                condition_prompt += "\n" + format_for_prompt(positive_features, "积极经验")
            if negative_features:
                condition_prompt += "\n" + format_for_prompt(negative_features, "消极经验")

        condition_prompt += "\n### 优化策略\n"

        if strategy == 'MUTATION':
            condition_prompt += self.strategy_MUT
        elif strategy == 'HYBRIDIZATION':
            condition_prompt += self.strategy_HYB
        else:
            condition_prompt += self.strategy_OPT

        # 将分析和生成合并为一个提示词，减少一次LLM调用
        result_prompt = self.analyze + "\n\n接下来，请直接完成这个新的启发式。\n"
        result_prompt += self.output_requirement
        result_prompt += f"注意，{self.fun_requirement}\n不要提供额外解释"

        # 一次性输出：先分析，后直接给出代码
        single_prompt = condition_prompt + "\n" + result_prompt

        return [condition_prompt, result_prompt, single_prompt]

    def altprompt_get(self):
        return self.fun_requirement, self.strategy_MUT, self.strategy_HYB, self.strategy_OPT, self.analyze

    def altprompt_set(self, fun_requirement, strategy_MUT, strategy_HYB, strategy_OPT, analyze):
        self.fun_requirement = fun_requirement
        self.strategy_MUT = strategy_MUT
        self.strategy_HYB = strategy_HYB
        self.strategy_OPT = strategy_OPT
        self.analyze = analyze


def parse_tags(tag_string):
    """
    从字符串中解析标签列表。
    支持格式: "[贪婪搜索] + [随机抖动]" 或 "贪婪搜索+随机抖动"
    返回: ["贪婪搜索", "随机抖动"]
    """
    if not tag_string or not tag_string.strip():
        return []

    # 尝试匹配 [tag] + [tag] 格式
    bracket_tags = re.findall(r'\[(.*?)\]', tag_string)
    if bracket_tags:
        return [t.strip() for t in bracket_tags if t.strip()]

    # 回退: 按 + 分割
    parts = re.split(r'\s*\+\s*', tag_string)
    return [p.strip() for p in parts if p.strip()]


def get_heuristic(heuristic_string):
    """从 LLM 回复中提取启发式字典"""
    bracket_contents = re.findall(r'\{(.*?)\}', heuristic_string, re.DOTALL)
    code_block = re.search(r'```python(.*?)```', heuristic_string, re.DOTALL)
    algorithm = code_block.group(1).strip() if code_block else ""

    concept = bracket_contents[0].strip() if len(bracket_contents) > 0 else ""

    # 解析 tags
    raw_tags = bracket_contents[1].strip() if len(bracket_contents) > 1 else ""
    tags = parse_tags(raw_tags)
    if not tags:
        tags = [raw_tags] if raw_tags else []

    heuristic = {
        'concept': concept,
        'feature': tags,  # feature 现在是 list of tag strings
        'algorithm': algorithm,
        'objective': np.inf
    }
    return heuristic


if __name__ == "__main__":
    strategies = ['MUTATION', 'HYBRIDIZATION', 'OPTIMIZATION']

    population_0 = {
        'heuristics': [],
        'memory': {
            'positive_features': [],
            'negative_features': []
        }
    }

    api_key = "sk-YOUR_API_KEY_XXXXXX"
    base_url = "https://api.deepseek.com/v1"
    llm_model = "deepseek-chat"
    if_stream = False
    message_list = []

    from core.llm_interface import llm_interface
    interface_example = llm_interface(api_key, base_url, llm_model, if_stream)

    problem = ("TSP问题,即给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
               "可以通过从当前节点开始逐步选择下一个节点来解决此任务。")
    fun_name = "select_next_node"
    fun_args = ["current_node", "destination_node", "univisited_nodes", "distance_matrix"]
    fun_return = ["next_node"]
    fun_notes = ("'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix'是节点的距离矩阵。"
                 "所有数据均为Numpy数组。")

    tmpl = prompt_template(problem, fun_name, fun_args, fun_return, fun_notes)

    # 初始化
    message_list_0 = list(message_list)
    initial_prompt = tmpl.prompt_initial_single()
    message_list_0.append({"role": "user", "content": initial_prompt})
    heuristic_string = interface_example.send_message(message_list_0)
    population_0['heuristics'].append(get_heuristic(heuristic_string))

    # 进化测试
    population_1 = dict(population_0)
    k1 = 5
    for i in range(k1):
        message_list_1 = list(message_list)
        evol_prompt = tmpl.prompt_evolve(strategies[0], population_1['heuristics'],
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
        population_1['heuristics'].append(get_heuristic(heuristic_string))

    print(f"\n\n\npopulation_1 = {population_1}")
