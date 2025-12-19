# -*- coding: utf-8 -*-

# ***************************************************
# * File        : vllm_client2.py
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
from dotenv import load_dotenv

from src_framework.core.llm import LLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# 加载环境变量
load_dotenv()

# vLLM 本地服务
# Python 代码中直接实例化即可: 将自动检测为 vllm
llm_client = LLM()




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
