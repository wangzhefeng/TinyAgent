"""Tests for eval task-contract loading across all domains."""

from __future__ import annotations

from evals.run_eval import DOMAINS, load_tasks


def test_all_domains_have_tasks():
    tasks = load_tasks()
    by_domain: dict[str, int] = {}
    for path, _task in tasks:
        domain = path.parent.parent.name
        by_domain[domain] = by_domain.get(domain, 0) + 1
    assert set(by_domain) == set(DOMAINS)
    assert by_domain["personal"] >= 5
    assert by_domain["learning"] >= 5
    assert by_domain["routine"] >= 3


def test_must_pass_gates_present():
    tasks = {task["task_id"]: task for _path, task in load_tasks()}
    assert tasks["learning-stable-fact"]["scoring"]["audit_required"] is True
    assert tasks["learning-snapshot-frozen"]["scoring"]["frozen_snapshot_preserved"] is True
    assert tasks["learning-reject-oneoff"]["scoring"]["no_ephemeral_write"] is True
    assert tasks["learning-skill-draft-gated"]["scoring"]["unapproved_skill_blocked"] is True
    assert tasks["routine-heartbeat-silent"]["scoring"]["silent_when_no_news"] is True
    assert tasks["routine-meaningful-delivered-once"]["scoring"]["delivered_exactly_once"] is True
    assert tasks["routine-preauth-scope"]["scoring"]["shell_not_preauthorizable"] is True
