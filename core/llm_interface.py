# -*- coding: utf-8 -*-
# llm_interface.py

from openai import OpenAI
import unicodedata
import json
import aiohttp

# llm_interface LLM 对话接口类实现
class llm_interface():
    def __init__(self, api_key, base_url, llm_model, if_stream = False):
        self.client= OpenAI(
        # defaults to os.environ.get("OPENAI_api_key")
        api_key=api_key,
        base_url=base_url
        )
        self.llm_model = llm_model
        self.if_stream = if_stream

        self.base_url = base_url
        self.api_key = api_key


    def send_message(self, message_list):
        completion = self.client.chat.completions.create(
            model = self.llm_model,
            messages = message_list,
            stream = self.if_stream
        )


        if self.if_stream:
            # 若采用流式输出
            response = []
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""

                # 应用Unicode规则化
                content = unicodedata.normalize('NFC', content)

                # 打印回复
                # print(content, end="", flush=True)
                response.append(content)
            return ''.join(response)
        else:
            # 若非流式输出
            content = completion.choices[0].message.content
            # 应用Unicode规则化
            content = unicodedata.normalize('NFC', content)
            # print("Assistant: ",content, end="", flush=True)
            return content


if __name__ == "__main__":
    # 设置api_key和base_url
    # api_key = "YOUR_api_key" # 替换为你的api_key
    api_key = "sk-YOUR_API_KEY_XXXXXX"  # 替换为你的api_key
    base_url = "https://api.deepseek.com/v1"
    # llm_model = "deepseek-chat"
    llm_model = "deepseek-chat"
    if_stream = False

    # message_list = [{"role": "user", "content": "你好，请自我介绍一下。"}]
    # 示例prompt
    test_prompt = ("TSP问题即，给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。"
                   "可以通过从当前节点开始逐步选择下一个节点来解决此任务。"
                   "请你帮我设计一个启发式算法。首先，用一句话描述您的新算法及主要步骤，描述必须放在大括号内。"
                   "接着，用Python实现一个名为select_next_node的函数。"
                   "该函数应接受4个输入：'current_node', 'destination_node', 'univisited_nodes', 'distance_matrix'。"
                   "函数应返回1个输出：'next_node'。"
                   "'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，"
                   "distance_matrix'是节点的距离矩阵。所有数据均为Numpy数组。不要提供额外解释。")

    message_list = [{"role": "user", "content": test_prompt}]

    interface_example = llm_interface(api_key, base_url, llm_model, if_stream)

    while True:
        response = interface_example.send_message(message_list)

        print(f"assisstant: {response}")
        # 保存至消息记录
        message_list.append({"role": "assistant", "content": response})
        user_message = input("\nUser: ")  # 输入回复
        message_list.append({"role": "user", "content": user_message})  # 保存至消息记录


