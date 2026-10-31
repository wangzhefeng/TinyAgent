import agent
import planning
from fake import FakeClient, tool_call
from permissions import PermissionManager, WORKSPACE


def test_plan_mode_blocks_writes_even_if_user_says_yes():
    pm = PermissionManager(ask=lambda n, a: ("a", ""))
    pm.check("write_file", {"path": "x.txt", "content": ""})       # 先"一直允许"写文件
    pm.mode = "plan"
    assert not pm.check("write_file", {"path": "x.txt", "content": ""}).allowed
    assert not pm.check("run_shell", {"command": "ls"}).allowed
    assert pm.check("read_file", {"path": "x.txt"}).allowed         # 读照常
    assert pm.check("submit_plan", {"plan": "1. ..."}).allowed      # 提交计划要问人，这里人说了 a


def test_approved_plan_unlocks_writes():
    c = FakeClient([
        [tool_call("c1", "write_file", {"path": "plan-test.txt", "content": "x"})],   # 计划模式下想写
        [tool_call("c2", "submit_plan", {"plan": "1. 写 plan-test.txt"})],
        [tool_call("c3", "write_file", {"path": "plan-test.txt", "content": "x"})],
        "完成",
    ])
    asked = []
    s = agent.Session("p1", ask=lambda n, a: (asked.append(n) or "y", ""), persist=False)
    agent.run(s, planning.enter_plan_mode(s, "建个文件"), c, log=lambda *_: None)
    tools = [m["content"] for m in s.messages if m["role"] == "tool"]
    assert tools[0].startswith("[权限拒绝] 当前是计划模式")
    assert "用户批准了计划" in tools[1]
    assert tools[2].startswith("已写入")
    assert asked == ["submit_plan", "write_file"]       # 计划模式下的写入根本没问人
    assert s.perms.mode == "normal" and (WORKSPACE / "plan-test.txt").exists()


def test_rejected_plan_stays_in_plan_mode():
    c = FakeClient([[tool_call("c1", "submit_plan", {"plan": "删库"})], "好的，我改计划"])
    s = agent.Session("p2", ask=lambda n, a: ("n", "别删库"), persist=False)
    agent.run(s, planning.enter_plan_mode(s, "清理"), c, log=lambda *_: None)
    assert "别删库" in s.messages[3]["content"] and s.perms.mode == "plan"


def test_update_plan_keeps_only_latest():
    steps1 = [{"step": "读代码", "status": "in_progress"}, {"step": "改代码", "status": "pending"}]
    steps2 = [{"step": "读代码", "status": "completed"}, {"step": "改代码", "status": "in_progress"}]
    c = FakeClient([[tool_call("c1", "update_plan", {"steps": steps1})],
                    [tool_call("c2", "update_plan", {"steps": steps2})], "ok"])
    s = agent.Session("p3", persist=False)
    agent.run(s, "做事", c, log=lambda *_: None)
    tools = [m["content"] for m in s.messages if m["role"] == "tool"]
    assert tools[0] == planning.OLD_PLAN
    assert tools[1].startswith("[plan] 当前计划（1/2 完成）") and "[→] 改代码" in tools[1]
    assert s.plan == steps2


def test_update_plan_validation():
    s = agent.Session("p4", persist=False)
    token = agent.CURRENT.set((s, None, "m", print))
    try:
        two = [{"step": "a", "status": "in_progress"}, {"step": "b", "status": "in_progress"}]
        assert planning.update_plan(two).startswith("Error")
        assert planning.update_plan([{"step": "a", "status": "done"}]).startswith("Error")
    finally:
        agent.CURRENT.reset(token)


def test_subagent_inherits_plan_mode():
    import subagent
    assert "submit_plan" not in subagent.toolset("worker")
    c = FakeClient([[tool_call("p", "delegate", {"task": "写文件", "kind": "worker"})],
                    [tool_call("s", "write_file", {"path": "sub-plan.txt", "content": "x"})],
                    "被拒了", "子 Agent 写不了"])
    s = agent.Session("p5", ask=lambda n, a: ("y", ""), persist=False)
    s.perms.mode = "plan"
    agent.run(s, "试试", c, log=lambda *_: None)
    assert not (WORKSPACE / "sub-plan.txt").exists()
