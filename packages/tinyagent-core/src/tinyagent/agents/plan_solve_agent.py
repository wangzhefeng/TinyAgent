"""PlanAndSolveAgent: plan first, then execute stepwise (ported capability).

能力并入自 `hello_agents/src/agents/plan_solve_agent.py`（L1 已验证并加固：
计划 3-5 步约束、```python 列表解析、每步结果截断入历史）。
"""

from __future__ import annotations

import ast

from ..core.protocols import ChatModel
from ..core.types import Message

PLANNER_PROMPT = """你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
计划应精简聚焦，控制在 3 到 5 个步骤内，不要超过 5 步。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```"""

EXECUTOR_PROMPT = """你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:"""


class PlanAndSolveAgent:
    """Two-stage agent: plan decomposition, then stepwise execution."""

    def __init__(self, model: ChatModel, max_plan_steps: int = 5) -> None:
        self.model = model
        self.max_plan_steps = max_plan_steps

    def _ask(self, prompt: str) -> str:
        return self.model.chat([Message("user", prompt)]).text

    def plan(self, question: str) -> list[str]:
        """Decompose the question into an ordered step list."""
        text = self._ask(PLANNER_PROMPT.format(question=question))
        try:
            block = text.split("```python")[1].split("```")[0].strip()
            steps = ast.literal_eval(block)
            if isinstance(steps, list):
                return [str(s) for s in steps[: self.max_plan_steps]]
        except (IndexError, ValueError, SyntaxError):
            pass
        return [question]

    def run(self, question: str) -> str:
        """Plan, then execute each step; the last step's answer wins."""
        steps = self.plan(question)
        history, answer = "", ""
        for i, step in enumerate(steps, 1):
            answer = self._ask(
                EXECUTOR_PROMPT.format(
                    question=question,
                    plan=steps,
                    history=history or "无",
                    current_step=step,
                )
            )
            history += f"步骤 {i}: {step}\n结果: {answer[:800]}\n\n"
        return answer
