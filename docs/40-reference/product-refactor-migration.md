> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# 个人 Agent 迁移与清理清单

状态：**已完成（2026-10-30）**。实施与门禁见[重构总纲](refactor-plan-product.md)和 [P5 执行文档](p5-execution.md)。

## 1. 迁移原则

- v1.0 采用应用优先的新实现，不保留旧公共 API 兼容门面，但提供内部模块和行为对照。
- P0 先扫描引用，P1–P4 小步建设，P5 才删除旧应用和外迁学习资产。
- 新场景不得读取 `~/projects/tsproj_ml`；旧数据不作为新基线。
- 现有 OpenClaw/Hermes 继续作为主力，新项目影子运行，验收后由用户决定是否迁移日常使用。
- 所有删除使用显式清单；无法确认归属的文件保留并记录，不猜测删除。

## 2. 资产处置

| 资产 | 动作 | 时点与说明 |
|---|---|---|
| `apps/experiment_copilot/` | **直接删除** | P5；D9/D10，不迁移、不运行、不作验收 |
| `evals/datasets/facts.jsonl`、`caliber.jsonl` | **直接删除** | P5；属于旧外部项目评测 |
| `evals/run_eval.py` | 重写 | 由 personal/learning/routine harness 替代，不保留 C0/C1/C3 入口 |
| `apps/survey_agent/` | 迁至 `TinyAgent-lab` | P0 已确认无旧外部项目依赖；作为旧框架毕业示例归档，共 4 个跟踪文件 |
| `learn/` | 迁至 `TinyAgent-lab` | P5；保留可运行历史，主仓删除前验证归档完整性 |
| 课程文档与课程测试 | 归档或重写 | 课程叙述外迁；MCP、部署等内容改为个人 Agent 用户文档 |
| `docs/30-copilot/` | 删除并清理索引 | P5；同步根 README、docs 索引、repo-map 与 cleanup-log |
| 循环、codec、MCP、Memory、Swarm | 语义已选择性重写，旧实现已归档 | 个人 Agent 使用原生工具调用并保留 MCP；多 Agent、双 codec 与旧 Memory 已淘汰 |
| `FileSessionStore`、`JsonlTracer` | 已替换并归档 | SQLite + FTS5 为事实源，JSONL 仅用于导出 |
| `TinyAgent.run` 及旧公共导出 | 已淘汰并归档到 `legacy-v0/` | v1.0 仅提供个人 Agent 公共 API，不设通用框架兼容层 |
| README、AGENTS、pyproject | 重写 | 去除教学、旧载体和 course/lab 依赖，改为单用户应用配置 |
| `examples/` | 已归档并删除 | CLI 用法保留在根 README，历史示例位于 `TinyAgent-lab/legacy-v0/` |

## 3. P0 扫描结果（2026-10-30）

- `learn/` 共 84 个 git 跟踪文件，全部进入 `TinyAgent-lab` 归档范围。
- `apps/experiment_copilot/` 共 37 个跟踪文件，按 D9/D10 直接删除。
- `apps/survey_agent/` 共 3 个跟踪文件，无旧外部项目依赖，作为旧框架毕业示例归档。
- `evals/run_eval.py` 直接导入 C0/C1/C3，必须重写；`examples/mcp_mount.py` 和 `learn/level5_ecosystem/mcp/` 含旧项目引用，分别重写或随学习资产归档。
- README、AGENTS、architecture、repo-map、environment、testing、outputs、project-summary 和 docs 索引存在旧定位引用，P5 同步重写。
- 已创建并验证私有归档仓库 `https://github.com/wangzhefeng/TinyAgent-lab`；归档提交为 `4ff9255383efe7296b9ab88d94c594de1e445559`，共 101 个跟踪文件。

## 4. P0 逐文件核对

1. 用引用搜索确认旧应用、旧评测、课程依赖和 `sys.path` 耦合，形成最终文件清单。
2. 已创建 `https://github.com/wangzhefeng/TinyAgent-lab` 私有仓库；首次推送使用 `main` 分支，保留历史和文档链接。
3. 将旧模块分为“保留语义 / 替换 / 后置 / 删除”，写入 v1.0 迁移指南。
4. 检查 `pyproject.toml`：移除教学元数据、course/lab 组；核心只保留必要依赖，MCP 等继续走 extras。
5. 检查 CI、tests、scripts 和 docs 索引，确保没有删除后才暴露的隐藏引用。
6. 按 [P0 执行文档](p0-execution.md) 建立定期监测与摘要、工作区任务、引用调研报告，不复制凭证或私人原文。

## 5. 实施与回滚

- 先提交 `TinyAgent-lab` 并验证文件数、关键入口和 git 历史，再删除主仓学习资产。
- 旧 Copilot 资产直接删除，不与学习资产混同归档；删除前再次确认清单。
- 数据迁移遵循 ADR-0009 的备份、校验和导出要求；不以数据库存在作为迁移成功。
- 每阶段独立提交并用 `git revert` 回滚；P5 清理必须在新场景全绿后单独提交。
- 影子运行失败不影响现有 Hermes/OpenClaw；不得在新项目验收前切换默认模型凭证、渠道或定时任务。

## 6. 完成定义

- 主仓无旧外部项目运行依赖和 C0/C1/C3 入口。
- 个人任务、学习循环、例行自动化及三门禁全部通过。
- 文档无失效链接，无教学或旧载体定位；清理记录、repo-map、架构和测试文档一致。
- 归档资产可定位、旧 JSONL 可回放、影子验收有记录；是否替换主力工具由用户另行决定。

## 相关

- [P0 执行文档](p0-execution.md) ｜ [重构总纲](refactor-plan-product.md) ｜ [ADR-0009](../10-framework/adr/0009-event-store-sqlite.md) ｜ [应用与评测规范](../20-evals/application-scenarios.md)
