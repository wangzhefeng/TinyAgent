"""Quickstart: mount tools from an MCP server over stdio.

Replace ``command`` and ``args`` with a trusted server launch command. This
example only lists mounted tools; it does not access any external repository.
Requires the ``mcp`` extra: ``pip install tinyagent[mcp]``.
"""

import sys

from tinyagent.ext.mcp import MCPToolSource


def main():
    source = MCPToolSource(
        command=sys.executable,
        args=["-m", "your_mcp_server_module"],
    )
    with source.tools() as tools:
        print(f"[mcp] mounted {len(tools)} tools: {[tool.spec.name for tool in tools]}")


if __name__ == "__main__":
    main()
