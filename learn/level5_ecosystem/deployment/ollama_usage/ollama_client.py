# -*- coding: utf-8 -*-

# ***************************************************
# * File        : ollama_client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : Ollama 本地服务接入（tinyagent OpenAIChatModel，OpenAI 兼容）
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


# Ollama 本地服务（先 `ollama run llama3` 或见 ollama_service.sh）
llm_client = OpenAIChatModel(
    model="llama3",  # 需与 `ollama run` 指定的模型一致
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # 本地服务不需要真实 Key，任意非空即可
)


# 测试代码 main 函数
def main():
    try:
        reply = llm_client.chat([Message("user", "用一句话介绍你自己")])
        logger.info(f"ollama 响应: {reply.text[:80]}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"连接失败（先启动本地服务）: {e}")


if __name__ == "__main__":
    main()
