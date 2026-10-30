> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P5：总验收、归档与清理

状态：**已完成（2026-10-30）**。本阶段完成真实任务验收、学习资产归档、旧应用删除和项目文档收尾，未替换当前 Hermes/OpenClaw 主力工具。

## 1. 总验收

三个日常任务各运行 3 轮 TinyAgent，全部满足验收：

- **定期监测与摘要**：有效更新正确识别并投递；第三轮使用正确工作区重新运行通过。
- **引用调研报告**：审核后的 `cited-research` Skill 稳定生成带引用结论和未决事项。
- **工作区修复**：三轮均仅修改允许文件，恢复后每轮测试均为 **4/4 通过**。

初次失败来自达到步数上限和一次错误的验收工作区。通过 resume 与干净重跑完成验收，原始失败记录与恢复记录均保留，见 `results/evals/p5/acceptance.md`。

## 2. 学习资产归档

- 私有仓库：`https://github.com/wangzhefeng/TinyAgent-lab`
- 远程分支：`main`
- 验证提交：`4ff9255383efe7296b9ab88d94c594de1e445559`
- 共 101 个跟踪文件，包含 `learn/`、Survey 示例和课程文档；不含 `__pycache__`。
- 归档文档检查通过，远程提交与本地提交一致。

## 3. 旧资产清理

- 删除 `apps/experiment_copilot/` 及旧 `facts.jsonl`、`caliber.jsonl`。
- `learn/` 与 `apps/survey_agent/` 在归档验证后从主仓移除。
- 删除 `docs/30-copilot/`、课程域文档、旧学习地图和相关参考页。
- `evals/run_eval.py` 改为个人任务契约与 fixtures 校验，不再导入 C0/C1/C3。
- `examples/mcp_mount.py` 移除旧项目耦合。
- `pyproject.toml` 移除 course/lab 依赖，保留核心依赖及 `mcp`、`socks` extras。
- README、AGENTS、架构、环境、repo-map、框架、评测和清理记录全部改为个人 Agent 形态。

## 4. 最终门禁

- `uv run pytest tests -q`：**69 项通过**。
- `uv run ruff check .`：通过。
- `uv run python scripts/check_docs.py`：通过。
- `uv run python -m evals.run_eval`：3 个场景、5 个任务契约通过。
- `uv lock` 与 `uv sync --all-extras` 完成，依赖可重建。

## 5. 后续决策

P0–P5 全部完成。是否将 TinyAgent 替换为日常主力工具由用户另行决定；当前 Hermes/OpenClaw 的配置、渠道、凭证和定时任务未改变。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [迁移清单](product-refactor-migration.md) ｜ [P4 执行文档](p4-execution.md) ｜ [清理记录](../30-development/cleanup-log.md)
