# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_part1.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 课程 part1 入口 —— 三封邮件跑完整流水线
# ***************************************************

# python libraries

# local libraries
from learn.level3_langgraph.part1_from_scratch import email_client
from learn.level3_langgraph.part1_from_scratch.agent import ScratchEmailAssistant


def main():
    assistant = ScratchEmailAssistant()
    for email in email_client.INBOX:
        print("=" * 60)
        assistant.handle(email)


if __name__ == "__main__":
    main()
