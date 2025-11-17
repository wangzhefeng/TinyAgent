# -*- coding: utf-8 -*-

# ***************************************************
# * File        : main.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-15
# * Version     : 1.0.111523
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
import re
from dotenv import find_dotenv, load_dotenv

from hello_agent_5min.tools import available_tools
from hello_agent_5min.llm_client import OpenAICompatibleClient

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# ##############################
# 指令模板(提示工程, Prompt Engineering)
# ##############################
AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""

# ##############################
# 1. 配置 LLM 客户端
# ##############################
# 读取本地/项目环境变量
_ = load_dotenv(find_dotenv())
MODEL_ID = os.environ.get("MODEL_ID")
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# LLM Client
llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL,
)

# ##############################
# 2. 初始化
# ##############################
# user prompt
user_prompt = "你好，请帮我查询一下今天背景的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]
logger.info(f"用户输入: {user_prompt}\n{'=' * 40}")


# ##############################
# 3. 运行主循环
# ##############################
for i in range(5):
    logger.info(f"--- 循环 {i+1} ---\n")
    # 3.1 构建 Prompt
    full_prompt = "\n".join(prompt_history)
    # 3.2 调用 LLM 进行思考
    # 3.3 解决并执行行动
    # 3.4 记录观察结果







# 测试代码 main 函数
def main():
    pass 

if __name__ == "__main__":
    main()
