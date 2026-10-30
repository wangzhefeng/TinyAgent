# -*- coding: utf-8 -*-

# ***************************************************
# * File        : client_remote.py
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

from smolagents.mcp_client import MCPClient

# global variable
LOGGING_LABEL = __file__.split('/')[-1][:-3]


with MCPClient(
    {"url": "https://abidlabs-mcp-tools.hf.space/gradio_api/mcp/sse"}
) as tools:
    # Tools from the remote server are available
    print("\n".join(f"{t.name}: {t.description}" for t in tools))




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
