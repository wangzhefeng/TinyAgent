"""Quickstart: mount tools from any MCP server (stdio).

Replace ``args``/``cwd`` with your own server launch command; this example
uses the repo's read-only tsproj_ml server from ``learn/level5_ecosystem``.
Requires the ``mcp`` extra: ``pip install tinyagent-core[mcp]``.
"""

import sys
from pathlib import Path

from tinyagent import TinyAgent
from tinyagent.ext.mcp import MCPToolSource

REPO_ROOT = Path(__file__).resolve().parents[1]


def main():
    source = MCPToolSource(
        command=sys.executable,
        args=["-m", "learn.level5_ecosystem.mcp.tsproj_tools_server"],
        cwd=str(REPO_ROOT),
    )
    with source.tools() as tools:
        print(f"[mcp] mounted {len(tools)} tools: {[t.spec.name for t in tools]}")
        agent = TinyAgent(tools=list(tools), codec="react", max_steps=6)
        result = agent.run("tsproj_ml 结果里 lightgbm-dirmo 的回测平均 MAE 是多少？")
        print(f"[answer] {result.text}")


if __name__ == "__main__":
    main()
