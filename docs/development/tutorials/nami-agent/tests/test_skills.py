import context
import skills
from permissions import WORKSPACE, PermissionManager


def write_skill(name, text):
    d = WORKSPACE / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text, encoding="utf-8")
    return d


def test_parse_skill():
    meta, body = skills.parse_skill("---\nname: a\ndescription: 做 A: 带冒号\n---\n正文")
    assert meta == {"name": "a", "description": "做 A: 带冒号"} and body == "正文"
    assert skills.parse_skill("无 frontmatter")[0] == {}
    assert skills.parse_skill("---\nname: a\n没闭合")[0] == {}


def test_discover_and_load():
    d = write_skill("git-commit", "---\nname: git-commit\ndescription: 写提交信息\n---\n规则正文")
    write_skill("broken", "---\nname: broken\n---\n没有描述")
    (d / "template.txt").write_text("x")
    found = skills.discover()
    assert "git-commit" in found and "broken" not in found
    assert "git-commit：写提交信息" in skills.skills_section()
    out = skills.load_skill("git-commit")
    assert out.startswith("[skill] git-commit") and "规则正文" in out and "template.txt" in out
    assert skills.load_skill("nope").startswith("Error")


def test_skill_dir_readonly_even_if_user_says_yes():
    pm = PermissionManager(ask=lambda n, a: ("y", ""))
    assert not pm.check("write_file", {"path": "skills/x/SKILL.md", "content": ""}).allowed
    assert pm.check("write_file", {"path": "notes.txt", "content": ""}).allowed


def test_clear_keeps_skill():
    msgs = [{"role": "system", "content": ""},
            {"role": "tool", "tool_call_id": "s", "content": "[skill] x\n正文"}]
    msgs += [{"role": "tool", "tool_call_id": str(i), "content": f"r{i}"} for i in range(5)]
    context.clear_old_tool_results(msgs, keep=1)
    assert msgs[1]["content"].startswith("[skill]")
    assert [m["content"] for m in msgs[2:]] == [context.PLACEHOLDER] * 4 + ["r4"]


def test_agents_md_in_notes():
    (WORKSPACE / "AGENTS.md").write_text("测试命令是 pytest -q", encoding="utf-8")
    assert "pytest -q" in skills.project_notes()
