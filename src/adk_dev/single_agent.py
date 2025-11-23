# -*- coding: utf-8 -*-

# ***************************************************
# * File        : single_agent.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-09-20
# * Version     : 1.0.092015
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

__all__ = []

# python libraries
import os
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")

from google.adk.agents import Agent
from google.adk.tools import google_search

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",  # or your preference Gemini model
    instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search],
)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
