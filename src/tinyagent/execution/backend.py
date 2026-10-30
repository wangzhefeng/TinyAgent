"""Local and operating-system sandbox execution for shell tools."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionResult:
    """Result of one shell command."""

    exit_code: int
    output: str
    backend: str


class ShellPolicy:
    """Allow only explicitly configured check and inspection commands."""

    def __init__(self, allowed_prefixes: tuple[str, ...] | None = None) -> None:
        self.allowed_prefixes = allowed_prefixes or (
            "uv run pytest",
            "python -m pytest",
            "python -m compileall",
            "git diff",
            "git status",
        )

    def allows(self, command: str) -> bool:
        """Return whether a command matches an allowed prefix."""
        return any(command.startswith(prefix) for prefix in self.allowed_prefixes)


class LocalExecutionBackend:
    """Execute commands on the host without a hard isolation boundary."""

    name = "local"
    sandboxed = False

    def run(self, command: str, workspace: Path, timeout: int = 30) -> ExecutionResult:
        """Run one command with fixed cwd, timeout, and captured output."""
        return self._run_process(["/bin/bash", "-lc", command], workspace, timeout)

    @staticmethod
    def _run_process(command: list[str], workspace: Path, timeout: int) -> ExecutionResult:
        workspace.joinpath(".tmp").mkdir(exist_ok=True)
        workspace.joinpath(".uv-cache").mkdir(exist_ok=True)
        env = os.environ.copy()
        env["TMPDIR"] = str(workspace / ".tmp")
        env["UV_CACHE_DIR"] = str(workspace / ".uv-cache")
        try:
            process = subprocess.run(
                command,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            output = process.stdout + process.stderr
            return ExecutionResult(process.returncode, output, "local")
        except subprocess.TimeoutExpired as error:
            output = (error.stdout or "") + (error.stderr or "")
            return ExecutionResult(124, f"{output}\nCommand timed out after {timeout}s", "local")


class SandboxedExecutionBackend(LocalExecutionBackend):
    """Execute commands with file writes confined to the workspace."""

    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir).expanduser().resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.name = "seatbelt" if sys.platform == "darwin" else "bubblewrap"
        self.sandboxed = True

    def run(self, command: str, workspace: Path, timeout: int = 30) -> ExecutionResult:
        """Run one command inside the operating-system sandbox."""
        if sys.platform == "darwin":
            profile = self._write_seatbelt_profile(workspace)
            command_line = ["sandbox-exec", "-f", str(profile), "/bin/bash", "-lc", command]
        else:
            command_line = [
                "bwrap",
                "--die-with-parent",
                "--ro-bind", "/", "/",
                "--bind", str(workspace), str(workspace),
                "--dev-bind", "/dev", "/dev",
                "--proc", "/proc",
                "--tmpfs", "/tmp",
                "--chdir", str(workspace),
                "/bin/bash", "-lc", command,
            ]
        result = self._run_process(command_line, workspace, timeout)
        return ExecutionResult(result.exit_code, result.output, self.name)

    def _write_seatbelt_profile(self, workspace: Path) -> Path:
        profile = self.state_dir / f"workspace-{uuid.uuid4().hex}.sb"
        profile.write_text(
            "(version 1)\n"
            "(allow default)\n"
            "(deny file-write* (subpath \"/\"))\n"
            f"(allow file-write* (subpath \"{workspace}\"))\n"
            f"(allow file-write* (subpath \"{Path(tempfile.gettempdir())}\"))\n"
            "(allow file-write* (subpath \"/dev/null\"))\n",
            encoding="utf-8",
        )
        return profile


def make_execution_backend(
    state_dir: str | Path,
    prefer_sandbox: bool = True,
) -> LocalExecutionBackend:
    """Create a sandbox when available, otherwise use the confirmed local fallback."""
    if prefer_sandbox:
        if sys.platform == "darwin" and shutil.which("sandbox-exec"):
            return SandboxedExecutionBackend(state_dir)
        if sys.platform.startswith("linux") and shutil.which("bwrap"):
            return SandboxedExecutionBackend(state_dir)
    return LocalExecutionBackend()
