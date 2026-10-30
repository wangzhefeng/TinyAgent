# -*- coding: utf-8 -*-

# ***************************************************
# * File        : client_mcp_packages.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-05-17
# * Version     : 1.0.051720
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

from smolagents import ToolCollection, CodeAgent
from mcp import StdioServerParameters

# global variable
LOGGING_LABEL = __file__.split('/')[-1][:-3]


server_parameters = StdioServerParameters(
    command="uv",
    args=["--quiet", "pubmedmcp@0.1.3"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

with ToolCollection.from_mcp(
    server_parameters, 
    trust_remote_code=True
) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], add_base_tools=True)
    agent.run("Please find a remedy for hangover.")




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
