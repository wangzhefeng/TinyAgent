# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-18
# * Version     : 1.0.121822
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
from typing import Optional

from openai import OpenAI
from src.llm_client import AgentsLLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


class LLM(AgentsLLM):
    """
    一个自定义的 LLM 客户端，通过继承增加了对 ModelScope 的支持
    """
    pass




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
