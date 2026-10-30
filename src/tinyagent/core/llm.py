"""OpenAI-compatible ChatModel with provider presets and a retry ladder."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from .types import Message, ModelReply, ToolCallReply, ToolSpec

# 读取根目录 .env（LLM_PROVIDER / LLM_BASE_URL / LLM_API_KEY / LLM_MODEL_ID）
_ = load_dotenv(find_dotenv(), override=True)

#: provider presets: base_url + env key/model names (see docs/00-overview/environment.md)
PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "LLM_API_KEY",
        "model_env": "LLM_MODEL_ID",
        "default_model": "glm-4.7-flash",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL_ID",
        "default_model": "deepseek-chat",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL_ID",
        "default_model": "gpt-4.1",
    },
}


def _specs_to_openai_tools(specs: list[ToolSpec]) -> list[dict[str, Any]]:
    """Convert ToolSpec list to the OpenAI ``tools`` request shape."""
    return [
        {
            "type": "function",
            "function": {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
            },
        }
        for s in specs
    ]


def _messages_to_openai(messages: list[Message]) -> list[dict[str, Any]]:
    """Convert internal messages to the OpenAI request shape."""
    out: list[dict[str, Any]] = []
    for m in messages:
        d: dict[str, Any] = {"role": m.role, "content": m.content}
        if m.tool_call_id is not None:
            d["tool_call_id"] = m.tool_call_id
        if m.tool_calls is not None:
            d["tool_calls"] = m.tool_calls
        out.append(d)
    return out


class OpenAIChatModel:
    """ChatModel over any OpenAI-compatible endpoint.

    The retry ladder follows docs/00-overview/environment.md: transient
    congestion gets exponential backoff; timeouts hint at ``LLM_TIMEOUT``.
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
        max_retries: int = 3,
    ) -> None:
        preset = PROVIDER_PRESETS.get(os.environ.get("LLM_PROVIDER", "zhipu"), None)
        model_env = (preset or {}).get("model_env") or "LLM_MODEL_ID"
        default_model = (preset or {}).get("default_model", "glm-4.7-flash")
        self.model = model or os.environ.get(model_env, default_model)
        base = base_url or os.environ.get(
            "LLM_BASE_URL", (preset or {}).get("base_url", "")
        )
        key = api_key or os.environ.get((preset or {}).get("api_key_env", "LLM_API_KEY"), "")
        self.max_retries = max_retries
        self.client = OpenAI(
            api_key=key,
            base_url=base or None,
            timeout=timeout or float(os.environ.get("LLM_TIMEOUT", "180")),
        )

    def chat(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> ModelReply:
        """Call the chat completions endpoint and normalize the reply."""
        params: dict[str, Any] = {
            "model": self.model,
            "messages": _messages_to_openai(messages),
        }
        if tools:
            params["tools"] = _specs_to_openai_tools(tools)
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.client.chat.completions.create(**params)
                choice = resp.choices[0].message
                usage = (
                    {
                        "input_tokens": resp.usage.prompt_tokens,
                        "output_tokens": resp.usage.completion_tokens,
                        "total_tokens": resp.usage.total_tokens,
                    }
                    if resp.usage is not None
                    else {}
                )
                return ModelReply(
                    text=choice.content or "",
                    tool_calls=[
                        ToolCallReply(
                            id=tc.id,
                            name=tc.function.name,
                            arguments=tc.function.arguments or "{}",
                        )
                        for tc in (choice.tool_calls or [])
                    ],
                    usage=usage,
                )
            except Exception as e:  # noqa: BLE001
                last_error = e
                time.sleep(2 * attempt)
        raise RuntimeError(
            f"LLM call failed {self.max_retries} times (model={self.model}): {last_error}"
        )


def parse_tool_arguments(raw: str) -> dict[str, Any]:
    """Parse raw tool-call arguments JSON, tolerating trailing text.

    模型可能在 Action Input 之后继续输出 Thought/Final Answer，
    此时只取首个 JSON 对象（M1 教训：宽松解析优于直接报错）。
    """
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        args = json.loads(raw)
        return args if isinstance(args, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*?\}", raw, re.S)
        if not match:
            return {}
        try:
            args = json.loads(match.group(0))
            return args if isinstance(args, dict) else {}
        except json.JSONDecodeError:
            return {}
