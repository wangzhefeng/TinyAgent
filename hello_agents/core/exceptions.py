# -*- coding: utf-8 -*-

# ***************************************************
# * File        : exceptions.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-20
# * Version     : 1.0.122000
# * Description : 异常体系
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

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class AgentsException(Exception):
    """
    Agents 基础异常类
    """
    pass

class LLMException(AgentsException):
    """
    LLM 相关异常
    """
    pass

class AgentException(AgentsException):
    """
    Agent 相关异常
    """
    pass

class ConfigException(AgentsException):
    """
    配置相关异常
    """
    pass

class ToolException(AgentsException):
    """
    工具相关异常
    """
    pass




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
