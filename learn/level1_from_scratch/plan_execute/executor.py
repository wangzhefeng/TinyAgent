# -*- coding: utf-8 -*-

# ***************************************************
# * File        : executor.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : Plan-and-Execute 执行器（M1 API 化；修复步骤计数 bug）
# ***************************************************

# python libraries
from typing import List

# local libraries
from learn.level0_llm_basics.llm_client import ChatClient

EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class Executor:
    def __init__(self, llm_client: ChatClient):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> str:
        """
        根据计划，逐步执行并解决问题。
        """
        # 用于存储历史步骤和结果的字符串
        history = ""

        print("\n--- 正在执行计划 ---")
        final_answer = ""
        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i + 1}/{len(plan)}: {step}")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 如果是第一步，则历史为空
                current_step=step,
            )
            response_text = self.llm_client.chat(prompt)[0]

            # 更新历史记录，为下一步做准备
            # （每步结果截断入历史，防止长计划下上下文膨胀导致超时；返回值不受影响）
            history += f"步骤 {i + 1}: {step}\n结果: {response_text[:800]}\n\n"
            print(f"步骤 {i + 1} 已完成，结果: {response_text}")
            # 每一步的响应先保存，循环结束后最后一步即最终答案
            final_answer = response_text

        return final_answer


# 测试代码 main 函数
def main():
    executor = Executor(ChatClient())
    print(
        executor.execute(
            "如何系统地学习时间序列预测？",
            ["列出核心概念", "推荐学习路径", "给出实践建议"],
        )
    )


if __name__ == "__main__":
    main()
