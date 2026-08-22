# -*- coding: utf-8 -*-
# prompt_template.py

import re
import numpy as np

from core.tag_memory import format_for_prompt, classify_tag


class prompt_template():
    def __init__(self, problem, fun_name, fun_args, fun_return, fun_notes, lang='zh'):
        self.problem = problem
        self.lang = lang if lang in ('zh', 'en') else 'zh'

        is_en = self.lang == 'en'
        if is_en:
            req_intro = (f"Implement a Python function named {fun_name}.\n"
                         f"The function should accept {len(fun_args)} input(s): ")
            req_join = ", "
            req_out = f"The function should return {len(fun_return)} output(s): "
            req_tail = f".\n{fun_notes}\n"
        else:
            req_intro = (f"用Python实现一个名为{fun_name}的函数。\n"
                         f"该函数应接受{len(fun_args)}个输入：")
            req_join = ", "
            req_out = f"；\n函数应返回{len(fun_return)}个输出："
            req_tail = f"。\n{fun_notes}\n"

        fun_requirement = req_intro
        amount_args = len(fun_args)
        for arg in fun_args:
            fun_requirement += f"'{arg}'"
            amount_args -= 1
            if amount_args >= 1:
                fun_requirement += req_join
        fun_requirement += req_out
        amount_return = len(fun_return)
        for val in fun_return:
            fun_requirement += f"'{val}'"
            amount_return -= 1
            if amount_return >= 1:
                fun_requirement += req_join
        fun_requirement += req_tail

        # 启发式输出要求 — 新增 tags 格式
        if is_en:
            self.output_requirement = (
                "You need to provide the following parts:\n"
                " - The conceptual idea of the heuristic, wrapped in curly braces\n"
                " - The strategy tags of the heuristic, each tag wrapped in square brackets, joined by +, all wrapped in curly braces\n"
                "   e.g.: { [Greedy Search] + [Random Perturbation] + [Nearest Neighbor] }\n"
                " - The Python code of the heuristic, written in a code block\n"
                "Please reply in the following format:\n"
                "{ write the conceptual idea here }\n"
                "{ [Tag1] + [Tag2] + [Tag3] }\n"
                "```python\nwrite the code here```\n"
            )
        else:
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
        if is_en:
            self.strategy_MUT = "Design a new heuristic algorithm that is as different as possible from the existing heuristic algorithms.\n"
            self.strategy_HYB = "Synthesize the key ideas of the existing heuristic algorithms and design a new heuristic algorithm.\n"
            self.strategy_OPT = ("Optimize the existing heuristic, using methods including but not limited to "
                                 "tuning its parameter values, optimizing its time/space complexity, or simplifying "
                                 "its structure, to obtain a new heuristic algorithm.\n")
            self.analyze = ("\nPlease review all the information and provide an analysis within 200 characters.\n"
                            "You may list the conditions that need to be considered when designing a new heuristic "
                            "and analyze how to design or improve it, so as to obtain a new heuristic.\n"
                            "Do not implement any code. Only give the improvement goals and describe how to design the new heuristic.")
        else:
            self.strategy_MUT = "请你设计一个与现有的这些启发式算法尽可能不同的新启发式算法。\n"
            self.strategy_HYB = "请你综合现有的这些启发式算法的关键思想，设计一个新的启发式算法。\n"
            self.strategy_OPT = ("请你对现有的这个启发式进行优化，"
                                 "使用包括但不限于调整其参数值、对其进行复杂度层面的优化或精简其结构等方式，得到一个新的启发式算法。\n")
            self.analyze = ("\n请你梳理所有信息，进行一个长度在200字内的分析。\n"
                            "你可以将构思新启发式需要纳入考量的条件列举出来，并分析该如何进行设计构思或改进，以得到新的启发式。\n"
                            "不要进行任何代码实现，只给出修改的目标，并构思如何设计新启发式。")

    def prompt_initial_single(self):
        if self.lang == 'en':
            prompt = f"Design a heuristic algorithm to solve the following problem:\n{self.problem}\n"
            prompt += self.output_requirement
            prompt += f"Note: {self.fun_requirement}\nDo not provide extra explanations."
        else:
            prompt = f"设计一个解决以下问题的启发式算法：\n{self.problem}\n"
            prompt += self.output_requirement
            prompt += f"注意：{self.fun_requirement}\n不要提供额外解释。"
        return prompt

    def prompt_evolve(self, strategy, parent_heuristics, positive_features, negative_features):
        is_en = self.lang == 'en'
        prompt_group = []
        if is_en:
            condition_prompt = f"You are helping me design a heuristic to solve the following problem: {self.problem}\n"
            condition_prompt += f"\n### Existing Heuristics\nI currently have the following {len(parent_heuristics)} heuristics:\n"
        else:
            condition_prompt = f"你需要协助我设计一个用于解决如下问题的启发式：{self.problem}\n"
            condition_prompt += f"\n### 已有启发式\n我这里有如下{len(parent_heuristics)}个启发式：\n"

        for i in range(len(parent_heuristics)):
            # If feature is a string (legacy), keep display; if list of tags, join
            feat_display = parent_heuristics[i].get('feature', '')
            if isinstance(feat_display, list):
                feat_display = ' + '.join(feat_display)

            if is_en:
                condition_prompt += (f"\n#### Heuristic_{i + 1}\n"
                                     f"Concept: {parent_heuristics[i]['concept']}\n"
                                     f"Strategy tags: {feat_display}\n"
                                     f"Code:\n```python{parent_heuristics[i]['algorithm']}```\n")
            else:
                condition_prompt += (f"\n#### 启发式_{i + 1}\n"
                                     f"思想概念：{parent_heuristics[i]['concept']}\n"
                                     f"策略标签：{feat_display}\n"
                                     f"代码如下\n```python{parent_heuristics[i]['algorithm']}```\n")

        if positive_features or negative_features:
            if is_en:
                condition_prompt += "\n### Research Experience"
                if positive_features:
                    condition_prompt += "\n" + format_for_prompt(positive_features, "Positive Experience", lang=self.lang)
                if negative_features:
                    condition_prompt += "\n" + format_for_prompt(negative_features, "Negative Experience", lang=self.lang)
            else:
                condition_prompt += "\n### 研究经验"
                # 使用分层记忆格式化
                if positive_features:
                    condition_prompt += "\n" + format_for_prompt(positive_features, "积极经验", lang=self.lang)
                if negative_features:
                    condition_prompt += "\n" + format_for_prompt(negative_features, "消极经验", lang=self.lang)

        if is_en:
            condition_prompt += "\n### Optimization Strategy\n"
        else:
            condition_prompt += "\n### 优化策略\n"

        if strategy == 'MUTATION':
            condition_prompt += self.strategy_MUT
        elif strategy == 'HYBRIDIZATION':
            condition_prompt += self.strategy_HYB
        else:
            condition_prompt += self.strategy_OPT

        # 将分析和生成合并为一个提示词，减少一次LLM调用
        if is_en:
            result_prompt = self.analyze + "\n\nNext, please directly complete this new heuristic.\n"
            result_prompt += self.output_requirement
            result_prompt += f"Note: {self.fun_requirement}\nDo not provide extra explanations"
        else:
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
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # 再回退: 按顿号/逗号分割（中英文标签行，如 "随机化、最近邻、扰动重启"）
    parts = re.split(r'[、，,;；]', tag_string)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    return [tag_string.strip()] if tag_string.strip() else []


