# -*- coding: utf-8 -*-

# ***************************************************
# * File        : agent.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part1 —— 手写邮件助手（triage 路由 + ReAct 工具循环 + 记忆）
# ***************************************************

# python libraries
import re
from typing import Dict, List

# third-party libraries
from openai import OpenAI

# local libraries
from learn.level3_langgraph.part1_from_scratch import email_client
from learn.level3_langgraph.part1_from_scratch.prompts import (
    RESPONDER_PROMPT,
    TRIAGE_PROMPT,
)


class ScratchEmailAssistant:
    """
    课程 part1 的"从零"实现：不使用任何 Agent 框架，
    只用最原始的模型调用 + 手写循环完成 triage 与响应。

    长期记忆（profile / hit_list）演示为进程内累积；
    对照 tinyagent 框架时，它们对应 Memory/SessionStore 协议。
    """

    def __init__(self):
        import os

        from dotenv import load_dotenv

        load_dotenv()
        self.client = OpenAI(
            api_key=os.environ["LLM_API_KEY"],
            base_url=os.environ.get(
                "LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
            ),
            timeout=float(os.environ.get("LLM_TIMEOUT", "180")),
        )
        self.model = os.environ.get("LLM_MODEL_ID", "glm-5.3-flash")
        self.profile = "时间序列方向算法工程师，重视口径严谨与数据准确性"
        self.hit_list: List[str] = []

    def _chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    # ---------------- triage ----------------
    def triage(self, email: Dict) -> str:
        """分诊：respond / notify / ignore。"""
        label = self._chat(
            TRIAGE_PROMPT.format(
                profile=self.profile,
                hit_list=self.hit_list or "（空）",
                author=email["from"],
                subject=email["subject"],
                body=email["body"],
            )
        ).strip().lower()
        for tag in ("respond", "notify", "ignore"):
            if tag in label:
                return tag
        return "notify"

    # ---------------- responder ----------------
    def respond(self, email: Dict, max_steps: int = 4) -> str:
        """ReAct 工具循环处理需要回复的邮件，返回最终草稿。"""
        tools = {
            "search_emails": email_client.search_emails,
            "write_email": email_client.write_email,
            "mark_as_read": email_client.mark_as_read,
        }
        drafts_before = len(email_client.DRAFTS)
        prompt = RESPONDER_PROMPT.format(
            profile=self.profile,
            hit_list=self.hit_list or "（空）",
            email_block=(
                f"#{email['id']} from={email['from']}\n"
                f"subject={email['subject']}\nbody={email['body']}"
            ),
        )
        import json

        for _ in range(max_steps):
            reply = self._chat(prompt)
            m = re.search(r"Action:\s*(\w+)\s*\nAction Input:\s*(\{.*?\})", reply, re.S)
            if not m:
                break
            name, raw_args = m.group(1), m.group(2)
            try:
                args = json.loads(raw_args)
                observation = tools[name](**args)
            except Exception as e:  # noqa: BLE001
                observation = f"tool error: {e}"
            print(f"  [tool] {name}({args}) -> {str(observation)[:60]}")
            prompt = reply + f"\nObservation: {observation}"
        # 兜底：模型未调用 write_email 时，从 Final Draft 提取正文落草稿
        if len(email_client.DRAFTS) == drafts_before:
            body = reply.split("Final Draft:")[-1].strip() or reply.strip()
            email_client.write_email(
                to=email["from"], subject=f"RE: {email['subject']}", body=body
            )
            print("  [fallback] 模型未调用 write_email，已从 Final Draft 自动落草稿")
        return reply

    # ---------------- pipeline ----------------
    def handle(self, email: Dict) -> str:
        """完整流水线：triage → 按标签处理（respond 才进入工具循环）。"""
        tag = self.triage(email)
        print(f"[triage] #{email['id']} {email['subject']!r} -> {tag}")
        if tag == "respond":
            if email["from"] not in self.hit_list:
                self.hit_list.append(email["from"])  # 长期记忆累积
            result = self.respond(email)
            print(f"[respond] 完成，草稿 {len(email_client.DRAFTS)} 封")
            return result
        if tag == "notify":
            return f"（转达用户：{email['subject']}）"
        return "（已忽略）"
