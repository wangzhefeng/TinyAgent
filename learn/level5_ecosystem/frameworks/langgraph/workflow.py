# -*- coding: utf-8 -*-

# ***************************************************
# * File        : workflow.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-06
# * Version     : 1.0.120619
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

from langgraph.graph import StateGraph, END

from src.framework_langgraph.framework.state import AgentState
from src.framework_langgraph.framework.nodes import (
    planner_node, 
    executor_node,
)
from src.framework_langgraph.framework.edges import should_continue

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


# 初始化一个状态图，并绑定我们定义的状态结构
workflow = StateGraph(AgentState)

# 将节点函数添加到图中
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)

# 设置图的入口点
workflow.set_entry_point("planner")

# 添加常规边，连接 planner 和 executor
workflow.add_edge("planner", "executor")

# 添加条件边，实现动态路由
workflow.add_conditional_edges(
    # 起始节点
    "executor",
    # 判断函数
    should_continue,
    # 路由映射；将判断函数的返回值映射到目标节点
    {
        "continue_to_planner": "planner",  # 如果返回 "continue_to_planner"，则跳回 planner
        "end_workflow": END,  # 如果返回 "end_workflow"，则流程结束
    }
)

# 编译图，生成可执行的应用
app = workflow.compile()

# 运行图
inputs = {
    "current_task": "分析最近的 AI 行业新闻", 
    "messages": [],
}
for event in app.stream(inputs):
    print(event)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
