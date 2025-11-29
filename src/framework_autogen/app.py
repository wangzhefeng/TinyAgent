# -*- coding: utf-8 -*-

# ***************************************************
# * File        : app.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-29
# * Version     : 1.0.112921
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
import asyncio

from autogen_agentchat.teams import Console

from team_chat import team_chat

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


async def run_software_development_team():
    """
    初始化客户端和智能体
    """
    # 定义任务描述
    task = """我们需要开发一个比特币价格显示应用，具体要求如下：
    核心功能：
    - 实时显示比特币当前价格（USD）
    - 显示24小时价格变化趋势（涨跌幅和涨跌额）
    - 提供价格刷新功能

    技术要求：
    - 使用 Streamlit 框架创建 Web 应用
    - 界面简洁美观，用户友好
    - 添加适当的错误处理和加载状态

    请团队协作完成这个任务，从需求分析到最终实现。"""
    
    # 异步执行团队写作，并流式输出对话过程
    result = await Console(
        team_chat.run_stream(
            task=task
        )
    )

    return result




# 测试代码 main 函数
def main():
    result = asyncio.run(run_software_development_team())

if __name__ == "__main__":
    main()
