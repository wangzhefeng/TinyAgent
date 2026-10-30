"""Workspace tools with shared path and execution boundaries."""

from __future__ import annotations

from pathlib import Path

from ..core.tools import ToolWrapper, tool
from ..execution import LocalExecutionBackend, ShellPolicy

_SAFE_SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".py", ".toml", ".yaml", ".yml"}
_MAX_SHELL_CHARS = 12000


class Workspace:
    """Resolve all tool paths inside one workspace."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def resolve(self, path: str) -> Path:
        """Resolve a user path and reject workspace escapes."""
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = self.root / candidate
        candidate = candidate.resolve()
        if not candidate.is_relative_to(self.root):
            raise PermissionError(f"path outside workspace: {path}")
        return candidate


def _cap_output(text: str) -> str:
    if len(text) <= _MAX_SHELL_CHARS:
        return text
    half = _MAX_SHELL_CHARS // 2
    return f"{text[:half]}\n...[中间省略 {len(text) - _MAX_SHELL_CHARS} 字符]...\n{text[-half:]}"


def make_workspace_tools(
    root: str | Path,
    execution: LocalExecutionBackend | None = None,
    shell_policy: ShellPolicy | None = None,
) -> list[ToolWrapper]:
    """Create read-only tools and optionally safe write/shell tools."""
    workspace = Workspace(root)
    policy = shell_policy or ShellPolicy()

    @tool
    def list_dir(path: str = ".") -> str:
        """List files and directories inside the workspace."""
        directory = workspace.resolve(path)
        entries = sorted(
            f"{entry.name}/" if entry.is_dir() else entry.name
            for entry in directory.iterdir()
        )
        if len(entries) > 200:
            return "\n".join(entries[:200]) + f"\n...（另有 {len(entries) - 200} 项）"
        return "\n".join(entries) or "(empty directory)"

    @tool
    def read_file(path: str) -> str:
        """Read one UTF-8 text file inside the workspace."""
        return workspace.resolve(path).read_text(encoding="utf-8")

    @tool
    def search_text(query: str, path: str = ".") -> str:
        """Search literal text in workspace text files and return matching lines."""
        base = workspace.resolve(path)
        files = [base] if base.is_file() else sorted(base.rglob("*"))
        hits: list[str] = []
        for file in files:
            if not file.is_file() or file.suffix.lower() not in _SAFE_SUFFIXES:
                continue
            try:
                lines = file.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError):
                continue
            for lineno, line in enumerate(lines, 1):
                if query in line:
                    hits.append(f"{file.relative_to(workspace.root)}:{lineno}:{line.strip()}")
                    if len(hits) >= 50:
                        return "\n".join(hits)
        return "\n".join(hits) or "No matches"

    tools = [list_dir, read_file, search_text]
    if execution is None:
        return tools

    @tool
    def write_file(path: str, content: str) -> str:
        """Write a complete UTF-8 file inside the workspace after approval."""
        target = workspace.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {target.relative_to(workspace.root)} ({len(content)} characters)"

    @tool
    def edit_file(path: str, old: str, new: str) -> str:
        """Replace exactly one occurrence of old text inside a workspace file."""
        target = workspace.resolve(path)
        text = target.read_text(encoding="utf-8")
        matches = text.count(old)
        if matches != 1:
            return f"Error: old text occurs {matches} times; provide more context for exactly one match"
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return f"Edited {target.relative_to(workspace.root)}"

    @tool
    def run_shell(command: str, timeout: int = 30) -> str:
        """Run an allowlisted shell command with approval, timeout, and output caps."""
        if not policy.allows(command):
            return f"Error: command not allowed by shell policy: {command}"
        result = execution.run(command, workspace.root, timeout)
        output = _cap_output(result.output)
        return f"[backend:{result.backend}] [exit {result.exit_code}]\n{output}"

    return [*tools, write_file, edit_file, run_shell]
