# -*- coding: utf-8 -*-

# ***************************************************
# * File        : routing_pattern.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式2 Routing —— 意图分类分发到不同处理链（框架版）
# ***************************************************

# python libraries

# local libraries
from learn.level4_patterns.common import ask, mark

CHAINS = {
    "math": "你是严谨的数学老师，逐步推理后给最终答案：\n{q}",
    "translate": "你是专业译者，中英互译（中文译英，英文译中文）：\n{q}",
    "code": "你是资深工程师，给简洁带注释的实现：\n{q}",
    "qa": "你是知识渊博的助手，准确回答：\n{q}",
}


def run(model, question: str = "3.5 * 12.8 + 7 = ?") -> None:  # noqa: ANN001
    """分类 + 分发两步。"""
    label = ask(
        model,
        "把问题分类为 math/translate/code/qa 之一，只输出标签：\n" + question,
    ).strip().lower()
    tag = next((k for k in CHAINS if k in label), "qa")
    reply = ask(model, CHAINS[tag].format(q=question))
    mark("routing", tag == "math" or bool(reply), f"route={tag} -> {reply[:50]}")
