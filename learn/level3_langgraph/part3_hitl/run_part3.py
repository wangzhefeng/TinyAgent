# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_part3.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part3 入口 —— interrupt 审批（accept/reject）+ 多智能体
# ***************************************************

# python libraries

# third-party libraries
from langchain_core.messages import HumanMessage
from langgraph.types import Command

# local libraries
from learn.level3_langgraph.part1_from_scratch import email_client
from learn.level3_langgraph.part3_hitl.graph import build_graph


def _handle(graph, email, decision: str, thread_id: str) -> None:
    """跑一封邮件；遇到 interrupt 按给定决策恢复。"""
    thread = {"configurable": {"thread_id": thread_id}}
    print(f"\n[邮件] {email['subject']}（审批决策：{decision}）")
    result = graph.invoke(
        {"messages": [HumanMessage(content=(
            f"收到邮件：#{email['id']} from={email['from']} "
            f"subject={email['subject']} body={email['body']}"
        ))]},
        config=thread,
    )
    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(f"  [interrupt] 图已暂停：{payload['question']}")
        print(f"  [interrupt] 待审批草稿 -> {payload['draft']['to']}: "
              f"{payload['draft']['subject']}")
        result = graph.invoke(
            Command(resume={"type": decision}), config=thread
        )
    last = result["messages"][-1]
    print(f"  [结果] {str(last.content)[:220]}")


def main():
    graph = build_graph()

    # 1) 需回信的邮件：write_email 触发 interrupt，人工批准
    _handle(graph, email_client.INBOX[0], "accept", "part3-email1")

    # 2) 运维通知：路由到 ops_agent（不回信，登记提醒，无 interrupt）
    _handle(graph, email_client.INBOX[2], "-", "part3-email3")

    print(f"\n[最终草稿数] {len(email_client.DRAFTS)}")
    for d in email_client.DRAFTS:
        print(f"  - to={d['to']} subject={d['subject']}")


if __name__ == "__main__":
    main()
