# -*- coding: utf-8 -*-

# ***************************************************
# * File        : executor.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-23
# * Version     : 1.0.112319
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import os
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")
from typing import List

from llm_client import AgentsLLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""


class Executor:
    def __init__(self, llm_client: AgentsLLM):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> str:
        """
        根据计划，；逐步执行并解决问题。
        """
        # 用于存储历史步骤和结果的字符串
        history = ""

        print("\n--- 正在执行计划 ---")
        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i + 1}/{len(step)}: {step}")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 如果是第一步，则历史为空
                current_step=step,
            )
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages) or ""

            # 更新历史记录，为下一步做准备
            history += f"步骤 {i + 1}: {step}\n结果: {response_text}\n\n"
            print(f"步骤 {i + 1} 已完成，结果: {response_text}")
        # 循环结束后，最后一步的响应就是最终答案
        final_answer = response_text

        return final_answer




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
