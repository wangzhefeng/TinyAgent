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
from typing import Dict

from langchain_core.messages import (
    SystemMessage,
    HumanMessage, 
    AIMessage, 
)

from src.framework_langgraph.three_step_QA_assistant.state import (
    SearchState
)
from src.framework_langgraph.three_step_QA_assistant.llm_client import (
    llm,
    tavily_client,
)

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


def understand_query_node(state: SearchState) -> Dict:
    """
    理解与查询节点

    步骤1：理解用户查询并生成搜索关键词
    """
    # User Message
    user_message = state["messages"][-1].content
    # System Message
    understand_prompt = f"""分析用户的查询：{user_message}
    请完成两个任务：
    1. 简洁总结用户想要了解什么
    2. 生成最适合搜索引擎的关键词（中英文均可，要精准）

    格式：
    理解：[用户需求总结]
    搜索词：[最佳搜索关键词]"""
    system_message = SystemMessage(content=understand_prompt)
    # LLM invoke
    response = llm.invoke([system_message])
    response_text = response.content

    # 解析 LLM 的输出，提取搜索关键词
    search_query = user_message  # 默认使用原始查询
    if "搜索词：" in response_text:
        search_query = response_text.split("搜索词：")[1].strip()

    return {
        "messages": [AIMessage(content=f"我将为您搜索：{search_query}")],
        "user_query": response_text,
        "search_query": search_query,
        "step": "understood",
    }


def tavily_search_node(state: SearchState) -> Dict:
    """
    搜索节点
    步骤2：使用Tavily API进行真实搜索
    """
    search_query = state["search_query"]
    try:
        print(f"🔍 正在搜索: {search_query}")
        response = tavily_client.search(
            query=search_query,
            search_depth="basic",
            max_results=5,
            include_answer=True,
        )
        # ... (处理和格式化搜索结果) ...
        search_results = ...  # 格式化后的结果字符串
        
        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content="✅ 搜索完成！正在整理答案...")],
        }
    except Exception as e:
        # ... (处理错误) ...
        return {
            "search_results": f"搜索失败：{e}",
            "step": "search_failed",
            "messages": [AIMessage(content=f"❌ 搜索遇到问题...")],
        }


def generate_answer_node(state: SearchState) -> Dict:
    """
    回答节点
    步骤3：基于搜索结果生成最终答案
    """
    if state["step"] == "search_failed":
        # 如果搜索失败，执行回退策略，基于LLM自身知识回答
        fallback_prompt = f"搜索API暂时不可用，请基于您的知识回答用户的问题：\n用户问题：{state['user_query']}"
        response = llm.invoke([SystemMessage(content=fallback_prompt)])
    else:
        # 搜索成功，基于搜索结果生成答案
        answer_prompt = f"""基于以下搜索结果为用户提供完整、准确的答案：
        用户问题：{state['user_query']}
        搜索结果：\n{state['search_results']}
        请综合搜索结果，提供准确、有用的回答...
        """
        response = llm.invoke([SystemMessage(content=answer_prompt)])
    
    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)],
    }




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
