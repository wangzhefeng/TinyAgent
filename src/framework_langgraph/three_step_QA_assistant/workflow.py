# -*- coding: utf-8 -*-

# ***************************************************
# * File        : workflow.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-06
# * Version     : 1.0.120620
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

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from src.framework_langgraph.three_step_QA_assistant.state import (
    SearchState,
)
from src.framework_langgraph.three_step_QA_assistant.nodes import (
    understand_query_node,
    tavily_search_node,
    generate_answer_node,
)

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


def create_search_assistant():
    workflow = StateGraph()

    # 添加节点
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavily_search_node)
    workflow.add_node("answer", generate_answer_node)

    # 设置线性流程
    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    # 编译图
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
