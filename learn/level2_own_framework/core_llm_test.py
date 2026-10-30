# -*- coding: utf-8 -*-

# ***************************************************
# * File        : core_llm_test.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : L2 —— 框架 LLM 层冒烟（原 hello_agents HelloAgentsLLM 测试的替代）
# ***************************************************

# python libraries
import os

# third-party libraries
from dotenv import load_dotenv
from tinyagent import OpenAIChatModel, PROVIDER_PRESETS
from tinyagent.core.types import Message


def offline_checks() -> None:
    """离线部分：provider 预设与配置解析（无 API 调用）。"""
    load_dotenv()
    provider = os.environ.get("LLM_PROVIDER", "zhipu")
    assert provider in PROVIDER_PRESETS, f"未知 provider: {provider}"
    model = OpenAIChatModel(api_key="dummy")
    print(f"[offline] provider={provider} model={model.model} 预设解析 OK")


def online_check() -> None:
    """在线部分：一次真实调用（需 .env 有效 key）。"""
    model = OpenAIChatModel()
    reply = model.chat([Message("user", "只回复两个字：成功")])
    print(f"[online] {model.model} -> {reply.text[:30]}")


# 测试代码 main 函数
def main():
    offline_checks()
    online_check()


if __name__ == "__main__":
    main()
