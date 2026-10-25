# -*- coding: utf-8 -*-

# ***************************************************
# * File        : vllm_client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-19
# * Version     : 1.0.121923
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

from hello_agents.core.llm import LLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# vLLM 本地服务
llm_client = LLM(
    provider="vllm",
    model="Qwen/Qwen1.5-0.5B-Chat",  # 需与服务启动时指定的模型一致
    base_url="http://localhost:8000/v1",
    api_key="vllm",  # 本地服务通常不需要真实API Key，可填任意非空字符串
)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
