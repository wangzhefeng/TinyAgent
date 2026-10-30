# -*- coding: utf-8 -*-

# ***************************************************
# * File        : email_client.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part1 —— 内存版邮件客户端（离线 mock，无 Gmail OAuth）
# ***************************************************

# python libraries
from typing import Dict, List

# global variable
INBOX: List[Dict] = [
    {
        "id": 1,
        "from": "alice@tsproj.org",
        "subject": "本周 dirmo 回测结果评审",
        "body": "dirmo 组的 MAE 看起来比 naive 高不少，评审会想请你确认两者是否同口径，"
        "并给一页结论。明天上午前回复。",
        "read": True,
    },
    {
        "id": 2,
        "from": "newsletter@ml-weekly.cn",
        "subject": "ML Weekly 第 200 期",
        "body": "本期专题：时序基础模型的工程化落地……（营销邮件）",
        "read": False,
    },
    {
        "id": 3,
        "from": "bob@platform.team",
        "subject": "GPU 集群维护通知",
        "body": "本周六 02:00-08:00 集群维护，期间任务将暂停调度，请提前安排。",
        "read": False,
    },
]

DRAFTS: List[Dict] = []


def search_emails(query: str) -> str:
    """按关键词在收件箱检索邮件（标题+正文），返回命中邮件摘要。"""
    q = query.lower()
    hits = [
        m for m in INBOX
        if q in m["subject"].lower() or q in m["body"].lower() or q in m["from"].lower()
    ]
    if not hits:
        return "没有命中邮件。"
    return "\n".join(
        f"#{m['id']} from={m['from']} subject={m['subject']} "
        f"read={m['read']} body={m['body'][:80]}"
        for m in hits
    )


def write_email(to: str, subject: str, body: str) -> str:
    """写一封邮件草稿（demo 环境：落入 DRAFTS，不真实发送）。"""
    DRAFTS.append({"to": to, "subject": subject, "body": body})
    return f"草稿已保存：to={to} subject={subject}"


def mark_as_read(email_id: int) -> str:
    """把指定 id 的邮件标记为已读。"""
    for m in INBOX:
        if m["id"] == email_id:
            m["read"] = True
            return f"#{email_id} 已标记为已读。"
    return f"#{email_id} 不存在。"
