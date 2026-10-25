"""Import-level smoke tests for the package examples (no API calls)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = (
    Path(__file__).resolve().parents[2] / "packages" / "tinyagent-core" / "examples"
)


@pytest.mark.parametrize(
    "name", sorted(p.stem for p in EXAMPLES_DIR.glob("*.py") if p.stem != "__init__")
)
def test_example_imports_cleanly(name: str) -> None:
    """Every example must import without side effects (main guarded)."""
    spec = importlib.util.spec_from_file_location(
        f"smoke_example_{name}", EXAMPLES_DIR / f"{name}.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "main")
    sys.modules.pop(f"smoke_example_{name}", None)
