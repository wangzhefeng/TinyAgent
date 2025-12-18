# -*- coding: utf-8 -*-

# ***************************************************
# * File        : nodes.py
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

from src.framework_langgraph.framework.state import AgentState

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


"""
每个节点都是一个接收当前状态作为输入、并返回一个更新后的状态作为输出的 Python 函数。
节点是执行具体工作的单元。
"""

def planner_node(state: AgentState) -> AgentState:
    """
    定义一个“规划者”节点函数
    根据当前任务指定计划，并更新状态
    """
    current_task = state["current_task"]
    
    # ... 调用 LLM 生成计划 ...
    plan = f"为任务 '{current_task}' 生成的计划..."
    
    # 新消息追加到状态中
    state["messages"].append(plan)

    return state


def executor_node(state: AgentState) -> AgentState:
    """
    定义一个“执行者”节点函数
    执行最新计划，并更新状态
    """
    latest_plan = state["messages"][-1]
    
    # ... 执行计划并获得结果 ...
    result = f"执行计划 '{latest_plan}' 的结果..."
    
    # 新消息追加到状态中
    state["messages"].append(result)

    return state




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
