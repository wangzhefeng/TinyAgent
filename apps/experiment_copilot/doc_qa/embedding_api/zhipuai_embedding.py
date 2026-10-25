# -*- coding: utf-8 -*-

# ***************************************************
# * File        : zhipuai_embedding.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 智谱 Embedding 兼容层（修复原教程缺失的 embedding_api 模块）
# ***************************************************

# python libraries
import os

# third-party libraries
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

_ = load_dotenv()


class ZhipuAIEmbeddings(OpenAIEmbeddings):
    """
    智谱 Embedding 模型，经 OpenAI 兼容端点（/api/paas/v4）接入。
    与原教程引用的同名类接口一致（embed_documents/embed_query）。
    """

    def __init__(self, model: str = "embedding-3", **kwargs):
        kwargs.setdefault("openai_api_key", os.environ["LLM_API_KEY"])
        kwargs.setdefault(
            "openai_api_base",
            os.environ.get("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        )
        super().__init__(model=model, **kwargs)
