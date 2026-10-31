"""Validate personal-agent task contracts and source fixtures across domains."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
DOMAINS = ("personal", "learning", "routine")
REQUIRED_FIELDS = {"task_id", "input", "allowed_actions", "expected", "scoring", "fixture_version"}
FILE_KEYS = ("previous", "current", "draft", "seed_user", "seed_memory")


def load_tasks() -> list[tuple[Path, dict]]:
    """Load and validate all scenario task definitions across domains."""
    tasks: list[tuple[Path, dict]] = []
    for domain in DOMAINS:
        for path in sorted(EVALS_DIR.glob(f"{domain}/*/tasks.jsonl")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                task = json.loads(line)
                missing = REQUIRED_FIELDS - task.keys()
                if missing:
                    raise ValueError(f"{path}:{lineno} missing fields: {sorted(missing)}")
                _validate_inputs(path.parent, task)
                tasks.append((path, task))
    if not tasks:
        raise ValueError("no tasks found")
    return tasks


def _validate_inputs(base: Path, task: dict) -> None:
    data = task["input"]
    for key in FILE_KEYS:
        if key in data and not (base / data[key]).is_file():
            raise ValueError(f"{task['task_id']}: missing input file {data[key]}")
    for name, relative in data.get("transcripts", {}).items():
        if not (base / relative).is_file():
            raise ValueError(f"{task['task_id']}: missing transcript {name}: {relative}")
    workspace = data.get("workspace")
    if workspace is not None:
        if not (base / workspace).is_dir():
            raise ValueError(f"{task['task_id']}: missing workspace {workspace}")
        if "workspace_file" in data and not (base / workspace / data["workspace_file"]).is_file():
            raise ValueError(f"{task['task_id']}: missing workspace file {data['workspace_file']}")
    for relative in data.get("allowed_files", []):
        if not (base / "fixture" / relative).is_file():
            raise ValueError(f"{task['task_id']}: missing allowed file {relative}")
    if "sources" in data:
        sources = json.loads((base / data["sources"]).read_text(encoding="utf-8"))
        for source in sources.values():
            if not (base / source["path"]).is_file():
                raise ValueError(f"{task['task_id']}: missing source {source['path']}")


def main() -> None:
    """Validate task files and print a compact manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List task IDs")
    args = parser.parse_args()
    tasks = load_tasks()
    if args.list:
        for _path, task in tasks:
            print(task["task_id"])
        return
    scenarios = sorted({f"{path.parent.parent.name}/{path.parent.name}" for path, _task in tasks})
    print(f"OK: {len(tasks)} tasks across {len(scenarios)} scenarios: {', '.join(scenarios)}")


if __name__ == "__main__":
    main()
