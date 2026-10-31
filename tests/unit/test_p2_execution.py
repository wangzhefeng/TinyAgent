"""Tests for P2 write, fetch, and execution tools."""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

import pytest

from tinyagent.core.tools import ToolRegistry
from tinyagent.execution import (
    LocalExecutionBackend,
    make_execution_backend,
)
from tinyagent.execution import backend as backend_module
from tinyagent.tools import make_workspace_tools


def test_write_and_exact_edit(tmp_path: Path):
    registry = ToolRegistry(make_workspace_tools(tmp_path, LocalExecutionBackend()))
    registry.call("write_file", path="note.txt", content="alpha beta")
    assert registry.call("edit_file", path="note.txt", old="alpha", new="gamma") == "Edited note.txt"
    assert (tmp_path / "note.txt").read_text() == "gamma beta"
    assert "0 times" in registry.call("edit_file", path="note.txt", old="missing", new="x")
    with pytest.raises(PermissionError):
        registry.call("write_file", path="../outside.txt", content="blocked")


def test_shell_policy_blocks_unlisted_commands(tmp_path: Path):
    registry = ToolRegistry(make_workspace_tools(tmp_path, LocalExecutionBackend()))
    result = registry.call("run_shell", command="echo unsafe")
    assert "not allowed by shell policy" in result
    assert not (tmp_path / "unsafe").exists()


def test_local_backend_runs_allowlisted_check(tmp_path: Path):
    (tmp_path / "sample.py").write_text("VALUE = 1\n", encoding="utf-8")
    registry = ToolRegistry(make_workspace_tools(tmp_path, LocalExecutionBackend()))
    result = registry.call("run_shell", command="python -m compileall sample.py")
    assert "[exit 0]" in result


def test_sandbox_blocks_write_outside_workspace(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    backend = make_execution_backend(tmp_path / "state")
    if not backend.sandboxed:
        pytest.skip("No OS sandbox available on this host")
    result = backend.run("echo blocked > ../outside.txt", workspace)
    assert result.exit_code != 0
    assert not (tmp_path / "outside.txt").exists()


def test_sandbox_unavailable_falls_back_to_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_module.shutil, "which", lambda _name: None)
    backend = make_execution_backend(tmp_path / "state")
    assert not backend.sandboxed
    assert backend.name == "local"


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self, _limit: int | None = None) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def test_fetch_url_returns_status_and_capped_body(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        urllib.request, "urlopen",
        lambda _req, timeout=None: _FakeResponse(("x" * 20_000).encode()),
    )
    registry = ToolRegistry(make_workspace_tools(tmp_path))
    result = registry.call("fetch_url", url="https://example.com/page")
    assert result.startswith("[status 200]")
    assert "中间省略" in result


def test_fetch_url_rejects_non_http_schemes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _fail(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("urlopen must not be called")

    monkeypatch.setattr(urllib.request, "urlopen", _fail)
    registry = ToolRegistry(make_workspace_tools(tmp_path))
    for url in ("file:///etc/passwd", "ftp://example.com/file"):
        assert "only http/https" in registry.call("fetch_url", url=url)


def test_fetch_url_reports_http_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _raise(*_args: object, **_kwargs: object) -> object:
        raise urllib.error.HTTPError("https://example.com", 404, "Not Found", None, None)

    monkeypatch.setattr(urllib.request, "urlopen", _raise)
    registry = ToolRegistry(make_workspace_tools(tmp_path))
    assert "HTTP 404" in registry.call("fetch_url", url="https://example.com/missing")
