# -*- coding: utf-8 -*-

# ***************************************************
# * File        : simple_agent.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-18
# * Version     : 1.0.121822
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
import re
from typing import Optional, Iterator, TYPE_CHECKING

from hello_agents.core.agent import Agent
from hello_agents.core.llm import AgentsLLM
from hello_agents.core.config import Config
from hello_agents.core.message import Message

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


if TYPE_CHECKING:
    from hello_agents.tools.registry import ToolRegistry


class SimpleAgent(Agent):
    """
    重写简单对话 Agent，展示如何基于框架基类构建自定义 Agent
    """
    def __init__(self,
                 name: str,
                 llm: AgentsLLM,
                 system_prompt: Optional[str] = None,
                 config: Optional[Config] = None,
                 tool_registry: Optional['ToolRegistry'] = None,
                 enable_tool_calling: bool = True):
        super().__init__(name, llm, system_prompt, config)
        
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(f"✅ {name} 初始化完成，工具调用: {'启用' if self.enable_tool_calling else '禁用'}")

    def run(self):
        pass




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