# ════════════════════════════════════════════════════════
#  特征提取自检与鲁棒回退
#
#  LLM 输出格式并不总是规范的 "{概念} {[标签1] + [标签2]}"，常见异常形态：
#    1) 特征块花括号未闭合（如 "{ [A] + [B]" 缺右花括号）
#    2) 特征块内嵌在概念块内（概念文字后直接跟 { [A] + [B] }）
#    3) 标签未用方括号包裹，或使用 "特征：xxx" 标签行
#    4) 标签与概念混排，或被代码块中的 [i] 索引干扰
#
#  本模块作为 get_heuristic 的自检环节：当标准解析得到的特征为空时，
#  逐层尝试更鲁棒的提取（L1 花括号块 → L2 全文方括号 → L3 标签行
#  → L4 概念短语模糊兜底），保证特征非空、可被记忆系统使用。
# ════════════════════════════════════════════════════════

_BRACKET_TAG_RE = re.compile(r'\[([^\[\]\n]+)\]')
_BRACE_BLOCK_RE = re.compile(r'\{([^{}]*)\}', re.DOTALL)
_CODE_FENCE_RE = re.compile(r'```[a-zA-Z]*\s*(.*?)```', re.DOTALL)
_FEATURE_LABEL_RE = re.compile(
    r'(?:特征|策略标签|标签|features?|strategy\s*tags?|tags?)\s*[:：]\s*([^\n]+)',
    re.IGNORECASE)

