
# ***************************************************
# * File        : run_eval.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : M5 评测 harness —— 三版本 Copilot 同一评测集对照
# ***************************************************

# python libraries
import json
import time
from datetime import datetime
from pathlib import Path

# global variable
EVALS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = Path("results/evals")


def load_dataset() -> list[dict]:
    """加载 evals/datasets/ 下全部场景文件（真 JSONL，逐行解析，按 id 排序）。"""
    items: list[dict] = []
    for path in sorted((EVALS_DIR / "datasets").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                items.append(json.loads(line))
    return sorted(items, key=lambda x: x["id"])


def make_runner(version: str):
    """按版本构造 answer(question) -> str。"""
    if version == "c0":
        from apps.experiment_copilot.copilot0.run_react import answer
    elif version == "c1":
        from apps.experiment_copilot.copilot1.run_framework import answer
    elif version == "c3":
        from apps.experiment_copilot.copilot3.multi_agent import run_pipeline

        def answer(question):  # noqa: ANN001, ANN202
            return run_pipeline(question)

    else:
        raise ValueError(f"unknown version: {version}")
    return answer


def score(text: str, facts: list[str]) -> list[bool]:
    """事实命中：期望子串是否出现在回答中。"""
    return [f in text for f in facts]


def main(versions: tuple[str, ...] = ("c0", "c1", "c3")) -> None:
    """跑全部版本并写对照报告（results/evals/，遵循 outputs 约定）。"""
    dataset = load_dataset()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for version in versions:
        answer = make_runner(version)
        for item in dataset:
            t0 = time.time()
            try:
                text = answer(item["question"])
                hits = score(text, item["expected_facts"])
                err = ""
            except Exception as e:  # noqa: BLE001
                text, hits, err = "", [False] * len(item["expected_facts"]), str(e)
            duration = time.time() - t0
            rows.append(
                {
                    "version": version,
                    "id": item["id"],
                    "scenario": item["scenario"],
                    "hits": hits,
                    "hit_rate": sum(hits) / len(hits),
                    "duration_s": round(duration, 1),
                    "error": err,
                }
            )
            print(
                f"[{version}] q{item['id']}({item['scenario']}) 命中 {sum(hits)}/{len(hits)} "
                f"({duration:.0f}s) {err[:60]}"
            )

    # 汇总与报告
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = RESULTS_DIR / f"comparison-{ts}.md"
    lines = [
        "# Copilot 三版本对照（M5 评测）",
        "",
        f"- 时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 评测集：`evals/datasets/*.jsonl`（{len(dataset)} 题，按场景分文件：facts 取数事实 / caliber 口径综合）",
        "",
        "## 汇总",
        "",
        "| 版本 | 平均事实命中率 | 平均耗时(s) | 失败题数 |",
        "|---|---|---|---|",
    ]
    for version in versions:
        vr = [r for r in rows if r["version"] == version]
        hit = sum(r["hit_rate"] for r in vr) / len(vr)
        dur = sum(r["duration_s"] for r in vr) / len(vr)
        fails = sum(1 for r in vr if r["error"])
        lines.append(
            f"| {version} | {hit:.0%} | {dur:.0f} | {fails} |"
        )
    lines += ["", "## 明细", "", "| 版本 | 题 | 场景 | 命中 | 耗时(s) | 错误 |", "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['version']} | {r['id']} | {r['scenario']} | {sum(r['hits'])}/{len(r['hits'])} "
            f"| {r['duration_s']} | {r['error'][:40]} |"
        )
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"[report] {report}")


# 测试代码 main 函数
if __name__ == "__main__":
    main()
