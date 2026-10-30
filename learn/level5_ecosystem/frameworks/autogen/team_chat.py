# -*- coding: utf-8 -*-

# ***************************************************
# * File        : team_chat.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-29
# * Version     : 1.0.112920
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

from agent_role import (
    create_product_manager, 
    create_engineer,
    create_code_reviewer,
    create_user_proxy,
)
from model_client import create_openai_model_client

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]

# model agent
model_agent = create_openai_model_client()

# agent role
product_manager = create_product_manager(model_client=model_agent)
engineer = create_engineer(model_client=model_agent)
code_reviewer = create_code_reviewer(model_client=model_agent)
user_proxy = create_user_proxy(model_agent=model_agent)

# 定义团队聊天和协作规则
team_chat = RoundRobinGroupChat(
    participants=[
        product_manager,
        engineer,
        code_reviewer,
        user_proxy,        
    ],
    termination_conditio=TextMentionTermination("TERMINATE"),
    max_turns=20,
)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
