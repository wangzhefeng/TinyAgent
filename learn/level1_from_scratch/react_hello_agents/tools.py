# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tools.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-22
# * Version     : 1.0.112221
# * Description : 一个良好定义的工具应包含以下三个核心要素：
# *               - 名称 (Name)： 一个简洁、唯一的标识符，供智能体在 Action 中调用，例如 Search。
# *               - 描述 (Description)： 一段清晰的自然语言描述，说明这个工具的用途。
# *                 这是整个机制中最关键的部分，因为大语言模型会依赖这段描述来判断何时使用哪个工具。
# *               - 执行逻辑 (Execution Logic)： 真正执行任务的函数或方法。
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
from typing import Dict, Any

from serpapi import SerpApiClient
from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


def search(query: str) -> str:
    """
    一个基于 SerpApi 的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优化返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误: SERPAPI_API_KEY 未在 .env 文件中配置。"
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn",  # 语言代码
        }
        client = SerpApiClient(params)
        results = client.get_dict()

        # 智能解析：优先寻找最直接地答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])

        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]

        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]

        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果地摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的结果。"
    except Exception as e:
        return f"搜索时发生错误: {e}"


class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        print("\n--- 工具注册 ---")
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])




# 测试代码 main 函数
def main():
    # --- 工具初始化与使用示例 ---
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    from ReAct.tools import search
    toolExecutor.registerTool("Search", search_description, search)

    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())
    
    # 4. 智能体的 Action 调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"
    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误: 未找到名为 '{tool_name}' 的工具。")

if __name__ == "__main__":
    main()
