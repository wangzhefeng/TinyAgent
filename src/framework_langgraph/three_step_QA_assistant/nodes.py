# -*- coding: utf-8 -*-

# ***************************************************
# * File        : nodes.py
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

from langchain_core.messages import (
    HumanMessage, 
    AIMessage, 
    SystemMessage
)

from src.framework_langgraph.three_step_QA_assistant.state import (
    SearchState
)

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


def understand_query_node(state: SearchState) -> dict:
    """
    理解与查询节点

    步骤1：理解用户查询并生成搜索关键词
    """
    pass


def tavily_search_node(state: SearchState) -> dict:
    """
    搜索节点
    步骤2：使用Tavily API进行真实搜索
    """
    pass


def generate_answer_node(state: SearchState) -> dict:
    """
    回答节点
    步骤3：基于搜索结果生成最终答案
    """
    pass




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