# 模糊兜底时的过滤词（避免把连接词/套话当特征）
_FEATURE_STOPWORDS = {
    '该启发式', '基于', '通过', '对于', '一个', '一种', '以及', '同时', '因此',
    '其中', '从而', '实现', '得到', '进行', '采用', '不同于', '现有', '设计',
    '并且', '或者', '考虑', '使得', '可以', '需要', '希望', '能够', '具有',
    'the', 'this', 'that', 'with', 'based', 'using', 'from', 'into', 'such',
    'than', 'more', 'and', 'for', 'are', 'was', 'were', 'will', 'have', 'has'
}

# 动词/介词开头的句子片段前缀（L4 兜底时排除，避免把整句当特征）
_FEATURE_VERB_PREFIXES = (
    '基于', '通过', '采用', '利用', '借助', '结合', '针对', '对于', '为了',
    '使得', '能够', '可以', '需要', '优先', '避免', '引入', '构建', '计算',
    '比较', '选择', '评估', '衡量', '考虑', '从', '在', '将', '把', '以',
    '该方法', '本启发式', '该启发式', '此方法', '这种', '这种策略'
)


def _strip_code_fences(text):
    """移除代码块，避免代码中的 [i] 索引、列表等干扰特征提取"""
    return _CODE_FENCE_RE.sub('', text)


def _extract_bracket_tags(text):
    """提取文本中所有 [标签] 形式的内容（不依赖花括号闭合），去重保序"""
    tags = [t.strip() for t in _BRACKET_TAG_RE.findall(text) if t.strip()]
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _find_feature_block(text):
    """
    查找特征标签块：优先匹配含 [x] 的闭合花括号块（取最后一个，
    特征块一般在概念之后）；其次匹配未闭合块（{ [A] + [B] 到行尾/代码围栏）。
    返回块内容字符串；找不到返回 None。
    """
    # 1) 闭合块
    blocks = _BRACE_BLOCK_RE.findall(text)
    for b in reversed(blocks):
        if _BRACKET_TAG_RE.search(b):
            return b.strip()
    # 2) 未闭合块：{ [A] + [B] 后跟行尾 / 代码围栏 / 普通文字（只要花括号内是纯标签序列）
    m = re.search(r'\{\s*((?:\[[^\[\]\n]+\]\s*\+\s*)*\[[^\[\]\n]+\]\s*(?:\+\s*\[[^\[\]\n]+\]\s*)*)\s*(?=\n|$|```|[^\[\s])', text)
    if m:
        return m.group(1).strip()
    return None


def _extract_feature_label_line(text):
    """从 '特征：xxx' / 'tags: xxx' 形式的标签行提取特征"""
    m = _FEATURE_LABEL_RE.search(text)
    if m:
        return parse_tags(m.group(1).strip())
    return []


def _fallback_phrase_features(text, max_n=5):
    """
    模糊兜底：从文本中抽取候选术语。
    保守策略：优先引号（“”""「」『』）包裹的术语；
    其次按标点切分出的 2~12 字、不含代码符号的名词短语。
    """
    if not text:
        return []
    candidates = []
    # 引号包裹的术语（“xx” "xx" 「xx」 『xx』）优先且必定保留
    quoted = re.findall(r'[“"「『]([^”"」』]{2,20})[”"」』]', text)
    candidates += quoted
    for seg in re.split(r'[，,。；;、\s]+', text):
        seg = seg.strip().strip('{}[]')
        # 引号术语已收录，跳过重复
        if seg in quoted:
            continue
        if 2 <= len(seg) <= 12 and not re.search(r'[\d_=<>+\-*/()]', seg):
            if seg in _FEATURE_STOPWORDS:
                continue
            # 排除动词/介词开头、明显是整句的片段
            if seg.startswith(_FEATURE_VERB_PREFIXES):
                continue
            candidates.append(seg)
    seen, out = set(), []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
        if len(out) >= max_n:
            break
    return out


def extract_features_robust(heuristic_string, concept=""):
    """
    鲁棒特征提取（自检回退），按鲁棒性从强到弱逐层尝试。
    返回 (features, method)；method 为 None 表示未命中任何回退。
    """
    text_no_code = _strip_code_fences(heuristic_string)

    # L1: 花括号特征块（闭合或未闭合）
    block = _find_feature_block(text_no_code)
    if block:
        tags = parse_tags(block)
        if tags:
            return tags, 'L1_brace_block'

    # L2: 全文方括号标签（已剔除代码块干扰）
    tags = _extract_bracket_tags(text_no_code)
    if tags:
        return tags, 'L2_any_brackets'

    # L3: "特征：xxx" 标签行
    tags = _extract_feature_label_line(text_no_code)
    if tags:
        return tags, 'L3_label_line'

    # L4: 概念文本短语模糊兜底
    tags = _fallback_phrase_features(concept or text_no_code)
    if tags:
        return tags, 'L4_phrase_fallback'

    return [], None


