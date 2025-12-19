# -*- coding: utf-8 -*-

# ***************************************************
# * File        : ollama_client.py
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

from src_framework.core.llm import LLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# Ollama 本地服务
llm_client = LLM(
    provider="ollama",
    model="llama3",  # 需与 `ollama run` 指定的模型一致
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 本地服务同样不需要真实 Key
)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
