# -*- coding: utf-8 -*-

# ***************************************************
# * File        : graph.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part2 —— LangGraph 状态图重建邮件助手
# ***************************************************

# python libraries
import operator
from typing import Annotated, Literal, TypedDict

# third-party libraries
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

# local libraries
from learn.level3_langgraph.part2_langgraph.llm import make_llm
from learn.level3_langgraph.part2_langgraph.tools import EMAIL_TOOLS


class EmailState(TypedDict):
    """图状态：短期记忆（messages 自动合并）+ 长期记忆（hit_list 累积）。"""

    messages: Annotated[list, add_messages]
    hit_list: Annotated[list[str], operator.add]
    triage_label: str


TRIAGE_SYSTEM = (
    "你是邮件分诊助手。对用户输入描述的邮件分类，只输出一个标签："
    "respond（需回复/行动）、notify（知晓即可）、ignore（噪音）。"
)

AGENT_SYSTEM = (
    "你是一位资深研究工程师的邮件助理。必要时检索邮件上下文，"
    "并调用 write_email 提交一封得体、专业、简洁的中文回复草稿，"
    "最后用一段话总结你做了什么。工具调用失败时如实调整，不要编造结果。"
)


def triage_node(state: EmailState) -> dict:
    """分诊节点：respond / notify / ignore。"""
    llm = make_llm(temperature=0.0)
    reply = llm.invoke(
        [
            SystemMessage(content=TRIAGE_SYSTEM),
            HumanMessage(content=str(state["messages"][-1].content)),
        ]
    )
    label = (reply.content or "").strip().lower()
    tag = next((t for t in ("respond", "notify", "ignore") if t in label), "notify")
    print(f"  [triage] -> {tag}")
    return {"triage_label": tag}


def route_after_triage(state: EmailState) -> Literal["response_agent", "__end__"]:
    """条件边：只有 respond 进入响应智能体。"""
    return "response_agent" if state["triage_label"] == "respond" else END


def response_agent_node(state: EmailState, config) -> dict:  # noqa: ANN001
    """响应智能体节点：原生 function calling 工具循环（≤4 轮）。"""
    llm = make_llm().bind_tools(EMAIL_TOOLS)
    messages = [
        SystemMessage(content=AGENT_SYSTEM),
        *state["messages"],
    ]
    hit_list_update: list[str] = []
    for _ in range(4):
        reply = llm.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            break
        for tc in reply.tool_calls:
            tool = next((t for t in EMAIL_TOOLS if t.name == tc["name"]), None)
            if tool is None:
                observation = f"unknown tool: {tc['name']}"
            else:
                try:
                    observation = str(tool.invoke(tc["args"]))
                except Exception as e:  # noqa: BLE001
                    observation = f"tool error: {e}"
            print(f"  [tool] {tc['name']}({tc['args']}) -> {observation[:60]}")
            from langchain_core.messages import ToolMessage

            messages.append(
                ToolMessage(content=observation, tool_call_id=tc["id"] or "")
            )
    # 长期记忆：记录需要响应的发件人（从首条用户消息提取）
    first = state["messages"][0].content if state["messages"] else ""
    for addr in ("alice@tsproj.org", "bob@platform.team"):
        if addr in str(first) and addr not in state.get("hit_list", []):
            hit_list_update.append(addr)
    # 只回传新增消息（add_messages 会合并）
    return {"messages": messages[1:], "hit_list": hit_list_update}


def build_graph():
    """组装：START → triage →(条件)→ response_agent → END，带 MemorySaver。"""
    builder = StateGraph(EmailState)
    builder.add_node("triage", triage_node)
    builder.add_node("response_agent", response_agent_node)
    builder.add_edge(START, "triage")
    builder.add_conditional_edges("triage", route_after_triage)
    builder.add_edge("response_agent", END)
    return builder.compile(checkpointer=MemorySaver())
