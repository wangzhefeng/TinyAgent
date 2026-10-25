# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tools.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part3 —— 含审批动作与运维助手的工具集
# ***************************************************

# python libraries

# third-party libraries
from langchain_core.tools import tool

# local libraries
from learn.level3_langgraph.part1_from_scratch import email_client


@tool
def search_emails(query: str) -> str:
    """按关键词检索收件箱邮件（标题/正文/发件人），返回命中摘要。"""
    return email_client.search_emails(query)


@tool
def write_email(to: str, subject: str, body: str) -> str:
    """提交一封回复邮件草稿（将触发人工审批 interrupt）。"""
    return email_client.write_email(to=to, subject=subject, body=body)


@tool
def mark_as_read(email_id: int) -> str:
    """把指定 id 的邮件标记为已读。"""
    return email_client.mark_as_read(email_id)


@tool
def schedule_reminder(when: str, what: str) -> str:
    """运维助手：登记一条提醒（when 如 周六 08:00，what 为事项）。"""
    return f"提醒已登记：{when} - {what}"


RESPONSE_TOOLS = [search_emails, write_email, mark_as_read]
OPS_TOOLS = [schedule_reminder, mark_as_read]
