# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part2 —— LangChain ChatOpenAI 接智谱 OpenAI 兼容端点
# ***************************************************

# python libraries
import os

# third-party libraries
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

_ = load_dotenv()


def make_llm(temperature: float = 0.2) -> ChatOpenAI:
    """构造接智谱端点的 ChatOpenAI（模型阶梯同 .env 约定）。"""
    return ChatOpenAI(
        model=os.environ.get("LLM_MODEL_ID", "glm-5.3-flash"),
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ.get(
            "LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
        ),
        temperature=temperature,
        timeout=float(os.environ.get("LLM_TIMEOUT", "180")),
    )
