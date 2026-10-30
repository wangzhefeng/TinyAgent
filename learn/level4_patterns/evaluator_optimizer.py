# -*- coding: utf-8 -*-

# ***************************************************
# * File        : evaluator_optimizer.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式9 Evaluator-Optimizer —— 打分者与优化者迭代
# ***************************************************

# python libraries
import re

# local libraries
from learn.level4_patterns.common import ask, mark


def _score(model, text: str) -> tuple[int, str]:  # noqa: ANN001
    """打分者：1-10 分 + 一句改进建议。"""
    reply = ask(
        model,
        "给下面这句话的清晰度打分（1-10，只输出整数），并紧跟一行改进建议：\n" + text,
    )
    m = re.search(r"(10|[1-9])", reply)
    return (int(m.group(1)) if m else 0), reply


def run(model, rounds: int = 2) -> None:  # noqa: ANN001
    """生成 -> 评分 -> 按建议改写，观察分数爬升。"""
    text = ask(model, "用一句话解释什么是时间序列预测。")
    best_score, history = 0, []
    for _ in range(rounds):
        score, advice = _score(model, text)
        history.append(score)
        best_score = max(best_score, score)
        if score >= 9:
            break
        text = ask(model, f"按建议改写这句话使其更清晰：\n{text}\n建议：{advice}")
    mark(
        "evaluator-optimizer",
        best_score >= 7,
        f"分数轨迹 {history}，终稿：{text[:50]}",
    )
