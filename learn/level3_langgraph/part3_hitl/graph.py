# -*- coding: utf-8 -*-

# ***************************************************
# * File        : graph.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part3 —— interrupt 人工审批 + 多智能体路由
# ***************************************************

# python libraries
import operator
from typing import Annotated, Literal, TypedDict

# third-party libraries
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt

# local libraries
from learn.level3_langgraph.part2_langgraph.llm import make_llm
from learn.level3_langgraph.part3_hitl.tools import OPS_TOOLS, RESPONSE_TOOLS


class Part3State(TypedDict):
    """part3 状态：在 part2 基础上增加 pending_draft（待审批草稿）。"""

    messages: Annotated[list, add_messages]
    hit_list: Annotated[list[str], operator.add]
    triage_label: str
    pending_draft: dict


TRIAGE_SYSTEM = (
    "你是邮件分诊助手，把邮件分给两个智能体之一，只输出一个标签："
    "respond=需要回信（交响应智能体）；"
    "notify=运维/日程/维护类通知（交运维智能体，不回信）；"
    "ignore=营销噪音。"
)

RESPONSE_SYSTEM = (
    "你是响应智能体：检索必要上下文后调用 write_email 提交一封专业简洁的中文"
    "回复草稿（草稿会经人工审批后才生效）。完成后总结你的动作。"
    "工具失败时如实调整，不要编造。"
)

OPS_SYSTEM = (
    "你是运维智能体：处理集群维护/日程类通知，不写回信；"
    "如对用户有价值，调用 schedule_reminder 登记提醒，并给出一段摘要。"
)


def triage_node(state: Part3State) -> dict:
    """分诊到三个后继之一。"""
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


def route_after_triage(
    state: Part3State,
) -> Literal["response_agent", "ops_agent", "__end__"]:
    """多智能体路由：respond→响应，notify→运维，ignore→结束。"""
    if state["triage_label"] == "respond":
        return "response_agent"
    if state["triage_label"] == "notify":
        return "ops_agent"
    return END


def _run_tool(tc: dict, tools: list) -> str:
    """执行一次工具调用；对 write_email 触发人工审批 interrupt。"""
    tool = next((t for t in tools if t.name == tc["name"]), None)
    if tool is None:
        return f"unknown tool: {tc['name']}"
    args = dict(tc["args"])
    if tc["name"] == "write_email":
        # —— 人工审批（HITL）：interrupt 暂停图，等待 Command(resume=...) ——
        decision = interrupt(
            {"question": "是否批准发送以下草稿？", "draft": args}
        )
        dtype = (decision or {}).get("type", "accept")
        if dtype == "reject":
            return "人工审批：用户拒绝发送，草稿作废。请改口告知用户已按要求不回信。"
        if dtype == "edit":
            args = decision.get("edited_args", args)
    try:
        return str(tool.invoke(args))
    except Exception as e:  # noqa: BLE001
        return f"tool error: {e}"


def response_agent_node(state: Part3State, config) -> dict:  # noqa: ANN001
    """响应智能体：原生工具循环；write_email 处经 interrupt 审批。"""
    llm = make_llm().bind_tools(RESPONSE_TOOLS)
    messages = [SystemMessage(content=RESPONSE_SYSTEM), *state["messages"]]
    pending: dict = {}
    for _ in range(4):
        reply = llm.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            break
        for tc in reply.tool_calls:
            observation = _run_tool(tc, RESPONSE_TOOLS)
            print(f"  [tool] {tc['name']} -> {observation[:60]}")
            messages.append(
                ToolMessage(content=observation, tool_call_id=tc["id"] or "")
            )
            if tc["name"] == "write_email":
                pending = dict(tc["args"])
    hit_update = (
        ["alice@tsproj.org"]
        if "alice@tsproj.org" in str(state["messages"][0].content)
        and "alice@tsproj.org" not in state.get("hit_list", [])
        else []
    )
    return {"messages": messages[1:], "hit_list": hit_update, "pending_draft": pending}


def ops_agent_node(state: Part3State, config) -> dict:  # noqa: ANN001
    """运维智能体：摘要 + 登记提醒，不回信。"""
    llm = make_llm().bind_tools(OPS_TOOLS)
    messages = [SystemMessage(content=OPS_SYSTEM), *state["messages"]]
    for _ in range(3):
        reply = llm.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            break
        for tc in reply.tool_calls:
            observation = _run_tool(tc, OPS_TOOLS)
            print(f"  [tool] {tc['name']} -> {observation[:60]}")
            messages.append(
                ToolMessage(content=observation, tool_call_id=tc["id"] or "")
            )
    return {"messages": messages[1:]}


def build_graph():
    """组装多智能体图：triage →（响应 | 运维 | 结束），带 checkpointer。"""
    builder = StateGraph(Part3State)
    builder.add_node("triage", triage_node)
    builder.add_node("response_agent", response_agent_node)
    builder.add_node("ops_agent", ops_agent_node)
    builder.add_edge(START, "triage")
    builder.add_conditional_edges("triage", route_after_triage)
    builder.add_edge("response_agent", END)
    builder.add_edge("ops_agent", END)
    return builder.compile(checkpointer=MemorySaver())
