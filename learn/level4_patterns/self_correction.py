# -*- coding: utf-8 -*-

# ***************************************************
# * File        : self_correction.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式6 Self-Correction —— 生成 + 校验器 + 失败重试循环
# ***************************************************

# python libraries
import json

# local libraries
from learn.level4_patterns.common import ask, mark


def _validate(text: str) -> str | None:
    """校验器：要求输出是含 name/version 字段的合法 JSON。"""
    try:
        data = json.loads(text.strip().removeprefix("```json").removesuffix("```"))
        if "name" in data and "version" in data:
            return None
        return "缺少 name 或 version 字段"
    except json.JSONDecodeError as e:
        return f"非法 JSON: {e}"


def run(model) -> None:  # noqa: ANN001
    """生成 -> 校验 -> 带错误反馈重试（≤3 次）。"""
    prompt = "输出一个 JSON 对象，包含 name（框架名）与 version 字段，只输出 JSON。"
    feedback = ""
    for attempt in range(1, 4):
        text = ask(model, prompt + (f"\n\n上次错误，请修正：{feedback}" if feedback else ""))
        feedback = _validate(text)
        if feedback is None:
            mark("self-correction", True, f"第 {attempt} 次通过：{text.strip()[:60]}")
            return
    mark("self-correction", False, f"3 次未通过：{feedback}")
