# -*- coding: utf-8 -*-

# ***************************************************
# * File        : planner.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-23
# * Version     : 1.0.112319
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")
import ast
from typing import List

from hello_agents.core.llm_simple import AgentsLLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""


class Planner:
    def __init__(self, llm_client: AgentsLLM):
        self.llm_client = llm_client

    def plan(self, question: str) -> List[str]:
        """
        根据用户问题生成一个行动计划
        """
        # format prompt
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # 为了生成计划，构建一个简单的消息列表
        messages = [{"role": "user", "content": prompt}]

        # 使用流式输出来获取完整的计划
        print("--- 正在生成计划 ---")
        response_text = self.llm_client.think(messages=messages) or ""
        print(f"✅ 计划已生成:\n{response_text}")
        
        # 解析LLM输出的列表字符串
        try:
            # 找到 ```python和```之间的内容
            plan_str = response_text \
                .split("```python")[1] \
                .split("```")[0] \
                .strip()
            # 使用 ast.literal_eval 来安全地执行字符串，将其转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            plan = plan if isinstance(plan, list) else []
            return plan
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
