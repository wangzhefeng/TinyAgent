# -*- coding: utf-8 -*-

# ***************************************************
# * File        : agent_run.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : 手写 ReAct Agent 演示入口（API 后端；本地后端见 llm_local.py）
# ***************************************************

# python libraries
import os

# local libraries
from learn.level0_llm_basics.llm_client import ChatClient
from learn.level1_from_scratch.react.Agent import Agent


def main():
    # 默认 API 后端（智谱 OpenAI 兼容端点，.env 控制）
    agent = Agent(model=ChatClient())
    print("=" * 60)
    print("ReAct system prompt:")
    print(agent.system_prompt)
    print("=" * 60)

    # 注意：history 显式传递并接收更新（原版 `history = _` 的误用已修复）
    response, history = agent.text_completion(text="你好", history=[])
    print(f"\n[回复 1] {response}\n")

    # 无需任何外部 key 的工具调用演示（calculator）
    response, history = agent.text_completion(
        text="请用计算器算一下 (123 + 456) * 2 的结果", history=history
    )
    print(f"\n[回复 2] {response}\n")

    # 搜索工具（可选）：需要 .env 配置 GOOGLE_SERPER_API_KEY
    if os.environ.get("GOOGLE_SERPER_API_KEY"):
        response, history = agent.text_completion(
            text="书生浦语是什么？", history=history
        )
        print(f"\n[回复 3] {response}\n")

    # 本地模型后端（可选，需要 torch/transformers + downloaded_models/）：
    #   from learn.level1_from_scratch.react.llm_local import InternLM2Chat
    #   agent = Agent(model=InternLM2Chat("./downloaded_models/..."))


if __name__ == "__main__":
    main()
