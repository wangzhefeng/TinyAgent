# -*- coding: utf-8 -*-

# ***************************************************
# * File        : chat_model.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-07-08
# * Version     : 1.0.070812
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
from dotenv import load_dotenv, find_dotenv
import warnings
warnings.filterwarnings("ignore")

from langchain.chat_models import init_chat_model
from rich.markdown import Markdown

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger

# load env variables
_ = load_dotenv(find_dotenv(), override=True)
LANGSMITH_API_KEY = os.environ["LANGSMITH_API_KEY"]
logger.info(f"LANGSMITH_API_KEY: {LANGSMITH_API_KEY}")

# chat model
llm = init_chat_model("openai:gpt-4.1", temperature=0)
result = llm.invoke("What is a agent?")
logger.info(f"result type: {type(result)}")
logger.info(f"result markdown: {Markdown(result)}")




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
