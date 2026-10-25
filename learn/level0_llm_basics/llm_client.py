# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm_client.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : L0/L1 共享的 OpenAI 兼容 Chat 客户端（默认智谱免费档）
# * Requirement : openai >= 1.0
# ***************************************************

# python libraries
import os
import time
from typing import List, Optional, Tuple

# third-party libraries
from dotenv import load_dotenv
from openai import OpenAI

# 读取根目录 .env（LLM_PROVIDER / LLM_BASE_URL / LLM_API_KEY / LLM_MODEL_ID / LLM_TIMEOUT）
_ = load_dotenv()


class ChatClient:
    """
    极简 OpenAI 兼容聊天客户端。

    接口对齐本地推理后端 ``react.llm_local.InternLM2Chat``：
    ``chat(prompt, history, meta_instruction) -> (reply, history)``，
    使 L1 的 Agent 循环不感知后端差异（API 或本地模型）。

    history 为 OpenAI 消息列表（仅 user/assistant 轮次，不含 system）。
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        self.model_id = model_id or os.environ.get("LLM_MODEL_ID", "glm-4.7-flash")
        self.max_retries = max_retries
        self.client = OpenAI(
            api_key=api_key or os.environ["LLM_API_KEY"],
            base_url=base_url
            or os.environ.get("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            timeout=float(os.environ.get("LLM_TIMEOUT", "60")),
        )

    def chat(
        self,
        prompt: str,
        history: Optional[List] = None,
        meta_instruction: str = "",
    ) -> Tuple[str, List]:
        """
        单轮对话（携带历史）。

        Args:
            prompt (str): 用户输入
            history (list, optional): 消息历史（user/assistant 轮次）。Defaults to None.
            meta_instruction (str, optional): system prompt。Defaults to "".

        Returns:
            tuple: (模型回复文本, 更新后的消息历史)
        """
        history = list(history or [])
        messages = (
            ([{"role": "system", "content": meta_instruction}] if meta_instruction else [])
            + history
            + [{"role": "user", "content": prompt}]
        )

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                )
                reply = response.choices[0].message.content or ""
                history = history + [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": reply},
                ]
                return reply, history
            except Exception as e:
                last_error = e
                msg = str(e)
                if "timed out" in msg:
                    # 思考型模型长输出易超时：提示调大 LLM_TIMEOUT
                    hint = "请求超时：可增大 .env 中 LLM_TIMEOUT 后重试"
                else:
                    # 免费档高峰可能 429 拥堵：指数退避重试
                    hint = "可按模型阶梯切换 .env 中 LLM_MODEL_ID 后重试"
                print(f"[ChatClient] 第 {attempt}/{self.max_retries} 次调用失败：{msg}\n提示: {hint}")
                time.sleep(2 * attempt)
        raise RuntimeError(
            f"LLM 调用连续 {self.max_retries} 次失败（model={self.model_id}）：{last_error}"
        )
