# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_part2.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part2 入口 —— 状态图 + checkpointer 断点/续跑演示
# ***************************************************

# python libraries

# third-party libraries
from langchain_core.messages import HumanMessage

# local libraries
from learn.level3_langgraph.part1_from_scratch import email_client
from learn.level3_langgraph.part2_langgraph.graph import build_graph


def main():
    graph = build_graph()
    thread = {"configurable": {"thread_id": "course-part2"}}

    email = email_client.INBOX[0]
    print("=" * 60)
    print(f"[轮次 1] 处理邮件: {email['subject']}")
    result = graph.invoke(
        {"messages": [HumanMessage(content=(
            f"收到邮件：#{email['id']} from={email['from']} "
            f"subject={email['subject']} body={email['body']}"
        ))]},
        config=thread,
    )
    print(f"[轮次 1 结果] {result['messages'][-1].content}")

    print("=" * 60)
    print("[轮次 2] 同一 thread 追问（验证 checkpointer 记忆）")
    result = graph.invoke(
        {"messages": [HumanMessage(content=(
            "刚才那封邮件是谁发来的？他要我们明天上午前做什么？不要写新草稿。"
        ))]},
        config=thread,
    )
    print(f"[轮次 2 结果] {result['messages'][-1].content}")
    print(f"[hit_list] {result.get('hit_list')}")
    print(f"[草稿数] {len(email_client.DRAFTS)}")


if __name__ == "__main__":
    main()
