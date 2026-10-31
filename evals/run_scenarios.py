"""Run learning and routine scenarios against a real model and grade outcomes."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evals.run_eval import load_tasks
from tinyagent.core.llm import OpenAIChatModel
from tinyagent.core.tools import ToolRegistry
from tinyagent.execution import LocalExecutionBackend
from tinyagent.memory import MemoryManager
from tinyagent.runtime import LocalOutbox, PersonalRuntime, Scheduler, SQLiteStore
from tinyagent.skills import SkillManager
from tinyagent.tools import make_learning_tools, make_workspace_tools

RESULTS_DIR = Path("results/evals")

FLAKY_TEST_CONTEXT = """# Session task

tests/test_order.py fails intermittently: it asserts a total while a background
refresh is still running. The fix is to wait for the refresh before asserting.
This workspace is read-only for this task; report your progress in the answer.
"""

CLAIM_KEYWORDS = {
    "depth": "3",
    "reports": "json",
    "retention": "14",
    "digest": "07:00",
}


def _runtime(
    state: Path,
    workspace: Path,
    model: OpenAIChatModel,
    store: SQLiteStore | None = None,
    writable: bool = False,
) -> PersonalRuntime:
    store = store or SQLiteStore(state / "state.db")
    memory = MemoryManager(state)
    skills = SkillManager(state)
    execution = LocalExecutionBackend() if writable else None
    runtime = PersonalRuntime(
        store=store,
        model=model,
        registry=ToolRegistry([
            *make_workspace_tools(workspace, execution),
            *make_learning_tools(memory, skills, store),
        ]),
        memory=memory,
        skills=skills,
    )
    runtime.scheduler = Scheduler(store, runtime, LocalOutbox(state / "deliveries.jsonl"))
    return runtime


def _session_runs(runtime: PersonalRuntime, session_id: str) -> list[Any]:
    run_ids = {event.run_id for event in runtime.store.session_events(session_id)}
    return [runtime.store.get_run(run_id) for run_id in run_ids]


def _tool_results(runtime: PersonalRuntime, session_id: str, name: str) -> list[str]:
    events = runtime.store.session_events(session_id)
    calls = {
        event.data["call_id"]
        for event in events
        if event.type == "tool_call" and event.data["name"] == name
    }
    return [
        event.data["content"]
        for event in events
        if event.type == "tool_result" and event.data["call_id"] in calls
    ]


def _usage(runtime: PersonalRuntime, session_ids: list[str]) -> dict[str, Any]:
    runs = [run for session in session_ids for run in _session_runs(runtime, session)]
    return {
        "api_calls": sum(run.usage.get("api_calls") or 0 for run in runs),
        "total_tokens": sum(run.usage.get("total_tokens") or 0 for run in runs)
        or (None if runs else None),
        "estimated": any(run.usage.get("estimated") for run in runs),
    }


def run_memory_lifecycle(task: dict, base: Path, out: Path, model: OpenAIChatModel) -> dict:
    """Execute one memory-lifecycle task across two sessions and grade persistence."""
    state = out / task["task_id"]
    workspace = state / "workspace"
    workspace.mkdir(parents=True)
    (workspace / "task.md").write_text(FLAKY_TEST_CONTEXT, encoding="utf-8")
    seed_user = (base / task["input"]["seed_user"]).read_text(encoding="utf-8")
    seed_memory = (base / task["input"]["seed_memory"]).read_text(encoding="utf-8")
    runtime = _runtime(state, workspace, model)
    runtime.memory.user_path.write_text(seed_user, encoding="utf-8")
    runtime.memory.memory_path.write_text(seed_memory, encoding="utf-8")

    started = time.monotonic()
    error = ""
    try:
        runtime.run(task["input"]["prompt"], session_id="s1")
        if task["task_id"] != "learning-reject-oneoff":
            runtime.run(task["input"]["second_session_prompt"], session_id="s2")
    except Exception as err:  # noqa: BLE001
        error = f"{type(err).__name__}: {err}"
    latency_ms = round((time.monotonic() - started) * 1000)

    expected = task["expected"]
    checks: dict[str, bool] = {}
    if task["task_id"] == "learning-reject-oneoff":
        checks["user_unchanged"] = runtime.memory.user_path.read_text(encoding="utf-8") == seed_user
        checks["memory_unchanged"] = (
            runtime.memory.memory_path.read_text(encoding="utf-8") == seed_memory
        )
        checks["no_memory_write_event"] = not any(
            event.type == "memory_write"
            for event in runtime.store.session_events("s1")
        )
    else:
        user_text = runtime.memory.user_path.read_text(encoding="utf-8")
        first_snapshot = runtime.store.get_session_state("s1")["prompt_snapshot"]["memory"]["user"]
        second_snapshot = runtime.store.get_session_state("s2")["prompt_snapshot"]["memory"]["user"]
        checks["file_contains"] = expected["contains"] in user_text
        checks["audit_event"] = any(
            event.type == "memory_write"
            for event in runtime.store.session_events("s1")
        )
        checks["frozen_snapshot"] = first_snapshot == seed_user
        checks["second_session_visible"] = expected["contains"] in second_snapshot
    sessions = ["s1"] + ([] if task["task_id"] == "learning-reject-oneoff" else ["s2"])
    return {
        "task_id": task["task_id"],
        "pass": not error and all(checks.values()),
        "checks": checks,
        "usage": _usage(runtime, sessions),
        "latency_ms": latency_ms,
        "error": error,
    }


def run_session_recall(task: dict, base: Path, out: Path, model: OpenAIChatModel) -> dict:
    """Replay transcripts into FTS and grade a model recall query."""
    state = out / task["task_id"]
    state.mkdir(parents=True)
    workspace = state / "workspace"
    workspace.mkdir()
    store = SQLiteStore(state / "state.db")
    for name, relative in task["input"]["transcripts"].items():
        run = store.create_run(f"seed-{name}", "seed transcript", kind="interactive")
        for line in (base / relative).read_text(encoding="utf-8").splitlines():
            if line.startswith("user:"):
                store.append_event(run.id, "user_input", {"text": line[len("user:"):].strip()})
            elif line.startswith("assistant:"):
                store.append_event(
                    run.id, "assistant_reply", {"text": line[len("assistant:"):].strip()}
                )
    runtime = _runtime(state, workspace, model, store=store)

    started = time.monotonic()
    error = ""
    output = ""
    try:
        output = runtime.run(
            f"{task['input']['query']} Use search_sessions and cite the session id "
            "of the evidence you used.",
            session_id="recall",
        )
    except Exception as err:  # noqa: BLE001
        error = f"{type(err).__name__}: {err}"
    latency_ms = round((time.monotonic() - started) * 1000)

    expected = task["expected"]
    checks = {
        "search_tool_called": bool(_tool_results(runtime, "recall", "search_sessions")),
        "correct_session_cited": expected["hit_session"] in output,
        "answer_contains_fact": expected["hit_contains"] in output,
        "no_wrong_session_cited": not any(
            name in output for name in task["input"]["transcripts"]
            if name != expected["hit_session"]
        ),
    }
    return {
        "task_id": task["task_id"],
        "pass": not error and all(checks.values()),
        "checks": checks,
        "usage": _usage(runtime, ["recall"]),
        "latency_ms": latency_ms,
        "error": error,
    }


def run_skill_gating(task: dict, base: Path, out: Path, model: OpenAIChatModel) -> dict:
    """Grade that a draft skill is unusable before approval and usable after."""
    state = out / task["task_id"]
    state.mkdir(parents=True)
    workspace = state / "workspace"
    workspace.mkdir()
    runtime = _runtime(state, workspace, model)
    name = task["input"]["draft_name"]
    draft_dir = runtime.skills.drafts_dir / name
    draft_dir.mkdir(parents=True)
    (draft_dir / "SKILL.md").write_text(
        (base / task["input"]["draft"]).read_text(encoding="utf-8"), encoding="utf-8"
    )

    started = time.monotonic()
    error = ""
    first_output = ""
    second_output = ""
    try:
        first_output = runtime.run(task["input"]["attempt_prompt"], session_id="gate-1")
        runtime.skills.approve_draft(name)
        second_output = runtime.run(
            "Load the release-notes skill and list its numbered steps.",
            session_id="gate-2",
        )
    except Exception as err:  # noqa: BLE001
        error = f"{type(err).__name__}: {err}"
    latency_ms = round((time.monotonic() - started) * 1000)

    expected = task["expected"]
    before_results = _tool_results(runtime, "gate-1", "load_skill")
    after_results = _tool_results(runtime, "gate-2", "load_skill")
    checks = {
        "load_attempted_before_approval": bool(before_results),
        "not_loadable_before_approval": bool(before_results)
        and all("not found" in result for result in before_results),
        "body_not_followed_before_approval": expected["after_approval_body_contains"]
        not in first_output,
        "loadable_after_approval": any(
            expected["after_approval_body_contains"] in result for result in after_results
        ),
        "steps_listed_after_approval": bool(second_output.strip()),
    }
    return {
        "task_id": task["task_id"],
        "pass": not error and all(checks.values()),
        "checks": checks,
        "usage": _usage(runtime, ["gate-1", "gate-2"]),
        "latency_ms": latency_ms,
        "error": error,
    }


def run_routine_delivery(task: dict, base: Path, out: Path, model: OpenAIChatModel) -> dict:
    """Grade one scheduled heartbeat delivery round including the rerun."""
    state = out / task["task_id"]
    workspace = state / "workspace" / "releases"
    workspace.mkdir(parents=True)
    data = task["input"]
    shutil.copy(base / data["previous"], workspace / "previous.txt")
    shutil.copy(base / data["current"], workspace / "current.txt")
    runtime = _runtime(state, workspace.parent, model)

    prompt = (
        f"Compare releases/previous.txt and releases/current.txt, the captured changelog "
        f"of {data['source_url']}. Read both files. If there is no meaningful change, "
        "respond exactly HEARTBEAT_OK. Otherwise summarize every meaningful change and "
        f"cite {data['source_url']} for each claim."
    )
    started = time.monotonic()
    error = ""
    outcomes: list[dict[str, Any]] = []
    rerun: list[dict[str, Any]] = []
    try:
        runtime.scheduler.add(data["spec"], prompt, kind=data["kind"], immediate=True)
        outcomes = runtime.scheduler.run_due()
        rerun = runtime.scheduler.run_due()
    except Exception as err:  # noqa: BLE001
        error = f"{type(err).__name__}: {err}"
    latency_ms = round((time.monotonic() - started) * 1000)

    outbox_path = state / "deliveries.jsonl"
    deliveries = (
        len(outbox_path.read_text(encoding="utf-8").splitlines())
        if outbox_path.exists() else 0
    )
    output = outcomes[0]["output"] if outcomes else ""
    delivered = [item for item in outcomes if item["delivered"]]
    runs = [runtime.store.get_run(item["run_id"]) for item in outcomes]
    usage = {
        "api_calls": sum(run.usage.get("api_calls") or 0 for run in runs),
        "total_tokens": sum(run.usage.get("total_tokens") or 0 for run in runs)
        or (None if runs else None),
        "estimated": any(run.usage.get("estimated") for run in runs),
    }
    checks = {
        "usage_recorded": usage["api_calls"] >= 1,
        "rerun_no_duplicate": rerun == [],
    }
    if data["current"].endswith("unchanged.txt"):
        checks["silent_when_no_news"] = not delivered and deliveries == 0
    else:
        checks["delivered_exactly_once"] = len(delivered) == 1 and deliveries == 1
        checks["all_claims_covered"] = all(
            keyword in output for keyword in CLAIM_KEYWORDS.values()
        )
        checks["citation_present"] = data["source_url"] in output
    return {
        "task_id": task["task_id"],
        "pass": not error and bool(outcomes) and all(checks.values()),
        "checks": checks,
        "usage": usage,
        "latency_ms": latency_ms,
        "error": error,
    }


def run_unattended_boundary(task: dict, base: Path, out: Path, model: OpenAIChatModel) -> dict:
    """Probe scheduled-run tool permissions deterministically without model calls."""
    state = out / task["task_id"]
    workspace = state / "workspace"
    workspace.mkdir(parents=True)
    shutil.copy(base / task["input"]["workspace"] / task["input"]["workspace_file"], workspace
                / task["input"]["workspace_file"])
    runtime = _runtime(state, workspace, model, writable=True)
    started = time.monotonic()
    error = ""
    attempt_results: dict[str, str] = {}
    try:
        entry = runtime.scheduler.add(
            "every 5m", "boundary probe",
            allow=set(task["input"]["preallow"]), immediate=True,
        )
        run = runtime.create_run("boundary probe", session_id="boundary", kind="scheduled")
        runtime.store.attach_scheduled_run(entry["id"], run.id)
        for attempt in task["input"]["attempts"]:
            attempt_results[attempt["tool"]] = runtime._call_tool(
                run.id, attempt["tool"], attempt["tool"], attempt["arguments"]
            )
    except Exception as err:  # noqa: BLE001
        error = f"{type(err).__name__}: {err}"
    latency_ms = round((time.monotonic() - started) * 1000)

    checks: dict[str, bool] = {}
    for attempt in task["input"]["attempts"]:
        result = attempt_results.get(attempt["tool"], "")
        if attempt["outcome"] == "allowed":
            checks[f"{attempt['tool']}_allowed"] = (
                "Permission denied" not in result and "tool error" not in result
            )
        else:
            checks[f"{attempt['tool']}_rejected"] = "not preauthorized" in result
    checks["no_memory_write"] = not error and not any(
        event.type == "memory_write" for event in runtime.store.list_events(run.id)
    )
    checks["no_skill_draft"] = not any(
        (runtime.skills.drafts_dir).glob("*/SKILL.md")
    )
    checks["no_nested_task"] = len(runtime.store.list_scheduled_tasks()) == 1
    return {
        "task_id": task["task_id"],
        "pass": not error and all(checks.values()),
        "checks": checks,
        "usage": {"api_calls": 0, "total_tokens": None, "estimated": True},
        "latency_ms": latency_ms,
        "error": error,
        "deterministic": True,
    }


RUNNERS = {
    "evals/learning/memory-lifecycle": run_memory_lifecycle,
    "evals/learning/session-recall": run_session_recall,
    "evals/learning/skill-gating": run_skill_gating,
    "evals/routine/routine-delivery": run_routine_delivery,
    "evals/routine/unattended-boundary": run_unattended_boundary,
}


def _percentile(values: list[int], ratio: float) -> int:
    ordered = sorted(values)
    index = max(0, math.ceil(ratio * len(ordered)) - 1)
    return ordered[index]


def main() -> None:
    """Run every learning/routine task for N rounds and write graded reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--only", action="append", help="Restrict to task ids (repeatable)")
    args = parser.parse_args()

    if not os.environ.get("LLM_API_KEY"):
        raise SystemExit("LLM_API_KEY is not set; configure .env first (see docs/usage/guide.md)")
    model = OpenAIChatModel()
    tasks = [
        (path.parent.parent.name, path.parent.name, path.parent, task)
        for path, task in load_tasks()
        if path.parent.parent.name in {"learning", "routine"}
    ]
    if args.only:
        tasks = [item for item in tasks if item[3]["task_id"] in set(args.only)]
    if not tasks:
        raise SystemExit("no learning/routine tasks selected")

    records: list[dict[str, Any]] = []
    for round_number in range(1, args.rounds + 1):
        for domain, scenario, base, task in tasks:
            out = RESULTS_DIR / domain / scenario / f"run-{round_number}"
            if out.exists():
                shutil.rmtree(out)
            report = RUNNERS[f"evals/{domain}/{scenario}"](task, base, out, model)
            report.update({
                "round": round_number,
                "scenario": f"{domain}/{scenario}",
                "model": model.model,
                "ts": datetime.now(UTC).isoformat(),
            })
            (out / "report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            records.append(report)
            status = "PASS" if report["pass"] else "FAIL"
            print(
                f"[round {round_number}] {status} {task['task_id']} "
                f"({report['usage']['api_calls']} calls, {report['latency_ms']} ms)"
                + (f" failed checks: {report['checks']}" if not report["pass"] else "")
            )

    summary: dict[str, Any] = {"model": model.model, "generated_at": datetime.now(UTC).isoformat()}
    task_summaries = []
    for domain, _scenario, _base, task in tasks:
        rows = [row for row in records if row["task_id"] == task["task_id"]]
        latencies = [row["latency_ms"] for row in rows]
        task_summaries.append({
            "task_id": task["task_id"],
            "scenario": rows[0]["scenario"] if rows else "",
            "rounds": len(rows),
            "success_rate": sum(1 for row in rows if row["pass"]) / len(rows) if rows else 0,
            "api_calls": sum(row["usage"]["api_calls"] for row in rows),
            "total_tokens": sum(row["usage"]["total_tokens"] or 0 for row in rows) or None,
            "latency_ms_avg": round(sum(latencies) / len(latencies)) if latencies else None,
            "latency_ms_p95": _percentile(latencies, 0.95) if latencies else None,
            "errors": [row["error"] for row in rows if row["error"]],
        })
    summary["tasks"] = task_summaries
    summary["all_pass"] = all(item["success_rate"] == 1.0 for item in task_summaries)
    target = RESULTS_DIR / "learning-routine" / "summary.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary: {target} all_pass={summary['all_pass']}")
    if not summary["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
