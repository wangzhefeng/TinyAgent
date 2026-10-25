# -*- coding: utf-8 -*-

# ***************************************************
# * File        : routing.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : L0 路由模式示例：意图分类 → 分发到不同处理链
# ***************************************************

# python libraries

# local libraries
from learn.level0_llm_basics.llm_client import ChatClient

ROUTER_PROMPT = """你是一个问题路由器。请把用户问题分类为以下标签之一，且只输出标签本身，不要任何其他内容：

- math：数学计算类问题
- translate：中英文翻译类问题
- code：编程实现类问题
- qa：一般问答类问题

用户问题: {question}

标签:"""

CHAIN_PROMPTS = {
    "math": "你是一位严谨的数学老师，请逐步推理并给出最终答案：\n{question}",
    "translate": "你是一位专业译者，请将下面的内容在中英文之间互译（输入是中文则译为英文，否则译为中文）：\n{question}",
    "code": "你是一位资深工程师，请给出简洁、带注释的实现方案：\n{question}",
    "qa": "你是一位知识渊博的助手，请准确回答：\n{question}",
}


def route(client: ChatClient, question: str) -> str:
    """
    第一步：让 LLM 对问题做意图分类（结构化标签输出）。

    Args:
        client (ChatClient): LLM 客户端
        question (str): 用户问题

    Returns:
        str: 路由标签（math/translate/code/qa）
    """
    label = client.chat(ROUTER_PROMPT.format(question=question))[0].strip().lower()
    for key in CHAIN_PROMPTS:
        if key in label:  # 容错：模型输出可能带标点或多余文字
            return key
    return "qa"


def answer(client: ChatClient, question: str) -> str:
    """
    第二步：按标签把问题分发到对应的处理链。

    Args:
        client (ChatClient): LLM 客户端
        question (str): 用户问题

    Returns:
        str: 最终回答
    """
    label = route(client, question)
    prompt = CHAIN_PROMPTS[label].format(question=question)
    reply = client.chat(prompt)[0]
    return f"[route -> {label}]\n{reply}"


# 测试代码 main 函数
def main():
    client = ChatClient()
    for question in [
        "3.5 乘以 12.8 再加上 7 是多少？",
        "把这句话翻译成英文：时序预测是能源行业的基础能力。",
        "用 Python 写一个求数组中位数的函数。",
        "智谱的 GLM 模型是什么？",
    ]:
        print("\n" + "=" * 50)
        print(f"问题: {question}")
        print("-" * 50)
        print(answer(client, question))


if __name__ == "__main__":
    main()
