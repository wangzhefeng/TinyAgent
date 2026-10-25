# -*- coding: utf-8 -*-

# ***************************************************
# * File        : routing.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-09-17
# * Version     : 1.0.091723
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
from dotenv import find_dotenv, load_dotenv
import warnings
warnings.filterwarnings("ignore")

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# load env variables
_ = load_dotenv(find_dotenv(), override=True)
DEEPSEEK_API_KEY = os.environ['DEEPSEEK_API_KEY']
logger.info(f'DEEPSEEK_API_KEY: {DEEPSEEK_API_KEY}')




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
