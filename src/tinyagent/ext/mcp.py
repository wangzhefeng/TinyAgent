"""MCPToolSource: mount tools from an MCP server (extra `mcp`).

The python MCP client is async (anyio cancel scopes must enter/exit in the
same task); tinyagent's loop is sync. Bridge: one long-lived *server
coroutine* owns the transport/session lifecycle, while tool calls are
dispatched onto the same background event loop as short tasks.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..core.types import ToolSpec

logger = logging.getLogger(__name__)


class McpTool:
    """One MCP server tool wrapped in the tinyagent Tool protocol."""

    def __init__(self, spec: ToolSpec, call_fn: Callable[[str, dict], str]) -> None:
        self._spec = spec
        self._call_fn = call_fn

    @property
    def spec(self) -> ToolSpec:
        """Declarative spec (mapped from the server's inputSchema)."""
        return self._spec

    def call(self, **kwargs: Any) -> str:
        """Forward the call to the server and stringify text contents."""
        return self._call_fn(self._spec.name, kwargs)


class MCPToolSource:
    """Launch/connect an MCP server over stdio and expose its tools (sync)."""

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> None:
        self.params = StdioServerParameters(
            command=command, args=args or [], env=env, cwd=cwd
        )

    @contextmanager
    def tools(self) -> Iterator[list[McpTool]]:
        """Yield the server's tools as tinyagent Tools; close on exit."""
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=loop.run_forever, daemon=True)
        thread.start()
        ready = threading.Event()
        stop = threading.Event()
        errors: list[Exception] = []
        state: dict[str, Any] = {}

        async def _serve() -> None:
            """Own the async context managers within a single task."""
            try:
                async with stdio_client(self.params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        listed = await session.list_tools()
                        state["specs"] = [
                            ToolSpec(
                                name=t.name,
                                description=(t.description or t.name).strip(),
                                parameters=t.inputSchema
                                or {"type": "object", "properties": {}},
                            )
                            for t in listed.tools
                        ]
                        state["session"] = session
                        ready.set()
                        while not stop.is_set():
                            await asyncio.sleep(0.05)
            except Exception as e:  # noqa: BLE001
                errors.append(e)
                ready.set()

        serve_future = asyncio.run_coroutine_threadsafe(_serve(), loop)
        ready.wait(timeout=60)
        if errors:
            loop.call_soon_threadsafe(loop.stop)
            raise errors[0]

        def call_fn(name: str, arguments: dict) -> str:
            session: ClientSession = state["session"]
            result = asyncio.run_coroutine_threadsafe(
                session.call_tool(name, arguments=arguments), loop
            ).result()
            texts = [
                c.text for c in (result.content or []) if getattr(c, "text", None)
            ]
            return "\n".join(texts) if texts else str(result)

        try:
            yield [McpTool(spec, call_fn) for spec in state["specs"]]
        finally:
            stop.set()
            try:
                serve_future.result(timeout=15)
            except Exception as e:  # noqa: BLE001
                logger.warning("MCP server shutdown issue: %s", e)
            loop.call_soon_threadsafe(loop.stop)
            thread.join(timeout=5)


class PrefixedMcpTool:
    """One MCP server tool re-exposed under the mcp__server__tool name."""

    def __init__(self, spec: ToolSpec, inner: McpTool) -> None:
        self._spec = spec
        self._inner = inner

    @property
    def spec(self) -> ToolSpec:
        """Declarative spec with the prefixed name and origin marker."""
        return self._spec

    def call(self, **kwargs: Any) -> str:
        """Forward the call to the wrapped MCP tool."""
        return self._inner.call(**kwargs)


@contextmanager
def mounted_mcp_tools(
    config_file: str | Path, log: Callable[[str], None] = print
) -> Iterator[list[PrefixedMcpTool]]:
    """Mount every configured server's tools as mcp__server__tool."""
    config = json.loads(Path(config_file).read_text(encoding="utf-8"))
    mounted: list[PrefixedMcpTool] = []
    with ExitStack() as stack:
        for server_name, server_spec in (config.get("servers") or {}).items():
            try:
                source = MCPToolSource(
                    server_spec["command"],
                    server_spec.get("args"),
                    server_spec.get("env"),
                    server_spec.get("cwd"),
                )
                tools = stack.enter_context(source.tools())
            except Exception as error:  # noqa: BLE001
                log(f"[MCP] {server_name} 启动失败：{error}")
                continue
            mounted.extend(
                PrefixedMcpTool(
                    ToolSpec(
                        name=f"mcp__{server_name}__{tool.spec.name}",
                        description=f"[MCP:{server_name}] {tool.spec.description}"[:1000],
                        parameters=tool.spec.parameters,
                    ),
                    tool,
                )
                for tool in tools
            )
            log(f"[MCP] {server_name}：已接入 {len(tools)} 个工具")
        yield mounted


def safe_tool_names(config_file: str | Path) -> set[str]:
    """Prefixed names of tools explicitly marked safe in the MCP config."""
    path = Path(config_file)
    if not path.is_file():
        return set()
    config = json.loads(path.read_text(encoding="utf-8"))
    return {
        f"mcp__{server_name}__{tool_name}"
        for server_name, server_spec in (config.get("servers") or {}).items()
        for tool_name in server_spec.get("safe_tools", [])
    }
