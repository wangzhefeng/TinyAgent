# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_react.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Copilot C0 演示：手写 ReAct Agent + tsproj_ml 只读工具
# ***************************************************

# python libraries

# local libraries
from apps.experiment_copilot.copilot0.tools import CopilotTools
from learn.level0_llm_basics.llm_client import ChatClient
from learn.level1_from_scratch.react.Agent import Agent

QUESTIONS = [
    "tsproj_ml 里有哪些实验配置？挑一个 AIDC 负荷相关的配置，说明它配置了什么。",
    "已有的实验结果里，lightgbm-dirmo 这一组的回测平均 MAE 和 RMSE 是多少？和 Naive 基线相比如何？",
]


def answer(question: str) -> str:
    """C0：手写 ReAct Agent + 只读工具，回答单个问题（评测 harness 复用）。"""
    agent = Agent(model=ChatClient(), tools=CopilotTools())
    response, _history = agent.text_completion(text=question, history=[])
    return response


def main():
    history = []
    for i, question in enumerate(QUESTIONS, 1):
        print("\n" + "=" * 60)
        print(f"[问题 {i}] {question}")
        print("-" * 60)
        agent = Agent(model=ChatClient(), tools=CopilotTools())
        response, history = agent.text_completion(text=question, history=history)
        print(f"[回答 {i}] {response}")


if __name__ == "__main__":
    main()
