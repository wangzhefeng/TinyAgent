# -*- coding: utf-8 -*-

# ***************************************************
# * File        : swarm_handoff.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式8 Swarm/Handoff —— 框架 Swarm 对等移交（ADR-0004）
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import Swarm, TinyAgent

# local libraries
from learn.level4_patterns.common import mark

DATA_SYSTEM = (
    "你是数据检索专家。若问题需要写作/总结而非检索，用 transfer_to_writer 移交；"
    "否则直接给出检索要点。"
)
WRITER_SYSTEM = "你是写作专家：把给定材料写成一段流畅的中文小结后结束。"


def run(model) -> None:  # noqa: ANN001
    """triage 由 data agent 起步，判断后移交 writer。"""
    swarm = Swarm(
        {
            "data": TinyAgent(model=model, system=DATA_SYSTEM),
            "writer": TinyAgent(model=model, system=WRITER_SYSTEM),
        },
        initial="data",
    )
    result = swarm.run(
        "把这句话改写成通顺的技术宣传语：tinyagent 用 30 行内核讲清 Agent 本质"
    )
    mark("swarm-handoff", bool(result.text.strip()), result.text.strip()[:60])
