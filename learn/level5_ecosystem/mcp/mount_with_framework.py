# -*- coding: utf-8 -*-

# ***************************************************
# * File        : mount_with_framework.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : M4 核心验收——tinyagent 挂载自建 MCP server 并回答真实问题
# ***************************************************

# python libraries
import sys
from pathlib import Path

# third-party libraries
from tinyagent import TinyAgent
from tinyagent.ext.mcp import MCPToolSource

# global variable
REPO_ROOT = str(Path(__file__).resolve().parents[3])


def main():
    """
    以 stdio 拉起 tsproj-ml-readonly MCP server，把其工具挂到 TinyAgent。
    工具与 @tool 函数在同一个 ToolRegistry 里一视同仁（ADR-0005）。
    """
    source = MCPToolSource(
        command=sys.executable,
        args=["-m", "learn.level5_ecosystem.mcp.tsproj_tools_server"],
        cwd=REPO_ROOT,
    )
    with source.tools() as mcp_tools:
        print(f"[mcp] 已挂载 {len(mcp_tools)} 个工具："
              f"{[t.spec.name for t in mcp_tools]}")
        agent = TinyAgent(tools=list(mcp_tools), codec="react", max_steps=6)
        result = agent.run(
            "tsproj_ml 的实验结果里，lightgbm-dirmo 的回测平均 MAE 和 RMSE 是多少？"
            "它与 naive 结果相比口径是否一致？"
        )
        print(f"[回答] {result.text}")
        print(f"[轮数] {result.steps}")


if __name__ == "__main__":
    main()