def _clean_concept(concept):
    """
    清洗概念文本：剥离混入其中的特征块残留。
    例如 "……结构辨识度。 { [完工时间梯度场] + [机器松弛度向量] }"
    → "……结构辨识度。"
    """
    if not concept:
        return concept
    # 1) 剥离闭合的特征块 {...}
    concept = _BRACE_BLOCK_RE.sub('', concept)
    # 2) 剥离未闭合的特征块 { [A] + [B]（到结尾）
    concept = re.sub(r'\{\s*(?:\[[^\[\]\n]+\]\s*\+\s*)*\[[^\[\]\n]+\]\s*\}?\s*$', '', concept)
    # 3) 剥离单独成段的标签行（[A] + [B] 且无其他文字）
    concept = re.sub(r'^\s*(?:\[[^\[\]\n]+\]\s*\+\s*)*\[[^\[\]\n]+\]\s*$', '', concept)
    # 4) 清理尾部符号
    concept = concept.strip().rstrip('，,。;；:：-—')
    return concept


def _recover_concept(heuristic_string):
    """
    当标准解析拿不到概念块时，从启发式文本中恢复概念：
    依次剥离代码块、闭合花括号块、未闭合特征块、标签行、纯标签段，
    剩余文本即概念描述。
    """
    text = _strip_code_fences(heuristic_string)
    if not text.strip():
        return ""
    # 剥离闭合花括号块
    text = _BRACE_BLOCK_RE.sub('', text)
    # 剥离未闭合特征块 { [A] + [B]（可能到结尾）
    text = re.sub(r'\{\s*(?:\[[^\[\]\n]+\]\s*\+\s*)*\[[^\[\]\n]+\]\s*\}?', '', text)
    # 剥离标签行（特征：xxx / tags: xxx）
    text = _FEATURE_LABEL_RE.sub('', text)
    # 剥离纯标签段（[A] + [B] 形式）
    text = re.sub(r'(?:\[[^\[\]\n]+\]\s*\+\s*)*\[[^\[\]\n]+\]', '', text)
    # 清理残留花括号与空白
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip().rstrip('，,。;；:：-—')
    return text


def get_heuristic(heuristic_string):
    """从 LLM 回复中提取启发式字典（含特征自检与鲁棒回退）"""
    bracket_contents = re.findall(r'\{(.*?)\}', heuristic_string, re.DOTALL)
    code_block = re.search(r'```python(.*?)```', heuristic_string, re.DOTALL)
    algorithm = code_block.group(1).strip() if code_block else ""

    concept = bracket_contents[0].strip() if len(bracket_contents) > 0 else ""

    # 解析 tags
    raw_tags = bracket_contents[1].strip() if len(bracket_contents) > 1 else ""
    tags = parse_tags(raw_tags)
    if not tags:
        tags = [raw_tags] if raw_tags else []

    # ── 自检环节：特征为空 → 逐层鲁棒提取 ──
    recovered_method = None
    if not tags:
        tags, recovered_method = extract_features_robust(heuristic_string, concept)
        if recovered_method:
            snippet = heuristic_string[:80].replace('\n', ' ')
            print(f"[自检] 标准解析特征为空，已通过 {recovered_method} 恢复 {len(tags)} 个特征: {tags}")
            print(f"[自检] 原文片段: {snippet}...")
        else:
            print(f"[自检] 标准解析特征为空，且所有鲁棒回退均未命中（原文 {len(heuristic_string)} 字符）")

    # 概念清洗：剥离混入概念文本的特征块残留；若标准解析拿不到概念则从文本恢复
    concept = _clean_concept(concept)
    if not concept and heuristic_string.strip():
        concept = _recover_concept(heuristic_string)

    if not tags:
        # 极端兜底：确保 feature 非空（下游记忆/分类依赖非空列表）
        tags = ['未分类']
        print(f"[自检] 所有提取方式均失败，使用兜底标签: {tags}")

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

    api_key = "sk-YOU…XXXX"
    base_url = "https://api.deepseek.com/v1"
    llm_model = "deepseek-v4-flash"
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
