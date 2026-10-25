# -*- coding: utf-8 -*-

# ***************************************************
# * File        : supervisor.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式7 Supervisor —— 顺序编排两个专家智能体（应用层编排）
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import TinyAgent

# local libraries
from learn.level4_patterns.common import mark

ANALYST_SYSTEM = "你是数据分析专家：只负责把原始信息提炼为 3 条要点，不做决策。"
REPORTER_SYSTEM = "你是技术报告撰写人：把要点整理为一段结构化中文小结，语气客观。"


def run(model) -> None:  # noqa: ANN001
    """analyst -> reporter 顺序流水（supervisor 即本函数的编排逻辑）。"""
    question = "多智能体系统中，工具调用可靠性最关键的三条工程实践是什么？"
    analyst = TinyAgent(model=model, system=ANALYST_SYSTEM, max_steps=1)
    reporter = TinyAgent(model=model, system=REPORTER_SYSTEM, max_steps=1)

    points = analyst.run(question).text
    report = reporter.run(f"原始问题：{question}\n\n分析要点：\n{points}").text
    mark("supervisor", len(report) > 30, f"报告 {len(report)} 字：{report[:60]}")
