# -*- coding: utf-8 -*-

# ***************************************************
# * File        : agent.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-18
# * Version     : 1.0.121822
# * Description : Agent 基类
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
from abc import ABC, abstractmethod
from typing import Optional, List

from hello_agents.core.message import Message
from hello_agents.core.llm import AgentsLLM
from hello_agents.core.config import Config

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class Agent(ABC):
    """
    Agent 基类
    """
    def __init__(
        self, 
        name: str, 
        llm: AgentsLLM, 
        system_prompt: Optional[str]=None, 
        config: Optional[Config]=None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: List[Message] = []
    
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """
        运行 Agent
        """
        pass

    def add_message(self, message: Message):
        """
        添加消息到历史记录
        """
        self._history.append(message)

    def clear_history(self):
        """
        清空历史记录
        """
        self._history.clear()

    def get_history(self) -> List[Message]:
        """
        获取历史记录
        """
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"

    def __repr__(self) -> str:
        return self.__str__()




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
