# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_framework.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Copilot C1 —— copilot0 只读工具迁到 tinyagent 框架
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import (
    AllowlistGuardrail,
    FileSessionStore,
    JsonlTracer,
    TinyAgent,
    tool,
)

# local libraries
from apps.experiment_copilot.copilot0.tools import (
    list_configs,
    list_results,
    read_config,
    read_result_summary,
)


@tool
def list_experiment_configs() -> str:
    """列出 tsproj_ml 仓库 config/ 下的全部实验配置 YAML 路径。"""
    return list_configs()


@tool
def read_experiment_config(rel_path: str) -> str:
    """读取指定实验配置 YAML 的完整内容（相对 config/ 的路径，先用 list 拿真实路径）。"""
    return read_config(rel_path)


@tool
def list_experiment_results() -> str:
    """列出 tsproj_ml 已有实验结果目录（模型-策略标识）。"""
    return list_results()


@tool
def read_experiment_result_summary(rel_dir: str) -> str:
    """读取单个实验结果的策略、回测几何与平均指标（MAE/RMSE/MAPE/Accuracy）。"""
    return read_result_summary(rel_dir)


TOOLS = [
    list_experiment_configs,
    read_experiment_config,
    list_experiment_results,
    read_experiment_result_summary,
]


def build_agent() -> TinyAgent:
    """
    组装 Copilot：tinyagent 六协议 + 白名单护栏（安全边界的框架化落地）。
    """
    return TinyAgent(
        tools=TOOLS,
        codec="react",
        guardrail=AllowlistGuardrail([t.spec.name for t in TOOLS]),
        session=FileSessionStore(),
        tracer=JsonlTracer(),
        max_steps=6,
    )


def answer(question: str) -> str:
    """C1：框架版 Copilot，回答单个问题（评测 harness 复用）。"""
    return build_agent().run(question, session_id="copilot-c1-eval").text


# 测试代码 main 函数
def main():
    agent = build_agent()
    result = agent.run(
        "已有的实验结果里 lightgbm-dirmo 的回测平均 MAE 是多少？和 Naive 基线相比如何？"
        "注意说明两者是否同口径。",
        session_id="copilot-c1",
    )
    print(result.text)


if __name__ == "__main__":
    main()
