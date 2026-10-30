# -*- coding: utf-8 -*-

# ***************************************************
# * File        : vllm_client2.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : vLLM 接入·环境变量版（.env 配置端点，自动检测 provider）
# ***************************************************

# python libraries
import os
from pathlib import Path

# third-party libraries
from dotenv import load_dotenv
from tinyagent import OpenAIChatModel
from tinyagent.core.types import Message

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ["LOG_NAME"] = LOGGING_LABEL
from utils.log_util import logger  # noqa: E402


# 加载环境变量：LLM_BASE_URL 指向 vllm 端点（如 http://localhost:8000/v1），
# LLM_PROVIDER / LLM_MODEL_ID 按需覆盖
load_dotenv()
llm_client = OpenAIChatModel()


# 测试代码 main 函数
def main():
    try:
        reply = llm_client.chat([Message("user", "用一句话介绍你自己")])
        logger.info(f"{llm_client.model} 响应: {reply.text[:80]}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"连接失败（检查 .env 的 LLM_BASE_URL）: {e}")


if __name__ == "__main__":
    main()
