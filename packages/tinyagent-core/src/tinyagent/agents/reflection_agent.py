"""ReflectionAgent: generate -> critique -> refine loop (ported capability).

能力并入自 `hello_agents/src/agents/reflection_agent.py`（其提示词与流程
在 L1 已验证），此处沉淀为框架开箱组件：直接组合 ChatModel，无工具参与。
"""

from __future__ import annotations

from ..core.protocols import ChatModel
from ..core.types import Message

INITIAL_PROMPT = """你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。"""

REFLECT_PROMPT = """你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在算法效率上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种算法上更优的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答"无需改进"。

请直接输出你的反馈，不要包含任何额外的解释。"""

REFINE_PROMPT = """你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
{last_code}
评审员的反馈：
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
请直接输出优化后的代码，不要包含任何额外的解释。"""


class ReflectionAgent:
    """Generate, critique, refine — until the critic says "无需改进"."""

    def __init__(
        self, model: ChatModel, max_iterations: int = 2, system: str = ""
    ) -> None:
        self.model = model
        self.max_iterations = max_iterations
        self.system = system

    def _ask(self, prompt: str) -> str:
        messages = (
            ([Message("system", self.system)] if self.system else [])
            + [Message("user", prompt)]
        )
        return self.model.chat(messages).text

    def run(self, task: str) -> str:
        """Run the reflection loop and return the final (best) output."""
        code = self._ask(INITIAL_PROMPT.format(task=task))
        for _ in range(self.max_iterations):
            feedback = self._ask(REFLECT_PROMPT.format(task=task, code=code))
            if "无需改进" in feedback:
                break
            code = self._ask(
                REFINE_PROMPT.format(task=task, last_code=code, feedback=feedback)
            )
        return code
