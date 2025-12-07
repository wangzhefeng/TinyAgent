# -*- coding: utf-8 -*-

# ***************************************************
# * File        : edges.py
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
边（Edges）。边负责连接节点，定义工作流的方向。
最简单的边是常规边，它指定了一个节点的输出总是流向另一个固定的节点。
而 LangGraph 最强大的功能在于条件边（Conditional Edges）。
它通过一个函数来判断当前的状态，然后动态地决定下一步应该跳转到哪个节点。
这正是实现循环和复杂逻辑分支的关键。
"""

def should_continue(state: AgentState) -> str:
    """
    条件函数：根据状态决定下一步路由
    """
    # 假设如果消息少于3条，则需要继续规划
    if len(state["messages"]) < 3:
        # 返回的字符串需要与添加条件边时定义的键匹配
        return "continue_to_planner"
    else:
        state["final_answer"] = state["messages"][-1]
        return "end_workflow"




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
