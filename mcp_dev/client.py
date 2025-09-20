# -*- coding: utf-8 -*-

# ***************************************************
# * File        : client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-05-17
# * Version     : 1.0.051719
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# * TODO        : 1.
# ***************************************************

__all__ = []

# python libraries
import os
import sys
ROOT = str(os.getcwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)

from mcp.client.stdio import StdioServerParameters
from smolagents import (
    ToolCollection, 
    CodeAgent, 
    InferenceClientModel
)

# global variable
LOGGING_LABEL = __file__.split('/')[-1][:-3]


# 用户页面客户端
model = InferenceClientModel()

# MCP 服务器
server_parameters = StdioServerParameters(
    command="mcp", 
    args=["run", "server.py"]
)

# 自动发现和注册来自 MCP 服务器的工具
with ToolCollection.from_mcp(
    server_parameters, trust_remote_code=True
) as tool_collection:
    # print("\n".join(f"{t.name}: {t.description}" for t in tool_collection))
    agent = CodeAgent(tools=[*tool_collection.tools], model=model)
    agent.run("What's the weather in Tokyo?")




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
