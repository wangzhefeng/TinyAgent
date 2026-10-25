# -*- coding: utf-8 -*-

# ***************************************************
# * File        : common.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式实验室公共助手（模型获取 + 演示标记打印）
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import OpenAIChatModel
from tinyagent.core.types import Message


def ask(model: OpenAIChatModel, prompt: str, system: str = "") -> str:
    """单轮便捷调用。"""
    messages = ([Message("system", system)] if system else []) + [
        Message("user", prompt)
    ]
    return model.chat(messages).text


def mark(name: str, ok: bool, detail: str = "") -> None:
    """打印模式演示的通过标记。"""
    print(f"{'✅' if ok else '❌'} [{name}] {detail}")
