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
from typing import (
    List, Dict, 
    Optional, Iterator, TYPE_CHECKING
)

from ..core.agent import Agent
from ..core.llm import AgentsLLM
from ..core.config import Config
from ..core.message import Message

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


if TYPE_CHECKING:
    from ..tools.registry import ToolRegistry


class SimpleAgent(Agent):
    """
    简单对话 Agent，支持可选的工具调用
    """
    def __init__(self,
                 name: str,
                 llm: AgentsLLM,
                 system_prompt: Optional[str] = None,
                 config: Optional[Config] = None,
                 tool_registry: Optional['ToolRegistry'] = None,
                 enable_tool_calling: bool = True):
        """
        初始化 SimpleAgent

        Args:
            name (str): Agent 名称
            llm (AgentsLLM): LLM 实例
            system_prompt (Optional[str], optional): 系统提示词. Defaults to None.
            config (Optional[Config], optional): 配置对象. Defaults to None.
            tool_registry (Optional[&#39;ToolRegistry&#39;], optional): 工具注册表(可选，如果提供则启用工具调用). Defaults to None.
            enable_tool_calling (bool, optional): 是否启用工具调用(只有在提供 tool_registry 时生效). Defaults to True.
        """
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None

    def _get_enhanced_system_prompt(self) -> str:
        pass

    def _parse_tool_calls(self, textg: str) -> List:
        pass

    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        pass

    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> Dict:
        pass

    def _convert_parameter_types(self, tool_name: str, param_dict: Dict) -> Dict:
        pass

    def _infer_action(self, tool_name: str, param_dict: Dict) -> Dict:
        pass

    def _infer_simple_parameters(self, tool_name: str, parameters: str) -> Dict:
        pass

    def run(self, input_text: str, max_tool_iterations: int=3, **kwargs) -> str:
        pass
    
    def add_tool(self, tool, auto_expand: bool=True) -> None:
        pass

    def remove_tool(self, tool_name: str) -> bool:
        pass
    
    def list_tools(sefl) -> List:
        pass
    
    def has_tools(self) -> bool:
        pass

    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        pass

    




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
