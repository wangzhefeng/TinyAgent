# -*- coding: utf-8 -*-

"""M3E 本地 Embedding 兼容层：需本地模型（m3e-base），未内置。

原教程的 M3E 依赖本地 sentence-transformers 模型，本仓库未内置。
请改用 ZhipuAIEmbeddings（智谱 Embedding-3，OpenAI 兼容端点）。
"""


class M3eEmbeddings:
    """占位实现：提示改用 ZhipuAIEmbeddings。"""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "M3E 需要本地 sentence-transformers 模型，本仓库未内置；"
            "请改用 embedding_api.zhipuai_embedding.ZhipuAIEmbeddings"
        )
