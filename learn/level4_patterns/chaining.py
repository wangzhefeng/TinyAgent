# -*- coding: utf-8 -*-

# ***************************************************
# * File        : chaining.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式1 Prompt Chaining —— 串行流水线，每步一个专注子任务
# ***************************************************

# python libraries

# local libraries
from learn.level4_patterns.common import ask, mark


def run(model) -> None:  # noqa: ANN001
    """提取 -> 润色 两段链。"""
    raw = "GLM-5.3 在推理、代码与智能体能力上达到开源 SOTA，工具调用表现出色。"
    extracted = ask(
        model, f"从下述文本提取一条关键事实，只输出事实本身：\n{raw}"
    )
    polished = ask(
        model,
        f"把这条事实改写成一句简洁的技术新闻标题：\n{extracted}",
    )
    mark("chaining", bool(polished.strip()), f"{extracted[:40]}... -> {polished[:50]}")
