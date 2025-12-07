# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm_client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-07
# * Version     : 1.0.120723
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

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化模型：将使用这个 llm 实例来驱动所有节点的智能
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "gpt-4o-mini"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    temperature=0.7,
)

# 初始化 Tavily 客户端
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
