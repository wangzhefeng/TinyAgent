# -*- coding: utf-8 -*-

# ***************************************************
# * File        : vllm_client1.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : vLLM 本地服务接入·显式配置（tinyagent OpenAIChatModel）
# ***************************************************

# python libraries
import os
from pathlib import Path

# third-party libraries
from tinyagent import OpenAIChatModel
from tinyagent.core.types import Message

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ["LOG_NAME"] = LOGGING_LABEL
from utils.log_util import logger  # noqa: E402


# vLLM 本地服务（启动方式见 vllm_service.sh）
llm_client = OpenAIChatModel(
    model="Qwen/Qwen1.5-0.5B-Chat",  # 需与服务启动时指定的模型一致
    base_url="http://localhost:8000/v1",
    api_key="vllm",  # 本地服务通常不需要真实 API Key
)


# 测试代码 main 函数
def main():
    try:
        reply = llm_client.chat([Message("user", "用一句话介绍你自己")])
        logger.info(f"vllm 响应: {reply.text[:80]}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"连接失败（先启动 vllm 服务）: {e}")


if __name__ == "__main__":
    main()
