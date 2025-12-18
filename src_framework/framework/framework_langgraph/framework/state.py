# -*- coding: utf-8 -*-

# ***************************************************
# * File        : state.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-06
# * Version     : 1.0.120617
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
from typing import TypedDict, List

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class AgentState(TypedDict):
    """
    全局状态(State)
    整个图的执行过程都围绕一个共享的状态对象进行。
    这个状态通常被定义为一个 Python 的 TypedDict，
    它可以包含任何你需要追踪的信息，如对话历史、中间结果、
    迭代次数等。所有的节点都能读取和更新这个中心状态。
    """
    messages: List[str]  # 对话历史
    current_task: str  # 当前任务
    final_answer: str  # 最终答案
    # ... 任何其他需要追踪的状态




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
