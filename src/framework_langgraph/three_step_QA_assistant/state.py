# -*- coding: utf-8 -*-

# ***************************************************
# * File        : state.py
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
from typing import TypedDict, Annotated, List

from langgraph.graph.message import add_messages

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class SearchState(TypedDict):
    """
    定义全局状态
    定义一个贯穿整个工作流的全局状态。这是一个共享的数据结构，
    它在图的每个节点之间传递，作为工作流的持久化上下文。 
    每个节点都可以读取该结构中的数据，并对其进行更新。
    """
    messages: Annotated[List, add_messages]
    user_query: str  # 经过 LLM 理解后的用户需求总结
    search_query: str  # 优化后用于 Tavily API 的搜索查询
    search_results: str  # Tavily 搜索返回的结果
    final_answer: str  # 最终生成的答案
    step: str  # 标记当前步骤




# 测试代码 main 函数
def main():
    state = SearchState(
        messages=[], 
        user_query="", 
        search_query="", 
        search_results="", 
        final_answer="", 
        step=""
    )
    print(state)

if __name__ == "__main__":
    main()
