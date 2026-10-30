# -*- coding: utf-8 -*-

# ***************************************************
# * File        : agent.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Survey Agent —— 时序基础模型调研工作流自动化（毕业项目）
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import OpenAIChatModel, TinyAgent, tool
from tinyagent.core.types import Message

# local libraries
from apps.survey_agent.baselines import describe_dataset, run_baselines
from apps.survey_agent.models_meta import MODELS_META


@tool
def describe_experiment_dataset() -> str:
    """查看实验数据集的统计与样例（决定评测设计前必读）。"""
    return describe_dataset()


@tool
def run_baseline_eval(horizon: int, methods: str) -> str:
    """真实执行基线评测。methods 取值 naive/seasonal/ma 逗号分隔，horizon 1-24。"""
    return run_baselines(horizon, methods)


SURVEY_SYSTEM = (
    "你是时序基础模型调研专家：基于给定材料为每个模型写 3-5 行方法论要点，"
    "覆盖架构/训练范式/预测形态/适用场景，不编造材料外的事实。"
)

EVAL_SYSTEM = (
    "你是评测设计专家：先查看数据集，再选择 horizon（12 或 24）与至少两个基线，"
    "真实执行评测并汇报指标表；说明你的设计理由。"
)

CONCLUSION_SYSTEM = (
    "你是综述撰写人：汇总调研要点、评测设计与真实指标表，输出 Markdown 报告，"
    "包含：①各模型方法论 ②基线评测结果 ③基础模型相对基线的预期差距分析 "
    "④结论与后续工作。只使用给定材料中的事实。"
)


def _ask(model: OpenAIChatModel, system: str, prompt: str) -> str:
    """直连单轮调用（非工具阶段使用）。"""
    messages = [Message("system", system), Message("user", prompt)]
    return model.chat(messages).text


def run_survey() -> str:
    """五段工作流：调研 -> 评测设计+真实执行 -> 对比 -> 结论报告。"""
    model = OpenAIChatModel()

    # 1. 调研（材料驱动，不联网）
    print("[1/3] 调研阶段：模型方法论")
    material = "\n\n".join(
        f"### {m['name']}\n- Paper: {m['paper']}\n- 方法: {m['method']}\n"
        f"- 范式: {m['paradigm']}"
        for m in MODELS_META
    )
    survey = _ask(model, SURVEY_SYSTEM, material)

    # 2. 评测设计与真实执行（框架 agent + 工具）
    print("[2/3] 评测阶段：agent 设计并真实执行基线评测")
    evaluator = TinyAgent(
        tools=[describe_experiment_dataset, run_baseline_eval],
        system=EVAL_SYSTEM,
        max_steps=4,
    )
    eval_report = evaluator.run(
        "为目标数据集设计并执行一次基线评测：先看数据，再选 horizon 与基线组合，"
        "真实运行并给出指标表。", session_id="survey-eval",
    ).text

    # 3. 对比与结论
    print("[3/3] 结论阶段：汇总报告")
    report = _ask(
        model,
        CONCLUSION_SYSTEM,
        f"# 调研材料与要点\n{survey}\n\n# 评测报告\n{eval_report}",
    )
    return report


# 测试代码 main 函数
def main():
    print(run_survey())


if __name__ == "__main__":
    main()
