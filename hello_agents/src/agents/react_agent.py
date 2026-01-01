# -*- coding: utf-8 -*-

# ***************************************************
# * File        : react_agent.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-18
# * Version     : 1.0.121822
# * Description : ReAct Agent 实现：推理与行动结合的智能体
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
import re
from typing import Optional, List, Tuple

from ..core.agent import Agent
from ..core.llm import AgentsLLM
from ..core.config import Config
from ..core.message import Message
from ..tools.registry import ToolRegistry

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


# 默认 ReAct 提示词模板
DEFAULT_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

Thought: 分析问题，确定需要什么信息，制定研究策略。
Action: 选择合适的工具获取信息，格式为：
- `{{tool_name}}[{{tool_input}}]`：调用工具获取信息。
- `Finish[研究结论]`：当你有足够信息得出结论时。

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""

class ReActAgent(Agent):
    """
    ReAct (Reasoning and Acting) Agent

    结合推理和行动的智能体，能够：
    1. 分析问题并制定行动计划
    2. 调用外部工具获取信息
    3. 基于观察结果进行推理
    4. 迭代执行直到得出最终答案
    
    这是一个经典的Agent范式，特别适合需要外部信息的任务。
    """

    def __init__(self,
                 name: str,
                 llm: AgentsLLM,
                 system_prompt: Optional[str] = None,
                 config: Optional[Config] = None,
                 tool_registry: Optional[ToolRegistry] = None,
                 max_steps: int = 5,
                 custom_prompt: Optional[str] = None):
        """
        初始化 ReActAgent

        Args:
            name (str): Agent 名称
            llm (AgentsLLM): LLM 实例
            system_prompt (Optional[str], optional): 系统提示词. Defaults to None.
            config (Optional[Config], optional): 配置对象. Defaults to None.
            tool_registry (Optional[ToolRegistry], optional): 工具注册表(如果不提供则创建空的工具注册表). Defaults to None.
            max_steps (int, optional): 最大执行步数. Defaults to 5.
            custom_prompt (Optional[str], optional): 自定义提示词模板. Defaults to None.
        """
        super().__init__(name, llm, system_prompt, config)

        # 如果没有提供 tool_registry，创建一个空的
        if tool_registry is None:
            self.tool_registry = ToolRegistry()
        else:
            self.tool_registry = tool_registry
        
        self.max_steps = max_steps
        self.current_history: List[str] = []

        # 设置提示词模板：用户自定义优先，否则使用默认模板
        self.prompt_template = custom_prompt if custom_prompt else DEFAULT_REACT_PROMPT



# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
