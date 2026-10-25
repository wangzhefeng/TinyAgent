# -*- coding: utf-8 -*-

# ***************************************************
# * File        : multi_agent.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Copilot C3 —— planner/executor/analyst/reporter 多智能体
# ***************************************************

# python libraries
import ast

# third-party libraries
from tinyagent import TinyAgent

# local libraries
from apps.experiment_copilot.copilot1.run_framework import TOOLS

QUESTION = "对比 tsproj_ml 实验结果中 lightgbm-dirmo 与 naive 基线的回测表现，并说明口径差异。"

PLANNER_SYSTEM = (
    "你是实验分析规划师。把研究问题拆成 2-3 个可用只读工具回答的子问题，"
    "输出 Python 列表字面量（```python 块包裹），不要解释。"
)
ANALYST_SYSTEM = "你是指标分析专家：基于给定材料给出口径与结论判断，标注不可比之处。"
REPORTER_SYSTEM = "你是报告撰写人：输出 Markdown 报告（结论先行 + 指标表 + 口径警示）。"


def plan(model) -> list[str]:  # noqa: ANN001
    """planner：拆解子问题。"""
    text = TinyAgent(model=model, system=PLANNER_SYSTEM, max_steps=1).run(
        f"研究问题：{QUESTION}\n可用工具：list_experiment_configs / "
        "list_experiment_results / read_experiment_config / "
        "read_experiment_result_summary"
    ).text
    try:
        block = text.split("```python")[1].split("```")[0].strip()
        plan_list = ast.literal_eval(block)
        return plan_list if isinstance(plan_list, list) else [QUESTION]
    except (IndexError, ValueError, SyntaxError):
        return [QUESTION]


def execute(model, sub_questions: list[str]) -> str:  # noqa: ANN001
    """executor：带只读工具的 TinyAgent 逐问检索。"""
    agent = TinyAgent(tools=TOOLS, codec="react", max_steps=6)
    findings = []
    for i, q in enumerate(sub_questions, 1):
        print(f"[executor] 子问题 {i}: {q}")
        result = agent.run(q, session_id=f"copilot-c3-q{i}")
        findings.append(f"## 子问题 {i}\n{q}\n\n结果：\n{result.text}")
    return "\n\n".join(findings)


def main():
    from tinyagent import OpenAIChatModel

    model = OpenAIChatModel()

    print("[planner] 拆解研究问题")
    sub_questions = plan(model)
    print(f"[planner] {len(sub_questions)} 个子问题")

    findings = execute(model, sub_questions)

    print("[analyst] 分析口径")
    analysis = TinyAgent(model=model, system=ANALYST_SYSTEM, max_steps=1).run(
        f"研究问题：{QUESTION}\n\n检索材料：\n{findings[:6000]}"
    ).text

    print("[reporter] 生成报告")
    report = TinyAgent(model=model, system=REPORTER_SYSTEM, max_steps=1).run(
        f"研究问题：{QUESTION}\n\n检索材料：\n{findings[:6000]}\n\n分析：\n{analysis}"
    ).text
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
