"""Execution backends for workspace commands."""

from .backend import (
    ExecutionResult,
    LocalExecutionBackend,
    SandboxedExecutionBackend,
    ShellPolicy,
    make_execution_backend,
)

__all__ = [
    "ExecutionResult",
    "LocalExecutionBackend",
    "SandboxedExecutionBackend",
    "ShellPolicy",
    "make_execution_backend",
]
