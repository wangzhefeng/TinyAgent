# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tools.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part2 —— LangChain @tool 版邮件工具（原生 function calling）
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
    """写一封回复邮件草稿。"""
    return email_client.write_email(to=to, subject=subject, body=body)


@tool
def mark_as_read(email_id: int) -> str:
    """把指定 id 的邮件标记为已读。"""
    return email_client.mark_as_read(email_id)


EMAIL_TOOLS = [search_emails, write_email, mark_as_read]
