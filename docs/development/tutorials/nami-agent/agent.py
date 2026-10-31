"""agent.py —— 第 6 课起：Agent 核心与输入输出分离（第 8 课 MCP，第 9 课子 Agent，第 10 课计划，第 11 课记忆）"""
import contextvars
import json
import os

from context import (truncate_tool_result, clear_old_tool_results, compact,
                     save_session, load_session)
from permissions import PermissionManager
from tools import get_schemas, execute
import skills      # noqa: F401  导入即注册 load_skill（第 5 课）
import scheduler   # noqa: F401  导入即注册 schedule_task 等（第 7 课）
import mcp_client  # 第 8 课
import subagent    # noqa: F401  导入即注册 delegate（第 9 课）
import planning    # 第 10 课
import memory      # 第 11 课

MODEL = os.environ.get("MODEL", "deepseek-chat")
CURRENT = contextvars.ContextVar("current_run", default=None)   # 第 9 课：子 Agent 要知道"谁派的我"
MAX_STEPS = 20
SOFT_LIMIT = 16000
HARD_LIMIT = 24000

BASE_SYSTEM = ("你是一个能使用工具的助手，在用户的工作区内完成任务。"
               "必要时调用工具，完成后用简洁的语言汇报结果。")


def make_client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ["API_KEY"],
                  base_url=os.environ.get("BASE_URL", "https://api.deepseek.com"))


def build_system():
    return (BASE_SYSTEM + skills.project_notes() + skills.skills_section()
            + memory.memory_section())    # 第 11 课：会话开始时的一份快照


class Session:
    """一个会话 = 一份 messages + 一个权限管理器 + 上一次的 token 数
    第 9 课新增：tools 限定能用的工具（None 表示全部），system 可替换，depth 记录是第几层"""

    def __init__(self, name, ask=None, persist=True, tools=None, system=None, depth=0):
        self.name = name
        self.persist = persist
        self.tools = set(tools) if tools is not None else None
        self.depth = depth
        saved = load_session(name) if persist else None
        self.messages = saved or [{"role": "system", "content": ""}]
        self.messages[0] = {"role": "system", "content": system or build_system()}
        self.perms = PermissionManager(ask=ask)
        self.prompt_tokens = 0
        self.plan = []            # 第 10 课：最新一版待办清单

    def schemas(self):
        all_ = get_schemas()
        if self.tools is None:
            return all_
        return [s for s in all_ if s["function"]["name"] in self.tools]

    def save(self):
        if self.persist:
            save_session(self.name, self.messages)


def handle_call(call, perms, allowed=None):
    name = call.function.name
    if allowed is not None and name not in allowed:      # 模型请求了一个没发给它的工具
        return f"Error: 当前不能使用工具 {name}"
    try:
        args = json.loads(call.function.arguments or "{}")
    except json.JSONDecodeError:
        return "Error: 参数不是合法的 JSON"
    decision = perms.check(name, args)
    if not decision.allowed:
        return f"[权限拒绝] {decision.reason}"
    return execute(name, args)


def run(session, user_input, client, model=MODEL, log=print, max_steps=MAX_STEPS):
    token = CURRENT.set((session, client, model, log))
    try:
        return _loop(session, user_input, client, model, log, max_steps)
    finally:
        CURRENT.reset(token)


def _loop(session, user_input, client, model, log, max_steps):
    messages = session.messages
    messages.append({"role": "user", "content": user_input})
    for _ in range(max_steps):
        if session.prompt_tokens > HARD_LIMIT:
            messages[:] = compact(client, model, messages)
        elif session.prompt_tokens > SOFT_LIMIT:
            clear_old_tool_results(messages)

        resp = client.chat.completions.create(model=model, messages=messages, tools=session.schemas())
        session.prompt_tokens = resp.usage.prompt_tokens if resp.usage else 0
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content or ""
        for call in msg.tool_calls:
            log(f"🔧 {call.function.name}({call.function.arguments[:80]})")
            result = handle_call(call, session.perms, session.tools)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": truncate_tool_result(result)})
    return "（达到最大步数，已停止）"


def main():
    client = make_client()
    mcp_client.load_servers()          # 第 8 课：先接入 MCP 工具，再建会话
    session = Session("default")
    while True:
        q = input("你> ").strip()
        if q in ("exit", "quit"):
            break
        if q.startswith("/plan "):                     # 第 10 课：由你决定要不要先出计划
            q = planning.enter_plan_mode(session, q[len("/plan "):])
        print("\n" + run(session, q, client) + "\n")
        session.save()


if __name__ == "__main__":
    main()
